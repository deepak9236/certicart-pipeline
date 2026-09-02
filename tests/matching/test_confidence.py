"""Unit tests for 100-point explainable product identity confidence scoring."""

from matching.confidence import (
    IdentityConfidenceScorer,
    MatchConfidenceTier,
)
from matching.fingerprint import ProductFingerprint


def test_confidence_scorer_deterministic_gtin_match() -> None:
    fp1 = ProductFingerprint(
        category="laptop",
        brand="apple",
        model_name="MacBook Air M3",
        gtin="195950690132",
        attributes={"ram_gb": 16, "storage_gb": 512},
    )
    fp2 = ProductFingerprint(
        category="laptop",
        brand="apple",
        model_name="Apple 2024 MacBook Air",
        gtin="195950690132",
        attributes={"ram_gb": 16, "storage_gb": 512},
    )

    score, tier, breakdown = IdentityConfidenceScorer.calculate_confidence(fp1, fp2)
    assert score == 100
    assert tier == MatchConfidenceTier.MATCH
    assert breakdown.brand_points == 20
    assert breakdown.identifier_points == 10


def test_confidence_scorer_attribute_breakdown_strong_match() -> None:
    fp1 = ProductFingerprint(
        category="laptop",
        brand="lenovo",
        family="ideapad",
        model_name="IdeaPad Slim 3 15AMN8",
        chip="Ryzen 7 5700U",
        ram_gb=16,
        storage_gb=512,
        attributes={"ram_gb": 16, "storage_gb": 512, "cpu_model": "Ryzen 7 5700U"},
    )
    fp2 = ProductFingerprint(
        category="laptop",
        brand="lenovo",
        family="ideapad",
        model_name="IdeaPad Slim 3 15AMN8",
        chip="Ryzen 7 5700U",
        ram_gb=16,
        storage_gb=512,
        attributes={"ram_gb": 16, "storage_gb": 512, "cpu_model": "Ryzen 7 5700U"},
    )

    score, tier, breakdown = IdentityConfidenceScorer.calculate_confidence(fp1, fp2)
    assert score >= 85
    assert tier in (MatchConfidenceTier.MATCH, MatchConfidenceTier.STRONG_MATCH)
    assert breakdown.brand_points == 20
    assert breakdown.model_points == 25
    assert breakdown.ram_points == 15
    assert breakdown.storage_points == 15
    assert breakdown.chip_points == 10


def test_confidence_scorer_different_brands_no_match() -> None:
    fp1 = ProductFingerprint(
        category="laptop",
        brand="apple",
        model_name="MacBook Air M3",
        attributes={"ram_gb": 16},
    )
    fp2 = ProductFingerprint(
        category="laptop",
        brand="dell",
        model_name="XPS 13",
        attributes={"ram_gb": 16},
    )

    _score, tier, breakdown = IdentityConfidenceScorer.calculate_confidence(fp1, fp2)
    assert breakdown.brand_points == 0
    assert tier == MatchConfidenceTier.NO_MATCH
