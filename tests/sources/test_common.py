"""Unit tests for shared source extraction and parsing utilities."""

from __future__ import annotations

from sources.common import (
    build_category_attributes,
    clean_capacity_str,
    extract_digits_to_paise,
    extract_json_ld_products,
    infer_brand,
)


def test_extract_digits_to_paise() -> None:
    assert extract_digits_to_paise("₹39,990.00") == 3999000
    assert extract_digits_to_paise("54,990") == 5499000
    assert extract_digits_to_paise("1,15,990.50") == 11599050
    assert extract_digits_to_paise("") is None
    assert extract_digits_to_paise(None) is None
    assert extract_digits_to_paise("Free / Not Available") is None


def test_infer_brand() -> None:
    assert infer_brand("ASUS Vivobook 15", None) == "Asus"
    assert infer_brand("Apple MacBook Air M5", None) == "Apple"
    assert infer_brand("HP Pavilion 14", None) == "Hp"
    assert infer_brand("Lenovo IdeaPad Slim 3", None) == "Lenovo"
    assert infer_brand("Unknown Laptop X", "Samsung") == "Samsung"
    assert infer_brand("Custom Device Pro", None) == "Custom"
    assert infer_brand("", None) == "Generic"


def test_clean_capacity_str() -> None:
    assert clean_capacity_str("16GB DDR5") == "16GB"
    assert clean_capacity_str("512 GB SSD") == "512 GB"
    assert clean_capacity_str("1 TB NVMe") == "1 TB"
    assert clean_capacity_str("Non-matching string") == "Non-matching string"


def test_extract_json_ld_products() -> None:
    html = """
    <html>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "ASUS Vivobook 15",
            "offers": {"price": 38990}
        }
        </script>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "Product",
                    "name": "Apple MacBook Air M5"
                }
            ]
        }
        </script>
    </html>
    """
    products = extract_json_ld_products(html)
    assert len(products) == 2
    assert products[0]["name"] == "ASUS Vivobook 15"
    assert products[1]["name"] == "Apple MacBook Air M5"


def test_build_category_attributes_laptop() -> None:
    raw_specs = {
        "RAM Size": "16 GB",
        "Hard Drive Size": "512 GB",
        "Processor Brand": "Intel Core i5-13420H",
        "Graphics Card Description": "NVIDIA GeForce RTX 3050",
        "Screen Size": "15.6 inch",
    }
    attrs = build_category_attributes(
        category="laptop",
        title="ASUS TUF Gaming Laptop",
        raw_specs=raw_specs,
    )
    assert attrs["ram_gb"] == 16
    assert attrs["storage_gb"] == 512
    assert attrs["cpu_model"] == "Intel Core i5-13420H"
    assert attrs["gpu_model"] == "NVIDIA GeForce RTX 3050"
    assert attrs["screen_size_inches"] == 15.6
    assert attrs["ram size"] == "16 GB"


def test_build_category_attributes_generic() -> None:
    raw_specs = {
        "Battery Capacity": "5000 mAh",
        "Camera Resolution": "50 MP",
    }
    attrs = build_category_attributes(
        category="mobile",
        title="Smartphone Pro Max",
        raw_specs=raw_specs,
    )
    assert attrs["battery capacity"] == "5000 mAh"
    assert attrs["camera resolution"] == "50 MP"
    assert "ram_gb" not in attrs
