"""Deterministic hard-conflict elimination rules for mobile product identity resolution."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from categories.contracts import CategoryDefinition

if TYPE_CHECKING:
    from matching.fingerprint import ProductFingerprint


class ConflictReason:
    """Standard hard conflict rejection reasons for mobile category."""

    DIFFERENT_CATEGORIES = "different categories"
    DIFFERENT_BRANDS = "different brands"
    DIFFERENT_FAMILIES = "different product families"
    DIFFERENT_CHIPSETS = "different mobile chipset"
    DIFFERENT_RAM = "different identity attribute: ram_gb"
    DIFFERENT_STORAGE = "different identity attribute: storage_gb"
    DIFFERENT_COLOR = "different color variant"
    DIFFERENT_CONNECTIVITY = "different network generation (4G vs 5G)"
    DIFFERENT_GTINS = "different GTINs"
    DIFFERENT_PART_NUMBERS = "different manufacturer part numbers"


def check_mobile_hard_conflicts(
    left: ProductFingerprint,
    right: ProductFingerprint,
    category_def: CategoryDefinition | None = None,
) -> tuple[bool, str | None]:
    """Check whether two smartphone product fingerprints have an irreconcilable hard conflict.

    Returns:
        (has_conflict, reason)
    """
    if left.category != right.category:
        return True, ConflictReason.DIFFERENT_CATEGORIES

    if left.brand != right.brand:
        return True, ConflictReason.DIFFERENT_BRANDS

    # GTIN / MPN Conflict
    if left.gtin and right.gtin and left.gtin != right.gtin:
        return True, ConflictReason.DIFFERENT_GTINS
    if (
        left.manufacturer_part_number
        and right.manufacturer_part_number
        and left.manufacturer_part_number != right.manufacturer_part_number
    ):
        return True, ConflictReason.DIFFERENT_PART_NUMBERS

    # RAM & Storage Identity Attributes
    if left.ram_gb is not None and right.ram_gb is not None and left.ram_gb != right.ram_gb:
        return True, f"{ConflictReason.DIFFERENT_RAM}: {left.ram_gb}GB vs {right.ram_gb}GB"

    if (
        left.storage_gb is not None
        and right.storage_gb is not None
        and left.storage_gb != right.storage_gb
    ):
        return (
            True,
            f"{ConflictReason.DIFFERENT_STORAGE}: {left.storage_gb}GB vs {right.storage_gb}GB",
        )

    # Product Family / Series Conflict (e.g. iPhone 16 Pro != Pro Max, Galaxy S24 != S24 Ultra)
    if left.family and right.family and left.family != right.family:
        return True, f"{ConflictReason.DIFFERENT_FAMILIES}: {left.family!r} vs {right.family!r}"

    # Chipset / Processor Generation Conflict (e.g. A17 Pro != A18 Pro, Snapdragon 8 Gen 2 != Gen 3)
    left_chip = left.chip or str(left.attributes.get("chipset", ""))
    right_chip = right.chip or str(right.attributes.get("chipset", ""))
    if left_chip and right_chip:
        clean_left = left_chip.casefold().strip()
        clean_right = right_chip.casefold().strip()
        if clean_left and clean_right and clean_left != clean_right:
            # Apple A-series
            left_a = re.findall(r"\ba\d{2}(?:\s+pro)?\b", clean_left)
            right_a = re.findall(r"\ba\d{2}(?:\s+pro)?\b", clean_right)
            if left_a and right_a and left_a[0] != right_a[0]:
                return True, f"{ConflictReason.DIFFERENT_CHIPSETS}: {clean_left} vs {clean_right}"

            # Snapdragon generations
            left_snap = re.findall(r"8\s+gen\s+[1-4]", clean_left)
            right_snap = re.findall(r"8\s+gen\s+[1-4]", clean_right)
            if left_snap and right_snap and left_snap[0] != right_snap[0]:
                return True, f"{ConflictReason.DIFFERENT_CHIPSETS}: {clean_left} vs {clean_right}"

    # 4G vs 5G Connectivity Conflict
    left_net = left.attributes.get("network_type")
    right_net = right.attributes.get("network_type")
    if left_net and right_net and str(left_net).casefold() != str(right_net).casefold():
        return True, ConflictReason.DIFFERENT_CONNECTIVITY

    return False, None
