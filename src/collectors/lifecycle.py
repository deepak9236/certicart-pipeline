"""Product and retailer offer lifecycle state machine."""

from __future__ import annotations

from enum import StrEnum


class LifecycleStatus(StrEnum):
    """Lifecycle states for retailer product listings and offers."""

    ACTIVE = "ACTIVE"  # Recently observed and in stock
    STALE = "STALE"  # Missed 1-2 expected crawl cycles
    UNAVAILABLE = "UNAVAILABLE"  # Explicitly out of stock or missed 3-9 crawl cycles
    DISCONTINUED = "DISCONTINUED"  # Missed 10+ crawl cycles or confirmed delisted


class LifecycleManager:
    """Deterministic state transitions for product and offer lifecycles."""

    STALE_THRESHOLD_MISSED = 1
    UNAVAILABLE_THRESHOLD_MISSED = 3
    DISCONTINUED_THRESHOLD_MISSED = 10

    @classmethod
    def transition_on_crawl_success(
        cls,
        current_status: LifecycleStatus | str,
        *,
        in_stock: bool,
    ) -> tuple[LifecycleStatus, int]:
        """Transition lifecycle status upon a successful crawl observation.

        Resets missed crawl counter to 0.
        """
        if in_stock:
            return LifecycleStatus.ACTIVE, 0
        return LifecycleStatus.UNAVAILABLE, 0

    @classmethod
    def transition_on_missed_crawl(
        cls,
        current_status: LifecycleStatus | str,
        missed_count: int,
    ) -> tuple[LifecycleStatus, int]:
        """Transition lifecycle status when a scheduled crawl fails or product is missing."""
        new_missed = missed_count + 1

        if new_missed >= cls.DISCONTINUED_THRESHOLD_MISSED:
            return LifecycleStatus.DISCONTINUED, new_missed

        if new_missed >= cls.UNAVAILABLE_THRESHOLD_MISSED:
            return LifecycleStatus.UNAVAILABLE, new_missed

        if new_missed >= cls.STALE_THRESHOLD_MISSED:
            return LifecycleStatus.STALE, new_missed

        curr = (
            LifecycleStatus(current_status) if isinstance(current_status, str) else current_status
        )
        return curr, new_missed
