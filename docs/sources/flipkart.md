# Flipkart Source Record

- Code: `flipkart`
- Allowed hosts: `flipkart.com`, `www.flipkart.com`
- Preferred access: official/authorized API, feed, or HTML/JSON-LD parsing via `FlipkartParser`
- Current state: adapter and parser active; supports live `HttpSourceTransport`
- Category scope: laptop initially; additional registered categories later
- Rate limit, retention, attribution, credentials, owner, kill switch: managed in pipeline configuration

Keep Flipkart-specific response fields and selectors inside `sources/flipkart/`.
