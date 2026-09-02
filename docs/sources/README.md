# Retailer Source Status

| Source | Adapter | Operational status |
|---|---|---|
| Amazon India | `sources/amazon/` | Registered; HTML/JSON-LD parser, HTTP transport, and adapter implemented |
| Flipkart | `sources/flipkart/` | Registered; HTML/JSON-LD parser, HTTP transport, and adapter implemented |
| Croma | `sources/croma/` | Registered; HTML/JSON-LD parser, HTTP transport, and adapter implemented |

The adapters accept explicitly configured product references on approved HTTPS hosts and parse raw HTML/JSON-LD payloads into normalized `ParsedProduct` instances with integer paise pricing and category identity attributes.

- [Amazon India](amazon.md)
- [Flipkart](flipkart.md)
- [Croma](croma.md)
