"""Deterministic hard-conflict elimination rules for product identity resolution."""

from __future__ import annotations

from categories.electronics.laptop.rules import ConflictReason, check_laptop_hard_conflicts
from categories.registry import get_category, get_category_handler
from matching.fingerprint import ProductFingerprint

__all__ = ["ConflictReason", "check_hard_conflicts", "check_laptop_hard_conflicts"]


def check_hard_conflicts(
    left: ProductFingerprint,
    right: ProductFingerprint,
) -> tuple[bool, str | None]:
    """Check whether two product fingerprints have an irreconcilable hard conflict.

    Returns:
        (has_conflict, reason)
    """
    if left.category != right.category:
        return True, ConflictReason.DIFFERENT_CATEGORIES

    if left.brand != right.brand:
        return True, ConflictReason.DIFFERENT_BRANDS

    try:
        handler = get_category_handler(left.category)
        return handler.check_hard_conflicts(left, right)
    except ValueError:
        category_def = get_category(left.category)
        return check_laptop_hard_conflicts(left, right, category_def=category_def)
