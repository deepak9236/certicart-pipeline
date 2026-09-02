from collections.abc import AsyncIterator
from datetime import UTC, datetime

import pytest
from pydantic import AnyHttpUrl

from collectors import ReviewPaginationError, collect_one, collect_reviews
from reviews import CollectedReview, ReviewCollectionPage, ReviewTarget
from sources import ParsedProduct, RawSourceRecord


class FakeAdapter:
    name = "fake"

    async def discover(self) -> AsyncIterator[str]:
        yield "SKU-1"

    async def fetch(self, source_product_id: str) -> RawSourceRecord:
        return RawSourceRecord(
            source=self.name,
            source_product_id=source_product_id,
            category="laptop",
            source_url="https://example.com/product",
            observed_at=datetime.now(UTC),
            payload={"title": "Laptop"},
            content_hash="0123456789abcdef",
        )

    def parse(self, record: RawSourceRecord) -> ParsedProduct:
        return ParsedProduct(
            source=self.name,
            source_product_id=record.source_product_id,
            category=record.category,
            title="Laptop",
            brand="Generic",
            model_name="Laptop",
            price_paise=5000000,
            source_url=AnyHttpUrl("https://example.com/product"),
            observed_at=record.observed_at,
        )


class MemorySink:
    def __init__(self) -> None:
        self.records: list[RawSourceRecord] = []

    async def append(self, record: RawSourceRecord) -> None:
        self.records.append(record)


class MemoryReviewSink:
    def __init__(self) -> None:
        self.reviews: list[CollectedReview] = []

    async def append(self, review: CollectedReview) -> None:
        self.reviews.append(review)


class FakeReviewAdapter:
    name = "amazon"

    def __init__(self, pages: dict[str | None, ReviewCollectionPage]) -> None:
        self.pages = pages
        self.calls: list[tuple[str | None, int]] = []

    async def fetch_reviews(
        self,
        source_product_id: str,
        *,
        cursor: str | None,
        limit: int,
    ) -> ReviewCollectionPage:
        assert source_product_id == "B0EXAMPLE1"
        self.calls.append((cursor, limit))
        return self.pages[cursor]


def review(review_id: str) -> CollectedReview:
    return CollectedReview(
        source="amazon",
        source_product_id="B0EXAMPLE1",
        review_id=review_id,
        category="laptop",
        target=ReviewTarget.PRODUCT,
        rating=4,
        body=f"Review {review_id}",
        source_url=f"https://www.amazon.in/review/{review_id}",
        observed_at=datetime.now(UTC),
        content_hash=f"0123456789abcdef{review_id}",
    )


def review_page(
    *reviews: CollectedReview,
    next_cursor: str | None,
) -> ReviewCollectionPage:
    return ReviewCollectionPage(
        source="amazon",
        source_product_id="B0EXAMPLE1",
        category="laptop",
        reviews=reviews,
        next_cursor=next_cursor,
        observed_at=datetime.now(UTC),
    )


@pytest.mark.asyncio
async def test_collect_one_fetches_and_persists_record() -> None:
    sink = MemorySink()

    record = await collect_one(FakeAdapter(), "SKU-1", sink)

    assert sink.records == [record]


@pytest.mark.asyncio
async def test_collect_reviews_paginates_and_enforces_hard_limit() -> None:
    adapter = FakeReviewAdapter(
        {
            None: review_page(review("R1"), review("R2"), next_cursor="second"),
            "second": review_page(review("R3"), review("R4"), next_cursor=None),
        }
    )
    sink = MemoryReviewSink()

    collected = await collect_reviews(
        adapter,
        "B0EXAMPLE1",
        sink,
        max_reviews=3,
        page_size=2,
    )

    assert [item.review_id for item in collected] == ["R1", "R2", "R3"]
    assert sink.reviews == list(collected)
    assert adapter.calls == [(None, 2), ("second", 1)]


@pytest.mark.asyncio
async def test_collect_reviews_stops_on_empty_page() -> None:
    adapter = FakeReviewAdapter({None: review_page(next_cursor="unused")})

    collected = await collect_reviews(
        adapter,
        "B0EXAMPLE1",
        MemoryReviewSink(),
        max_reviews=5,
    )

    assert collected == ()


@pytest.mark.asyncio
async def test_collect_reviews_rejects_repeated_cursor() -> None:
    adapter = FakeReviewAdapter(
        {
            None: review_page(review("R1"), next_cursor="repeat"),
            "repeat": review_page(review("R2"), next_cursor="repeat"),
        }
    )

    with pytest.raises(ReviewPaginationError, match="repeated review cursor"):
        await collect_reviews(
            adapter,
            "B0EXAMPLE1",
            MemoryReviewSink(),
            max_reviews=3,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("max_reviews", "page_size", "message"),
    [(0, 25, "max reviews"), (5, 101, "page size")],
)
async def test_collect_reviews_rejects_invalid_limits(
    max_reviews: int,
    page_size: int,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        await collect_reviews(
            FakeReviewAdapter({}),
            "B0EXAMPLE1",
            MemoryReviewSink(),
            max_reviews=max_reviews,
            page_size=page_size,
        )
