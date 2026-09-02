"""XML Sitemap and Sitemap Index discovery engine for catalog-scale URL harvesting."""

from __future__ import annotations

import contextlib
import gzip
import re
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from sources.contracts import SourceProductReference, SourceTransport


class SitemapItem(BaseModel):
    """An individual discovered product entry from an XML sitemap."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    url: str = Field(min_length=1)
    source: str = Field(min_length=1)
    source_product_id: str | None = None
    lastmod: datetime | None = None
    changefreq: str | None = None
    priority: float | None = None


# Retailer product URL pattern matchers
RETAILER_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "amazon": [
        re.compile(r"/dp/([A-Z0-9]{10})", re.IGNORECASE),
        re.compile(r"/gp/product/([A-Z0-9]{10})", re.IGNORECASE),
    ],
    "flipkart": [
        re.compile(r"/p/(itm[a-zA-Z0-9]{13,16})", re.IGNORECASE),
        re.compile(r"pid=([A-Z0-9]{16})", re.IGNORECASE),
    ],
    "croma": [
        re.compile(r"/p/(\d{6})", re.IGNORECASE),
        re.compile(r"productCode=(\d{6})", re.IGNORECASE),
    ],
}


def _extract_product_id(url: str, source: str) -> str | None:
    patterns = RETAILER_PATTERNS.get(source.casefold().strip(), [])
    for pattern in patterns:
        m = pattern.search(url)
        if m:
            return m.group(1)
    return None


def _parse_iso_datetime(dt_str: str | None) -> datetime | None:
    if not dt_str:
        return None
    cleaned = dt_str.strip()
    try:
        # Handle YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DD
        if len(cleaned) == 10:
            return datetime.strptime(cleaned, "%Y-%m-%d").replace(tzinfo=UTC)
        return datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
    except ValueError:
        return None


class SitemapDiscoveryEngine:
    """Engine for ingesting and processing XML sitemaps and sitemap indexes."""

    @classmethod
    def parse_sitemap_content(
        cls,
        content: str | bytes,
        source: str,
        *,
        category_filter: str | None = None,
    ) -> list[SitemapItem]:
        """Parse raw XML or gzip-compressed XML content into filtered SitemapItems."""
        raw_xml: str
        if isinstance(content, bytes):
            # Check for gzip magic header (0x1f 0x8b)
            if content.startswith(b"\x1f\x8b"):
                with contextlib.suppress(Exception):
                    content = gzip.decompress(content)
            raw_xml = content.decode("utf-8", errors="replace")
        else:
            raw_xml = content

        items: list[SitemapItem] = []
        try:
            # Strip namespaces for robust parsing
            cleaned_xml = re.sub(r'xmlns(:\w+)?="[^"]+"', "", raw_xml, count=1)
            root = ET.fromstring(cleaned_xml)
        except ET.ParseError:
            return []

        # 1. Handle <urlset> containing <url> entries
        for url_tag in root.findall(".//url"):
            loc = url_tag.findtext("loc")
            if not loc:
                continue

            loc_str = loc.strip()
            # Category filter check if specified
            if category_filter:
                cat_lower = category_filter.casefold()
                if cat_lower == "laptop":
                    laptop_kws = (
                        "laptop",
                        "macbook",
                        "notebook",
                        "chromebook",
                        "vivobook",
                        "zenbook",
                        "thinkpad",
                        "ideapad",
                        "inspiron",
                        "victus",
                        "omen",
                        "legion",
                    )
                    if not any(kw in loc_str.casefold() for kw in laptop_kws):
                        continue
                elif cat_lower not in loc_str.casefold():
                    continue

            product_id = _extract_product_id(loc_str, source)
            lastmod = _parse_iso_datetime(url_tag.findtext("lastmod"))
            changefreq = url_tag.findtext("changefreq")
            priority_val: float | None = None
            p_text = url_tag.findtext("priority")
            if p_text:
                with contextlib.suppress(ValueError):
                    priority_val = float(p_text.strip())

            items.append(
                SitemapItem(
                    url=loc_str,
                    source=source,
                    source_product_id=product_id,
                    lastmod=lastmod,
                    changefreq=changefreq.strip() if changefreq else None,
                    priority=priority_val,
                )
            )

        # Sort items by lastmod descending (freshest first)
        items.sort(
            key=lambda it: it.lastmod or datetime.min.replace(tzinfo=UTC),
            reverse=True,
        )
        return items

    @classmethod
    async def discover_from_sitemap(
        cls,
        sitemap_url: str,
        source: str,
        transport: SourceTransport,
        *,
        max_items: int = 100,
        category: str = "laptop",
    ) -> list[SourceProductReference]:
        """Fetch a remote sitemap and extract product references."""
        from sources.contracts import SourceProductReference

        doc = await transport.fetch(AnyHttpUrl(sitemap_url))
        content = doc.payload.get("content") or doc.payload.get("html") or ""
        sitemap_items = cls.parse_sitemap_content(
            str(content),
            source=source,
            category_filter=category,
        )

        references: list[SourceProductReference] = []
        seen_ids: set[str] = set()

        for it in sitemap_items:
            if len(references) >= max_items:
                break
            p_id = it.source_product_id or it.url
            if p_id not in seen_ids:
                seen_ids.add(p_id)
                with contextlib.suppress(Exception):
                    references.append(
                        SourceProductReference(
                            source_product_id=p_id,
                            category=category,
                            subcategory=None,
                            source_url=AnyHttpUrl(it.url),
                        )
                    )

        return references
