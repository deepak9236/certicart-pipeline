"""Tests for CrawlFrontierStore, URL canonicalization, priority queuing, and backoff scheduling."""

from collectors.frontier import (
    CrawlFrontierStore,
    CrawlPriority,
    FrontierItem,
    FrontierStatus,
    canonicalize_url,
)


def test_url_canonicalization_strips_tracking_params() -> None:
    raw = (
        "https://www.amazon.in/dp/B0CX000001/"
        "?utm_source=google&utm_medium=cpc&ref=sr_1_1&tag=affiliate_123&qid=1720000000"
    )
    canon = canonicalize_url(raw)
    assert canon == "https://amazon.in/dp/B0CX000001"


def test_frontier_enqueue_and_deduplication() -> None:
    frontier = CrawlFrontierStore()
    item1 = FrontierItem.from_url(
        "https://www.croma.com/p/324343?utm_source=ad",
        source="croma",
        source_product_id="324343",
    )
    item2 = FrontierItem.from_url(
        "https://croma.com/p/324343?ref=search",
        source="croma",
        source_product_id="324343",
    )

    assert frontier.enqueue(item1) is True
    assert frontier.enqueue(item2) is False  # Deduplicated via canonical URL

    stats = frontier.stats()
    assert stats["total_urls"] == 1
    assert stats["pending"] == 1


def test_frontier_priority_ordering() -> None:
    frontier = CrawlFrontierStore()
    low = FrontierItem.from_url(
        "https://croma.com/p/100",
        source="croma",
        source_product_id="100",
        priority=int(CrawlPriority.LOW),
    )
    high = FrontierItem.from_url(
        "https://croma.com/p/200",
        source="croma",
        source_product_id="200",
        priority=int(CrawlPriority.HIGH),
    )
    normal = FrontierItem.from_url(
        "https://croma.com/p/300",
        source="croma",
        source_product_id="300",
        priority=int(CrawlPriority.NORMAL),
    )

    frontier.enqueue_batch([low, high, normal])

    popped = frontier.pop_batch(batch_size=3)
    assert len(popped) == 3
    # HIGH (priority 1) comes first, then NORMAL (2), then LOW (3)
    assert popped[0].source_product_id == "200"
    assert popped[1].source_product_id == "300"
    assert popped[2].source_product_id == "100"


def test_frontier_completion_and_failure_backoff() -> None:
    frontier = CrawlFrontierStore()
    item = FrontierItem.from_url("https://croma.com/p/324343", source="croma")
    frontier.enqueue(item)

    popped = frontier.pop_batch(batch_size=1)
    assert len(popped) == 1
    assert popped[0].status == FrontierStatus.IN_PROGRESS

    # Mark failed -> exponential backoff
    frontier.mark_failed(popped[0].canonical_url, "503 Service Unavailable")
    stats = frontier.stats()
    assert stats["failed"] == 1

    item_failed = frontier._items[popped[0].canonical_url]
    assert item_failed.error_count == 1
    assert item_failed.recrawl_after is not None

    # Mark completed -> scheduled 24h later
    frontier.mark_completed(popped[0].canonical_url, recrawl_interval_hours=24)
    stats_done = frontier.stats()
    assert stats_done["completed"] == 1
    item_done = frontier._items[popped[0].canonical_url]
    assert item_done.error_count == 0
    assert item_done.last_crawled_at is not None
