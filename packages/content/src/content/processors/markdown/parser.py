from collections.abc import Iterator

from markdown_it import MarkdownIt

from ...normalized.page import NormalizedPage
from .blocks import extract_blocks
from .exceptions import MarkdownEmptyError, MarkdownEncodingError
from .statistics import MarkdownProcessorStatistics


class MarkdownItParser:
    def __init__(self, stream_bytes: bytes) -> None:
        try:
            self.text = stream_bytes.decode("utf-8")
        except UnicodeDecodeError as e:
            raise MarkdownEncodingError(f"Failed to decode Markdown file: {e}") from e

        if not self.text.strip():
            raise MarkdownEmptyError("Markdown file is empty.")

        self.md = MarkdownIt("commonmark").enable("table")

    def iter_pages(self, stats: MarkdownProcessorStatistics) -> Iterator[NormalizedPage]:
        tokens = self.md.parse(self.text)
        blocks = extract_blocks(tokens, stats)

        if not blocks:
            raise MarkdownEmptyError("Markdown file contains no readable blocks.")

        yield NormalizedPage(
            page_number=1,
            blocks=blocks
        )
