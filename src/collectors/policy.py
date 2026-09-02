"""Bounded collection profiles and per-run planning."""

from enum import StrEnum
from types import MappingProxyType

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CollectionProfileName(StrEnum):
    SMOKE = "smoke"
    SHADOW = "shadow"
    INCREMENTAL = "incremental"
    BACKFILL = "backfill"


class CollectionBudget(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    profile: CollectionProfileName
    max_products_per_source: int = Field(ge=1, le=10_000)
    product_batch_size: int = Field(ge=1, le=500)
    max_reviews_per_product: int = Field(ge=0, le=500)
    max_concurrency: int = Field(ge=1, le=10)
    minimum_request_delay_seconds: float = Field(ge=0, le=60)

    @model_validator(mode="after")
    def require_batch_within_run_limit(self) -> "CollectionBudget":
        if self.product_batch_size > self.max_products_per_source:
            raise ValueError("product batch size cannot exceed the per-source run limit")
        return self


class CollectionRunPlan(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    source: str = Field(min_length=1)
    category: str = Field(min_length=1)
    profile: CollectionProfileName
    available_products: int = Field(ge=0)
    planned_products: int = Field(ge=0)
    product_batch_size: int = Field(ge=1)
    max_concurrency: int = Field(ge=1)
    minimum_request_delay_seconds: float = Field(ge=0)
    max_reviews_per_product: int = Field(ge=0)
    maximum_review_records: int = Field(ge=0)
    maximum_total_records: int = Field(ge=0)


_PROFILES = MappingProxyType(
    {
        CollectionProfileName.SMOKE: CollectionBudget(
            profile=CollectionProfileName.SMOKE,
            max_products_per_source=5,
            product_batch_size=5,
            max_reviews_per_product=5,
            max_concurrency=1,
            minimum_request_delay_seconds=2,
        ),
        CollectionProfileName.SHADOW: CollectionBudget(
            profile=CollectionProfileName.SHADOW,
            max_products_per_source=25,
            product_batch_size=10,
            max_reviews_per_product=10,
            max_concurrency=1,
            minimum_request_delay_seconds=2,
        ),
        CollectionProfileName.INCREMENTAL: CollectionBudget(
            profile=CollectionProfileName.INCREMENTAL,
            max_products_per_source=100,
            product_batch_size=25,
            max_reviews_per_product=25,
            max_concurrency=2,
            minimum_request_delay_seconds=2,
        ),
        CollectionProfileName.BACKFILL: CollectionBudget(
            profile=CollectionProfileName.BACKFILL,
            max_products_per_source=500,
            product_batch_size=50,
            max_reviews_per_product=50,
            max_concurrency=2,
            minimum_request_delay_seconds=2,
        ),
    }
)


def get_collection_budget(profile: str | CollectionProfileName) -> CollectionBudget:
    try:
        normalized = CollectionProfileName(profile)
        return _PROFILES[normalized]
    except (KeyError, ValueError) as error:
        raise ValueError(f"unsupported collection profile: {profile!r}") from error


def create_collection_plan(
    *,
    source: str,
    category: str,
    available_products: int,
    profile: str | CollectionProfileName,
) -> CollectionRunPlan:
    if available_products < 0:
        raise ValueError("available products cannot be negative")
    budget = get_collection_budget(profile)
    planned_products = min(available_products, budget.max_products_per_source)
    maximum_review_records = planned_products * budget.max_reviews_per_product
    return CollectionRunPlan(
        source=source,
        category=category,
        profile=budget.profile,
        available_products=available_products,
        planned_products=planned_products,
        product_batch_size=budget.product_batch_size,
        max_concurrency=budget.max_concurrency,
        minimum_request_delay_seconds=budget.minimum_request_delay_seconds,
        max_reviews_per_product=budget.max_reviews_per_product,
        maximum_review_records=maximum_review_records,
        maximum_total_records=planned_products + maximum_review_records,
    )
