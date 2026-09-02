# Development and Delivery Workflow

## Local setup

```bash
cp .env.example .env
make install
make dev-up
make pre-commit
make doctor
make check
```

See [Docker deployment](../deployment/docker.md) for image and production configuration rules.

## Feature workflow

1. State the customer or operator outcome.
2. Identify the owning module and update the relevant document/ADR.
3. Define or change the typed contract first.
4. Implement pure domain/application logic before infrastructure.
5. Add unit tests for examples and property tests for invariants.
6. Add adapter contract tests using permitted saved fixtures.
7. Add integration tests for database/event boundaries when introduced.
8. Run `make check` and the relevant targeted tests.
9. Run `make security` for dependency or release changes.
10. Deploy behind a source/feature/engine-version flag.
11. Observe metrics and retain a rollback path.

## Definition of done

- behavior and non-goals are documented;
- schemas are versioned and backwards compatibility is addressed;
- logs/metrics contain correlation IDs but no secrets;
- idempotency, retry, and failure behavior are tested;
- recommendation changes include scenario evaluation;
- data changes include migration and rollback/forward-fix plans;
- compliance/terms review is recorded for new external sources;
- `make check` succeeds;
- operational runbook and owner are known.

## Branching and commits

Use short-lived branches, focused commits, and reviewed migrations. Do not combine a new source, schema rewrite, and engine-policy change in one release unless a coordinated migration requires it.
