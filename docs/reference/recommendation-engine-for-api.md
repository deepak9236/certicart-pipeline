# Deterministic Recommendation Engine

## Responsibility split

```text
LLM or guided form       -> understand requirements
Deterministic engine     -> decide and rank
LLM or templates         -> explain structured results
Retailer/NestJS          -> fulfil or route purchase
```

An LLM cannot select a winner directly. Any generated explanation must be grounded in the engine's contribution and trade-off objects.

## Input contract

The confirmed profile contains:

- category and use cases;
- minimum/maximum budget plus explicit stretch tolerance;
- hard requirements such as RAM, storage, OS, or required feature;
- preferences and importance from 1–5;
- brand exclusions/preferences;
- expected ownership period;
- contextual requirements such as portability or software/games.

The conversational layer extracts known fields and asks only questions that can materially change eligibility or ranking. The user confirms the summary before scoring.

## Algorithm V1

1. Validate the profile schema.
2. Select published, fresh, in-stock exact variants.
3. Apply hard filters.
4. Load category/use-case base weights.
5. Adjust weights using confirmed priorities and normalize to 1.0.
6. Calculate weighted feature fit from evidence-backed 0–100 component scores.
7. Apply transparent penalties for missing/low-confidence evidence and known incompatibility.
8. Attach current offer and historical deal information.
9. Rank deterministically with a stable tie-breaker.
10. Diversify the visible shortlist by meaningful trade-off archetype.
11. Return reasons, trade-offs, rejected alternatives, confidence, and version metadata.

## Scores

- **Fit score** answers how well a variant satisfies confirmed needs.
- **Data confidence** answers how complete and trustworthy the evidence is.
- **Ranking score** is an internal ordering value combining fit with a bounded confidence penalty.
- **Deal score** compares the unconditional price with recent history; it does not claim product suitability.

Do not label fit as a purchase probability. Use `91/100 fit` or a verbal band, not scientific-looking certainty.

## Versioning and reproducibility

Every run records:

- engine version;
- requirement schema version;
- feature-score version;
- candidate catalog snapshot/version;
- offer freshness cutoff;
- complete normalized weights;
- rule/penalty outputs;
- ordered result and latency.

A material rule change creates a new engine version. Never reinterpret stored historical recommendation runs using new code.

## Evaluation before release

Maintain a reviewed scenario suite covering budgets, workloads, must-haves, conflicting preferences, no-result cases, poor data, and boundary prices. A change is releasable only when:

- hard requirements are never violated;
- scores remain bounded and deterministic;
- reference outcomes do not regress without an accepted rationale;
- fairness slices do not reveal unexplained brand or retailer bias;
- explanations match actual scoring contributions;
- affiliate commission is absent from ranking features.

Start ML ranking only after the events are trustworthy, outcome labels are defined, offline evaluation beats the rule baseline, and rollback/shadow evaluation exists. Keep the deterministic engine as a fallback.

