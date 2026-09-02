from datetime import UTC, datetime

from pydantic import AnyHttpUrl

from sources import AmazonSourceAdapter, FetchedSourceDocument, RawSourceRecord
from sources.amazon.parser import parse_amazon_payload


class FakeTransport:
    async def fetch(self, source_url: AnyHttpUrl) -> FetchedSourceDocument:
        return FetchedSourceDocument(
            observed_at=datetime.now(UTC),
            payload={},
            content_hash="0123456789abcdef0123456789abcdef",
        )


def test_amazon_parser_extracts_all_fields_from_html() -> None:
    html = """
    <html>
        <span id="productTitle">ASUS Vivobook 15 Intel Core i3 (8 GB RAM/512GB SSD)</span>
        <span class="a-price"><span class="a-offscreen">₹38,990.00</span></span>
        <span class="a-text-price"><span class="a-offscreen">₹52,990.00</span></span>
        <div id="merchant-info">Sold by Appario Retail Private Ltd</div>
        <span class="a-icon-alt">4.1 out of 5 stars</span>
        <span id="acrCustomerReviewText">890 ratings</span>
        <table id="productDetails_techSpec_section_1">
            <tr><th>Processor Brand</th><td>Intel Core i3-1215U</td></tr>
            <tr><th>RAM Size</th><td>8 GB</td></tr>
            <tr><th>Hard Drive Size</th><td>512 GB</td></tr>
            <tr><th>Graphics Coprocessor</th><td>Intel UHD Graphics</td></tr>
        </table>
    </html>
    """
    now = datetime.now(UTC)
    url = AnyHttpUrl("https://www.amazon.in/dp/B0CX98765")

    parsed = parse_amazon_payload(
        payload={"html": html},
        source_url=url,
        source_product_id="B0CX98765",
        observed_at=now,
        category="laptop",
    )

    assert parsed.source == "amazon"
    assert parsed.source_product_id == "B0CX98765"
    assert parsed.brand == "Asus"
    assert parsed.price_paise == 3899000
    assert parsed.mrp_paise == 5299000
    assert parsed.in_stock is True
    assert parsed.seller == "Sold by Appario Retail Private Ltd"
    assert parsed.rating == 4.1
    assert parsed.review_count == 890
    assert parsed.attributes["cpu_model"] == "Intel Core i3-1215U"
    assert parsed.attributes["gpu_model"] == "Intel UHD Graphics"
    assert parsed.attributes["ram_gb"] == 8
    assert parsed.attributes["storage_gb"] == 512

    fp = parsed.to_fingerprint()
    assert fp.brand == "asus"
    assert fp.attributes["ram_gb"] == 8

    obs = parsed.to_price_observation()
    assert obs.price_paise == 3899000
    assert obs.mrp_paise == 5299000


def test_amazon_parser_detects_out_of_stock() -> None:
    html = """
    <html>
        <span id="productTitle">Lenovo Legion Pro 5 Laptop</span>
        <span class="a-price"><span class="a-offscreen">₹1,45,000.00</span></span>
        <div id="availability"><span>Currently unavailable.</span></div>
    </html>
    """
    now = datetime.now(UTC)
    url = AnyHttpUrl("https://www.amazon.in/dp/B0CXOUTOFSTOCK")

    parsed = parse_amazon_payload(
        payload={"html": html},
        source_url=url,
        source_product_id="B0CXOUTOFSTOCK",
        observed_at=now,
    )

    assert parsed.brand == "Lenovo"
    assert parsed.in_stock is False
    assert parsed.price_paise == 14500000


def test_amazon_adapter_parse_method() -> None:
    adapter = AmazonSourceAdapter([], FakeTransport())
    now = datetime.now(UTC)
    record = RawSourceRecord(
        source="amazon",
        source_product_id="B0CXDEMO1",
        category="laptop",
        source_url=AnyHttpUrl("https://www.amazon.in/dp/B0CXDEMO1"),
        observed_at=now,
        payload={"title": "Apple MacBook Air M3", "price_paise": 11490000},
        content_hash="0123456789abcdef0123456789abcdef",
    )

    parsed = adapter.parse(record)
    assert parsed.source == "amazon"
    assert parsed.brand == "Apple"
    assert parsed.price_paise == 11490000


def test_amazon_parser_json_ld_and_bullets() -> None:
    html = """
    <html>
        <script type="application/ld+json">
        {
            "@type": "Product",
            "name": "Dell XPS 13 Plus",
            "offers": {"price": "199990"}
        }
        </script>
        <div id="detailBullets_feature_div">
            <ul>
                <li>
                    <span class="a-list-item">
                        <span>Processor Brand: </span>
                        <span>Intel Core i7-1360P</span>
                    </span>
                </li>
                <li>
                    <span class="a-list-item">
                        <span>RAM Size: </span>
                        <span>32 GB</span>
                    </span>
                </li>
                <li>
                    <span class="a-list-item">
                        <span>Hard Drive Size: </span>
                        <span>1 TB</span>
                    </span>
                </li>
            </ul>
        </div>
    </html>
    """
    now = datetime.now(UTC)
    url = AnyHttpUrl("https://www.amazon.in/dp/B0CXJSONLD")

    parsed = parse_amazon_payload(
        payload={"html": html},
        source_url=url,
        source_product_id="B0CXJSONLD",
        observed_at=now,
    )

    assert parsed.title == "Dell XPS 13 Plus"
    assert parsed.brand == "Dell"
    assert parsed.price_paise == 19999000
    assert parsed.attributes["cpu_model"] == "Intel Core i7-1360P"
    assert parsed.attributes["ram_gb"] == 32
    assert parsed.attributes["storage_gb"] == 1024


def test_amazon_parser_json_ld_list_and_fallbacks() -> None:
    html = """
    <html>
        <script type="application/ld+json">
        [
            {"@type": "BreadcrumbList"},
            {"@type": "Product", "name": "CustomBrand UltraBook", "offers": {"price": "89000"}}
        ]
        </script>
    </html>
    """
    now = datetime.now(UTC)
    url = AnyHttpUrl("https://www.amazon.in/dp/B0CXCUSTOM")

    parsed = parse_amazon_payload(
        payload={"html": html, "seller": "Cloudtail", "mrp_paise": 9900000},
        source_url=url,
        source_product_id="B0CXCUSTOM",
        observed_at=now,
    )

    assert parsed.title == "CustomBrand UltraBook"
    assert parsed.brand == "CustomBrand"
    assert parsed.price_paise == 8900000
    assert parsed.mrp_paise == 9900000
    assert parsed.seller == "Cloudtail"
