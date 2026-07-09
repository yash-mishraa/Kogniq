from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from content.normalized import (
    BlockType,
    DocumentMetadata,
    InvalidBlockError,
    InvalidDocumentError,
    InvalidPageError,
    NormalizedBlock,
    NormalizedDocument,
    NormalizedPage,
    NormalizedSpan,
)


def test_span_formatting() -> None:
    span = NormalizedSpan(text="test", bold=True, italic=False)
    assert span.text == "test"
    assert span.bold is True
    assert span.italic is False
    assert span.underline is False
    assert span.hyperlink is None


def test_block_ordering() -> None:
    block = NormalizedBlock(
        block_id="b1", block_type=BlockType.PARAGRAPH, text="paragraph text", order=0
    )
    assert block.order == 0


def test_invalid_block_ordering() -> None:
    with pytest.raises(InvalidBlockError, match="order cannot be negative"):
        NormalizedBlock(block_id="b2", block_type=BlockType.HEADING, text="heading", order=-1)


def test_page_validation() -> None:
    page = NormalizedPage(page_number=1, blocks=())
    assert page.page_number == 1


def test_invalid_page_validation() -> None:
    with pytest.raises(InvalidPageError, match="page_number must be positive"):
        NormalizedPage(page_number=0, blocks=())
    with pytest.raises(InvalidPageError, match="page_number must be positive"):
        NormalizedPage(page_number=-5, blocks=())


def test_document_validation() -> None:
    page = NormalizedPage(page_number=1, blocks=())
    doc = NormalizedDocument(
        id="d1",
        title="Valid Document",
        pages=(page,),
        source="src",
        checksum="chk",
        version="v1",
        created_at=datetime.now(UTC),
    )
    assert doc.title == "Valid Document"
    assert len(doc.pages) == 1


def test_invalid_document_validation() -> None:
    page = NormalizedPage(page_number=1, blocks=())

    with pytest.raises(InvalidDocumentError, match="title cannot be empty"):
        NormalizedDocument(
            id="d1",
            title="   ",
            pages=(page,),
            source="src",
            checksum="chk",
            version="v1",
            created_at=datetime.now(UTC),
        )

    with pytest.raises(InvalidDocumentError, match="Document must contain at least one page"):
        NormalizedDocument(
            id="d1",
            title="Valid title",
            pages=(),
            source="src",
            checksum="chk",
            version="v1",
            created_at=datetime.now(UTC),
        )


def test_immutability() -> None:
    page = NormalizedPage(page_number=1, blocks=())
    doc = NormalizedDocument(
        id="d1",
        title="Doc",
        pages=(page,),
        source="src",
        checksum="chk",
        version="1.0",
        created_at=datetime.now(UTC),
    )
    with pytest.raises(FrozenInstanceError):
        doc.title = "Mutated"  # type: ignore


def test_metadata() -> None:
    meta = DocumentMetadata(author="John Doe", keywords=("ai", "learning"))
    assert meta.author == "John Doe"
    assert meta.keywords == ("ai", "learning")
