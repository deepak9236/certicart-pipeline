"""Unit test validating the mathematical benchmark evaluation runner."""

from matching.benchmark_runner import evaluate_matcher_benchmark


def test_evaluate_matcher_benchmark_metrics() -> None:
    metrics = evaluate_matcher_benchmark()
    assert metrics.total_pairs > 50
    assert metrics.precision == 100.0
    assert metrics.false_positive_rate == 0.0
    assert metrics.recall >= 85.0
    assert metrics.f1_score >= 90.0
