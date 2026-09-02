"""Amazon India parser extracting structured product metadata and specifications."""

from __future__ import annotations

import contextlib
import json
import re
from datetime import datetime

from parsel import Selector
from pydantic import AnyHttpUrl

from normalization import normalize_text
from sources.common import (
    build_category_attributes,
    extract_digits_to_paise,
    infer_brand,
)
from sources.contracts import ParsedProduct, RawSourceRecord


def parse_amazon_payload(
    payload: dict[str, object],
    source_url: AnyHttpUrl,
    source_product_id: str,
    observed_at: datetime,
    category: str = "laptop",
    subcategory: str | None = None,
) -> ParsedProduct:
    """Parse raw Amazon India payload or HTML string into normalized ParsedProduct."""
    html = str(payload.get("html", ""))
    sel = Selector(text=html) if html else None

    # Check JSON-LD if present
    json_ld_data: dict[str, object] = {}
    if sel:
        for raw_json_ld in sel.css('script[type="application/ld+json"]::text').getall():
            try:
                loaded = json.loads(raw_json_ld)
                if isinstance(loaded, dict) and loaded.get("@type") in ("Product", "ItemPage"):
                    json_ld_data = loaded
                    break
                if isinstance(loaded, list):
                    for item in loaded:
                        if isinstance(item, dict) and item.get("@type") == "Product":
                            json_ld_data = item
                            break
            except (json.JSONDecodeError, TypeError):
                continue

    # Title
    title = ""
    if sel:
        title = (
            sel.css("span#productTitle::text").get()
            or sel.css("h1#title::text").get()
            or sel.css("meta[name='title']::attr(content)").get()
            or sel.css("meta[property='og:title']::attr(content)").get()
            or sel.css("h1::text").get()
            or ""
        ).strip()
    if not title and json_ld_data.get("name"):
        title = str(json_ld_data["name"]).strip()
    if not title and sel:
        raw_page_title = sel.css("title::text").get()
        if raw_page_title and "page not found" not in raw_page_title.casefold():
            title = raw_page_title.split(":")[0].split("|")[0].strip()
    if not title:
        title = str(payload.get("title", f"Amazon Product {source_product_id}"))

    # Prices
    price_paise: int | None = None
    mrp_paise: int | None = None

    if sel:
        offscreen_prices = [
            p.strip()
            for p in sel.css("span.a-price span.a-offscreen::text").getall()
            if p.strip() and "₹" in p
        ]
        whole_price = (
            sel.css("span.priceToPay span.a-price-whole::text").get()
            or sel.css("span.a-price span.a-price-whole::text").get()
            or sel.css("div#corePriceDisplay_desktop_feature_div span.a-price-whole::text").get()
        )
        price_text = (
            (offscreen_prices[0] if offscreen_prices else None)
            or whole_price
            or sel.css("span.priceToPay span.a-offscreen::text").get()
            or sel.css("span.apexPriceToPay span.a-offscreen::text").get()
            or sel.css("div#corePrice_desktop span.a-offscreen::text").get()
        )
        price_paise = extract_digits_to_paise(price_text)

        mrp_text = (
            sel.css("span.basisPrice span.a-offscreen::text").get()
            or sel.css("span.a-text-price span.a-offscreen::text").get()
            or sel.css("span.a-price[data-a-strike='true'] span.a-offscreen::text").get()
            or sel.css(
                "div#corePriceDisplay_desktop_feature_div "
                "span.a-price.a-text-price span.a-offscreen::text"
            ).get()
            or sel.css("div#corePrice_desktop span.a-text-price span.a-offscreen::text").get()
        )
        mrp_paise = extract_digits_to_paise(mrp_text)

        if price_paise is None and html:
            price_match = re.search(r"₹\s*([\d,]+(?:\.\d{2})?)", html)
            if price_match:
                price_paise = extract_digits_to_paise(price_match.group(1))

        if mrp_paise is None and html:
            mrp_match = re.search(
                r"(?:M\.R\.P\.|MRP)[^\d₹]*₹?\s*([\d,]+(?:\.\d{2})?)", html, re.IGNORECASE
            )
            if mrp_match:
                mrp_paise = extract_digits_to_paise(mrp_match.group(1))

    if price_paise is None and "offers" in json_ld_data:
        offers = json_ld_data["offers"]
        if isinstance(offers, dict) and "price" in offers:
            price_paise = extract_digits_to_paise(str(offers["price"]))

    if price_paise is None:
        raw_price = payload.get("price_paise") or payload.get("price")
        price_paise = (
            int(raw_price)
            if isinstance(raw_price, int)
            else (extract_digits_to_paise(str(raw_price)) or 0)
        )

    if mrp_paise is None and "mrp_paise" in payload:
        raw_mrp = payload["mrp_paise"]
        if isinstance(raw_mrp, int):
            mrp_paise = raw_mrp
        elif raw_mrp is not None:
            mrp_paise = extract_digits_to_paise(str(raw_mrp))

    # In stock check
    in_stock = True
    if sel:
        avail_text = sel.css("div#availability span::text").get() or ""
        if (
            "currently unavailable" in avail_text.casefold()
            or "out of stock" in avail_text.casefold()
        ):
            in_stock = False

    # Seller
    seller: str | None = None
    if sel:
        seller_raw = (
            sel.css("a#sellerProfileTriggerId::text").get()
            or sel.css("div#merchant-info a span::text").get()
            or sel.css("div#merchant-info::text").get()
            or sel.css("#tabular-buybox-truncate-0 span::text").get()
            or sel.css("div.tabular-buybox-text[tabular-attribute-name='Sold by'] span::text").get()
        )
        if seller_raw:
            seller = seller_raw.strip()
    if not seller and payload.get("seller"):
        seller = str(payload["seller"])

    # Rating & Reviews
    rating: float | None = None
    review_count: int | None = None
    if sel:
        rating_text = sel.css("span.a-icon-alt::text, i.a-icon-star span::text").get()
        if rating_text:
            match = re.search(r"(\d+(?:\.\d+)?)\s*out of 5", rating_text)
            if match:
                with contextlib.suppress(ValueError):
                    rating = float(match.group(1))
        rev_text = sel.css("span#acrCustomerReviewText::text").get()
        if rev_text:
            rev_match = re.search(r"([\d,]+)", rev_text)
            if rev_match:
                review_count = int(rev_match.group(1).replace(",", ""))

    # Specifications
    specs: dict[str, str] = {}
    if sel:
        spec_selector = (
            "#productDetails_techSpec_section_1 tr, #poExpander tr, "
            "#technicalSpecifications_section_1 tr"
        )
        for row in sel.css(spec_selector):
            key_el = row.css("th::text, td.a-span3 span::text, td:first-child::text").get()
            val_el = row.css("td::text, td.a-span9 span::text, td:last-child::text").get()
            if key_el and val_el:
                specs[normalize_text(key_el)] = val_el.strip()

        for li in sel.css("#detailBullets_feature_div li span.a-list-item"):
            parts = [p.strip() for p in li.css("span::text").getall() if p.strip()]
            if len(parts) >= 2:
                specs[normalize_text(parts[0].replace(":", ""))] = parts[1].strip()

    brand = infer_brand(
        title, specs.get("brand") or specs.get("manufacturer") or specs.get("brand name")
    )
    model_name = specs.get("model name") or specs.get("model") or specs.get("series") or title

    attributes = build_category_attributes(category, title, specs)

    return ParsedProduct(
        source="amazon",
        source_product_id=source_product_id,
        category=category,
        subcategory=subcategory,
        title=title,
        brand=brand,
        model_name=model_name,
        price_paise=price_paise,
        mrp_paise=mrp_paise,
        in_stock=in_stock,
        seller=seller,
        rating=rating,
        review_count=review_count,
        source_url=source_url,
        attributes=attributes,
        observed_at=observed_at,
    )


def parse_amazon_record(record: RawSourceRecord) -> ParsedProduct:
    """Parse a RawSourceRecord using Amazon extraction rules."""
    return parse_amazon_payload(
        payload=dict(record.payload),
        source_url=record.source_url,
        source_product_id=record.source_product_id,
        observed_at=record.observed_at,
        category=record.category,
        subcategory=record.subcategory,
    )
