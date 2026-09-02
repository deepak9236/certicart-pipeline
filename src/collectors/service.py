"""Idempotency-ready product and review collection use cases."""

from typing import Protocol

from reviews import CollectedReview
from sources import RawSourceRecord, ReviewSourceAdapter, SourceAdapter


class RawRecordSink(Protocol):
    async def append(self, record: RawSourceRecord) -> None: ...


class ReviewRecordSink(Protocol):
    async def append(self, review: CollectedReview) -> None: ...


class ReviewPaginationError(RuntimeError):
    """Raised when a source repeats a review cursor indefinitely."""


async def collect_one(
    adapter: SourceAdapter,
    source_product_id: str,
    sink: RawRecordSink,
) -> RawSourceRecord:
    record = await adapter.fetch(source_product_id)
    await sink.append(record)
    return record


async def collect_reviews(
    adapter: ReviewSourceAdapter,
    source_product_id: str,
    sink: ReviewRecordSink,
    *,
    max_reviews: int,
    page_size: int = 25,
) -> tuple[CollectedReview, ...]:
    if max_reviews < 1:
        raise ValueError("max reviews must be positive")
    if not 1 <= page_size <= 100:
        raise ValueError("review page size must be between 1 and 100")

    collected: list[CollectedReview] = []
    cursor: str | None = None
    seen_cursors: set[str] = set()

    while len(collected) < max_reviews:
        remaining = max_reviews - len(collected)
        page = await adapter.fetch_reviews(
            source_product_id,
            cursor=cursor,
            limit=min(page_size, remaining),
        )
        reviews = page.reviews[:remaining]
        for review in reviews:
            await sink.append(review)
            collected.append(review)

        if page.next_cursor is None or not page.reviews:
            break
        if page.next_cursor in seen_cursors:
            raise ReviewPaginationError(f"repeated review cursor: {page.next_cursor!r}")
        seen_cursors.add(page.next_cursor)
        cursor = page.next_cursor

    return tuple(collected)
