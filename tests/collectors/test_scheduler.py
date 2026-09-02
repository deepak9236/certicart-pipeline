"""Tests for IncrementalRecrawlScheduler policy tiers and due checks."""

from datetime import UTC, datetime, timedelta

from collectors.lifecycle import LifecycleStatus
from collectors.scheduler import IncrementalRecrawlScheduler


def test_recrawl_window_calculation_by_tier() -> None:
    # Standard Active -> 4 hours
    assert IncrementalRecrawlScheduler.compute_recrawl_window(LifecycleStatus.ACTIVE) == timedelta(
        hours=4
    )

    # Volatile / Price Drop -> 30 minutes
    assert IncrementalRecrawlScheduler.compute_recrawl_window(
        LifecycleStatus.ACTIVE,
        is_volatile=True,
    ) == timedelta(minutes=30)

    # Stable Price -> 24 hours
    assert IncrementalRecrawlScheduler.compute_recrawl_window(
        LifecycleStatus.ACTIVE,
        is_stable=True,
    ) == timedelta(hours=24)

    # Unavailable / Stale -> 48 hours
    assert IncrementalRecrawlScheduler.compute_recrawl_window(
        LifecycleStatus.UNAVAILABLE
    ) == timedelta(hours=48)
    assert IncrementalRecrawlScheduler.compute_recrawl_window(LifecycleStatus.STALE) == timedelta(
        hours=48
    )

    # Discontinued -> 7 days
    assert IncrementalRecrawlScheduler.compute_recrawl_window(
        LifecycleStatus.DISCONTINUED
    ) == timedelta(days=7)


def test_error_backoff_precedence() -> None:
    # Error 1 -> 30 mins
    assert IncrementalRecrawlScheduler.compute_recrawl_window(
        LifecycleStatus.ACTIVE,
        error_count=1,
    ) == timedelta(minutes=30)

    # Error 2 -> 60 mins
    assert IncrementalRecrawlScheduler.compute_recrawl_window(
        LifecycleStatus.ACTIVE,
        error_count=2,
    ) == timedelta(minutes=60)

    # Error 3 -> 120 mins
    assert IncrementalRecrawlScheduler.compute_recrawl_window(
        LifecycleStatus.ACTIVE,
        error_count=3,
    ) == timedelta(minutes=120)


def test_is_due_for_crawl() -> None:
    now = datetime(2026, 9, 1, 12, 0, 0, tzinfo=UTC)

    # None -> immediately due
    assert IncrementalRecrawlScheduler.is_due_for_crawl(None, now=now) is True

    # Past time -> due
    past = now - timedelta(minutes=5)
    assert IncrementalRecrawlScheduler.is_due_for_crawl(past, now=now) is True

    # Future time -> not due
    future = now + timedelta(minutes=30)
    assert IncrementalRecrawlScheduler.is_due_for_crawl(future, now=now) is False
