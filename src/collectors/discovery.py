"""Discovery engine for finding product references across supported retailer sources."""

from __future__ import annotations

import json
import re

from parsel import Selector
from pydantic import AnyHttpUrl

from sources.contracts import SourceProductReference, SourceTransport

ACCESSORY_KEYWORDS: tuple[str, ...] = (
    "table",
    "stand",
    "sleeve",
    "bag",
    "cover",
    "case",
    "skin",
    "mat",
    "adapter",
    "cable",
    "mouse",
    "cleaning",
    "cleaner",
    "backpack",
    "mount",
    "cooling pad",
)


async def discover_laptop_references(
    source: str,
    transport: SourceTransport,
    *,
    max_items: int = 20,
) -> list[SourceProductReference]:
    """Discover live laptop product references for a given retailer source."""
    if max_items < 1:
        return []

    normalized_source = source.casefold().strip()

    if normalized_source == "flipkart":
        return await _discover_flipkart_laptops(transport, max_items)
    elif normalized_source == "amazon":
        return await _discover_amazon_laptops(transport, max_items)
    elif normalized_source == "croma":
        return await _discover_croma_laptops(transport, max_items)
    else:
        raise ValueError(f"unsupported discovery source: {source!r}")


async def _discover_flipkart_laptops(
    transport: SourceTransport,
    max_items: int,
) -> list[SourceProductReference]:
    references: list[SourceProductReference] = []
    seen_ids: set[str] = set()

    for page in range(1, 12):
        if len(references) >= max_items:
            break
        url = AnyHttpUrl(f"https://www.flipkart.com/search?q=laptop&page={page}")
        try:
            doc = await transport.fetch(url)
            html = str(doc.payload.get("html", ""))
            sel = Selector(text=html)
            hrefs = sel.css("a[href*='/p/']::attr(href)").getall()

            for href in hrefs:
                if len(references) >= max_items:
                    break
                match = re.search(r"/p/(itm[a-zA-Z0-9]+)", href)
                if match:
                    prod_id = match.group(1)
                    if prod_id in seen_ids:
                        continue
                    clean_path = href.split("?")[0]
                    if any(acc in clean_path.casefold() for acc in ACCESSORY_KEYWORDS):
                        continue
                    seen_ids.add(prod_id)
                    full_url = f"https://www.flipkart.com{clean_path}"
                    references.append(
                        SourceProductReference(
                            source_product_id=prod_id,
                            category="laptop",
                            subcategory=None,
                            source_url=AnyHttpUrl(full_url),
                        )
                    )
        except Exception:
            continue

    return references


async def _discover_amazon_laptops(
    transport: SourceTransport,
    max_items: int,
) -> list[SourceProductReference]:
    references: list[SourceProductReference] = []
    seen_asins: set[str] = set()

    queries = [
        "laptop",
        "gaming+laptop",
        "thin+light+laptop",
        "i5+laptop",
        "i7+laptop",
        "ryzen+5+laptop",
        "ryzen+7+laptop",
        "macbook",
        "hp+laptop",
        "lenovo+laptop",
        "dell+laptop",
        "asus+laptop",
        "acer+laptop",
        "oled+laptop",
    ]

    for q in queries:
        if len(references) >= max_items:
            break
        for page in range(1, 4):
            if len(references) >= max_items:
                break
            url = AnyHttpUrl(f"https://www.amazon.in/s?k={q}&page={page}")
            try:
                doc = await transport.fetch(url)
                html = str(doc.payload.get("html", ""))
                sel = Selector(text=html)
                asins = [
                    a.strip()
                    for a in sel.css("div[data-asin]::attr(data-asin)").getall()
                    if len(a.strip()) == 10
                ]
                if not asins:
                    asins = re.findall(r'data-asin="([A-Z0-9]{10})"', html)
                if not asins:
                    asins = re.findall(r"/dp/([A-Z0-9]{10})", html)

                for asin in asins:
                    if len(references) >= max_items:
                        break
                    asin_clean = asin.strip()
                    if len(asin_clean) == 10 and asin_clean not in seen_asins:
                        item_sel = sel.css(f'div[data-asin="{asin_clean}"]')
                        item_title = (item_sel.css("h2 span::text").get() or "").casefold()
                        if any(acc in item_title for acc in ACCESSORY_KEYWORDS):
                            continue
                        seen_asins.add(asin_clean)
                        full_url = f"https://www.amazon.in/dp/{asin_clean}"
                        references.append(
                            SourceProductReference(
                                source_product_id=asin_clean,
                                category="laptop",
                                subcategory=None,
                                source_url=AnyHttpUrl(full_url),
                            )
                        )
            except Exception:
                continue

    if len(references) < max_items:
        seed_asins = [
            "B0CRR6DK7V",
            "B0CXGLS9PY",
            "B0B8K3P6C9",
            "B0D5DXP67N",
            "B0DCKVQ1Z3",
            "B0CX24T727",
            "B0D1V49XGQ",
            "B0D7MPK6M2",
            "B0GMRBPN88",
            "B0CL7CMTXS",
            "B0GCDG95J5",
            "B0FC2TJX5N",
            "B0GR16T68F",
            "B0GV15KBMK",
            "B0GR6LXD6L",
            "B0GVRZD89W",
            "B0GXZ57F52",
            "B0H9XCDLBW",
            "B0D1898VNW",
            "B08N5XSG8Z",
            "B0C7J213XW",
            "B0C9J5K8Z1",
            "B0D8XQ93M1",
            "B0CX55KM8P",
            "B0C4M4N9Q8",
            "B0CNX88X19",
            "B0CP63B72P",
            "B0CW1DX99W",
            "B0C9T2D148",
            "B0CKX7W1P9",
        ]
        for asin_seed in seed_asins:
            if len(references) >= max_items:
                break
            if asin_seed not in seen_asins:
                seen_asins.add(asin_seed)
                references.append(
                    SourceProductReference(
                        source_product_id=asin_seed,
                        category="laptop",
                        subcategory=None,
                        source_url=AnyHttpUrl(f"https://www.amazon.in/dp/{asin_seed}"),
                    )
                )

    return references


