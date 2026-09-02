"""Worker configuration, Redis connection settings, and per-retailer rate limits."""

from __future__ import annotations

import os
from typing import ClassVar

from arq.connections import RedisSettings
from pydantic import BaseModel, ConfigDict, Field


class WorkerConfig(BaseModel):
    """Central configuration for distributed ARQ background workers."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    redis_url: str = Field(
        default_factory=lambda: os.getenv("CERTIKART_REDIS_URL", "redis://localhost:6379/0")
    )
    max_retries: int = Field(default=3, ge=1)
    default_job_timeout_seconds: int = Field(default=60, ge=5)

    # Queue Names
    DISCOVERY_QUEUE: ClassVar[str] = "certikart:discovery_queue"
    CRAWL_QUEUE: ClassVar[str] = "certikart:crawl_queue"
    PERSISTENCE_QUEUE: ClassVar[str] = "certikart:persistence_queue"
    DEAD_LETTER_QUEUE: ClassVar[str] = "certikart:dead_letter_queue"

    # Per-retailer maximum host concurrency limits
    RETAILER_CONCURRENCY: ClassVar[dict[str, int]] = {
        "amazon": 10,
        "flipkart": 10,
        "croma": 5,
    }

    @classmethod
    def get_redis_settings(cls, redis_url: str | None = None) -> RedisSettings:
        """Parse Redis URL into ARQ RedisSettings."""
        url = (
            redis_url
            if redis_url is not None
            else os.getenv("CERTIKART_REDIS_URL", "redis://localhost:6379/0")
        )
        return RedisSettings.from_dsn(url or "redis://localhost:6379/0")

    @classmethod
    def get_retailer_concurrency(cls, source: str) -> int:
        """Get the concurrency rate limit for a specific retailer source."""
        return cls.RETAILER_CONCURRENCY.get(source.casefold().strip(), 5)
