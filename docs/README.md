# Certikart Pipeline Documentation

This repository documents only the background product-data pipeline. The Next.js frontend lives in `certikart`; FastAPI and the recommendation engine belong in the separate `certikart-api` project. Files under `docs/reference/` are context, not pipeline instructions.

## Read by task

| Task | Start here |
|---|---|
| Understand pipeline scope | [Architecture overview](architecture/overview.md) |
| Add a product category | [Category extensibility](architecture/category-extensibility.md) |
| Design tables or events | [Data model](architecture/data-model.md) |
| Add collection/normalization stages | [Pipeline architecture](architecture/pipeline.md) |
| Analyze customer reviews | [Review intelligence](architecture/review-intelligence.md) |
| Make a technical decision | [Architecture decisions](architecture/decisions.md) |
| Understand runtime safeguards | [Production safety](standards/production-safety.md) |
| Run PostgreSQL or deploy the image | [Docker deployment](deployment/docker.md) |
| Understand Python typing rules | [Type safety](standards/type-safety.md) |
| Implement and ship a feature | [Development workflow](workflows/development.md) |
| Add a retailer/API/feed | [Source onboarding](workflows/source-onboarding.md) |
| View configured retailers | [Retailer source status](sources/README.md) |
| Plan delivery | [MVP roadmap](roadmap.md) |

## Reference material

- [Product vision and developer pitch](reference/Certikart_Product_Vision_Developer_Pitch.md)
- [Recommendation design for the future FastAPI project](reference/recommendation-engine-for-api.md)
- `reference/frontend/` contains copied frontend documentation and the original starter blueprint.

The reference documents explain the broader product. Pipeline changes follow this repository's own rules and quality gate.
