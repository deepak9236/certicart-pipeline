"""Unit tests for multi-signal data quality classification and accessory detection."""

from datetime import UTC, datetime

from pydantic import AnyHttpUrl

from quality import DataQualityClassifier, QualityStatus
from sources.contracts import ParsedProduct


def test_accessory_detection_identifies_covers_sleeves_and_stands() -> None:
    # Sleeve
    is_acc, reason = DataQualityClassifier.detect_accessory(
        "Shopper's Cloud Laptop Sleeve Case Cover for MacBook Air",
    )
    assert is_acc is True
    assert reason is not None

    # Stand
    is_acc2, reason2 = DataQualityClassifier.detect_accessory(
        "Aluminum Adjustable Laptop Stand Mount for Desk",
    )
    assert is_acc2 is True
    assert reason2 is not None

    # Genuine laptop
    is_acc3, reason3 = DataQualityClassifier.detect_accessory(
        "Apple MacBook Air M3 13.6 inch (16GB RAM, 512GB SSD)",
    )
    assert is_acc3 is False
    assert reason3 is None


def test_price_sanity_evaluation() -> None:
    # Normal laptop price
    ok, _ = DataQualityClassifier.evaluate_price_sanity("laptop", 4500000)
    assert ok is True

    # Too cheap laptop (e.g. ₹899 accessory wrongly classified as laptop)
    too_cheap, reason = DataQualityClassifier.evaluate_price_sanity("laptop", 89900)
    assert too_cheap is False
    assert "below minimum sanity threshold" in str(reason)

    # Negative price
    neg, reason_neg = DataQualityClassifier.evaluate_price_sanity("laptop", 0)
    assert neg is False
    assert "non-positive" in str(reason_neg)


def test_quality_classifier_full_flow() -> None:
    # 1. Valid Product
    valid_product = ParsedProduct(
        source="amazon",
        source_product_id="B0VALID001",
        source_url=AnyHttpUrl("https://amazon.in/dp/B0VALID001"),
        category="laptop",
        title="Lenovo IdeaPad Slim 3 (16GB RAM, 512GB SSD, Ryzen 7)",
        brand="Lenovo",
        model_name="IdeaPad Slim 3",
        price_paise=5899000,
        attributes={"ram_gb": 16, "storage_gb": 512, "cpu_model": "ryzen 7"},
        in_stock=True,
        observed_at=datetime.now(UTC),
    )
    report_valid = DataQualityClassifier.classify(valid_product)
    assert report_valid.status == QualityStatus.VALID
    assert report_valid.score >= 80
    assert report_valid.is_accessory is False
    assert report_valid.price_sanity_passed is True

    # 2. Rejected Accessory
    acc_product = ParsedProduct(
        source="amazon",
        source_product_id="B0ACC001",
        source_url=AnyHttpUrl("https://amazon.in/dp/B0ACC001"),
        category="laptop",
        title="Laptop Sleeve Case 15.6 Inch Protective Bag",
        brand="Generic",
        model_name="Laptop Sleeve Case",
        price_paise=79900,
        in_stock=True,
        observed_at=datetime.now(UTC),
    )
    report_acc = DataQualityClassifier.classify(acc_product)
    assert report_acc.status == QualityStatus.REJECTED
    assert report_acc.is_accessory is True
    assert len(report_acc.flags) >= 1
