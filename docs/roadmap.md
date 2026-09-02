# MVP Delivery Roadmap

## Phase 0: Foundations

- Agree on laptop variant identity and controlled vocabularies.
- Create PostgreSQL schema and migrations.
- Create source policy registry and audit trail.
- Build CI, telemetry, secrets, and deployment baseline.

## Phase 1: Curated laptop catalog

- Publish 50–100 manually verified laptop variants.
- Record evidence and confidence for decision-critical attributes.
- Add current offers from one or two authorized sources.
- Start append-only price observations and daily aggregation.

Exit: operators can explain every published claim and trace it to evidence.

## Phase 2: Recommendation MVP

- Implement confirmed requirement profile and adaptive-question contract.
- Expand deterministic laptop rules and penalties.
- Build 50–100 expert-reviewed golden scenarios.
- Return top match, alternatives, reasons, trade-offs, and confidence.

Exit: no golden scenario violates a hard requirement; recommendation changes are reproducible.

## Phase 3: Frontend integration

- Connect the Next.js experience through NestJS to the internal data/recommendation boundary.
- Replace demo products and scores with versioned real outputs.
- Add comparison, before-you-buy, offer freshness, and feedback events.

Exit: a real user can complete the 12-step definition of done in the product pitch.

## Phase 4: Collection automation

- Add sources one at a time using the onboarding workflow.
- Add anomaly quarantine, manual-review queue, and source dashboards.
- Increase collection frequency only after stability and policy review.

## Phase 5: Review intelligence

- Build multilingual, target-aware aspect extraction.
- Validate on human-labeled English/Hindi/Hinglish data.
- Publish only aggregated evidence meeting sample/confidence thresholds.

## Phase 6: Behavioural personalization

- Validate event quality and consent.
- Establish rule-engine baseline and offline metrics.
- Shadow-test learning-to-rank; release only if it improves outcomes without harming constraints, fairness, or explainability.

Do not build a marketplace, dozens of categories, or autonomous LLM purchasing logic before the laptop recommendation journey proves trust and conversion.

