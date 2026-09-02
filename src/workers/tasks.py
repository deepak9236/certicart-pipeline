"""Distributed task functions for ARQ background worker execution."""

from __future__ import annotations

import asyncio
import contextlib
from typing import Any

from pydantic import AnyHttpUrl

from collectors.sitemaps import SitemapDiscoveryEngine
from matching.reconciliation import reconcile_products
from sources.contracts import ParsedProduct, SourceProductReference
from sources.registry import get_source_adapter
from sources.transport import HttpSourceTransport
from storage.engine import create_database_engine, get_session_factory, init_db
from storage.repository import PipelineRepository
from workers.config import WorkerConfig


async def task_discover_sitemap(
    ctx: dict[str, Any],
    source: str,
    sitemap_url: str,
    *,
    limit: int = 100,
    category: str = "laptop",
) -> dict[str, Any]:
    """Worker task: Ingest XML sitemap and discover product URLs."""
    transport = ctx.get("transport") or HttpSourceTransport()
    refs = await SitemapDiscoveryEngine.discover_from_sitemap(
        sitemap_url,
        source=source,
        transport=transport,
        max_items=limit,
        category=category,
    )
    return {
        "source": source,
        "sitemap_url": sitemap_url,
        "category": category,
        "discovered_count": len(refs),
        "product_ids": [r.source_product_id for r in refs],
    }


async def task_crawl_product(
    ctx: dict[str, Any],
    url: str,
    source: str,
    *,
    source_product_id: str | None = None,
    category: str = "laptop",
) -> dict[str, Any]:
    """Worker task: Fetch and parse a single product listing with host rate limiting."""
    transport = ctx.get("transport") or HttpSourceTransport()
    adapter_cls = get_source_adapter(source)

    p_id = source_product_id or url
    ref = SourceProductReference(
        source_product_id=p_id,
        category=category,
        subcategory=None,
        source_url=AnyHttpUrl(url),
    )
    adapter = adapter_cls([ref], transport)

    # Acquire retailer concurrency semaphore if registered in context
    semaphores: dict[str, asyncio.Semaphore] = ctx.get("semaphores", {})
    sem = semaphores.get(source.casefold().strip())

    async with sem if sem is not None else contextlib.nullcontext():
        raw_doc = await adapter.fetch(p_id)
        parsed = adapter.parse(raw_doc)

    return {
        "status": "success",
        "source": parsed.source,
        "source_product_id": parsed.source_product_id,
        "title": parsed.title,
        "brand": parsed.brand,
        "model_name": parsed.model_name,
        "price_paise": parsed.price_paise,
        "in_stock": parsed.in_stock,
        "parsed_payload": parsed.model_dump(mode="json"),
    }


async def task_reconcile_and_persist(
    ctx: dict[str, Any],
    parsed_product_payloads: list[dict[str, Any]],
    *,
    persist: bool = True,
) -> dict[str, Any]:
    """Worker task: Reconcile parsed products and persist to PostgreSQL."""
    parsed_products: list[ParsedProduct] = [
        ParsedProduct.model_validate(p) for p in parsed_product_payloads
    ]
    report = reconcile_products(parsed_products)

    metrics: dict[str, int] = {
        "products_persisted": 0,
        "offers_persisted": 0,
    }

    if persist:
        engine = ctx.get("db_engine") or create_database_engine()
        init_db(engine)
        session_factory = ctx.get("session_factory") or get_session_factory(engine)
        with session_factory() as session, session.begin():
            metrics = PipelineRepository.persist_reconciliation_report(session, report)

    return {
        "total_collected": report.total_collected,
        "total_clusters": report.total_clusters,
        "multi_source_clusters": report.multi_source_clusters,
        "source_breakdown": {k: v.model_dump() for k, v in report.source_breakdown.items()},
        "db_metrics": metrics,
    }


async def task_send_to_dead_letter(
    ctx: dict[str, Any],
    url: str,
    source: str,
    error_message: str,
    attempts: int,
) -> dict[str, Any]:
    """Worker task: Isolate repeated failures in the dead-letter queue."""
    return {
        "status": "dead_lettered",
        "url": url,
        "source": source,
        "error": error_message,
        "attempts": attempts,
        "queue": WorkerConfig.DEAD_LETTER_QUEUE,
    }
