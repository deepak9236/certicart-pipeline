# Review Intelligence and Aspect Sentiment

## Purpose

Review intelligence supports product evidence; it does not replace specifications, expert measurements, or fit logic. Simple positive/negative sentiment is too coarse. Extract sentiment about named aspects and its target.

## Flow

```text
Permitted review source
  -> bounded cursor-based pagination
  -> immutable review record + content hash
  -> exact review deduplication
  -> language detection
  -> spam/low-information classification
  -> product/seller/delivery target classification
  -> laptop aspect extraction
  -> aspect sentiment + confidence + evidence span
  -> variant-aware aggregation
  -> minimum-sample and recency rules
  -> supporting recommendation evidence
```

Supported laptop aspects should begin with performance, battery, thermals, display, keyboard, trackpad, build, weight, fan noise, webcam, speakers, ports, gaming, upgradeability, reliability, service, seller, and delivery.

## Collection contract

Each collected review stores source, source product ID, review ID, category, target, rating, title/body, verified-purchase flag, helpful-vote count, source URL, published/observed timestamps, and a content hash. Reviewer names or profiles are not required and are not part of the contract.

Product, seller, delivery, and service reviews share the transport but remain separate `ReviewTarget` values. Review adapters return cursor-based pages of at most 100 records. The collector applies the selected profile's hard `max_reviews_per_product`, stops on empty pages, and rejects repeated cursors instead of looping indefinitely.

The normal `incremental` ceiling is 25 reviews per product per run. Existing reviews are deduplicated by `(source, source_product_id, review_id, content_hash)`; changed review text becomes a new auditable observation rather than silently overwriting history.

## Safety rules

- Follow source terms, licensing, robots policy, and data-retention requirements.
- Do not collect private profiles or unnecessary reviewer identifiers.
- Never merge reviews across variants without explicit family-level labeling.
- Separate product, seller, shipping, packaging, and service targets.
- Down-weight duplicated, templated, very short, or suspicious reviews.
- Treat `verified purchase` as evidence, not proof of truth.
- Preserve source, date, model version, confidence, and the minimal supporting evidence span.
- Support English, Hindi, and Hinglish evaluation before using results publicly.

## Aggregation

Never display raw ratios without sample size and uncertainty. Use minimum sample thresholds, Bayesian shrinkage toward a neutral prior, recency weighting, and confidence intervals where appropriate. Publish language such as:

> Battery complaints appeared in 31% of 84 relevant recent review mentions; evidence confidence is medium.

Do not publish:

> This laptop has bad battery.

Review evidence receives a bounded supporting weight. It cannot override a hard requirement or a verified measurement by itself.

## Evaluation set

Create a human-labeled, variant-aware dataset spanning English, Hindi, Hinglish, negation, sarcasm, mixed sentiment, seller complaints, comparison statements, and conditional statements such as "battery is good only in power saver." Track precision/recall per aspect and target, not only aggregate accuracy.
