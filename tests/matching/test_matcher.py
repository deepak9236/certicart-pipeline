import pytest
from pydantic import ValidationError

from matching import MatchDecision, ProductFingerprint, compare_products


def fingerprint(**updates: object) -> ProductFingerprint:
    values: dict[str, object] = {
        "category": "laptop",
        "brand": "Lenovo",
        "model_name": "ThinkBook 14",
        "manufacturer_part_number": None,
        "gtin": None,
        "attributes": {
            "cpu_model": "Ryzen 7",
            "gpu_model": "Integrated",
            "ram_gb": 16,
            "storage_gb": 512,
        },
    }
    values.update(updates)
    return ProductFingerprint.model_validate(values)


def test_exact_gtin_matches() -> None:
    result = compare_products(
        fingerprint(gtin="8901234567890"),
        fingerprint(model_name="Different title", gtin="8901234567890"),
    )

    assert result.decision is MatchDecision.MATCH
    assert result.reasons == ("exact GTIN",)


def test_fingerprint_normalizes_attribute_names_and_values() -> None:
    product = fingerprint(
        attributes={
            " CPU_MODEL ": " Ryzen  7 ",
            "gpu_model": "Integrated",
            "ram_gb": 16,
            "storage_gb": 512,
        }
    )

    assert product.attributes["cpu_model"] == "ryzen 7"


def test_fingerprint_rejects_blank_attribute_name() -> None:
    with pytest.raises(ValidationError, match="attribute names cannot be blank"):
        fingerprint(attributes={" ": "value"})


def test_fingerprint_rejects_unregistered_category() -> None:
    with pytest.raises(ValidationError, match="unsupported category"):
        fingerprint(category="television")


def test_exact_part_number_matches() -> None:
    result = compare_products(
        fingerprint(manufacturer_part_number="21KJ001IN"),
        fingerprint(model_name="Different title", manufacturer_part_number="21kj001in"),
    )

    assert result.decision is MatchDecision.MATCH
    assert result.confidence == 100


def test_different_part_numbers_do_not_match() -> None:
    result = compare_products(
        fingerprint(manufacturer_part_number="SKU-A"),
        fingerprint(manufacturer_part_number="SKU-B"),
    )

    assert result.decision is MatchDecision.NO_MATCH


def test_different_brands_do_not_match() -> None:
    result = compare_products(fingerprint(), fingerprint(brand="HP"))

    assert result.decision is MatchDecision.NO_MATCH
    assert result.reasons == ("different brands",)


def test_different_configuration_does_not_match() -> None:
    attributes = dict(fingerprint().attributes)
    attributes["ram_gb"] = 8
    result = compare_products(fingerprint(), fingerprint(attributes=attributes))

    assert result.decision is MatchDecision.NO_MATCH
    assert "ram_gb" in result.reasons[0]


def test_same_configuration_and_model_matches() -> None:
    result = compare_products(fingerprint(), fingerprint())

    assert result.decision is MatchDecision.MATCH


def test_uncertain_model_name_requires_review() -> None:
    result = compare_products(fingerprint(), fingerprint(model_name="Business Laptop"))

    assert result.decision is MatchDecision.REVIEW


def test_different_categories_do_not_match() -> None:
    right = fingerprint().model_copy(update={"category": "mobile"})

    result = compare_products(fingerprint(), right)

    assert result.decision is MatchDecision.NO_MATCH
    assert result.reasons == ("different categories",)


def test_missing_identity_attribute_requires_review() -> None:
    attributes = dict(fingerprint().attributes)
    del attributes["storage_gb"]

    result = compare_products(fingerprint(), fingerprint(attributes=attributes))

    assert result.decision is MatchDecision.REVIEW
    assert "storage_gb" in result.reasons[0]
