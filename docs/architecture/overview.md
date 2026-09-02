# Pipeline Architecture Overview

## Repository Boundary

```text
certikart/             Next.js frontend
certikart-api/         FastAPI backend + recommendation engine
certikart-pipeline/    Background collection and processing (this repository)
```

This project does not serve public customer-facing HTTP requests. It runs scheduled/background collection jobs, executes distributed async worker queues, resolves exact product variants across retailers, and publishes validated product intelligence to PostgreSQL for FastAPI to read.

## End-to-End Data Flow

```text
Retailer APIs / Sitemaps / Permitted Web Pages
                     │
                     ▼
         Catalog Sitemap Discovery Engine
                     │
                     ▼
           Priority Crawl Frontier
                     │
                     ▼
          Distributed ARQ Workers
                     │
                     ▼
         Retailer Platform Parsers (sources/)
                     │
                     ▼
         Domain Intelligence Plugins (categories/)
                     │
                     ▼
       Canonical Product Fingerprint Normalizer
                     │
                     ▼
      Hierarchical Matcher & Hard Conflict Engine
                     │
                     ▼
        Canonical Variant Clusters & Linked Offers
                     │
                     ▼
       Transactional PostgreSQL Persistence (storage/)
      (products, retailer_products, offers, price_history)
                     │
                     ▼
           certikart-api (FastAPI)
                     │
                     ▼
             certikart (Next.js)
```

## Source Layout

```text
src/
├── categories/          # Hierarchical domain taxonomy (department -> category plugin) & registry
│   ├── contracts.py     # CategoryDefinition, SubcategoryDefinition, AttributeValue
│   ├── handler.py       # CategoryHandler Protocol interface
│   ├── registry.py      # Department, category, and handler lookup registry
│   └── electronics/     # Top-Level Category (Department)
│       └── laptop/      # Laptop domain plugin (handler, normalizer, rules)
├── sources/             # Retailer adapters and shared parsing mechanics
│   ├── common.py        # Generic price extraction, brand recognition, JSON-LD decoding
│   ├── amazon/          # Amazon India adapter and DOM parser
│   ├── flipkart/        # Flipkart adapter and DOM/JSON-LD parser
│   └── croma/           # Croma adapter and hydration state parser
├── collectors/          # Sitemap discovery engine, priority crawl frontier, and policies
├── matching/            # Product fingerprinting, reconciliation, and hard conflict engine
├── pricing/             # Append-only price observations and daily aggregates
├── reviews/             # Review evidence and aspect-sentiment contracts
├── storage/             # PostgreSQL SQLAlchemy models, engine, and transactional repository
├── workers/             # Distributed ARQ async worker daemon, queues, and background tasks
└── jobs/                # Scheduled and operator-triggered CLI commands
```

## Module Ownership

| Module | Owns |
|---|---|
| `categories` | Department & category taxonomy, `CategoryHandler` domain plugins, identity attributes, and hard conflict rules |
| `sources` | Retailer access contracts, platform DOM/JSON-LD parsers, and shared source extraction mechanics |
| `collectors` | Catalog XML sitemap harvesting, priority crawl frontier, freshness scheduling, and collection policies |
| `matching` | Product fingerprint generation, exact-variant reconciliation, and deterministic hard conflict rejection |
| `pricing` | Append-only price observations and daily aggregates |
| `reviews` | Review target/aspect evidence and sentiment contracts |
| `storage` | PostgreSQL schema models, engine initialization, and transactional repository upserts |
| `workers` | Distributed ARQ task workers, concurrency semaphores, and queue orchestration |
| `jobs` | Typer CLI commands for operations, diagnostics, and daemon execution |

## Data Invariants

- **Monetary Values**: Stored in non-negative integer paise (`BIGINT`).
- **Timestamps**: All stored timestamps are timezone-aware UTC (`TIMESTAMPTZ`).
- **Idempotency**: Scraping and reconciliation runs are idempotent by `(source, source_product_id, observed_at)`.
- **Append-only History**: Historical price changes are never overwritten or deleted.
- **Strict Separation**: Product families, exact variants, offers, sellers, and observations remain strictly separate.
