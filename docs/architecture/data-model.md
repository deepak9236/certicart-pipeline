# Data Model and Invariants

## Core identity graph

```text
category
  -> product_family
       -> product_variant
            -> variant_specification
            -> evidence
            -> offer
                 -> seller
                 -> price_observation
            -> review
                 -> review_aspect
```

## Recommended tables

### Catalog

- `categories`: laptop, monitor, GPU, and future category metadata.
- `product_families`: human grouping such as "Lenovo ThinkBook 14 Gen 6".
- `product_variants`: exact CPU/GPU/RAM/storage/display/OS configuration.
- `variant_identifiers`: manufacturer part number, GTIN/EAN, retailer IDs, and aliases.
- `specification_definitions`: category-specific field definitions, unit, validation range, and score eligibility.
- `variant_specifications`: typed normalized values with provenance and confidence.
- `evidence`: source URL, source type, observed time, content hash, permitted raw-object reference, and review state.

### Commerce and pricing

- `retailers`: source configuration and collection policy.
- `sellers`: seller identity scoped to a retailer.
- `offers`: exact variant + retailer + seller + URL + external ID.
- `price_observations`: immutable price, MRP, stock, seller, delivery context, and observed timestamp.
- `conditional_offers`: coupon, card, exchange, EMI, membership, and eligibility metadata.
- `daily_offer_prices`: derived minimum, maximum, last, sample count, and freshness.

### Recommendation and feedback

- `requirement_profiles`: confirmed structured profile, consent, and schema version.
- `recommendation_runs`: input snapshot hash, engine version, candidate-set version, result, and latency.
- `recommendation_items`: rank, fit score, confidence, contributions, reasons, and trade-offs.
- `interaction_events`: impression, click, save, dismiss, compare, outbound click, and feedback.
- `purchase_outcomes`: only when legitimately measurable and consented.

### Reviews

- `reviews`: exact variant when known, source, source ID, rating, text, language, verified flag, and dates.
- `review_aspects`: aspect, sentiment, confidence, evidence span, and target type.
- `review_aggregates`: minimum-sample, time-decayed aspect summary with model version.

## Important invariants

- Monetary columns use integer paise (`BIGINT`) with non-negative constraints.
- Stored timestamps use `TIMESTAMPTZ` in UTC. Product-facing daily aggregation uses `Asia/Kolkata` explicitly.
- Every normalized claim points to evidence and a transformation version.
- `price_observations` are append-only and partitionable by observation date.
- One source record is idempotent by `(source, source_product_id, content_hash)`.
- One offer is unique by stable retailer product ID plus seller/variant context.
- Published variants cannot lack their category's identity-critical fields.
- Recommendation runs store engine and catalog snapshot versions for reproducibility.
- User-identifying data is not copied into analytical evidence fields.

## Product matching order

1. Exact manufacturer part number.
2. Exact GTIN/EAN plus region/configuration checks.
3. Known retailer ID mapping.
4. High-confidence structured fingerprint.
5. Fuzzy candidate generation followed by deterministic field comparison.
6. Manual review when confidence is below the publish threshold.

Never merge variants solely from title similarity. RAM, storage, GPU, panel, OS, keyboard region, and warranty can differ within the same family.

