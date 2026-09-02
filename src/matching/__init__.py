"""Exact product identity resolution and matching."""

from matching.confidence import (
    ConfidenceScoreBreakdown,
    IdentityConfidenceScorer,
    MatchConfidenceTier,
)
from matching.fingerprint import ProductFingerprint
from matching.matcher import MatchDecision, MatchResult, compare_products
from matching.normalizer import LaptopIdentityNormalizer
from matching.reconciliation import (
    CanonicalVariantCluster,
    LinkedOffer,
    ReconciliationReport,
    reconcile_products,
)
from matching.rules import ConflictReason, check_hard_conflicts

__all__ = [
    "CanonicalVariantCluster",
    "ConfidenceScoreBreakdown",
    "ConflictReason",
    "IdentityConfidenceScorer",
    "LaptopIdentityNormalizer",
    "LinkedOffer",
    "MatchConfidenceTier",
    "MatchDecision",
    "MatchResult",
    "ProductFingerprint",
    "ReconciliationReport",
    "check_hard_conflicts",
    "compare_products",
    "reconcile_products",
]
