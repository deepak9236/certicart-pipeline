import pytest

from sources import supported_sources
from sources.registry import get_source_adapter


def test_supported_sources_are_stable_and_sorted() -> None:
    assert supported_sources() == ("amazon", "croma", "flipkart")


def test_unknown_source_is_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported source"):
        get_source_adapter("unknown")
