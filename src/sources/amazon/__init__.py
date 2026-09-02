"""Amazon India source adapter."""

from sources.amazon.adapter import AmazonSourceAdapter
from sources.amazon.parser import parse_amazon_payload, parse_amazon_record

__all__ = ["AmazonSourceAdapter", "parse_amazon_payload", "parse_amazon_record"]
