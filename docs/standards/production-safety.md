# Production Safety and Reliability

## Security baseline

- Secrets come from a secret manager or environment, never Git.
- Least-privilege roles separate collectors, workers, API, migrations, and humans.
- Outbound source domains are allow-listed per adapter.
- Credentials and personal data are redacted from structured logs and traces.
- Dependencies are locked with `uv.lock`, audited, and updated through reviewed changes.
- Raw content is encrypted, access-controlled, retention-limited, and collected only when permitted.
- Internal API authentication and network isolation are mandatory outside local development.
- Production images run as a non-root user with a read-only filesystem, dropped capabilities, and no privilege escalation.
- Production uses managed/external PostgreSQL; the local Compose database is never promoted or exposed.
- Image releases use immutable digests, vulnerability scanning, an SBOM, signing, and an explicit rollback target.

## Collection safety

- Each source has its own concurrency, timeout, retry, and circuit breaker.
- A global kill switch and a per-source kill switch can stop collection immediately.
- Requests use an honest product user agent and contact policy where appropriate.
- Robots and contractual policies are explicit configuration, not implicit assumptions.
- CAPTCHAs and access controls are stop signals, never bypass targets.
- Parser releases can run in shadow mode against saved permitted fixtures before deployment.

## Data integrity

- Raw evidence is immutable and content-addressed when retained.
- Transformations record version, input hash, and output hash.
- Database writes are transactional and idempotent.
- Price anomalies are quarantined rather than published automatically.
- Manual edits record actor, reason, old value, new value, and evidence.
- Backups and restore drills cover structured data and required evidence manifests.

## Recommendation safety

- Commission and retailer payout are prohibited ranking features.
- Hard requirements cannot be relaxed silently.
- Missing evidence lowers confidence and may prevent publication.
- Explanations must be generated from structured reasons/trade-offs.
- Every engine version has golden scenarios, property tests, rollout metrics, and rollback support.
- Shadow or canary releases compare new results before full activation.

## Privacy

- Collect only profile fields needed for a recommendation.
- Anonymous sessions are the default for the MVP.
- Remembered preferences require clear consent and deletion controls.
- Separate operational identities from analytical event identifiers.
- Define retention for raw prompts, profiles, events, and purchase outcomes.
- Never train on personal prompts or reviews without the appropriate legal basis and disclosure.

## Observability and SLO starters

Track structured metrics for source freshness, collection success, parser yield, match confidence, publication lag, API latency/errors, recommendation no-result rate, and explanation completeness.

Initial targets should be measured and revised, not presented as guarantees. Useful starting objectives are:

- internal recommendation API: 99.9% monthly availability;
- p95 recommendation latency under 300 ms for a preselected candidate set;
- published price freshness under the source-specific collection interval;
- zero published records without provenance;
- zero recommendations violating confirmed hard requirements.

## Incident response

1. Stop or isolate the affected source/engine version.
2. Preserve logs, versions, evidence IDs, and affected record IDs.
3. Prevent further publication.
4. Correct through audited records or a new derived version; do not rewrite history silently.
5. Backfill safely and validate aggregates.
6. Document root cause, customer impact, detection gap, and prevention action.
