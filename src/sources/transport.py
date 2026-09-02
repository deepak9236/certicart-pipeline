"""HTTP network transport for live source document fetching."""

import hashlib
from collections.abc import Mapping
from datetime import UTC, datetime

import httpx
from curl_cffi.requests import AsyncSession
from pydantic import AnyHttpUrl

from sources.contracts import FetchedSourceDocument, SourceTransport

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0.0.0 Safari/537.36"
)

DEFAULT_HEADERS: Mapping[str, str] = {
    "User-Agent": DEFAULT_USER_AGENT,
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"macOS"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}


class HttpSourceTransport(SourceTransport):
    """Async HTTP transport using curl_cffi browser TLS impersonation and HTTP/2."""

    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = None,
        timeout_seconds: float = 30.0,
        headers: Mapping[str, str] | None = None,
        impersonate: str = "chrome124",
    ) -> None:
        self._custom_client = client
        self._timeout_seconds = timeout_seconds
        self._headers = dict(headers if headers is not None else DEFAULT_HEADERS)
        self._impersonate = impersonate

    async def fetch(self, source_url: AnyHttpUrl) -> FetchedSourceDocument:
        url_str = str(source_url)
        if self._custom_client is not None:
            response = await self._custom_client.get(
                url_str,
                headers=self._headers,
                timeout=self._timeout_seconds,
                follow_redirects=True,
            )
            response.raise_for_status()
            content_bytes = response.content
            html_text = response.text
            status_code = response.status_code
        else:
            try:
                async with AsyncSession(
                    impersonate=self._impersonate,
                    headers=self._headers,
                    timeout=self._timeout_seconds,
                ) as session:
                    res = await session.get(url_str, allow_redirects=True)
                    if res.status_code >= 400:
                        res.raise_for_status()
                    content_bytes = res.content
                    html_text = res.text
                    status_code = res.status_code
            except Exception:
                async with httpx.AsyncClient(
                    http2=True,
                    headers=self._headers,
                    timeout=self._timeout_seconds,
                    follow_redirects=True,
                ) as fallback_client:
                    fb_res = await fallback_client.get(url_str)
                    fb_res.raise_for_status()
                    content_bytes = fb_res.content
                    html_text = fb_res.text
                    status_code = fb_res.status_code

        content_hash = hashlib.sha256(content_bytes).hexdigest()
        now = datetime.now(UTC)

        payload: dict[str, object] = {
            "html": html_text,
            "status_code": status_code,
            "url": url_str,
        }

        return FetchedSourceDocument(
            observed_at=now,
            payload=payload,
            content_hash=content_hash,
        )
