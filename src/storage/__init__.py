"""Relational persistence layer for products, offers, and price history."""

from storage.engine import create_database_engine, get_session_factory, init_db
from storage.models import (
    Base,
    OfferModel,
    PriceHistoryModel,
    ProductIdentifierModel,
    ProductModel,
    RetailerProductModel,
    ScrapeRunModel,
)
from storage.repository import PipelineRepository

__all__ = [
    "Base",
    "OfferModel",
    "PipelineRepository",
    "PriceHistoryModel",
    "ProductIdentifierModel",
    "ProductModel",
    "RetailerProductModel",
    "ScrapeRunModel",
    "create_database_engine",
    "get_session_factory",
    "init_db",
]
