"""Retailer, API, feed, and permitted-page source contracts."""

from sources.amazon import AmazonSourceAdapter
from sources.base import ConfiguredSourceAdapter, UnknownSourceProductError
from sources.common import (
    build_category_attributes,
    clean_capacity_str,
    extract_digits_to_paise,
    extract_json_ld_products,
    infer_brand,
)
from sources.contracts import (
    FetchedSourceDocument,
    ParsedProduct,
    RawSourceRecord,
    ReviewSourceAdapter,
    SourceAdapter,
    SourceProductReference,
    SourceTransport,
)
from sources.croma import CromaSourceAdapter
from sources.flipkart import FlipkartSourceAdapter
from sources.registry import get_source_adapter, supported_sources
from sources.transport import HttpSourceTransport

__all__ = [
    "AmazonSourceAdapter",
    "ConfiguredSourceAdapter",
    "CromaSourceAdapter",
    "FetchedSourceDocument",
    "FlipkartSourceAdapter",
    "HttpSourceTransport",
    "ParsedProduct",
    "RawSourceRecord",
    "ReviewSourceAdapter",
    "SourceAdapter",
    "SourceProductReference",
    "SourceTransport",
    "UnknownSourceProductError",
    "build_category_attributes",
    "clean_capacity_str",
    "extract_digits_to_paise",
    "extract_json_ld_products",
    "get_source_adapter",
    "infer_brand",
    "supported_sources",
]
