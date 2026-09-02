"""Laptop category handler implementation for domain-specific normalization and matching."""

from __future__ import annotations

from typing import TYPE_CHECKING

from categories.contracts import AttributeValue
from categories.electronics.laptop.normalizer import LaptopIdentityNormalizer
from categories.electronics.laptop.rules import check_laptop_hard_conflicts
from matching.fingerprint import ProductFingerprint

if TYPE_CHECKING:
    from sources.contracts import ParsedProduct


class LaptopCategoryHandler:
    """Domain intelligence plugin for the Laptop category under Electronics department."""

    @property
    def category_code(self) -> str:
        return "laptop"

    def normalize(self, product: ParsedProduct) -> ProductFingerprint:
        """Extract structured attributes and build canonical laptop fingerprint."""
        extra_attrs: dict[str, AttributeValue] = dict(product.attributes)
        specs: dict[str, str] = {str(k): str(v) for k, v in product.attributes.items()}

        return LaptopIdentityNormalizer.normalize(
            title=product.title,
            category=self.category_code,
            brand_raw=product.brand,
            model_name_raw=product.model_name,
            specs=specs,
            manufacturer_part_number=product.manufacturer_part_number,
            gtin=product.gtin,
            extra_attributes=extra_attrs,
        )

    def check_hard_conflicts(
        self,
        left: ProductFingerprint,
        right: ProductFingerprint,
    ) -> tuple[bool, str | None]:
        """Check for laptop-specific hard conflicts (CPU, GPU, RAM, storage, screen, family)."""
        return check_laptop_hard_conflicts(left, right)

    def compute_similarity(
        self,
        left: ProductFingerprint,
        right: ProductFingerprint,
    ) -> float:
        """Compute weighted laptop attribute similarity."""
        weights = {
            "brand": 0.25,
            "chip": 0.25,
            "ram_gb": 0.15,
            "storage_gb": 0.15,
            "gpu_model": 0.10,
            "screen_size_inches": 0.10,
        }
        score = 0.0
        if left.brand == right.brand:
            score += weights["brand"]
        if left.chip and right.chip and left.chip.casefold() == right.chip.casefold():
            score += weights["chip"]
        if left.ram_gb and right.ram_gb and left.ram_gb == right.ram_gb:
            score += weights["ram_gb"]
        if left.storage_gb and right.storage_gb and left.storage_gb == right.storage_gb:
            score += weights["storage_gb"]
        if left.gpu_model and right.gpu_model and left.gpu_model == right.gpu_model:
            score += weights["gpu_model"]
        if (
            left.screen_size_inches
            and right.screen_size_inches
            and abs(left.screen_size_inches - right.screen_size_inches) < 0.1
        ):
            score += weights["screen_size_inches"]

        return round(score, 4)
