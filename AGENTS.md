# Certikart Pipeline Engineering Rules

Read `docs/README.md` before architectural changes.

## Scope

This repository owns collection, normalization, matching, price history, review processing, data quality, and scheduled jobs. FastAPI, authentication, questionnaires, and recommendations belong to `certikart-api`.

## Mandatory rules

1. Keep source code directly in the prescribed `src/` folders; do not add a `src/certikart_pipeline/` wrapper.
2. Keep retailer selectors and field names inside `sources/<source>/`.
3. Validate every external boundary with Pydantic.
4. Use integer paise for money and timezone-aware UTC timestamps.
5. Keep product families, exact variants, offers, sellers, and observations separate.
6. Keep price history append-only and auditable.
7. Every claim needs source, observation time, transformation version, and confidence.
8. Keep product, seller, service, and delivery sentiment separate.
9. Avoid `Any`, unchecked casts, broad exceptions, and mutable global state.
10. Run `make check` before committing and `make security` for releases.
