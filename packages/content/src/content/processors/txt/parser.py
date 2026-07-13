from collections.abc import Iterator

from ...normalized.page import NormalizedPage
from .blocks import extract_blocks
from .exceptions import TXTEmptyError, TXTUnsupportedEncodingError
from .statistics import TXTProcessorStatistics


class TxtParser:
    def __init__(self, stream_bytes: bytes) -> None:
        self.stream_bytes = stream_bytes
        self.text = self._decode(stream_bytes)

    def _decode(self, b: bytes) -> str:
        try:
            if b.startswith(b"\xef\xbb\xbf"):
                return b[3:].decode("utf-8")
            return b.decode("utf-8")
        except UnicodeDecodeError as e:
            raise TXTUnsupportedEncodingError("File is not valid UTF-8 or UTF-8 BOM.") from e

    def iter_pages(self, stats: TXTProcessorStatistics) -> Iterator[NormalizedPage]:
        lines = self.text.splitlines(keepends=True)
        blocks = extract_blocks(lines, stats)

        if not blocks:
            raise TXTEmptyError("TXT file contains no readable blocks.")

        yield NormalizedPage(page_number=1, blocks=blocks)
