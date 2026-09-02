"""Multi-signal data quality classification, accessory detection, and completeness scoring."""

from __future__ import annotations

import re
from enum import StrEnum
from typing import TYPE_CHECKING, ClassVar

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from sources.contracts import ParsedProduct


class QualityStatus(StrEnum):
    """Quality classification tiers for ingested retailer listings."""

    VALID = "VALID"
    SUSPICIOUS = "SUSPICIOUS"
    REJECTED = "REJECTED"


class QualityReport(BaseModel):
    """Structured quality assessment report for a product record."""

    model_config = ConfigDict(frozen=True)

    status: QualityStatus = Field(description="Ingestion quality classification status")
    score: int = Field(ge=0, le=100, description="Overall quality confidence score (0-100)")
    is_accessory: bool = Field(
        default=False, description="True if listing is detected as an accessory"
    )
    price_sanity_passed: bool = Field(
        default=True, description="True if price falls within valid category band"
    )
    completeness_score: int = Field(ge=0, le=100, description="Spec completeness score (0-100)")
    flags: tuple[str, ...] = Field(
        default_factory=tuple, description="Audit anomaly reasons and warning flags"
    )


class DataQualityClassifier:
    """Evaluates product listings across category classification, price sanity, and completeness."""

    # Explicit accessory patterns that disqualify a listing from becoming a standalone device
    ACCESSORY_PATTERNS: ClassVar[tuple[str, ...]] = (
        r"\b(?:laptop|phone|macbook|iphone|galaxy|ipad)\s+(?:case|cover|sleeve|skin|bag|backpack|stand|mount|pouch|holder)\b",
        r"\b(?:tempered\s+glass|screen\s+protector|back\s+cover|flip\s+cover|bumper\s+case)\b",
        r"\b(?:power\s+adapter|charger|charging\s+cable|usb\s+cable|hdmi\s+cable|lightning\s+cable|type-c\s+cable)\b",
        r"\b(?:cooling\s+pad|keyboard\s+cover|keyboard\s+skin|keypad\s+skin|trackpad\s+protector|cleaning\s+kit|cleaner)\b",
        r"\b(?:stylus\s+pen|stylus|camera\s+lens\s+protector|dust\s+plug|protective\s+sticker)\b",
        r"\b(?:wireless\s+mouse|optical\s+mouse|bluetooth\s+mouse|gaming\s+mouse|mouse\s+pad|desk\s+mat|table\s+mat)\b",
        r"\b(?:mechanical\s+keyboard|wireless\s+keyboard|bluetooth\s+keyboard|usb\s+hub|docking\s+station|laptop\s+riser)\b",
        r"\b(?:earphones|headphones|earbuds|headset|neckband|smartwatch\s+strap|watch\s+band)\b",
    )

    # Category price sanity bands (in integer paise)
    PRICE_BANDS: ClassVar[dict[str, tuple[int, int]]] = {
        "laptop": (1000000, 100000000),  # ₹10,000 to ₹10,00,000
        "mobile": (250000, 35000000),  # ₹2,500 to ₹3,50,000
    }

    @classmethod
    def detect_accessory(cls, title: str, source_url: str = "") -> tuple[bool, str | None]:
        """Detect whether a title or URL indicates an accessory rather than a device."""
        combined = f"{title} {source_url}".casefold()
        for pattern in cls.ACCESSORY_PATTERNS:
            match = re.search(pattern, combined, re.IGNORECASE)
            if match:
                return True, f"accessory detected via pattern: {match.group(0)!r}"
        return False, None

    @classmethod
    def evaluate_price_sanity(
        cls,
        category: str,
        price_paise: int | None,
    ) -> tuple[bool, str | None]:
        """Validate whether the price falls within plausible category sanity thresholds."""
        if price_paise is None or price_paise <= 0:
            return False, "missing or non-positive price"

        band = cls.PRICE_BANDS.get(category.casefold().strip())
        if band:
            min_p, max_p = band
            if price_paise < min_p:
                inr_val = price_paise / 100
                min_inr = min_p / 100
                return (
                    False,
                    f"price ₹{inr_val:,.2f} is below minimum sanity threshold ₹{min_inr:,.2f}",
                )
            if price_paise > max_p:
                inr_val = price_paise / 100
                max_inr = max_p / 100
                return (
                    False,
                    f"price ₹{inr_val:,.2f} exceeds maximum sanity threshold ₹{max_inr:,.2f}",
                )

        return True, None

    @classmethod
    def compute_completeness_score(cls, product: ParsedProduct) -> int:
        """Calculate spec completeness score from 0 to 100."""
        score = 0
        if product.title and len(product.title.strip()) > 5:
            score += 20
        if product.brand and product.brand.casefold() not in ("unknown", "generic"):
            score += 20
        if product.price_paise and product.price_paise > 0:
            score += 20
        if product.model_name and product.model_name != product.title:
            score += 15

        # Identity specs in attributes
        attrs = product.attributes
        if any(k in attrs for k in ("ram_gb", "ram")):
            score += 10
        if any(k in attrs for k in ("storage_gb", "storage", "ssd capacity", "hdd capacity")):
            score += 10
        if any(k in attrs for k in ("cpu_model", "chipset", "processor", "processor type", "chip")):
            score += 5

        return min(score, 100)

    @classmethod
    def classify(cls, product: ParsedProduct) -> QualityReport:
        """Run multi-signal quality classification on a parsed product record."""
        flags: list[str] = []

        # 1. Accessory Detection
        is_accessory, acc_reason = cls.detect_accessory(product.title, str(product.source_url))
        if is_accessory and acc_reason:
            flags.append(acc_reason)

        # 2. Price Sanity
        price_ok, price_reason = cls.evaluate_price_sanity(product.category, product.price_paise)
        if not price_ok and price_reason:
            flags.append(price_reason)

        # 3. Completeness Score
        completeness = cls.compute_completeness_score(product)

        # Overall Status & Quality Score Calculation
        if is_accessory:
            status = QualityStatus.REJECTED
            score = min(completeness // 3, 30)
        elif not price_ok:
            status = QualityStatus.SUSPICIOUS
            score = min(completeness, 60)
        elif completeness < 50:
            status = QualityStatus.SUSPICIOUS
            flags.append(f"low completeness score: {completeness}/100")
            score = completeness
        else:
            status = QualityStatus.VALID
            score = completeness

        return QualityReport(
            status=status,
            score=score,
            is_accessory=is_accessory,
            price_sanity_passed=price_ok,
            completeness_score=completeness,
            flags=tuple(flags),
        )
