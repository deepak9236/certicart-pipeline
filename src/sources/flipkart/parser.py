"""Flipkart parser extracting structured product metadata and specifications."""

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


def parse_flipkart_payload(
    payload: dict[str, object],
    source_url: AnyHttpUrl,
    source_product_id: str,
    observed_at: datetime,
    category: str = "laptop",
    subcategory: str | None = None,
) -> ParsedProduct:
    """Parse raw Flipkart payload or HTML string into normalized ParsedProduct."""
    html = str(payload.get("html", ""))
    sel = Selector(text=html) if html else None

    # Check JSON-LD if present in HTML
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
            sel.css("h1.VU-ZEz::text").get()
            or sel.css("span.B_NuCI::text").get()
            or sel.css("h1._6EBuvT::text").get()
            or sel.css("meta[property='og:title']::attr(content)").get()
            or sel.css("meta[name='twitter:title']::attr(content)").get()
            or sel.css("h1::text").get()
            or ""
        ).strip()
    if not title and json_ld_data.get("name"):
        title = str(json_ld_data["name"]).strip()
    if not title and sel:
        raw_page_title = sel.css("title::text").get()
        if raw_page_title and "buy products online" not in raw_page_title.casefold():
            title = raw_page_title.split("|")[0].split("-")[0].strip()
    if not title:
        title = str(payload.get("title", f"Flipkart Product {source_product_id}"))

    # Clean title stop-phrases
    if title:
        title = re.sub(
            r"\s*(?:online\s+at\s+best\s+price\s+(?:on|in)\s+[^.]+|\(includes\s+extra\s+discount[^)]*\))\s*$",
            "",
            title,
            flags=re.IGNORECASE,
        ).strip()

    # Prices
    price_paise: int | None = None
    mrp_paise: int | None = None

    if sel:
        price_text = (
            sel.css("div._30jeq3._16J0da::text").get()
            or sel.css("div.Nx9bqj._4b5DiR::text").get()
            or sel.css("div._30jeq3::text").get()
            or sel.css("div.Nx9bqj::text").get()
        )
        price_paise = extract_digits_to_paise(price_text)

        # Strikethrough MRP extraction
        mrp_elements = sel.css(
            "div.yRaY8j, div._3I9_wc, div._3I9_wc._2p6cR5, div.yRaY8j._14Ij5r, span.k3eYh1"
        ).getall()
        for el in mrp_elements:
            m = re.search(r"₹\s*([\d,]{3,})", el)
            if m:
                val = extract_digits_to_paise(m.group(1))
                if val and (price_paise is None or val >= price_paise):
                    mrp_paise = val
                    break

        if mrp_paise is None and html:
            mrp_match = re.search(
                r"(?:MRP|Maximum Retail Price)[^\d₹]*₹?\s*([\d,]{3,})", html, re.IGNORECASE
            )
            if mrp_match:
                val = extract_digits_to_paise(mrp_match.group(1))
                if val and (price_paise is None or val >= price_paise):
                    mrp_paise = val

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
        out_of_stock_text = sel.css("div._16FRp0::text, div._16FRp0 span::text").get()
        if out_of_stock_text and "out of stock" in out_of_stock_text.casefold():
            in_stock = False
        sold_out = sel.css("button:disabled::text, div._1t_v5X::text").get()
        if sold_out and ("sold out" in sold_out.casefold() or "unavailable" in sold_out.casefold()):
            in_stock = False

    # Seller
    seller: str | None = None
    if sel:
        seller_raw = (
            sel.css("div#sellerName span span::text").get()
            or sel.css("div.DByuf4 span::text").get()
            or sel.css("div._1RLviY span::text").get()
            or sel.css("div._1RLviY::text").get()
            or sel.css("div._2mD1Ys span::text").get()
            or sel.css("span.h8pY3V::text").get()
        )
        if seller_raw:
            seller = seller_raw.strip()
    if not seller and payload.get("seller"):
        seller = str(payload["seller"])

    # Rating & Reviews
    rating: float | None = None
    review_count: int | None = None
    if sel:
        rating_text = sel.css("div._3LWZlK::text, div.XQDdHH::text").get()
        if rating_text:
            with contextlib.suppress(ValueError):
                rating = float(rating_text.strip())
        reviews_text = sel.css("span._2_R_DZ span::text, span.Wphh3N span::text").getall()
        for r_text in reviews_text:
            rev_match = re.search(r"([\d,]+)\s*Reviews", r_text, re.IGNORECASE)
            if rev_match:
                review_count = int(rev_match.group(1).replace(",", ""))
                break

    # Specs table extraction
    specs: dict[str, str] = {}
    if sel:
        for row in sel.css("tr._1s_Smc, tr.row, div._14cfVK tr"):
            key_el = row.css("td._1hKmda::text, td:first-child::text").get()
            val_el = row.css("td._21lJal li::text, td._21lJal::text, td:last-child::text").get()
            if key_el and val_el:
                specs[normalize_text(key_el)] = val_el.strip()

        # Also bullet points in description
        for li in sel.css("li._21Ahn-::text, div._2418kt li::text").getall():
            if ":" in li:
                k, v = li.split(":", 1)
                specs[normalize_text(k)] = v.strip()

    # Brand and Model
    brand = infer_brand(title, specs.get("brand") or specs.get("model brand"))
    model_name = specs.get("model name") or specs.get("model") or specs.get("series") or title

    attributes = build_category_attributes(category, title, specs)

    return ParsedProduct(
        source="flipkart",
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


def parse_flipkart_record(record: RawSourceRecord) -> ParsedProduct:
    """Parse a RawSourceRecord using Flipkart extraction rules."""
    return parse_flipkart_payload(
        payload=dict(record.payload),
        source_url=record.source_url,
        source_product_id=record.source_product_id,
        observed_at=record.observed_at,
        category=record.category,
        subcategory=record.subcategory,
    )
