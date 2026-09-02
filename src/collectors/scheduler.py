"""Policy-driven incremental recrawl scheduler and freshness calculation."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import ClassVar

from collectors.lifecycle import LifecycleStatus


class RecrawlTier(StrEnum):
    """Recrawl policy tiers."""

    NEW = "NEW"  # Immediate crawl
    VOLATILE = "VOLATILE"  # Price dropped or volatile (30 min)
    ACTIVE_STANDARD = "ACTIVE_STANDARD"  # Regular active product (4 hours)
    STABLE_PRICE = "STABLE_PRICE"  # Unchanged price > 7 days (24 hours)
    UNAVAILABLE = "UNAVAILABLE"  # Out of stock or missing (48 hours)
    DISCONTINUED = "DISCONTINUED"  # Inactive long-term (7 days)
    FAILURE_BACKOFF = "FAILURE_BACKOFF"  # Exponential error retry backoff


class IncrementalRecrawlScheduler:
    """Calculates freshness deadlines and dynamic recrawl windows."""

    INTERVALS: ClassVar[dict[RecrawlTier, timedelta]] = {
        RecrawlTier.NEW: timedelta(seconds=0),
        RecrawlTier.VOLATILE: timedelta(minutes=30),
        RecrawlTier.ACTIVE_STANDARD: timedelta(hours=4),
        RecrawlTier.STABLE_PRICE: timedelta(hours=24),
        RecrawlTier.UNAVAILABLE: timedelta(hours=48),
        RecrawlTier.DISCONTINUED: timedelta(days=7),
    }

    @classmethod
    def compute_recrawl_window(
        cls,
        status: LifecycleStatus | str = LifecycleStatus.ACTIVE,
        *,
        is_volatile: bool = False,
        is_stable: bool = False,
        error_count: int = 0,
        base_backoff_minutes: int = 30,
    ) -> timedelta:
        """Compute the duration before the next crawl should occur."""
        # 1. Error backoff takes highest precedence
        if error_count > 0:
            delay_mins = base_backoff_minutes * (2 ** min(error_count - 1, 4))
            return timedelta(minutes=delay_mins)

        lifecycle = LifecycleStatus(status) if isinstance(status, str) else status

        # 2. Lifecycle status routing
        if lifecycle == LifecycleStatus.DISCONTINUED:
            return cls.INTERVALS[RecrawlTier.DISCONTINUED]

        if lifecycle == LifecycleStatus.UNAVAILABLE or lifecycle == LifecycleStatus.STALE:
            return cls.INTERVALS[RecrawlTier.UNAVAILABLE]

        # 3. Active product volatility & stability
        if is_volatile:
            return cls.INTERVALS[RecrawlTier.VOLATILE]

        if is_stable:
            return cls.INTERVALS[RecrawlTier.STABLE_PRICE]

        return cls.INTERVALS[RecrawlTier.ACTIVE_STANDARD]

    @classmethod
    def get_next_recrawl_time(
        cls,
        status: LifecycleStatus | str = LifecycleStatus.ACTIVE,
        *,
        is_volatile: bool = False,
        is_stable: bool = False,
        error_count: int = 0,
        base_time: datetime | None = None,
    ) -> datetime:
        """Calculate the UTC timestamp when the product is due for next crawl."""
        ref_time = base_time or datetime.now(UTC)
        if ref_time.tzinfo is None:
            ref_time = ref_time.replace(tzinfo=UTC)
        window = cls.compute_recrawl_window(
            status=status,
            is_volatile=is_volatile,
            is_stable=is_stable,
            error_count=error_count,
        )
        return ref_time + window

    @classmethod
    def is_due_for_crawl(
        cls,
        recrawl_after: datetime | None,
        now: datetime | None = None,
    ) -> bool:
        """Check if an item is ready to be crawled."""
        if recrawl_after is None:
            return True
        curr_time = now or datetime.now(UTC)
        if curr_time.tzinfo is None:
            curr_time = curr_time.replace(tzinfo=UTC)
        if recrawl_after.tzinfo is None:
            recrawl_after = recrawl_after.replace(tzinfo=UTC)
        return curr_time >= recrawl_after
