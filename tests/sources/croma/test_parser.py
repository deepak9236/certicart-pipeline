"""Comprehensive test suite for Croma parser covering hydration state decoding,

classifications, pricing, and error resilience.
"""

from datetime import UTC, datetime

from pydantic import AnyHttpUrl

from sources import CromaSourceAdapter, FetchedSourceDocument, RawSourceRecord
from sources.croma.parser import parse_croma_payload


class FakeTransport:
    async def fetch(self, source_url: AnyHttpUrl) -> FetchedSourceDocument:
        return FetchedSourceDocument(
            observed_at=datetime.now(UTC),
            payload={},
            content_hash="0123456789abcdef0123456789abcdef",
        )


def test_1_valid_initial_data_extraction() -> None:
    html = """
    <html>
        <script>
        window.__INITIAL_DATA__= {
            "pdpReducer": {
                "pdpData": {
                    "name": "ASUS TUF Gaming A15 AMD Ryzen 7 (16GB, 512GB SSD, RTX 4060)",
                    "manufacturer": "ASUS",
                    "price": {"value": 89990.0, "formattedValue": "₹89,990"},
                    "mrp": {"value": 115990.0, "formattedValue": "₹1,15,990"},
                    "stock": "inStock"
                }
            }
        };
        </script>
    </html>
    """
    url = AnyHttpUrl("https://www.croma.com/asus-tuf-gaming-a15/p/320001")
    parsed = parse_croma_payload(
        payload={"html": html},
        source_url=url,
        source_product_id="320001",
        observed_at=datetime.now(UTC),
    )
    assert parsed.brand == "Asus"
    assert parsed.price_paise == 8999000
    assert parsed.mrp_paise == 11599000
    assert parsed.in_stock is True


def test_2_hydration_state_containing_error_message_undefined() -> None:
    html = """
    <html>
        <script>
        window.__INITIAL_DATA__= {
            "pdpReducer": {
                "pdpData": {
                    "name": "Lenovo IdeaPad Slim 3 (16GB, 512GB SSD)",
                    "manufacturer": "Lenovo",
                    "price": {"value": 54990.0}
                }
            },
            "errorMessage": undefined,
            "isFetching": false
        };
        </script>
    </html>
    """
    url = AnyHttpUrl("https://www.croma.com/lenovo-ideapad-slim-3/p/320002")
    parsed = parse_croma_payload(
        payload={"html": html},
        source_url=url,
        source_product_id="320002",
        observed_at=datetime.now(UTC),
    )
    assert parsed.brand == "Lenovo"
    assert parsed.price_paise == 5499000


def test_3_product_title_cleaning() -> None:
    html = """
    <html>
        <script>
        window.__INITIAL_DATA__= {
            "pdpReducer": {
                "pdpData": {
                    "name": "Buy Apple MacBook Air 13.6 M5 (16GB, 512GB SSD) Online - Croma"
                }
            }
        };
        </script>
    </html>
    """
    url = AnyHttpUrl("https://www.croma.com/apple-macbook-air-m5/p/320003")
    parsed = parse_croma_payload(
        payload={"html": html},
        source_url=url,
        source_product_id="320003",
        observed_at=datetime.now(UTC),
    )
    assert parsed.title == "Apple MacBook Air 13.6 M5 (16GB, 512GB SSD)"


def test_4_and_5_brand_and_model_family_extraction() -> None:
    html = """
    <html>
        <script>
        window.__INITIAL_DATA__= {
            "pdpReducer": {
                "pdpData": {
                    "name": "HP Victus Gaming Laptop 15-fa1234TX (16GB, 512GB SSD)",
                    "manufacturer": "HP",
                    "classifications": [
                        {
                            "name": "Manufacturer Details",
                            "features": [
                                {"name": "Model Series", "featureValues": [{"value": "Victus 15"}]}
                            ]
                        }
                    ]
                }
            }
        };
        </script>
    </html>
    """
    url = AnyHttpUrl("https://www.croma.com/hp-victus-15/p/320004")
    parsed = parse_croma_payload(
        payload={"html": html},
        source_url=url,
        source_product_id="320004",
        observed_at=datetime.now(UTC),
    )
    assert parsed.brand == "Hp"
    assert parsed.model_name == "Victus 15"


