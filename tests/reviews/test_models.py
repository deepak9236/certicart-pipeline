from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from reviews import (
    CollectedReview,
    ReviewAspectEvidence,
    ReviewCollectionPage,
    ReviewTarget,
    Sentiment,
)


def collected_review(**updates: object) -> CollectedReview:
    values: dict[str, object] = {
        "source": "amazon",
        "source_product_id": "B0EXAMPLE1",
        "review_id": "R-1",
        "category": "laptop",
        "target": ReviewTarget.PRODUCT,
        "rating": 4,
        "body": "Good performance and battery life.",
        "verified_purchase": True,
        "source_url": "https://www.amazon.in/review/R-1",
        "published_at": datetime.now(UTC),
        "observed_at": datetime.now(UTC),
        "content_hash": "0123456789abcdef",
    }
    values.update(updates)
    return CollectedReview.model_validate(values)


def test_collected_review_has_provenance_without_author_identity() -> None:
    review = collected_review()

    assert review.review_id == "R-1"
    assert review.target is ReviewTarget.PRODUCT
    assert "author" not in CollectedReview.model_fields


def test_collected_review_rejects_naive_timestamp() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        collected_review(observed_at=datetime.now())


def test_review_page_requires_one_product_identity() -> None:
    with pytest.raises(ValidationError, match="different product"):
        ReviewCollectionPage(
            source="amazon",
            source_product_id="B0OTHER",
            category="laptop",
            reviews=(collected_review(),),
            observed_at=datetime.now(UTC),
        )


def test_review_evidence_separates_target_and_aspect() -> None:
    evidence = ReviewAspectEvidence(
        review_id="review-1",
        variant_id="variant-1",
        category="laptop",
        target=ReviewTarget.PRODUCT,
        aspect="battery",
        sentiment=Sentiment.NEGATIVE,
        confidence=0.9,
        evidence_text="battery is weak",
        model_version="aspect-v1",
    )

    assert evidence.target is ReviewTarget.PRODUCT
    assert evidence.aspect == "battery"


def test_review_confidence_is_bounded() -> None:
    with pytest.raises(ValidationError):
        ReviewAspectEvidence(
            review_id="review-1",
            category="laptop",
            target=ReviewTarget.SELLER,
            aspect="reliability",
            sentiment=Sentiment.NEGATIVE,
            confidence=1.5,
            evidence_text="wrong charger",
            model_version="aspect-v1",
        )


def test_review_aspect_must_belong_to_category() -> None:
    with pytest.raises(ValidationError, match="unsupported laptop review aspect"):
        ReviewAspectEvidence(
            review_id="review-1",
            category="laptop",
            target=ReviewTarget.PRODUCT,
            aspect="camera",
            sentiment=Sentiment.NEUTRAL,
            confidence=0.7,
            evidence_text="camera is okay",
            model_version="aspect-v1",
        )
