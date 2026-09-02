"""Tests for SitemapDiscoveryEngine including XML parsing, GZIP decompression, and URL filtering."""

import gzip
from datetime import UTC, datetime

import pytest
from pydantic import AnyHttpUrl

from collectors.sitemaps import SitemapDiscoveryEngine
from sources.contracts import FetchedSourceDocument, SourceTransport


class MockSitemapTransport(SourceTransport):
    def __init__(self, content: str) -> None:
        self._content = content

    async def fetch(self, source_url: AnyHttpUrl) -> FetchedSourceDocument:
        return FetchedSourceDocument(
            observed_at=datetime.now(UTC),
            payload={"content": self._content},
            content_hash="0123456789abcdef0123456789abcdef",
        )


def test_parse_sitemap_xml_basic() -> None:
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>https://www.croma.com/apple-macbook-air-m5/p/324343</loc>
            <lastmod>2026-09-01T10:00:00Z</lastmod>
            <changefreq>daily</changefreq>
            <priority>0.9</priority>
        </url>
        <url>
            <loc>https://www.croma.com/dell-inspiron-15/p/323906</loc>
            <lastmod>2026-08-30T12:00:00Z</lastmod>
            <priority>0.8</priority>
        </url>
    </urlset>
    """
    items = SitemapDiscoveryEngine.parse_sitemap_content(xml, source="croma")
    assert len(items) == 2
    assert items[0].source_product_id == "324343"
    assert items[0].priority == 0.9
    assert items[0].lastmod is not None
    assert items[0].lastmod == datetime(2026, 9, 1, 10, 0, 0, tzinfo=UTC)
    # Freshest first
    assert items[0].source_product_id == "324343"
    assert items[1].source_product_id == "323906"


def test_parse_sitemap_gzip_compressed() -> None:
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>https://www.flipkart.com/apple-macbook-air/p/itm1234567890123</loc>
            <lastmod>2026-09-01</lastmod>
        </url>
    </urlset>
    """
    compressed_bytes = gzip.compress(xml.encode("utf-8"))
    items = SitemapDiscoveryEngine.parse_sitemap_content(compressed_bytes, source="flipkart")
    assert len(items) == 1
    assert items[0].source_product_id == "itm1234567890123"
    assert items[0].lastmod == datetime(2026, 9, 1, 0, 0, 0, tzinfo=UTC)


def test_sitemap_retailer_product_id_extraction() -> None:
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset>
        <url><loc>https://www.amazon.in/Apple-MacBook-Air-13-6-inch-Midnight/dp/B0CX000001</loc></url>
        <url><loc>https://www.amazon.in/gp/product/B0CX000002</loc></url>
        <url><loc>https://www.flipkart.com/item/p/itmabcdef0123456</loc></url>
        <url><loc>https://www.croma.com/p/324343</loc></url>
        <url><loc>https://www.croma.com/product/details?productCode=323906</loc></url>
    </urlset>
    """
    amz_items = SitemapDiscoveryEngine.parse_sitemap_content(xml, source="amazon")
    assert len(amz_items) == 5
    assert amz_items[0].source_product_id == "B0CX000001"
    assert amz_items[1].source_product_id == "B0CX000002"

    croma_items = SitemapDiscoveryEngine.parse_sitemap_content(xml, source="croma")
    assert any(it.source_product_id == "324343" for it in croma_items)
    assert any(it.source_product_id == "323906" for it in croma_items)


def test_sitemap_invalid_xml_returns_empty_list() -> None:
    items = SitemapDiscoveryEngine.parse_sitemap_content("<malformed > xml", source="croma")
    assert items == []


@pytest.mark.asyncio
async def test_discover_from_sitemap_integration() -> None:
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset>
        <url><loc>https://www.croma.com/apple-macbook-air/p/324343</loc></url>
        <url><loc>https://www.croma.com/dell-inspiron-laptop/p/323906</loc></url>
        <url><loc>https://www.croma.com/refrigerator/p/999999</loc></url>
    </urlset>
    """
    transport = MockSitemapTransport(xml)
    refs = await SitemapDiscoveryEngine.discover_from_sitemap(
        "https://www.croma.com/sitemap.xml",
        source="croma",
        transport=transport,
        max_items=5,
        category="laptop",
    )
    assert len(refs) == 2
    assert refs[0].source_product_id == "324343"
    assert refs[1].source_product_id == "323906"