def test_6_and_7_cpu_and_gpu_extraction() -> None:
    html = """
    <html>
        <script>
        window.__INITIAL_DATA__= {
            "pdpReducer": {
                "pdpData": {
                    "name": "Dell Inspiron 15 (16GB, 512GB SSD)",
                    "classifications": [
                        {
                            "name": "Processor",
                            "features": [
                                {
                                    "name": "Processor Type",
                                    "featureValues": [{"value": "Intel Core i5-1335U"}]
                                },
                                {
                                    "name": "Graphics Processor",
                                    "featureValues": [{"value": "NVIDIA GeForce RTX 3050"}]
                                }
                            ]
                        }
                    ]
                }
            }
        };
        </script>
    </html>
    """
    url = AnyHttpUrl("https://www.croma.com/dell-inspiron-15/p/320005")
    parsed = parse_croma_payload(
        payload={"html": html},
        source_url=url,
        source_product_id="320005",
        observed_at=datetime.now(UTC),
    )
    assert parsed.attributes["cpu_model"] == "Intel Core i5-1335U"
    assert parsed.attributes["gpu_model"] == "NVIDIA GeForce RTX 3050"


def test_8_and_9_ram_and_storage_extraction() -> None:
    html = """
    <html>
        <script>
        window.__INITIAL_DATA__= {
            "pdpReducer": {
                "pdpData": {
                    "name": "Acer Swift Go 14 Laptop",
                    "classifications": [
                        {
                            "name": "Memory & Storage",
                            "features": [
                                {"name": "RAM", "featureValues": [{"value": "16 GB"}]},
                                {"name": "SSD Capacity", "featureValues": [{"value": "1 TB"}]}
                            ]
                        }
                    ]
                }
            }
        };
        </script>
    </html>
    """
    url = AnyHttpUrl("https://www.croma.com/acer-swift-go/p/320006")
    parsed = parse_croma_payload(
        payload={"html": html},
        source_url=url,
        source_product_id="320006",
        observed_at=datetime.now(UTC),
    )
    assert parsed.attributes["ram_gb"] == 16
    assert parsed.attributes["storage_gb"] == 1024


def test_10_screen_size_and_storage_type_extraction() -> None:
    html = """
    <html>
        <script>
        window.__INITIAL_DATA__= {
            "pdpReducer": {
                "pdpData": {
                    "name": "Samsung Galaxy Book4 15.6 inch SSD Laptop",
                    "classifications": [
                        {
                            "name": "Display",
                            "features": [
                                {
                                    "name": "Screen Size (In Inches)",
                                    "featureValues": [{"value": "15.6"}]
                                }
                            ]
                        }
                    ]
                }
            }
        };
        </script>
    </html>
    """
    url = AnyHttpUrl("https://www.croma.com/samsung-galaxy-book4/p/320007")
    parsed = parse_croma_payload(
        payload={"html": html},
        source_url=url,
        source_product_id="320007",
        observed_at=datetime.now(UTC),
    )
    assert parsed.attributes["screen_size_inches"] == 15.6
    assert parsed.attributes["storage_type"] == "SSD"


def test_11_gtin_ean_and_mpn_extraction() -> None:
    html = """
    <html>
        <script>
        window.__INITIAL_DATA__= {
            "pdpReducer": {
                "pdpData": {
                    "name": "Apple MacBook Air M5",
                    "ean": "195949778899",
                    "classifications": [
                        {
                            "name": "Manufacturer",
                            "features": [
                                {"name": "Model Number", "featureValues": [{"value": "MRYR3HN/A"}]}
                            ]
                        }
                    ]
                }
            }
        };
        </script>
    </html>
    """
    url = AnyHttpUrl("https://www.croma.com/apple-macbook-air-m5/p/320008")
    parsed = parse_croma_payload(
        payload={"html": html},
        source_url=url,
        source_product_id="320008",
        observed_at=datetime.now(UTC),
    )
    assert parsed.attributes["ean"] == "195949778899"
    assert parsed.attributes["gtin"] == "195949778899"
    assert parsed.attributes["mpn"] == "MRYR3HN/A"


