"""Laptop category domain package under Electronics department."""

from categories.electronics.laptop.handler import LaptopCategoryHandler
from categories.electronics.laptop.normalizer import LaptopIdentityNormalizer
from categories.electronics.laptop.rules import ConflictReason, check_laptop_hard_conflicts
from categories.electronics.laptop.schemas import LaptopAttributes

__all__ = [
    "ConflictReason",
    "LaptopAttributes",
    "LaptopCategoryHandler",
    "LaptopIdentityNormalizer",
    "check_laptop_hard_conflicts",
]
