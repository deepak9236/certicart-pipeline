# Amazon India Source Record

- Code: `amazon`
- Allowed hosts: `amazon.in`, `www.amazon.in`
- Preferred access: official API or authorized feed; HTML/JSON-LD parsing supported via `AmazonParser`
- Current state: adapter and parser active; supports live `HttpSourceTransport`
- Category scope: laptop initially; additional registered categories later
- Rate limit, retention, attribution, credentials, owner, kill switch: managed in pipeline configuration

Keep Amazon-specific response fields and selectors inside `sources/amazon/`.
