# Product and Price Pipeline

## Stage Model

```text
Catalog Sitemap Discovery (XML/GZ)
     │
     ▼
Priority Crawl Frontier (Freshness Scheduling + Exponential Backoff)
     │
     ▼
Distributed ARQ Workers (Host-level Concurrency Semaphores)
     │
     ▼
Platform Parsers (sources/) & Shared Extraction Mechanics (sources/common.py)
     │
     ▼
Canonical Domain Normalization (categories/<dept>/<cat>/normalizer.py)
     │
     ▼
ProductFingerprint Construction
     │
     ▼
Deterministic Hard Conflict Elimination (categories/<dept>/<cat>/rules.py)
     │
     ▼
Hierarchical Matcher & Cluster Reconciliation (matching/)
     │
     ▼
Transactional PostgreSQL Persistence (storage/repository.py)
  ├── Canonical Products
  ├── Retailer Product Records & Lifecycle Status (ACTIVE / STALE / UNAVAILABLE)
  ├── Live Offers
  └── Append-Only Price History
```

---

## 1. Catalog Discovery & Priority Crawl Frontier

- **XML & GZ Sitemap Harvesting**: Recursively parses sitemap indexes and product sitemaps with regex URL matchers for Amazon (`/dp/ASIN`), Flipkart (`/p/itm...`), and Croma (`/p/CODE`).
- **Priority Frontier**: Multi-priority queue (`HIGH`, `NORMAL`, `LOW`) with $O(1)$ URL deduplication, crawl recrawl windows, and jittered exponential retry backoff.
- **Incremental Scheduling**: Products are assigned adaptive crawl intervals based on volatility:
  - `NEW` $\to$ Immediate
  - `VOLATILE` $\to$ 30 minutes
  - `ACTIVE` $\to$ 4 hours
  - `STABLE` $\to$ 24 hours

---

## 2. Distributed ARQ Background Workers

- **Redis-Backed Task Queues**:
  - `discovery`: Handles sitemap ingestion and catalog URL expansion.
  - `crawl`: Fetches and parses individual PDP pages with retailer host-level concurrency limits.
  - `persistence`: Reconciles product clusters and persists to PostgreSQL.
  - `dead_letter`: Captures failed records for inspection and replay.
- **Concurrency Rate Limiting**: Per-retailer `asyncio.Semaphore` guards to ensure compliance with rate policies.

---

## 3. Extraction & Normalization Layer

- **Clean Decoupling**:
  - **`sources/common.py`**: Shared currency parsing (`extract_digits_to_paise`), brand inference (`infer_brand`), and JSON-LD schema.org parsing.
  - **`sources/<source>/parser.py`**: Pure platform selectors (DOM, hydration state, script tags).
  - **`categories/<dept>/<cat>/`**: Pure domain logic (CPU/GPU/RAM/storage normalization and conflict detection).

---

## 4. Exact-Variant Matching & Hard Conflict Engine

- **ProductFingerprint**: Structured representation containing canonical brand, family, model name, chip, RAM GB, storage GB, screen size, GPU model, MPN, and GTIN.
- **Deterministic Hard Conflict Elimination**: Rejects incompatible variants before similarity evaluation:
  - Different brand or product family (`MacBook Air != MacBook Pro`, `Vivobook != Zenbook`).
  - Different CPU chip tier / generation (`M4 != M5`, `i5-1235U != i5-1335U`, `Ryzen 5 7520U != 7530U`).
  - Dedicated GPU mismatch (`RTX 3050 != RTX 4050`).
  - RAM / Storage size mismatch (`16GB != 32GB`, `512GB != 1TB`).
  - Screen size difference ($\ge 0.7$ inch).
  - MPN or GTIN conflict.

---

## 5. Transactional PostgreSQL Persistence

- **Idempotent Upserts**: Safe re-scraping without duplicate product or retailer product creation.
- **Lifecycle Tracking**: Tracks product health (`ACTIVE` $\to$ `STALE` $\to$ `UNAVAILABLE` $\to$ `DISCONTINUED`) based on consecutive crawl outcomes.
- **Append-Only Price History**: Records every meaningful price/stock change with exact timestamp, selling price, MRP, and discount percentage.
