import pytest
from pydantic import ValidationError

from categories import CategoryDefinition, SubcategoryDefinition


def test_category_definition_normalizes_extension_points() -> None:
    definition = CategoryDefinition(
        department_code="electronics",
        code="mobile",
        label="Mobile phone",
        identity_attributes=(" Storage_GB ", "Color"),
        review_aspects=(" Camera ", "Battery"),
    )

    assert definition.identity_attributes == ("storage_gb", "color")
    assert definition.review_aspects == ("camera", "battery")


def test_category_definition_rejects_duplicate_names() -> None:
    with pytest.raises(ValidationError, match="must be unique"):
        CategoryDefinition(
            department_code="electronics",
            code="mobile",
            label="Mobile phone",
            identity_attributes=("storage_gb", "STORAGE_GB"),
            review_aspects=("camera",),
        )


def test_category_definition_rejects_blank_names() -> None:
    with pytest.raises(ValidationError, match="cannot be blank"):
        CategoryDefinition(
            department_code="electronics",
            code="mobile",
            label="Mobile phone",
            identity_attributes=("storage_gb",),
            review_aspects=(" ",),
        )


def test_category_definition_rejects_duplicate_subcategories() -> None:
    duplicate = SubcategoryDefinition(code="gaming", label="Gaming")
    with pytest.raises(ValidationError, match="subcategory codes must be unique"):
        CategoryDefinition(
            department_code="electronics",
            code="laptop",
            label="Laptop",
            subcategories=(duplicate, duplicate),
            identity_attributes=("model",),
            review_aspects=("performance",),
        )
