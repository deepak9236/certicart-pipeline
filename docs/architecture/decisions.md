# Architecture Decisions

## ADR-001: PostgreSQL is the source of truth

**Decision:** Use PostgreSQL with JSONB for category-specific attributes.

**Why:** The identity graph and audit history require relational constraints, transactions, joins, append-only observations, and reproducible snapshots. Flexible specifications still fit JSONB or typed child tables.

## ADR-002: Start as a modular monolith

**Decision:** Keep one repository and one deployable image with separate job/API entrypoints.

**Why:** It minimizes deployment and observability cost while module contracts preserve future extraction options.

## ADR-003: Deterministic recommendation V1

**Decision:** Hard filters plus versioned weighted scoring and explicit penalties.

**Why:** Certikart needs explainability, reproducibility, controlled cold-start behavior, and expert evaluation before behavioural ML is justified.

## ADR-004: API/feed first collection

**Decision:** Official APIs and feeds precede permitted HTML collection; Playwright is last resort.

**Why:** Reliability, compliance, cost, and data quality are generally better. Browser rendering increases brittleness and operational load.

## ADR-005: Append-only observations

**Decision:** Prices and recommendation runs are immutable observations.

**Why:** Historical charts, deal claims, investigations, and model evaluation depend on trustworthy time-series evidence.

## ADR-006: NestJS remains the public gateway

**Decision:** The Python API is internal. Next.js talks to the public NestJS application API when backend integration begins.

**Why:** This preserves the product pitch's application architecture and keeps collection/ML libraries away from the public boundary.

