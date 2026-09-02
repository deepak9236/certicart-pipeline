from datetime import UTC, datetime

import pytest
from pydantic import AnyHttpUrl

from sources import (
    AmazonSourceAdapter,
    FetchedSourceDocument,
    SourceProductReference,
    UnknownSourceProductError,
)


class FakeTransport:
    async def fetch(self, source_url: AnyHttpUrl) -> FetchedSourceDocument:
        return FetchedSourceDocument(
            observed_at=datetime.now(UTC),
            payload={"title": "Laptop", "url": str(source_url)},
            content_hash="0123456789abcdef",
        )


def reference(
    source_product_id: str = "B0EXAMPLE1",
    source_url: str = "https://www.amazon.in/dp/B0EXAMPLE1",
) -> SourceProductReference:
    return SourceProductReference(
        source_product_id=source_product_id,
        category="laptop",
        subcategory="business_laptop",
        source_url=source_url,
    )


@pytest.mark.asyncio
async def test_configured_adapter_discovers_and_fetches_approved_reference() -> None:
    adapter = AmazonSourceAdapter([reference()], FakeTransport())

    discovered = [source_product_id async for source_product_id in adapter.discover()]
    record = await adapter.fetch("B0EXAMPLE1")

    assert discovered == ["B0EXAMPLE1"]
    assert record.source == "amazon"
    assert record.category == "laptop"
    assert record.subcategory == "business_laptop"
    assert record.payload["title"] == "Laptop"


def test_configured_adapter_rejects_duplicate_product_ids() -> None:
    with pytest.raises(ValueError, match="duplicate source product ID"):
        AmazonSourceAdapter([reference(), reference()], FakeTransport())


@pytest.mark.parametrize(
    "source_url",
    ["http://www.amazon.in/dp/B0EXAMPLE1", "https://example.com/dp/B0EXAMPLE1"],
)
def test_configured_adapter_rejects_unapproved_urls(source_url: str) -> None:
    with pytest.raises(ValueError, match="approved host"):
        AmazonSourceAdapter([reference(source_url=source_url)], FakeTransport())


@pytest.mark.asyncio
async def test_configured_adapter_rejects_unknown_product() -> None:
    adapter = AmazonSourceAdapter([], FakeTransport())

    with pytest.raises(UnknownSourceProductError, match="UNKNOWN"):
        await adapter.fetch("UNKNOWN")
