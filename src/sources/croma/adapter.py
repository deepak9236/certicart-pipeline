from sources.base import ConfiguredSourceAdapter
from sources.contracts import ParsedProduct, RawSourceRecord
from sources.croma.parser import parse_croma_record


class CromaSourceAdapter(ConfiguredSourceAdapter):
    name = "croma"
    allowed_hosts = frozenset({"croma.com", "www.croma.com"})

    def parse(self, record: RawSourceRecord) -> ParsedProduct:
        return parse_croma_record(record)
