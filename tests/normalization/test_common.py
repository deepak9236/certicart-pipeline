import pytest

from normalization import normalize_capacity_gb, normalize_text


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("512 GB", 512), ("1 TB", 1024), ("0.5tb", 512)],
)
def test_normalize_capacity_gb(raw: str, expected: int) -> None:
    assert normalize_capacity_gb(raw) == expected


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        ("unknown", "unsupported capacity"),
        ("0 GB", "capacity must be positive"),
        ("1.2 GB", "whole GB"),
    ],
)
def test_normalize_capacity_rejects_invalid_values(raw: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        normalize_capacity_gb(raw)


def test_normalize_text_collapses_spacing_and_case() -> None:
    assert normalize_text(" Lenovo   ThinkBook ") == "lenovo thinkbook"
