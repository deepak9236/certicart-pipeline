"""Tests for CategoryHandler protocol, LaptopCategoryHandler, and Category Registry."""

from datetime import UTC, datetime

from pydantic import AnyHttpUrl

from categories.electronics.laptop import (
    ConflictReason,
    LaptopCategoryHandler,
    LaptopIdentityNormalizer,
)
from categories.handler import CategoryHandler
from categories.registry import (
    get_category_handler,
    is_category_supported,
    register_category_handler,
)
from matching.fingerprint import ProductFingerprint
from matching.matcher import MatchDecision, compare_products
from sources.contracts import ParsedProduct


def test_laptop_category_handler_interface() -> None:
    handler = LaptopCategoryHandler()
    assert isinstance(handler, CategoryHandler)
    assert handler.category_code == "laptop"

    parsed = ParsedProduct(
        source="amazon",
        source_product_id="B0TEST001",
        source_url=AnyHttpUrl("https://amazon.in/dp/B0TEST001"),
        category="laptop",
        title="Apple MacBook Air M5 (16GB RAM, 512GB SSD, 15.3 inch)",
        brand="Apple",
        model_name="MacBook Air M5",
        price_paise=13490000,
        mrp_paise=14990000,
        coupon_price_paise=None,
        in_stock=True,
        attributes={"ram_gb": 16, "storage_gb": 512, "screen_size_inches": 15.3},
        observed_at=datetime.now(UTC),
    )

    fp = handler.normalize(parsed)
    assert fp.category == "laptop"
    assert fp.brand == "apple"
    assert fp.family == "macbook air"
    assert fp.chip == "m5"
    assert fp.ram_gb == 16
    assert fp.storage_gb == 512
    assert fp.screen_size_inches == 15.3


def test_laptop_category_handler_conflicts_and_similarity() -> None:
    handler = get_category_handler("laptop")

    fp_m5 = ProductFingerprint(
        category="laptop",
        brand="apple",
        family="macbook air",
        model_name="MacBook Air M5",
        chip="m5",
        ram_gb=16,
        storage_gb=512,
        attributes={"ram_gb": 16, "storage_gb": 512, "cpu_model": "m5"},
    )

    fp_m4 = ProductFingerprint(
        category="laptop",
        brand="apple",
        family="macbook air",
        model_name="MacBook Air M4",
        chip="m4",
        ram_gb=16,
        storage_gb=512,
        attributes={"ram_gb": 16, "storage_gb": 512, "cpu_model": "m4"},
    )

    has_conflict, reason = handler.check_hard_conflicts(fp_m5, fp_m4)
    assert has_conflict is True
    assert "different processor" in str(reason)

    sim = handler.compute_similarity(fp_m5, fp_m5)
    assert sim >= 0.75


def test_retailer_category_matrix_and_custom_registration() -> None:
    assert is_category_supported("amazon", "laptop") is True
    assert is_category_supported("flipkart", "laptop") is True
    assert is_category_supported("croma", "laptop") is True
    assert is_category_supported("croma", "mobile") is True
    assert is_category_supported("croma", "television") is False

    from categories.contracts import CategoryDefinition
    from categories.registry import _CATEGORIES, _CATEGORY_HANDLERS

    try:
        _CATEGORIES["television"] = CategoryDefinition(
            department_code="electronics",
            code="television",
            label="Television",
            identity_attributes=("screen_size",),
            review_aspects=("display",),
        )

        class DummyTVHandler:
            @property
            def category_code(self) -> str:
                return "television"

            def normalize(self, product: ParsedProduct) -> ProductFingerprint:
                return ProductFingerprint(
                    category="television",
                    brand=product.brand or "unknown",
                    model_name=product.title,
                    attributes={},
                )

            def check_hard_conflicts(
                self,
                left: ProductFingerprint,
                right: ProductFingerprint,
            ) -> tuple[bool, str | None]:
                if left.brand != right.brand:
                    return True, ConflictReason.DIFFERENT_BRANDS
                return False, None

            def compute_similarity(
                self,
                left: ProductFingerprint,
                right: ProductFingerprint,
            ) -> float:
                return 1.0

        register_category_handler("television", DummyTVHandler())
        handler = get_category_handler("television")
        assert handler.category_code == "television"
    finally:
        _CATEGORIES.pop("television", None)
        _CATEGORY_HANDLERS.pop("television", None)


def test_cross_category_matching_rejection() -> None:
    fp_laptop = ProductFingerprint(
        category="laptop",
        brand="apple",
        model_name="MacBook Air M5",
        attributes={"ram_gb": 16, "storage_gb": 512},
    )

    fp_phone = ProductFingerprint(
        category="mobile",
        brand="apple",
        model_name="iPhone 16 Pro",
        attributes={"ram_gb": 8, "storage_gb": 256},
    )

    res = compare_products(fp_laptop, fp_phone)
    assert res.decision == MatchDecision.NO_MATCH
    assert res.reasons == (ConflictReason.DIFFERENT_CATEGORIES,)


def test_electronics_laptop_exports() -> None:
    handler = LaptopCategoryHandler()
    assert handler.category_code == "laptop"
    assert issubclass(LaptopIdentityNormalizer, object)
    assert ConflictReason.DIFFERENT_CATEGORIES == "different categories"


def test_electronics_mobile_category_handler() -> None:
    from categories.electronics.mobile import (
        MobileCategoryHandler,
        MobileIdentityNormalizer,
        check_mobile_hard_conflicts,
    )

    handler = get_category_handler("mobile")
    assert isinstance(handler, MobileCategoryHandler)
    assert handler.category_code == "mobile"

    parsed = ParsedProduct(
        source="amazon",
        source_product_id="B0MOBILE01",
        source_url=AnyHttpUrl("https://amazon.in/dp/B0MOBILE01"),
        category="mobile",
        title="Apple iPhone 16 Pro (128 GB) - Natural Titanium",
        brand="Apple",
        model_name="iPhone 16 Pro",
        price_paise=11990000,
        in_stock=True,
        observed_at=datetime.now(UTC),
    )
    fp = handler.normalize(parsed)
    assert fp.brand == "apple"
    assert fp.storage_gb == 128
    assert fp.attributes["color"] == "natural titanium"

    # Test conflict detection
    fp2 = MobileIdentityNormalizer.normalize("Apple iPhone 16 Pro (256 GB) - Desert Titanium")
    has_conflict, reason = check_mobile_hard_conflicts(fp, fp2)
    assert has_conflict is True
    assert "storage_gb" in str(reason)

    # Test conflict on different brand
    fp_samsung = MobileIdentityNormalizer.normalize(
        "Samsung Galaxy S24 Ultra (12GB RAM, 256GB Storage)"
    )
    conf_brand, _ = handler.check_hard_conflicts(fp, fp_samsung)
    assert conf_brand is True

    # Test similarity computation
    sim = handler.compute_similarity(fp, fp)
    assert sim >= 0.50
