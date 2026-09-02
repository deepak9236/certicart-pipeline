"""Flipkart source adapter."""

from sources.flipkart.adapter import FlipkartSourceAdapter
from sources.flipkart.parser import parse_flipkart_payload, parse_flipkart_record

__all__ = ["FlipkartSourceAdapter", "parse_flipkart_payload", "parse_flipkart_record"]
