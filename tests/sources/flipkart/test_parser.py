from datetime import UTC, datetime

from pydantic import AnyHttpUrl

from sources import FetchedSourceDocument, FlipkartSourceAdapter, RawSourceRecord
from sources.flipkart.parser import parse_flipkart_payload


class FakeTransport:
    async def fetch(self, source_url: AnyHttpUrl) -> FetchedSourceDocument:
        return FetchedSourceDocument(
            observed_at=datetime.now(UTC),
            payload={},
            content_hash="0123456789abcdef0123456789abcdef",
        )


def test_flipkart_parser_extracts_all_fields_from_html() -> None:
    html = """
    <html>
        <h1 class="VU-ZEz">Lenovo IdeaPad Slim 3 Laptop (16 GB/512 GB SSD)</h1>
        <div class="Nx9bqj">₹49,990</div>
        <div class="yRaY8j">₹68,990</div>
        <div id="sellerName"><span><span>RetailNet</span></span></div>
        <div class="XQDdHH">4.3</div>
        <span class="Wphh3N"><span>450 Ratings & 45 Reviews</span></span>
        <table class="_14cfVK">
            <tr class="_1s_Smc">
                <td class="_1hKmda">Processor Name</td>
                <td class="_21lJal">Core i5 1235U</td>
            </tr>
            <tr class="_1s_Smc">
                <td class="_1hKmda">RAM</td>
                <td class="_21lJal">16 GB</td>
            </tr>
            <tr class="_1s_Smc">
                <td class="_1hKmda">SSD Capacity</td>
                <td class="_21lJal">512 GB</td>
            </tr>
            <tr class="_1s_Smc">
                <td class="_1hKmda">Graphic Processor</td>
                <td class="_21lJal">Intel Integrated Iris Xe</td>
            </tr>
        </table>
    </html>
    """
    now = datetime.now(UTC)
    url = AnyHttpUrl("https://www.flipkart.com/lenovo-ideapad-slim-3/p/itm123")

    parsed = parse_flipkart_payload(
        payload={"html": html},
        source_url=url,
        source_product_id="FLIP-001",
        observed_at=now,
        category="laptop",
    )

    assert parsed.source == "flipkart"
    assert parsed.source_product_id == "FLIP-001"
    assert parsed.brand == "Lenovo"
    assert parsed.price_paise == 4999000
    assert parsed.mrp_paise == 6899000
    assert parsed.in_stock is True
    assert parsed.seller == "RetailNet"
    assert parsed.rating == 4.3
    assert parsed.review_count == 45
    assert parsed.attributes["cpu_model"] == "Core i5 1235U"
    assert parsed.attributes["gpu_model"] == "Intel Integrated Iris Xe"
    assert parsed.attributes["ram_gb"] == 16
    assert parsed.attributes["storage_gb"] == 512

    # Verify conversions
    fp = parsed.to_fingerprint()
    assert fp.brand == "lenovo"
    assert fp.attributes["ram_gb"] == 16

    obs = parsed.to_price_observation()
    assert obs.price_paise == 4999000
    assert obs.mrp_paise == 6899000
    assert obs.in_stock is True


def test_flipkart_parser_detects_out_of_stock() -> None:
    html = """
    <html>
        <h1 class="VU-ZEz">Apple MacBook Air M2 - (8 GB/256 GB SSD)</h1>
        <div class="Nx9bqj">₹89,900</div>
        <div class="_16FRp0"><span>This item is currently out of stock</span></div>
    </html>
    """
    now = datetime.now(UTC)
    url = AnyHttpUrl("https://www.flipkart.com/apple-macbook-air-m2/p/itm456")

    parsed = parse_flipkart_payload(
        payload={"html": html},
        source_url=url,
        source_product_id="FLIP-002",
        observed_at=now,
    )

    assert parsed.brand == "Apple"
    assert parsed.in_stock is False
    assert parsed.price_paise == 8990000


def test_flipkart_adapter_parse_method() -> None:
    adapter = FlipkartSourceAdapter([], FakeTransport())
    now = datetime.now(UTC)
    record = RawSourceRecord(
        source="flipkart",
        source_product_id="FLIP-003",
        category="laptop",
        source_url=AnyHttpUrl("https://www.flipkart.com/p/itm789"),
        observed_at=now,
        payload={"title": "ASUS TUF Gaming F15", "price_paise": 6500000},
        content_hash="0123456789abcdef0123456789abcdef",
    )

    parsed = adapter.parse(record)
    assert parsed.source == "flipkart"
    assert parsed.brand == "Asus"
    assert parsed.price_paise == 6500000


def test_flipkart_parser_json_ld_and_bullet_points() -> None:
    html = """
    <html>
        <script type="application/ld+json">
        {
            "@type": "Product",
            "name": "Acer Predator Helios 16",
            "offers": {"price": "149990.00"}
        }
        </script>
        <div class="_2418kt">
            <ul>
                <li class="_21Ahn-">Processor: Intel Core i9-13900HX</li>
                <li class="_21Ahn-">RAM: 32 GB</li>
                <li class="_21Ahn-">Storage: 1 TB SSD</li>
                <li class="_21Ahn-">Graphics: NVIDIA GeForce RTX 4080</li>
            </ul>
        </div>
    </html>
    """
    now = datetime.now(UTC)
    url = AnyHttpUrl("https://www.flipkart.com/acer-predator/p/itm999")

    parsed = parse_flipkart_payload(
        payload={"html": html},
        source_url=url,
        source_product_id="FLIP-JSONLD",
        observed_at=now,
    )

    assert parsed.title == "Acer Predator Helios 16"
    assert parsed.brand == "Acer"
    assert parsed.price_paise == 14999000
    assert parsed.attributes["cpu_model"] == "Intel Core i9-13900HX"
    assert parsed.attributes["ram_gb"] == 32
    assert parsed.attributes["storage_gb"] == 1024
    assert parsed.attributes["gpu_model"] == "NVIDIA GeForce RTX 4080"


def test_flipkart_parser_json_ld_list_and_fallbacks() -> None:
    html = """
    <html>
        <script type="application/ld+json">
        [
            {"@type": "BreadcrumbList"},
            {"@type": "Product", "name": "CustomBrand ProBook", "offers": {"price": "55000"}}
        ]
        </script>
    </html>
    """
    now = datetime.now(UTC)
    url = AnyHttpUrl("https://www.flipkart.com/custom/p/itm111")

    parsed = parse_flipkart_payload(
        payload={"html": html, "seller": "RetailNet", "mrp_paise": 6500000},
        source_url=url,
        source_product_id="FLIP-LIST",
        observed_at=now,
    )

    assert parsed.title == "CustomBrand ProBook"
    assert parsed.brand == "CustomBrand"
    assert parsed.price_paise == 5500000
    assert parsed.mrp_paise == 6500000
    assert parsed.seller == "RetailNet"
