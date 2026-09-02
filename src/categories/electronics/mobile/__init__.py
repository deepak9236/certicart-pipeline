"""Mobile / Smartphone domain plugin package under Electronics department."""

from categories.electronics.mobile.handler import MobileCategoryHandler
from categories.electronics.mobile.normalizer import MobileIdentityNormalizer
from categories.electronics.mobile.rules import ConflictReason, check_mobile_hard_conflicts
from categories.electronics.mobile.schemas import MobileAttributes

__all__ = [
    "ConflictReason",
    "MobileAttributes",
    "MobileCategoryHandler",
    "MobileIdentityNormalizer",
    "check_mobile_hard_conflicts",
]
