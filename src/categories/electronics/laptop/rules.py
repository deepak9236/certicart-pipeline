"""Deterministic hard-conflict elimination rules for laptop product identity resolution."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from categories.contracts import CategoryDefinition

if TYPE_CHECKING:
    from matching.fingerprint import ProductFingerprint


class ConflictReason:
    """Standard hard conflict rejection reasons."""

    DIFFERENT_CATEGORIES = "different categories"
    DIFFERENT_BRANDS = "different brands"
    DIFFERENT_FAMILIES = "different product families"
    DIFFERENT_CHIPS = "different processor/chip generation"
    DIFFERENT_GPU = "different dedicated GPU model"
    DIFFERENT_RAM = "different identity attribute: ram_gb"
    DIFFERENT_STORAGE = "different identity attribute: storage_gb"
    DIFFERENT_SCREEN_SIZE = "different screen size"
    DIFFERENT_GTINS = "different GTINs"
    DIFFERENT_PART_NUMBERS = "different manufacturer part numbers"


def check_laptop_hard_conflicts(
    left: ProductFingerprint,
    right: ProductFingerprint,
    category_def: CategoryDefinition | None = None,
) -> tuple[bool, str | None]:
    """Check whether two laptop product fingerprints have an irreconcilable hard conflict.

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

    # Identity Attributes Check (ram_gb, storage_gb)
    identity_attributes = (
        category_def.identity_attributes if category_def else ("ram_gb", "storage_gb")
    )
    for attr in identity_attributes:
        if attr in ("cpu_model", "gpu_model"):
            continue
        left_val = (
            getattr(left, attr, None)
            if hasattr(left, attr) and getattr(left, attr) is not None
            else left.attributes.get(attr)
        )
        right_val = (
            getattr(right, attr, None)
            if hasattr(right, attr) and getattr(right, attr) is not None
            else right.attributes.get(attr)
        )
        if left_val is not None and right_val is not None:
            try:
                if int(str(left_val)) != int(str(right_val)):
                    return True, f"different identity attribute: {attr}"
            except ValueError:
                if str(left_val).casefold().strip() != str(right_val).casefold().strip():
                    return True, f"different identity attribute: {attr}"

    # Product Family Conflict (e.g. MacBook Air != MacBook Pro, Vivobook != Zenbook)
    if left.family and right.family and left.family != right.family:
        return True, f"{ConflictReason.DIFFERENT_FAMILIES}: {left.family!r} vs {right.family!r}"

    # Dedicated GPU Conflict (e.g. RTX 2050 != RTX 3050 != RTX 4050 != RTX 4060)
    left_gpu = left.gpu_model or str(left.attributes.get("gpu_model", ""))
    right_gpu = right.gpu_model or str(right.attributes.get("gpu_model", ""))
    if left_gpu and right_gpu:
        clean_left_gpu = left_gpu.casefold().strip()
        clean_right_gpu = right_gpu.casefold().strip()
        if (
            "nvidia" in clean_left_gpu
            and "nvidia" in clean_right_gpu
            and clean_left_gpu != clean_right_gpu
        ):
            return True, (
                f"{ConflictReason.DIFFERENT_GPU}: {clean_left_gpu!r} vs {clean_right_gpu!r}"
            )

    # Chip / Processor Generation Conflict (e.g. M4 != M5, i3 != i7, Ryzen 5 7520U != 7530U)
    left_chip = left.chip or str(left.attributes.get("cpu_model", ""))
    right_chip = right.chip or str(right.attributes.get("cpu_model", ""))
    if left_chip and right_chip:
        clean_left = left_chip.casefold().strip()
        clean_right = right_chip.casefold().strip()
        if clean_left and clean_right and clean_left != clean_right:
            # Apple M-series tier and generation
            left_m = re.findall(r"\bm[1-5](?:\s+(?:pro|max|ultra))?\b", clean_left)
            right_m = re.findall(r"\bm[1-5](?:\s+(?:pro|max|ultra))?\b", clean_right)
            if left_m and right_m and left_m[0] != right_m[0]:
                return True, f"{ConflictReason.DIFFERENT_CHIPS}: {clean_left!r} vs {clean_right!r}"

            # Intel Core Ultra tier/model
            if "ultra" in clean_left and "ultra" in clean_right and clean_left != clean_right:
                return (
                    True,
                    f"{ConflictReason.DIFFERENT_CHIPS}: {clean_left!r} vs {clean_right!r}",
                )

            # Intel Core i-series (e.g. i5-1235u vs i5-1335u, i7-13650hx vs i7-14650hx)
            left_i_sku = re.findall(r"\bi[3579]-?[0-9]{4,5}[a-z]{0,2}\b", clean_left)
            right_i_sku = re.findall(r"\bi[3579]-?[0-9]{4,5}[a-z]{0,2}\b", clean_right)
            if (
                left_i_sku
                and right_i_sku
                and left_i_sku[0].replace("-", "") != right_i_sku[0].replace("-", "")
            ):
                return (
                    True,
                    f"{ConflictReason.DIFFERENT_CHIPS}: {clean_left!r} vs {clean_right!r}",
                )

            # Intel Core i-tier (i3 vs i5 vs i7 vs i9)
            left_i = re.findall(r"\bi[3579]\b", clean_left)
            right_i = re.findall(r"\bi[3579]\b", clean_right)
            if left_i and right_i and left_i[0] != right_i[0]:
                return True, f"{ConflictReason.DIFFERENT_CHIPS}: {clean_left!r} vs {clean_right!r}"

            # AMD Ryzen sub-SKU (e.g. 7520u vs 7530u, 7730u vs 7840h)
            left_r_sku = re.findall(r"\bryzen\s+[3579]\s+[0-9]{4}[a-z]{0,2}\b", clean_left)
            right_r_sku = re.findall(r"\bryzen\s+[3579]\s+[0-9]{4}[a-z]{0,2}\b", clean_right)
            if left_r_sku and right_r_sku and left_r_sku[0] != right_r_sku[0]:
                return (
                    True,
                    f"{ConflictReason.DIFFERENT_CHIPS}: {clean_left!r} vs {clean_right!r}",
                )

            # Generation Conflict (e.g. 12th Gen vs 13th Gen, 13th Gen vs 14th Gen)
            left_gen = left.generation or (
                left.attributes.get("generation") if left.attributes else None
            )
            right_gen = right.generation or (
                right.attributes.get("generation") if right.attributes else None
            )
            if left_gen and right_gen and left_gen != right_gen:
                return True, f"{ConflictReason.DIFFERENT_CHIPS}: {left_gen} vs {right_gen}"

            # AMD Ryzen tier (Ryzen 3 vs Ryzen 5 vs Ryzen 7 vs Ryzen 9)
            left_ryzen = re.findall(r"\bryzen\s+[3579]\b", clean_left)
            right_ryzen = re.findall(r"\bryzen\s+[3579]\b", clean_right)
            if left_ryzen and right_ryzen and left_ryzen[0] != right_ryzen[0]:
                return True, f"{ConflictReason.DIFFERENT_CHIPS}: {clean_left!r} vs {clean_right!r}"

    # Screen Size Conflict (> 0.6 inch difference)
    left_screen = left.screen_size_inches or left.attributes.get("screen_size_inches")
    right_screen = right.screen_size_inches or right.attributes.get("screen_size_inches")
    if left_screen is not None and right_screen is not None:
        try:
            diff = abs(float(str(left_screen)) - float(str(right_screen)))
            if diff >= 0.7:
                return True, (
                    f'{ConflictReason.DIFFERENT_SCREEN_SIZE}: {left_screen}" vs {right_screen}"'
                )
        except ValueError:
            pass

    return False, None
