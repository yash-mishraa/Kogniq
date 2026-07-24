import io
from datetime import UTC, datetime
from typing import Any

import fitz  # type: ignore
import pytest

from content.normalized import BlockType
from content.processors.pdf import (
    PDFCorruptedError,
    PDFEmptyError,
    PDFEncryptedError,
    PDFProcessor,
)
from content.resource import (
    AbstractStreamReference,
    Checksum,
    ChecksumAlgorithm,
    ContentSource,
    LifecycleState,
    ResourceHandle,
    ResourceMetadata as HandleMetadata,
)


class MemoryStreamReference(AbstractStreamReference):
    def __init__(self, data: bytes) -> None:
        self.data = data

    def open_stream(self) -> io.BytesIO:
        return io.BytesIO(self.data)


def create_handle(data: bytes, filename: str = "test.pdf") -> ResourceHandle:
    return ResourceHandle(
        id="res_pdf_1",
        filename=filename,
        extension=".pdf",
        mime_type="application/pdf",
        source=ContentSource.UPLOAD,
        checksum=Checksum(algorithm=ChecksumAlgorithm.SHA256, value="hash"),
        size_bytes=len(data),
        created_at=datetime.now(UTC),
        metadata=HandleMetadata(),
        stream_reference=MemoryStreamReference(data),
        lifecycle_state=LifecycleState.CREATED,
    )


def test_pdf_processor_success() -> None:
    # Generate synthetic PDF
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(fitz.Point(50, 50), "Hello Kogniq")
    doc.set_metadata({"title": "Test Title", "author": "Tester"})

    pdf_bytes = doc.write()
    doc.close()

    handle = create_handle(pdf_bytes)
    processor = PDFProcessor()

    result = processor.process(handle)

    assert result.title == "Test Title"
    assert result.metadata is not None
    assert result.metadata.author == "Tester"
    assert len(result.pages) == 1

    page_obj = result.pages[0]
    assert page_obj.page_number == 1
    assert len(page_obj.blocks) >= 1
    assert "Hello Kogniq" in page_obj.blocks[0].text
    assert page_obj.blocks[0].block_type == BlockType.PARAGRAPH

    stats = result.statistics
    assert stats is not None
    assert stats["pages_processed"] == 1
    assert stats["blocks_extracted"] >= 1
    assert stats["metadata_available"] is True
    assert stats["processor"] == "fitz"


def test_pdf_processor_title_fallback_to_text() -> None:
    # Generate synthetic PDF with no title in metadata
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(fitz.Point(50, 50), "First Block Heading")
    page.insert_text(fitz.Point(50, 100), "Second Block Text")

    pdf_bytes = doc.write()
    doc.close()

    handle = create_handle(pdf_bytes)
    processor = PDFProcessor()

    result = processor.process(handle)

    # Title should fall back to the first non-empty text block
    assert result.title == "First Block Heading"


def test_pdf_processor_title_fallback_to_filename() -> None:
    # Generate synthetic PDF with no metadata and no text
    doc = fitz.open()
    doc.new_page()  # blank page

    pdf_bytes = doc.write()
    doc.close()

    handle = create_handle(pdf_bytes, filename="empty_paper.pdf")
    processor = PDFProcessor()

    result = processor.process(handle)

    # Title should fall back to filename because metadata and text are missing
    assert result.title == "empty_paper"


def test_pdf_processor_corrupted() -> None:
    corrupted_data = b"This is definitely not a PDF file"
    handle = create_handle(corrupted_data)
    processor = PDFProcessor()

    with pytest.raises(PDFCorruptedError, match="Failed to open PDF"):
        processor.process(handle)


def test_pdf_processor_encrypted() -> None:
    doc = fitz.open()
    doc.new_page()

    # Save with encryption to memory
    pdf_bytes = doc.write(encryption=fitz.PDF_ENCRYPT_RC4_40, owner_pw="owner", user_pw="secret")
    doc.close()

    handle = create_handle(pdf_bytes)
    processor = PDFProcessor()

    with pytest.raises(PDFEncryptedError, match="Encrypted PDFs are not supported"):
        processor.process(handle)


def test_pdf_processor_empty_pages(mocker: Any) -> None:
    # Needs valid PDF bytes to pass the open phase
    valid_doc = fitz.open()
    valid_doc.new_page()
    valid_bytes = valid_doc.write()
    valid_doc.close()
    valid_handle = create_handle(valid_bytes)

    mocker.patch(
        "content.processors.pdf.parser.fitz.Document.page_count",
        new_callable=mocker.PropertyMock,
        return_value=0,
    )
    processor = PDFProcessor()

    with pytest.raises(PDFEmptyError, match="PDF contains no pages"):
        processor.process(valid_handle)


def test_processor_info() -> None:
    processor = PDFProcessor()
    info = processor.processor_info

    assert info.name == "kogniq-pdf"
    assert "pdf" in info.supported_extensions
    assert "application/pdf" in info.supported_mime_types
