from sources.base import ConfiguredSourceAdapter
from sources.contracts import ParsedProduct, RawSourceRecord
from sources.flipkart.parser import parse_flipkart_record


class FlipkartSourceAdapter(ConfiguredSourceAdapter):
    name = "flipkart"
    allowed_hosts = frozenset({"flipkart.com", "www.flipkart.com"})

    def parse(self, record: RawSourceRecord) -> ParsedProduct:
        return parse_flipkart_record(record)
