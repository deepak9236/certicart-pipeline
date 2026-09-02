"""Tests for LifecycleManager state transitions and rules."""

from collectors.lifecycle import LifecycleManager, LifecycleStatus


def test_transition_on_crawl_success() -> None:
    # In-stock product transitions to ACTIVE and resets missed counter
    status, missed = LifecycleManager.transition_on_crawl_success(
        LifecycleStatus.STALE,
        in_stock=True,
    )
    assert status == LifecycleStatus.ACTIVE
    assert missed == 0

    # Out-of-stock product transitions to UNAVAILABLE and resets missed counter
    status_oos, missed_oos = LifecycleManager.transition_on_crawl_success(
        LifecycleStatus.ACTIVE,
        in_stock=False,
    )
    assert status_oos == LifecycleStatus.UNAVAILABLE
    assert missed_oos == 0


def test_transition_on_missed_crawl_progression() -> None:
    # Missed 1 -> STALE
    st1, cnt1 = LifecycleManager.transition_on_missed_crawl(LifecycleStatus.ACTIVE, missed_count=0)
    assert st1 == LifecycleStatus.STALE
    assert cnt1 == 1

    # Missed 2 -> STALE
    st2, cnt2 = LifecycleManager.transition_on_missed_crawl(st1, missed_count=1)
    assert st2 == LifecycleStatus.STALE
    assert cnt2 == 2

    # Missed 3 -> UNAVAILABLE
    st3, cnt3 = LifecycleManager.transition_on_missed_crawl(st2, missed_count=2)
    assert st3 == LifecycleStatus.UNAVAILABLE
    assert cnt3 == 3

    # Missed 10 -> DISCONTINUED
    st10, cnt10 = LifecycleManager.transition_on_missed_crawl(st3, missed_count=9)
    assert st10 == LifecycleStatus.DISCONTINUED
    assert cnt10 == 10