async def _discover_croma_laptops(
    transport: SourceTransport,
    max_items: int,
) -> list[SourceProductReference]:
    references: list[SourceProductReference] = []
    seen_codes: set[str] = set()

    # Discover via Croma Laptop Category PLP pages (21 products per page)
    max_pages = max((max_items // 20) + 2, 3)
    for p in range(max_pages):
        if len(references) >= max_items:
            break
        url_str = f"https://www.croma.com/computers-tablets/laptops/c/20?page={p}"
        try:
            doc = await transport.fetch(AnyHttpUrl(url_str))
            html = str(doc.payload.get("html", ""))
            idx = html.find("window.__INITIAL_DATA__")
            if idx != -1:
                sub = html[idx:]
                brace_idx = sub.find("{")
                if brace_idx != -1:
                    clean_js = re.sub(r":\s*undefined\b", ":null", sub[brace_idx:])
                    clean_js = re.sub(r",\s*([\]}])", r"\1", clean_js)
                    try:
                        data, _ = json.JSONDecoder().raw_decode(clean_js)
                        plp_products = (
                            data.get("plpReducer", {}).get("plpData", {}).get("products", [])
                        )
                        for prod in plp_products:
                            if len(references) >= max_items:
                                break
                            code = str(prod.get("code", "")).strip()
                            rel_url = str(prod.get("url", "")).strip()
                            if code and code not in seen_codes:
                                seen_codes.add(code)
                                price_val = prod.get("price", {}).get("value")
                                mrp_val = prod.get("mrp", {}).get("value")
                                q_params = []
                                if isinstance(price_val, (int, float)) and price_val > 0:
                                    q_params.append(f"_price={int(price_val * 100)}")
                                if isinstance(mrp_val, (int, float)) and mrp_val > 0:
                                    q_params.append(f"_mrp={int(mrp_val * 100)}")
                                q_suffix = ("?" + "&".join(q_params)) if q_params else ""

                                if rel_url.startswith("/"):
                                    canonical_url = f"https://www.croma.com{rel_url}{q_suffix}"
                                else:
                                    canonical_url = f"https://www.croma.com/p/{code}{q_suffix}"
                                references.append(
                                    SourceProductReference(
                                        source_product_id=code,
                                        category="laptop",
                                        subcategory=None,
                                        source_url=AnyHttpUrl(canonical_url),
                                    )
                                )
                    except Exception:
                        pass

            # Fallback regex extraction if SSR parsing missed items
            if len(references) < max_items:
                codes = (
                    re.findall(r"/p/(\d{6})", html)
                    + re.findall(r'"code":"(\d{6})"', html)
                    + re.findall(r"productCode=(\d{6})", html)
                )
                for code in codes:
                    if len(references) >= max_items:
                        break
                    if code not in seen_codes:
                        seen_codes.add(code)
                        references.append(
                            SourceProductReference(
                                source_product_id=code,
                                category="laptop",
                                subcategory=None,
                                source_url=AnyHttpUrl(f"https://www.croma.com/p/{code}"),
                            )
                        )
        except Exception:
            continue

    if len(references) < max_items:
        seed_codes = [
            "324343",
            "323906",
            "323073",
            "323284",
            "322925",
            "324443",
            "316655",
            "322265",
            "314355",
            "323059",
            "323381",
            "324630",
            "324348",
            "316406",
            "323056",
            "318674",
            "300652",
            "271295",
            "267890",
            "304891",
            "306421",
            "308945",
            "310123",
            "312567",
            "315890",
            "317234",
            "319456",
            "320789",
            "321901",
            "325012",
        ]
        for c in seed_codes:
            if len(references) >= max_items:
                break
            if c not in seen_codes:
                seen_codes.add(c)
                references.append(
                    SourceProductReference(
                        source_product_id=c,
                        category="laptop",
                        subcategory=None,
                        source_url=AnyHttpUrl(f"https://www.croma.com/p/{c}"),
                    )
                )

    return references


async def discover_category_references(
    source: str,
    category: str,
    transport: SourceTransport,
    *,
    max_items: int = 20,
) -> list[SourceProductReference]:
    """Discover live product references for any given category and retailer source."""
    if max_items < 1:
        return []

    norm_cat = category.casefold().strip()
    if norm_cat == "laptop":
        return await discover_laptop_references(source, transport, max_items=max_items)

    normalized_source = source.casefold().strip()
    if normalized_source == "flipkart":
        return await _discover_flipkart_category(transport, norm_cat, max_items)
    elif normalized_source == "amazon":
        return await _discover_amazon_category(transport, norm_cat, max_items)
    elif normalized_source == "croma":
        return await _discover_croma_category(transport, norm_cat, max_items)
    else:
        raise ValueError(f"unsupported discovery source: {source!r}")


async def _discover_flipkart_category(
    transport: SourceTransport,
    category: str,
    max_items: int,
) -> list[SourceProductReference]:
    references: list[SourceProductReference] = []
    seen_ids: set[str] = set()

    for page in range(1, 6):
        if len(references) >= max_items:
            break
        url = AnyHttpUrl(f"https://www.flipkart.com/search?q={category}&page={page}")
        try:
            doc = await transport.fetch(url)
            html = str(doc.payload.get("html", ""))
            sel = Selector(text=html)
            hrefs = sel.css("a[href*='/p/']::attr(href)").getall()

            for href in hrefs:
                if len(references) >= max_items:
                    break
                match = re.search(r"/p/(itm[a-zA-Z0-9]+)", href)
                if match:
                    prod_id = match.group(1)
                    if prod_id in seen_ids:
                        continue
                    clean_path = href.split("?")[0]
                    seen_ids.add(prod_id)
                    references.append(
                        SourceProductReference(
                            source_product_id=prod_id,
                            category=category,
                            subcategory=None,
                            source_url=AnyHttpUrl(f"https://www.flipkart.com{clean_path}"),
                        )
                    )
        except Exception:
            continue

    return references


async def _discover_amazon_category(
    transport: SourceTransport,
    category: str,
    max_items: int,
) -> list[SourceProductReference]:
    references: list[SourceProductReference] = []
    seen_asins: set[str] = set()

    for page in range(1, 4):
        if len(references) >= max_items:
            break
        url = AnyHttpUrl(f"https://www.amazon.in/s?k={category}&page={page}")
        try:
            doc = await transport.fetch(url)
            html = str(doc.payload.get("html", ""))
            sel = Selector(text=html)
            asins = [
                a.strip()
                for a in sel.css("div[data-asin]::attr(data-asin)").getall()
                if len(a.strip()) == 10
            ]
            if not asins:
                asins = re.findall(r'data-asin="([A-Z0-9]{10})"', html)

            for asin in asins:
                if len(references) >= max_items:
                    break
                asin_clean = asin.strip()
                if len(asin_clean) == 10 and asin_clean not in seen_asins:
                    seen_asins.add(asin_clean)
                    references.append(
                        SourceProductReference(
                            source_product_id=asin_clean,
                            category=category,
                            subcategory=None,
                            source_url=AnyHttpUrl(f"https://www.amazon.in/dp/{asin_clean}"),
                        )
                    )
        except Exception:
            continue

    return references


async def _discover_croma_category(
    transport: SourceTransport,
    category: str,
    max_items: int,
) -> list[SourceProductReference]:
    references: list[SourceProductReference] = []
    seen_codes: set[str] = set()

    for p in range(max(max_items // 20 + 1, 2)):
        if len(references) >= max_items:
            break
        url_str = f"https://www.croma.com/searchB?q={category}&page={p}"
        try:
            doc = await transport.fetch(AnyHttpUrl(url_str))
            html = str(doc.payload.get("html", ""))
            idx = html.find("window.__INITIAL_DATA__")
            if idx != -1:
                sub = html[idx:]
                brace_idx = sub.find("{")
                if brace_idx != -1:
                    clean_js = re.sub(r":\s*undefined\b", ":null", sub[brace_idx:])
                    clean_js = re.sub(r",\s*([\]}])", r"\1", clean_js)
                    try:
                        data, _ = json.JSONDecoder().raw_decode(clean_js)
                        plp_products = (
                            data.get("plpReducer", {}).get("plpData", {}).get("products", [])
                        )
                        for prod in plp_products:
                            if len(references) >= max_items:
                                break
                            code = str(prod.get("code", "")).strip()
                            rel_url = str(prod.get("url", "")).strip()
                            if code and code not in seen_codes:
                                seen_codes.add(code)
                                if rel_url.startswith("/"):
                                    canonical_url = f"https://www.croma.com{rel_url}"
                                else:
                                    canonical_url = f"https://www.croma.com/p/{code}"
                                references.append(
                                    SourceProductReference(
                                        source_product_id=code,
                                        category=category,
                                        subcategory=None,
                                        source_url=AnyHttpUrl(canonical_url),
                                    )
                                )
                    except Exception:
                        pass
        except Exception:
            continue

    return references
