from sources import FlipkartSourceAdapter, get_source_adapter


def test_flipkart_source_is_registered() -> None:
    assert get_source_adapter("flipkart") is FlipkartSourceAdapter
    assert "www.flipkart.com" in FlipkartSourceAdapter.allowed_hosts
