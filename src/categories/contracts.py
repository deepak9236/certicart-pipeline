"""Contracts shared by every product category."""

from typing import Any, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, field_validator

AttributeValue: TypeAlias = str | int | float | bool | dict[str, Any] | list[Any]


class SubcategoryDefinition(BaseModel):
    """A category-specific merchandising/classification branch."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    label: str = Field(min_length=1)


class CategoryDefinition(BaseModel):
    """Identity and review rules owned by a category adapter."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    department_code: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    code: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    label: str = Field(min_length=1)
    subcategories: tuple[SubcategoryDefinition, ...] = ()
    identity_attributes: tuple[str, ...] = Field(min_length=1)
    review_aspects: tuple[str, ...] = Field(min_length=1)

    @field_validator("identity_attributes", "review_aspects")
    @classmethod
    def validate_unique_names(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(value.casefold().strip() for value in values)
        if any(not value for value in normalized):
            raise ValueError("category names cannot be blank")
        if len(set(normalized)) != len(normalized):
            raise ValueError("category names must be unique")
        return normalized

    @field_validator("subcategories")
    @classmethod
    def validate_unique_subcategories(
        cls, values: tuple[SubcategoryDefinition, ...]
    ) -> tuple[SubcategoryDefinition, ...]:
        codes = tuple(value.code for value in values)
        if len(set(codes)) != len(codes):
            raise ValueError("subcategory codes must be unique")
        return values
