"""Ground-truth benchmark test suite for product matching precision and recall.

Stress-tests the deterministic matcher across 55+ cross-retailer edge cases,
adversarial negative pairs, and ambiguous incomplete descriptions.
"""

import pytest
from tests.matching.benchmark_dataset import (
    AMBIGUOUS_REVIEW_PAIRS,
    NEGATIVE_ADVERSARIAL_PAIRS,
    POSITIVE_PAIRS,
)

from matching.matcher import MatchDecision, compare_products
from matching.normalizer import LaptopIdentityNormalizer


@pytest.mark.parametrize(("title_a", "title_b", "description"), POSITIVE_PAIRS)
def test_positive_matching_benchmark(title_a: str, title_b: str, description: str) -> None:
    fp_a = LaptopIdentityNormalizer.normalize_product(title_a)
    fp_b = LaptopIdentityNormalizer.normalize_product(title_b)

    result = compare_products(fp_a, fp_b)
    assert result.decision is MatchDecision.MATCH, (
        f"Failed to match positive pair [{description}]:\n"
        f"A: {fp_a.model_dump()}\n"
        f"B: {fp_b.model_dump()}\n"
        f"Result: {result}"
    )
    assert result.confidence >= 88.0


@pytest.mark.parametrize(("title_a", "title_b", "description"), NEGATIVE_ADVERSARIAL_PAIRS)
def test_negative_matching_benchmark_zero_false_positives(
    title_a: str,
    title_b: str,
    description: str,
) -> None:
    fp_a = LaptopIdentityNormalizer.normalize_product(title_a)
    fp_b = LaptopIdentityNormalizer.normalize_product(title_b)

    result = compare_products(fp_a, fp_b)
    assert result.decision is MatchDecision.NO_MATCH, (
        f"FALSE POSITIVE MATCH on [{description}]:\n"
        f"A: {fp_a.model_dump()}\n"
        f"B: {fp_b.model_dump()}\n"
        f"Result: {result}"
    )


@pytest.mark.parametrize(("title_a", "title_b", "description"), AMBIGUOUS_REVIEW_PAIRS)
def test_ambiguous_incomplete_matching_benchmark(
    title_a: str,
    title_b: str,
    description: str,
) -> None:
    fp_a = LaptopIdentityNormalizer.normalize_product(title_a)
    fp_b = LaptopIdentityNormalizer.normalize_product(title_b)

    result = compare_products(fp_a, fp_b)
    assert result.decision is MatchDecision.REVIEW, (
        f"Expected REVIEW on ambiguous pair [{description}] but got {result.decision}:\n"
        f"A: {fp_a.model_dump()}\n"
        f"B: {fp_b.model_dump()}\n"
        f"Result: {result}"
    )


def test_benchmark_overall_precision_and_recall() -> None:
    """Evaluate global precision and recall across the 55+ benchmark dataset."""
    true_positives = 0
    false_positives = 0
    false_negatives = 0

    # Evaluate positives
    for title_a, title_b, _ in POSITIVE_PAIRS:
        fp_a = LaptopIdentityNormalizer.normalize_product(title_a)
        fp_b = LaptopIdentityNormalizer.normalize_product(title_b)
        result = compare_products(fp_a, fp_b)
        if result.decision is MatchDecision.MATCH:
            true_positives += 1
        else:
            false_negatives += 1

    # Evaluate adversarial negatives
    for title_a, title_b, _ in NEGATIVE_ADVERSARIAL_PAIRS:
        fp_a = LaptopIdentityNormalizer.normalize_product(title_a)
        fp_b = LaptopIdentityNormalizer.normalize_product(title_b)
        result = compare_products(fp_a, fp_b)
        if result.decision is MatchDecision.MATCH:
            false_positives += 1

    precision = (
        true_positives / (true_positives + false_positives)
        if (true_positives + false_positives) > 0
        else 1.0
    )
    recall = (
        true_positives / (true_positives + false_negatives)
        if (true_positives + false_negatives) > 0
        else 1.0
    )

    # Acceptance Criteria: Zero False Positives (Precision >= 98%), Recall >= 90%
    assert precision >= 0.98, f"Precision was {precision:.2%}, expected >= 98%"
    assert recall >= 0.90, f"Recall was {recall:.2%}, expected >= 90%"