def test_12_and_13_price_and_mrp_extraction() -> None:
    html = """
    <html>
        <script>
        window.__INITIAL_DATA__= {
            "pdpReducer": {
                "pdpData": {
                    "name": "HP Pavilion 15",
                    "price": {"value": 67990.0},
                    "mrp": {"value": 85990.0}
                }
            }
        };
        </script>
    </html>
    """
    url = AnyHttpUrl("https://www.croma.com/hp-pavilion-15/p/320009")
    parsed = parse_croma_payload(
        payload={"html": html},
        source_url=url,
        source_product_id="320009",
        observed_at=datetime.now(UTC),
    )
    assert parsed.price_paise == 6799000
    assert parsed.mrp_paise == 8599000


def test_14_json_ld_fallback_price_extraction() -> None:
    html = """
    <html>
        <script type="application/ld+json">
        {
            "@type": "Product",
            "name": "MSI Modern 14 Laptop",
            "offers": {"price": "43990"}
        }
        </script>
    </html>
    """
    url = AnyHttpUrl("https://www.croma.com/msi-modern-14/p/320010")
    parsed = parse_croma_payload(
        payload={"html": html},
        source_url=url,
        source_product_id="320010",
        observed_at=datetime.now(UTC),
    )
    assert parsed.brand == "Msi"
    assert parsed.price_paise == 4399000


def test_15_and_16_product_url_and_code_extraction() -> None:
    adapter = CromaSourceAdapter([], FakeTransport())
    url = AnyHttpUrl("https://www.croma.com/dell-latitude-3440/p/320011")
    record = RawSourceRecord(
        source="croma",
        source_product_id="320011",
        category="laptop",
        source_url=url,
        observed_at=datetime.now(UTC),
        payload={"title": "Dell Latitude 3440", "price_paise": 6200000},
        content_hash="0123456789abcdef0123456789abcdef",
    )
    parsed = adapter.parse(record)
    assert parsed.source == "croma"
    assert parsed.source_product_id == "320011"
    assert str(parsed.source_url) == "https://www.croma.com/dell-latitude-3440/p/320011"


def test_17_missing_optional_specifications() -> None:
    html = """
    <html>
        <script>
        window.__INITIAL_DATA__= {
            "pdpReducer": {
                "pdpData": {
                    "name": "Generic Office Laptop",
                    "price": {"value": 25000.0}
                }
            }
        };
        </script>
    </html>
    """
    url = AnyHttpUrl("https://www.croma.com/generic-laptop/p/320012")
    parsed = parse_croma_payload(
        payload={"html": html},
        source_url=url,
        source_product_id="320012",
        observed_at=datetime.now(UTC),
    )
    assert parsed.title == "Generic Office Laptop"
    assert parsed.price_paise == 2500000
    assert "screen_size_inches" not in parsed.attributes
    assert "ean" not in parsed.attributes


def test_18_malformed_hydration_state_fallback() -> None:
    html = """
    <html>
        <script>
        window.__INITIAL_DATA__= { this is corrupted unparseable javascript }}};;
        </script>
        <h1 class="pd-title">HP 15s Notebook</h1>
        <span class="amount">₹41,990</span>
    </html>
    """
    url = AnyHttpUrl("https://www.croma.com/hp-15s/p/320013")
    parsed = parse_croma_payload(
        payload={"html": html},
        source_url=url,
        source_product_id="320013",
        observed_at=datetime.now(UTC),
    )
    assert parsed.title == "HP 15s Notebook"
    assert parsed.brand == "Hp"
    assert parsed.price_paise == 4199000


def test_19_empty_product_payload() -> None:
    url = AnyHttpUrl("https://www.croma.com/p/320014")
    parsed = parse_croma_payload(
        payload={},
        source_url=url,
        source_product_id="320014",
        observed_at=datetime.now(UTC),
    )
    assert parsed.source_product_id == "320014"
    assert parsed.title == "Croma Product 320014"
    assert parsed.price_paise == 0


def test_20_query_param_price_fallback() -> None:
    html = """
    <html>
        <h1>Lenovo V15 Laptop</h1>
    </html>
    """
    url = AnyHttpUrl("https://www.croma.com/lenovo-v15/p/320015?_price=3799000&_mrp=4999000")
    parsed = parse_croma_payload(
        payload={"html": html},
        source_url=url,
        source_product_id="320015",
        observed_at=datetime.now(UTC),
    )
    assert parsed.price_paise == 3799000
    assert parsed.mrp_paise == 4999000
