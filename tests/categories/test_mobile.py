"""Unit tests for Electronics / Mobile category normalizer, rules, and handler."""

from categories.electronics.mobile import (
    ConflictReason,
    MobileCategoryHandler,
    MobileIdentityNormalizer,
    check_mobile_hard_conflicts,
)
from matching.fingerprint import ProductFingerprint


def test_mobile_normalizer_extracts_brands() -> None:
    assert MobileIdentityNormalizer.extract_brand("Apple iPhone 16 Pro") == "apple"
    assert MobileIdentityNormalizer.extract_brand("Samsung Galaxy S24 Ultra") == "samsung"
    assert MobileIdentityNormalizer.extract_brand("OnePlus 12 (16GB RAM)") == "oneplus"
    assert MobileIdentityNormalizer.extract_brand("Google Pixel 9 Pro") == "google"
    assert MobileIdentityNormalizer.extract_brand("Redmi Note 13 Pro+") == "redmi"
    assert MobileIdentityNormalizer.extract_brand("Unknown Phone XYZ") == "unknown"


def test_mobile_normalizer_extracts_ram_and_storage() -> None:
    norm = MobileIdentityNormalizer.normalize(
        "OnePlus 12 5G (Flowy Emerald, 16GB RAM, 512GB Storage)",
        category="mobile",
    )
    assert norm.brand == "oneplus"
    assert norm.ram_gb == 16
    assert norm.storage_gb == 512
    assert norm.attributes["network_type"] == "5g"

    # Terabyte storage
    norm_tb = MobileIdentityNormalizer.normalize(
        "Apple iPhone 16 Pro Max (1 TB) - Desert Titanium",
        category="mobile",
    )
    assert norm_tb.brand == "apple"
    assert norm_tb.storage_gb == 1024
    assert norm_tb.family == "iphone pro max"


def test_mobile_normalizer_extracts_chipsets() -> None:
    norm_snap = MobileIdentityNormalizer.normalize(
        "Samsung Galaxy S24 Ultra (Snapdragon 8 Gen 3, 12GB RAM)",
        category="mobile",
    )
    assert norm_snap.chip == "snapdragon 8 gen 3"

    norm_dim = MobileIdentityNormalizer.normalize(
        "Vivo X100 Pro (Dimensity 9300, 16GB RAM)",
        category="mobile",
    )
    assert norm_dim.chip == "dimensity 9300"


def test_mobile_hard_conflicts() -> None:
    fp_a = MobileIdentityNormalizer.normalize("Apple iPhone 16 Pro (128GB) - Natural Titanium")
    fp_b = MobileIdentityNormalizer.normalize("Apple iPhone 16 Pro (256GB) - Natural Titanium")
    fp_max = MobileIdentityNormalizer.normalize(
        "Apple iPhone 16 Pro Max (128GB) - Natural Titanium"
    )

    # Storage conflict
    conf, reason = check_mobile_hard_conflicts(fp_a, fp_b)
    assert conf is True
    assert "storage_gb" in str(reason)

    # Family conflict (Pro vs Pro Max)
    conf_fam, reason_fam = check_mobile_hard_conflicts(fp_a, fp_max)
    assert conf_fam is True
    assert ConflictReason.DIFFERENT_FAMILIES in str(reason_fam)

    # Different categories conflict
    fp_laptop = ProductFingerprint(
        category="laptop",
        brand="apple",
        model_name="MacBook Pro",
        attributes={},
    )
    conf_cat, _ = check_mobile_hard_conflicts(fp_a, fp_laptop)
    assert conf_cat is True

    # GTIN and MPN conflict
    fp_gtin1 = MobileIdentityNormalizer.normalize("Google Pixel 9 (128GB)", gtin="1111111111111")
    fp_gtin2 = MobileIdentityNormalizer.normalize("Google Pixel 9 (128GB)", gtin="2222222222222")
    conf_gtin, _ = check_mobile_hard_conflicts(fp_gtin1, fp_gtin2)
    assert conf_gtin is True

    # Chipset conflict
    fp_a17 = MobileIdentityNormalizer.normalize("Apple iPhone 15 Pro A17 Pro (128GB)")
    fp_a18 = MobileIdentityNormalizer.normalize("Apple iPhone 16 Pro A18 Pro (128GB)")
    conf_chip, _ = check_mobile_hard_conflicts(fp_a17, fp_a18)
    assert conf_chip is True


def test_mobile_handler_similarity() -> None:
    handler = MobileCategoryHandler()
    fp1 = MobileIdentityNormalizer.normalize("Apple iPhone 16 Pro (128GB)")
    fp2 = MobileIdentityNormalizer.normalize("Apple iPhone 16 Pro (128GB)")
    sim = handler.compute_similarity(fp1, fp2)
    assert sim >= 0.50
