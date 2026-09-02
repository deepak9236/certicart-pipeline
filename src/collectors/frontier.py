"""Priority crawl frontier, canonical URL normalization, and freshness scheduling."""

from __future__ import annotations

import heapq
import urllib.parse
from datetime import UTC, datetime, timedelta
from enum import IntEnum, StrEnum
from typing import NamedTuple

from pydantic import BaseModel, ConfigDict, Field


class CrawlPriority(IntEnum):
    """Crawl priority tiers."""

    HIGH = 1  # Volatile prices, out of stock, user watchlist
    NORMAL = 2  # Standard scheduled discovery
    LOW = 3  # Long-tail backfill


class FrontierStatus(StrEnum):
    """Status of an item in the crawl frontier."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


# Query parameters stripped during canonicalization
TRACKING_PARAMS = frozenset(
    {
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_term",
        "utm_content",
        "ref",
        "ref_",
        "tag",
        "tag_id",
        "fbclid",
        "gclid",
        "sr",
        "qid",
        "sprefix",
        "crid",
        "keywords",
        "_price",
        "_mrp",
    }
)


def canonicalize_url(raw_url: str) -> str:
    """Normalize and strip tracking/session parameters from a product URL."""
    if not raw_url:
        return ""
    try:
        parsed = urllib.parse.urlparse(raw_url.strip())
        scheme = "https"
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]

        # Clean query parameters
        qs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=False)
        cleaned_qs = [
            (k, v)
            for k, v in qs
            if k.lower() not in TRACKING_PARAMS and not k.lower().startswith("utm_")
        ]
        new_query = urllib.parse.urlencode(cleaned_qs)

        # Normalize path
        path = parsed.path
        if path.endswith("/") and len(path) > 1:
            path = path[:-1]

        return urllib.parse.urlunparse((scheme, netloc, path, "", new_query, ""))
    except Exception:
        return raw_url.strip()


class FrontierItem(BaseModel):
    """An individual work item in the crawl frontier queue."""

    model_config = ConfigDict(extra="forbid")

    url: str = Field(min_length=1)
    canonical_url: str = Field(min_length=1)
    source: str = Field(min_length=1)
    source_product_id: str | None = None
    category: str = "laptop"
    priority: int = Field(default=int(CrawlPriority.NORMAL), ge=1, le=3)
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_crawled_at: datetime | None = None
    recrawl_after: datetime | None = None
    status: str = FrontierStatus.PENDING
    error_count: int = Field(default=0, ge=0)
    last_error: str | None = None

    @classmethod
    def from_url(
        cls,
        url: str,
        source: str,
        *,
        source_product_id: str | None = None,
        category: str = "laptop",
        priority: int = int(CrawlPriority.NORMAL),
    ) -> FrontierItem:
        return cls(
            url=url,
            canonical_url=canonicalize_url(url),
            source=source.casefold().strip(),
            source_product_id=source_product_id,
            category=category,
            priority=priority,
        )


class _QueueEntry(NamedTuple):
    priority: int
    recrawl_timestamp: float
    canonical_url: str


class CrawlFrontierStore:
    """In-memory thread-safe priority crawl frontier store with freshness scheduling."""

    def __init__(self) -> None:
        self._items: dict[str, FrontierItem] = {}
        self._heap: list[_QueueEntry] = []

    def enqueue(self, item: FrontierItem) -> bool:
        """Enqueue a FrontierItem. Returns True if newly added, False if already exists."""
        key = item.canonical_url
        if key in self._items:
            existing = self._items[key]
            # If new priority is higher (lower int value), upgrade it
            if item.priority < existing.priority:
                existing.priority = item.priority
            return False

        self._items[key] = item
        ts = item.recrawl_after.timestamp() if item.recrawl_after else 0.0
        heapq.heappush(self._heap, _QueueEntry(item.priority, ts, key))
        return True

    def enqueue_batch(self, items: list[FrontierItem]) -> int:
        """Enqueue multiple FrontierItems. Returns count of newly added items."""
        added = 0
        for it in items:
            if self.enqueue(it):
                added += 1
        return added

    def pop_batch(
        self,
        batch_size: int = 20,
        *,
        source: str | None = None,
    ) -> list[FrontierItem]:
        """Pop the highest priority ready items from the frontier."""
        now = datetime.now(UTC)
        now_ts = now.timestamp()
        results: list[FrontierItem] = []
        re_enqueue: list[_QueueEntry] = []

        while self._heap and len(results) < batch_size:
            entry = heapq.heappop(self._heap)
            item = self._items.get(entry.canonical_url)
            if item is None:
                continue

            if source and item.source != source.casefold().strip():
                re_enqueue.append(entry)
                continue

            # Check if scheduled for the future
            if entry.recrawl_timestamp > now_ts:
                re_enqueue.append(entry)
                continue

            item.status = FrontierStatus.IN_PROGRESS
            results.append(item)

        # Put back items not selected in this batch
        for entry in re_enqueue:
            heapq.heappush(self._heap, entry)

        return results

    def mark_completed(
        self,
        canonical_url: str,
        *,
        recrawl_interval_hours: int = 24,
    ) -> None:
        """Mark a crawled URL as completed and schedule next recrawl window."""
        item = self._items.get(canonical_url)
        if item is not None:
            now = datetime.now(UTC)
            item.status = FrontierStatus.COMPLETED
            item.last_crawled_at = now
            item.recrawl_after = now + timedelta(hours=recrawl_interval_hours)
            item.error_count = 0
            item.last_error = None
            heapq.heappush(
                self._heap,
                _QueueEntry(item.priority, item.recrawl_after.timestamp(), canonical_url),
            )

    def mark_failed(
        self,
        canonical_url: str,
        error_message: str,
        *,
        backoff_minutes: int = 30,
    ) -> None:
        """Mark an item as failed with exponential backoff retry scheduling."""
        item = self._items.get(canonical_url)
        if item is not None:
            now = datetime.now(UTC)
            item.status = FrontierStatus.FAILED
            item.error_count += 1
            item.last_error = error_message
            delay = backoff_minutes * (2 ** min(item.error_count - 1, 4))
            item.recrawl_after = now + timedelta(minutes=delay)
            heapq.heappush(
                self._heap,
                _QueueEntry(item.priority, item.recrawl_after.timestamp(), canonical_url),
            )

    def stats(self) -> dict[str, int]:
        """Summary statistics of frontier queue."""
        total = len(self._items)
        pending = sum(1 for it in self._items.values() if it.status == FrontierStatus.PENDING)
        in_progress = sum(
            1 for it in self._items.values() if it.status == FrontierStatus.IN_PROGRESS
        )
        completed = sum(1 for it in self._items.values() if it.status == FrontierStatus.COMPLETED)
        failed = sum(1 for it in self._items.values() if it.status == FrontierStatus.FAILED)
        return {
            "total_urls": total,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "failed": failed,
        }
