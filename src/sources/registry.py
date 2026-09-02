"""Retailer source registry."""

from sources.amazon import AmazonSourceAdapter
from sources.base import ConfiguredSourceAdapter
from sources.croma import CromaSourceAdapter
from sources.flipkart import FlipkartSourceAdapter

_SOURCE_ADAPTERS: dict[str, type[ConfiguredSourceAdapter]] = {
    AmazonSourceAdapter.name: AmazonSourceAdapter,
    CromaSourceAdapter.name: CromaSourceAdapter,
    FlipkartSourceAdapter.name: FlipkartSourceAdapter,
}


def get_source_adapter(name: str) -> type[ConfiguredSourceAdapter]:
    normalized = name.casefold().strip()
    try:
        return _SOURCE_ADAPTERS[normalized]
    except KeyError as error:
        raise ValueError(f"unsupported source: {name!r}") from error


def supported_sources() -> tuple[str, ...]:
    return tuple(sorted(_SOURCE_ADAPTERS))
