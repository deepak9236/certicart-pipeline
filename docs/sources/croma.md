# Croma Source Record

- Code: `croma`
- Allowed hosts: `croma.com`, `www.croma.com`
- Preferred access: official/authorized API, feed, or HTML/JSON-LD parsing via `CromaParser`
- Current state: adapter and parser active; supports live `HttpSourceTransport`
- Category scope: laptop initially; additional registered categories later
- Rate limit, retention, attribution, credentials, owner, kill switch: managed in pipeline configuration

Keep Croma-specific response fields and selectors inside `sources/croma/`.
