import pytest
from pydantic import ValidationError

from collectors import (
    CollectionBudget,
    CollectionProfileName,
    create_collection_plan,
    get_collection_budget,
)


def test_incremental_plan_is_capped_per_source_and_includes_reviews() -> None:
    plan = create_collection_plan(
        source="amazon",
        category="laptop",
        available_products=1_000,
        profile="incremental",
    )

    assert plan.planned_products == 100
    assert plan.maximum_review_records == 2_500
    assert plan.maximum_total_records == 2_600
    assert plan.max_concurrency == 2


def test_smoke_plan_reports_zero_when_nothing_is_seeded() -> None:
    plan = create_collection_plan(
        source="amazon",
        category="laptop",
        available_products=0,
        profile=CollectionProfileName.SMOKE,
    )

    assert plan.planned_products == 0
    assert plan.maximum_total_records == 0


def test_collection_budget_rejects_batch_larger_than_run() -> None:
    with pytest.raises(ValidationError, match="batch size cannot exceed"):
        CollectionBudget(
            profile=CollectionProfileName.SMOKE,
            max_products_per_source=5,
            product_batch_size=6,
            max_reviews_per_product=5,
            max_concurrency=1,
            minimum_request_delay_seconds=2,
        )


def test_unknown_profile_is_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported collection profile"):
        get_collection_budget("unlimited")


def test_negative_available_products_are_rejected() -> None:
    with pytest.raises(ValueError, match="cannot be negative"):
        create_collection_plan(
            source="amazon",
            category="laptop",
            available_products=-1,
            profile="smoke",
        )
