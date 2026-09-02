"""Smartphone / Mobile category handler for domain normalization and matching."""

from __future__ import annotations

from typing import TYPE_CHECKING

from categories.contracts import AttributeValue
from categories.electronics.mobile.normalizer import MobileIdentityNormalizer
from categories.electronics.mobile.rules import check_mobile_hard_conflicts
from matching.fingerprint import ProductFingerprint

if TYPE_CHECKING:
    from sources.contracts import ParsedProduct


class MobileCategoryHandler:
    """Domain intelligence plugin for the Mobile category under Electronics department."""

    @property
    def category_code(self) -> str:
        return "mobile"

    def normalize(self, product: ParsedProduct) -> ProductFingerprint:
        """Extract structured attributes and build canonical mobile product fingerprint."""
        extra_attrs: dict[str, AttributeValue] = dict(product.attributes)
        specs: dict[str, str] = {str(k): str(v) for k, v in product.attributes.items()}

        return MobileIdentityNormalizer.normalize(
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
        """Check for mobile-specific hard conflicts (storage, RAM, brand, family, chipset)."""
        return check_mobile_hard_conflicts(left, right)

    def compute_similarity(
        self,
        left: ProductFingerprint,
        right: ProductFingerprint,
    ) -> float:
        """Compute weighted mobile attribute similarity."""
        weights = {
            "brand": 0.30,
            "chip": 0.25,
            "storage_gb": 0.25,
            "ram_gb": 0.15,
            "family": 0.05,
        }
        score = 0.0
        if left.brand == right.brand:
            score += weights["brand"]
        if left.chip and right.chip and left.chip.casefold() == right.chip.casefold():
            score += weights["chip"]
        if left.storage_gb and right.storage_gb and left.storage_gb == right.storage_gb:
            score += weights["storage_gb"]
        if left.ram_gb and right.ram_gb and left.ram_gb == right.ram_gb:
            score += weights["ram_gb"]
        if left.family and right.family and left.family == right.family:
            score += weights["family"]

        return round(score, 4)
