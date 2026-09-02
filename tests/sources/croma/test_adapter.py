from sources import CromaSourceAdapter, get_source_adapter


def test_croma_source_is_registered() -> None:
    assert get_source_adapter("croma") is CromaSourceAdapter
    assert "www.croma.com" in CromaSourceAdapter.allowed_hosts
