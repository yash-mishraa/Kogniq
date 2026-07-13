import io
import zipfile
from collections.abc import Iterator

import docx
from docx.document import Document as DocxDocument

from ...normalized.page import NormalizedPage
from .blocks import extract_blocks
from .exceptions import DOCXCorruptedError, DOCXEmptyError
from .statistics import DOCXProcessorStatistics


class DocxParser:
    def __init__(self, stream_bytes: bytes) -> None:
        self.stream = io.BytesIO(stream_bytes)
        try:
            self.doc: DocxDocument = docx.Document(self.stream)
        except zipfile.BadZipFile as e:
            raise DOCXCorruptedError(
                "Provided file is not a valid ZIP package or DOCX file."
            ) from e
        except Exception as e:
            raise DOCXCorruptedError(f"Failed to open DOCX file: {e}") from e

    def get_document(self) -> DocxDocument:
        return self.doc

    def iter_pages(self, stats: DOCXProcessorStatistics) -> Iterator[NormalizedPage]:
        # We treat the entire DOCX as a single logical page because 
        # python-docx does not reliably expose dynamic pagination breaks.
        blocks = extract_blocks(self.doc, stats)
        
        if not blocks:
            raise DOCXEmptyError("DOCX file contains no readable blocks.")
            
        yield NormalizedPage(
            page_number=1,
            blocks=blocks
        )
