"""Category-neutral text and unit normalization helpers."""

import re
from decimal import Decimal

CAPACITY_PATTERN = re.compile(r"(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>tb|gb)", re.IGNORECASE)


def normalize_text(value: str) -> str:
    return " ".join(value.casefold().strip().split())


def normalize_capacity_gb(value: str) -> int:
    match = CAPACITY_PATTERN.fullmatch(value.strip())
    if match is None:
        raise ValueError(f"unsupported capacity: {value!r}")

    amount = Decimal(match.group("value"))
    if amount <= 0:
        raise ValueError("capacity must be positive")

    multiplier = 1024 if match.group("unit").casefold() == "tb" else 1
    capacity = amount * multiplier
    if capacity != capacity.to_integral_value():
        raise ValueError("capacity must normalize to whole GB")
    return int(capacity)
