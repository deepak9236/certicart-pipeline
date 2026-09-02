"""Shared mechanics for configured retailer adapters."""

from collections.abc import AsyncIterator, Iterable

from pydantic import AnyHttpUrl

from sources.contracts import (
    ParsedProduct,
    RawSourceRecord,
    SourceProductReference,
    SourceTransport,
)


class UnknownSourceProductError(LookupError):
    """Raised when a job asks an adapter for an undiscovered product."""


class ConfiguredSourceAdapter:
    """Collect approved references through an injected, policy-specific transport."""

    name: str
    allowed_hosts: frozenset[str]

    def __init__(
        self,
        references: Iterable[SourceProductReference],
        transport: SourceTransport,
    ) -> None:
        self._transport = transport
        self._references: dict[str, SourceProductReference] = {}
        for reference in references:
            self._validate_url(reference.source_url)
            if reference.source_product_id in self._references:
                raise ValueError(f"duplicate source product ID: {reference.source_product_id!r}")
            self._references[reference.source_product_id] = reference

    def _validate_url(self, source_url: AnyHttpUrl) -> None:
        host = str(source_url.host).casefold()
        if source_url.scheme != "https" or host not in self.allowed_hosts:
            raise ValueError(f"{self.name} reference must use HTTPS on an approved host")

    async def discover(self) -> AsyncIterator[str]:
        for source_product_id in self._references:
            yield source_product_id

    async def fetch(self, source_product_id: str) -> RawSourceRecord:
        try:
            reference = self._references[source_product_id]
        except KeyError as error:
            raise UnknownSourceProductError(source_product_id) from error

        document = await self._transport.fetch(reference.source_url)
        return RawSourceRecord(
            source=self.name,
            source_product_id=reference.source_product_id,
            category=reference.category,
            subcategory=reference.subcategory,
            source_url=reference.source_url,
            observed_at=document.observed_at,
            payload=document.payload,
            content_hash=document.content_hash,
        )

    def parse(self, record: RawSourceRecord) -> ParsedProduct:
        raise NotImplementedError
