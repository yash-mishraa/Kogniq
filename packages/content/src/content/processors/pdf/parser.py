from collections.abc import Iterator

import fitz  # type: ignore

from ...normalized.metadata import DocumentMetadata
from ...normalized.page import NormalizedPage
from .blocks import extract_blocks
from .exceptions import PDFCorruptedError, PDFEmptyError, PDFEncryptedError
from .metadata import extract_metadata


class PyMuPDFParser:
    def __init__(self, stream_bytes: bytes) -> None:
        try:
            self.doc = fitz.Document(stream=stream_bytes, filetype="pdf")
        except fitz.FileDataError as e:
            raise PDFCorruptedError(f"Failed to open PDF: {e}") from e

        if self.doc.is_encrypted or self.doc.needs_pass:
            raise PDFEncryptedError("Encrypted PDFs are not supported.")

        if self.doc.page_count == 0:
            raise PDFEmptyError("PDF contains no pages.")

    def get_metadata(self) -> tuple[str, DocumentMetadata]:
        return extract_metadata(self.doc)

    def iter_pages(self) -> Iterator[NormalizedPage]:
        for page_num in range(self.doc.page_count):
            page = self.doc[page_num]
            blocks = extract_blocks(page)
            yield NormalizedPage(
                page_number=page_num + 1,
                blocks=blocks,
                width=page.rect.width,
                height=page.rect.height,
            )

    def close(self) -> None:
        self.doc.close()
