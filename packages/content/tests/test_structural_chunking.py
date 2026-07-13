from datetime import UTC, datetime

from content.chunking.strategies.structural import StructuralChunkStrategy
from content.normalized.block import NormalizedBlock
from content.normalized.document import NormalizedDocument
from content.normalized.enums import BlockType
from content.normalized.page import NormalizedPage


def create_doc(blocks: list[NormalizedBlock]) -> NormalizedDocument:
    return NormalizedDocument(
        id="doc-1",
        title="Test Doc",
        pages=(NormalizedPage(page_number=1, blocks=tuple(blocks)),),
        source="test",
        checksum="123",
        version="1.0",
        created_at=datetime.now(UTC)
    )

def test_empty_document() -> None:
    doc = create_doc([])
    strategy = StructuralChunkStrategy()
    collection = strategy.chunk(doc)
    assert collection.total_chunks == 0

def test_single_heading() -> None:
    blocks = [
        NormalizedBlock(block_id="1", block_type=BlockType.HEADING, text="Heading 1", order=0),
        NormalizedBlock(block_id="2", block_type=BlockType.PARAGRAPH, text="Paragraph 1", order=1),
    ]
    doc = create_doc(blocks)
    strategy = StructuralChunkStrategy()
    collection = strategy.chunk(doc)
    
    assert collection.total_chunks == 1
    assert collection.chunks[0].title == "Heading 1"
    assert "Heading 1\nParagraph 1" in collection.chunks[0].text

def test_multiple_headings() -> None:
    blocks = [
        NormalizedBlock(block_id="1", block_type=BlockType.HEADING, text="Heading 1", order=0),
        NormalizedBlock(block_id="2", block_type=BlockType.PARAGRAPH, text="P1", order=1),
        NormalizedBlock(block_id="3", block_type=BlockType.HEADING, text="Heading 2", order=2),
        NormalizedBlock(block_id="4", block_type=BlockType.PARAGRAPH, text="P2", order=3),
    ]
    doc = create_doc(blocks)
    strategy = StructuralChunkStrategy()
    collection = strategy.chunk(doc)
    
    assert collection.total_chunks == 2
    assert collection.chunks[0].title == "Heading 1"
    assert "P1" in collection.chunks[0].text
    assert collection.chunks[1].title == "Heading 2"
    assert "P2" in collection.chunks[1].text
    
    assert collection.chunks[0].chunk_index == 0
    assert collection.chunks[1].chunk_index == 1

def test_document_without_headings() -> None:
    blocks = [
        NormalizedBlock(block_id="1", block_type=BlockType.PARAGRAPH, text="P1", order=0),
        NormalizedBlock(block_id="2", block_type=BlockType.PARAGRAPH, text="P2", order=1),
    ]
    doc = create_doc(blocks)
    strategy = StructuralChunkStrategy()
    collection = strategy.chunk(doc)
    
    assert collection.total_chunks == 1
    assert collection.chunks[0].title == "Introduction"
    assert collection.chunks[0].text == "P1\nP2"

def test_consecutive_headings() -> None:
    blocks = [
        NormalizedBlock(block_id="1", block_type=BlockType.HEADING, text="H1", order=0),
        NormalizedBlock(block_id="2", block_type=BlockType.HEADING, text="H2", order=1),
        NormalizedBlock(block_id="3", block_type=BlockType.PARAGRAPH, text="P1", order=2),
    ]
    doc = create_doc(blocks)
    strategy = StructuralChunkStrategy()
    collection = strategy.chunk(doc)
    
    # H1 is a chunk by itself, H2 owns P1
    assert collection.total_chunks == 2
    assert collection.chunks[0].title == "H1"
    assert collection.chunks[0].text == "H1"
    assert collection.chunks[1].title == "H2"
    assert collection.chunks[1].text == "H2\nP1"

def test_multiple_empty_paragraphs() -> None:
    blocks = [
        NormalizedBlock(block_id="1", block_type=BlockType.HEADING, text="H1", order=0),
        NormalizedBlock(block_id="2", block_type=BlockType.PARAGRAPH, text="   \n  ", order=1),
        NormalizedBlock(block_id="3", block_type=BlockType.PARAGRAPH, text="", order=2),
        NormalizedBlock(block_id="4", block_type=BlockType.PARAGRAPH, text="P1", order=3),
    ]
    doc = create_doc(blocks)
    strategy = StructuralChunkStrategy()
    collection = strategy.chunk(doc)
    
    assert collection.total_chunks == 1
    assert collection.chunks[0].text == "H1\nP1"

def test_documents_containing_only_headings() -> None:
    blocks = [
        NormalizedBlock(block_id="1", block_type=BlockType.HEADING, text="H1", order=0),
        NormalizedBlock(block_id="2", block_type=BlockType.HEADING, text="H2", order=1),
    ]
    doc = create_doc(blocks)
    strategy = StructuralChunkStrategy()
    collection = strategy.chunk(doc)
    
    assert collection.total_chunks == 2
    assert collection.chunks[0].text == "H1"
    assert collection.chunks[1].text == "H2"

def test_various_block_types() -> None:
    blocks = [
        NormalizedBlock(block_id="1", block_type=BlockType.HEADING, text="H1", order=0),
        NormalizedBlock(block_id="2", block_type=BlockType.TABLE, text="Table 1", order=1),
        NormalizedBlock(block_id="3", block_type=BlockType.LIST, text="List 1", order=2),
        NormalizedBlock(block_id="4", block_type=BlockType.CODE, text="Code 1", order=3),
        NormalizedBlock(block_id="5", block_type=BlockType.QUOTE, text="Quote 1", order=4),
    ]
    doc = create_doc(blocks)
    strategy = StructuralChunkStrategy()
    collection = strategy.chunk(doc)
    
    assert collection.total_chunks == 1
    assert collection.chunks[0].text == "H1\nTable 1\nList 1\nCode 1\nQuote 1"

def test_page_number_assignment() -> None:
    pages = (
        NormalizedPage(
            page_number=1,
            blocks=(
                NormalizedBlock(block_id="1", block_type=BlockType.PARAGRAPH, text="P1", order=0),
            )
        ),
        NormalizedPage(
            page_number=2,
            blocks=(
                NormalizedBlock(block_id="2", block_type=BlockType.HEADING, text="H1", order=1),
            )
        ),
        NormalizedPage(
            page_number=3,
            blocks=(
                NormalizedBlock(block_id="3", block_type=BlockType.PARAGRAPH, text="P2", order=2),
            )
        ),
    )
    doc = NormalizedDocument(
        id="doc-1",
        title="Test Doc",
        pages=pages,
        source="test",
        checksum="123",
        version="1.0",
        created_at=datetime.now(UTC)
    )
    strategy = StructuralChunkStrategy()
    collection = strategy.chunk(doc)
    
    assert collection.total_chunks == 2
    assert collection.chunks[0].title == "Introduction"
    assert collection.chunks[0].page_number == 1
    
    assert collection.chunks[1].title == "H1"
    assert collection.chunks[1].page_number == 2
