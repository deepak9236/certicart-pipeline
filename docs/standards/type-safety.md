# Type Safety Standard

## Static and runtime boundaries

Python is dynamically executed, so production safety requires both:

- strict `mypy` for code paths and interfaces;
- Pydantic validation for environment, API, source, event, and persistence boundaries;
- PostgreSQL constraints for durable invariants;
- tests for business properties that types cannot express.

## Rules

1. Use Python 3.11+ annotations on every public function and method.
2. Do not use `Any`. Use `object`, `Protocol`, generics, discriminated unions, or explicit parsing.
3. External dictionaries never enter the domain without validation.
4. Prefer frozen Pydantic domain models and immutable tuples/frozensets.
5. Use `StrEnum` or `Literal` for controlled vocabularies.
6. Store money as integer paise. Floating point is allowed only for bounded analytical scores.
7. Store timezone-aware UTC datetimes; reject naive values at boundaries.
8. Use explicit `None` and model missing, unknown, not-applicable, and zero distinctly.
9. Avoid unchecked casts and `# type: ignore`. Any exception needs a narrow code and justification.
10. Use `Protocol` for adapters so domain/application modules do not depend on implementations.
11. Do not catch `Exception` unless adding context and re-raising or terminating a top-level job safely.
12. Do not serialize secrets in models, logs, traces, errors, or health endpoints.

## Required checks

```bash
make format-check
make lint
make typecheck
make test
```

`make check` runs all four. CI must block merging if any fails.

