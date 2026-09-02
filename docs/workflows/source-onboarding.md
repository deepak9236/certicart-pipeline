# Source Onboarding Workflow

## Before code

Create a source record containing:

- business owner and technical owner;
- API/feed/page access method;
- terms and robots review date;
- permitted fields, request rate, retention, and attribution requirements;
- credential scope and rotation owner;
- source-specific delivery/pincode behavior;
- stable identifiers and known variant ambiguity;
- kill switch and escalation contact.

If permission or scope is unclear, do not collect until resolved.

## Adapter implementation

1. Implement the `SourceAdapter` protocol.
2. Keep selectors and source field names inside the adapter.
3. Emit immutable `RawSourceRecord` values with UTC observation time and content hash.
4. Add saved permitted fixtures for representative success, missing fields, out-of-stock, multiple sellers, variant ambiguity, and changed markup.
5. Configure source-specific concurrency, timeouts, retryable statuses, and freshness.
6. Add parser completeness and anomaly metrics.
7. Run in shadow mode; do not publish immediately.

## Publication checklist

- Exact variant identity is proven or routed to manual review.
- Price components and conditional offers are separated.
- Seller and delivery context are retained.
- Required provenance is present.
- Data-quality thresholds pass for several collection cycles.
- Source policy and kill switch are tested.
- Alert routing has an owner.

## Ongoing maintenance

Review source terms and access periodically. Trigger investigation for discovery collapse, parser-yield changes, price discontinuities, freshness breaches, or rising unresolved-match rates. Disable a source safely before unreliable data reaches customers.

