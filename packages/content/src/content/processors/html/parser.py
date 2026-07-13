from bs4 import BeautifulSoup

from ...normalized.page import NormalizedPage
from .blocks import extract_blocks
from .exceptions import HTMLEmptyError, HTMLUnsupportedEncodingError
from .statistics import HTMLProcessorStatistics


class HTMLParser:
    def __init__(self, stream_bytes: bytes) -> None:
        self.stream_bytes = stream_bytes

    def parse(self, stats: HTMLProcessorStatistics) -> tuple[NormalizedPage, BeautifulSoup]:
        try:
            html_text = self.stream_bytes.decode('utf-8')
        except UnicodeDecodeError as e:
            raise HTMLUnsupportedEncodingError(
                "HTML stream uses an unsupported or invalid encoding."
            ) from e
            
        soup = BeautifulSoup(html_text, 'html.parser')
            
        blocks = extract_blocks(soup, stats)
        
        if not blocks:
            raise HTMLEmptyError("HTML document contains no extractable blocks.")
            
        page = NormalizedPage(
            page_number=1,
            blocks=blocks
        )
        
        return page, soup
