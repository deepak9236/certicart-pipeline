import httpx
import pytest
from pydantic import AnyHttpUrl

from sources.transport import HttpSourceTransport


@pytest.mark.asyncio
async def test_http_source_transport_fetches_document() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            status_code=200,
            text="<html><title>Sample Page</title></html>",
            headers={"content-type": "text/html"},
        )
    )

    async with httpx.AsyncClient(transport=transport) as client:
        http_transport = HttpSourceTransport(client=client)
        url = AnyHttpUrl("https://www.flipkart.com/sample-product/p/itm123")
        document = await http_transport.fetch(url)

    assert document.observed_at is not None
    assert document.payload["status_code"] == 200
    assert document.payload["html"] == "<html><title>Sample Page</title></html>"
    assert len(document.content_hash) == 64


@pytest.mark.asyncio
async def test_http_source_transport_default_client(monkeypatch: pytest.MonkeyPatch) -> None:
    async def mock_get(self: httpx.AsyncClient, url: str, **kwargs: object) -> httpx.Response:
        req = httpx.Request("GET", url)
        return httpx.Response(
            status_code=200,
            text="<html>Default</html>",
            headers={"content-type": "text/html"},
            request=req,
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    http_transport = HttpSourceTransport()
    url = AnyHttpUrl("https://www.flipkart.com/sample")
    document = await http_transport.fetch(url)

    assert document.payload["status_code"] == 200
    assert document.payload["html"] == "<html>Default</html>"
