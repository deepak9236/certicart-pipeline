from sources.amazon.parser import parse_amazon_record
from sources.base import ConfiguredSourceAdapter
from sources.contracts import ParsedProduct, RawSourceRecord


class AmazonSourceAdapter(ConfiguredSourceAdapter):
    name = "amazon"
    allowed_hosts = frozenset({"amazon.in", "www.amazon.in"})

    def parse(self, record: RawSourceRecord) -> ParsedProduct:
        return parse_amazon_record(record)
