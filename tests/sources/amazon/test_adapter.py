from sources import AmazonSourceAdapter, get_source_adapter


def test_amazon_source_is_registered_with_india_hosts() -> None:
    assert get_source_adapter(" Amazon ") is AmazonSourceAdapter
    assert AmazonSourceAdapter.allowed_hosts == frozenset({"amazon.in", "www.amazon.in"})
