from datetime import UTC, datetime

import pytest

from content.chunking.strategies.exceptions import ChunkStrategyError
from content.chunking.strategies.fixed_size import FixedSizeChunkStrategy
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

def test_constructor_validation() -> None:
    with pytest.raises(ChunkStrategyError):
        FixedSizeChunkStrategy(max_characters=0)
    
    with pytest.raises(ChunkStrategyError):
        FixedSizeChunkStrategy(max_characters=-50)

def test_max_characters_equals_one() -> None:
    blocks = [
        NormalizedBlock(block_id="1", block_type=BlockType.PARAGRAPH, text="Hello", order=0),
        NormalizedBlock(block_id="2", block_type=BlockType.PARAGRAPH, text="World", order=1),
    ]
    doc = create_doc(blocks)
    strategy = FixedSizeChunkStrategy(max_characters=1)
    collection = strategy.chunk(doc)
    
    # Since max is 1, each block is technically an oversized block and emits immediately.
    assert collection.total_chunks == 2
    assert collection.chunks[0].text == "Hello"
    assert collection.chunks[1].text == "World"
    assert collection.chunks[0].title == "Chunk 0"
    assert collection.chunks[1].title == "Chunk 1"

def test_oversized_block() -> None:
    blocks = [
        NormalizedBlock(
            block_id="1", 
            block_type=BlockType.PARAGRAPH, 
            text="This is an extremely long block that exceeds the 10 char limit.", 
            order=0
        ),
    ]
    doc = create_doc(blocks)
    strategy = FixedSizeChunkStrategy(max_characters=10)
    collection = strategy.chunk(doc)
    
    assert collection.total_chunks == 1
    assert collection.chunks[0].text == (
        "This is an extremely long block that exceeds the 10 char limit."
    )

def test_documents_containing_only_headings() -> None:
    blocks = [
        NormalizedBlock(block_id="1", block_type=BlockType.HEADING, text="H1", order=0),
        NormalizedBlock(block_id="2", block_type=BlockType.HEADING, text="H2", order=1),
    ]
    doc = create_doc(blocks)
    strategy = FixedSizeChunkStrategy(max_characters=10)
    collection = strategy.chunk(doc)
    
    # H1 = 2 chars. H2 = 2 chars. Total = 4. Less than 10.
    assert collection.total_chunks == 1
    assert collection.chunks[0].text == "H1\nH2"
    assert collection.chunks[0].section_title == "H2"
    assert collection.chunks[0].title == "H2"

def test_multiple_consecutive_headings() -> None:
    blocks = [
        NormalizedBlock(block_id="1", block_type=BlockType.HEADING, text="Header 1", order=0),
        NormalizedBlock(block_id="2", block_type=BlockType.HEADING, text="Header 2", order=1),
        NormalizedBlock(block_id="3", block_type=BlockType.HEADING, text="Header 3", order=2),
    ]
    doc = create_doc(blocks)
    # Header 1 = 8 chars. Header 2 = 8. (8 + 1 + 8 = 17). Exceeds 15.
    strategy = FixedSizeChunkStrategy(max_characters=15)
    collection = strategy.chunk(doc)
    
    assert collection.total_chunks == 3
    assert collection.chunks[0].text == "Header 1"
    assert collection.chunks[0].section_title == "Header 1"
    assert collection.chunks[1].text == "Header 2"
    assert collection.chunks[1].section_title == "Header 2"
    assert collection.chunks[2].text == "Header 3"
    assert collection.chunks[2].section_title == "Header 3"

def test_empty_paragraphs_between_headings() -> None:
    blocks = [
        NormalizedBlock(block_id="1", block_type=BlockType.HEADING, text="H1", order=0),
        NormalizedBlock(block_id="2", block_type=BlockType.PARAGRAPH, text="   ", order=1),
        NormalizedBlock(block_id="3", block_type=BlockType.PARAGRAPH, text="", order=2),
        NormalizedBlock(block_id="4", block_type=BlockType.HEADING, text="H2", order=3),
    ]
    doc = create_doc(blocks)
    strategy = FixedSizeChunkStrategy(max_characters=10)
    collection = strategy.chunk(doc)
    
    assert collection.total_chunks == 1
    assert collection.chunks[0].text == "H1\nH2"

def test_multi_page_documents() -> None:
    pages = (
        NormalizedPage(
            page_number=1,
            blocks=(
                NormalizedBlock(
                    block_id="1", block_type=BlockType.PARAGRAPH, text="A" * 10, order=0
                ),
            )
        ),
        NormalizedPage(
            page_number=2,
            blocks=(
                NormalizedBlock(
                    block_id="2", block_type=BlockType.PARAGRAPH, text="B" * 10, order=1
                ),
                NormalizedBlock(
                    block_id="3", block_type=BlockType.PARAGRAPH, text="C" * 10, order=2
                ),
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
    strategy = FixedSizeChunkStrategy(max_characters=25)
    collection = strategy.chunk(doc)
    
    # 10 + 1 + 10 = 21 chars. Adding 3rd would be 21 + 1 + 10 = 32 > 25.
    assert collection.total_chunks == 2
    assert collection.chunks[0].text == f"{'A'*10}\n{'B'*10}"
    assert collection.chunks[0].page_number == 1
    assert collection.chunks[1].text == f"{'C'*10}"
    assert collection.chunks[1].page_number == 2

def test_deterministic_repeated_execution() -> None:
    blocks = [
        NormalizedBlock(
            block_id="1", block_type=BlockType.PARAGRAPH, text="Chunk 1 Part A", order=0
        ),
        NormalizedBlock(
            block_id="2", block_type=BlockType.PARAGRAPH, text="Chunk 1 Part B", order=1
        ),
        NormalizedBlock(
            block_id="3", block_type=BlockType.HEADING, text="Chunk 2 H1", order=2
        ),
        NormalizedBlock(
            block_id="4", block_type=BlockType.PARAGRAPH, text="Chunk 2 Part C", order=3
        ),
    ]
    doc = create_doc(blocks)
    strategy = FixedSizeChunkStrategy(max_characters=35)
    
    collection1 = strategy.chunk(doc)
    collection2 = strategy.chunk(doc)
    
    assert collection1.total_chunks == collection2.total_chunks
    assert [c.text for c in collection1.chunks] == [c.text for c in collection2.chunks]
    assert [c.title for c in collection1.chunks] == [c.title for c in collection2.chunks]
    
    idx1 = [c.chunk_index for c in collection1.chunks]
    idx2 = [c.chunk_index for c in collection2.chunks]
    assert idx1 == idx2

def test_preservation_of_heading_blocks_inside_chunk_text() -> None:
    blocks = [
        NormalizedBlock(
            block_id="1", block_type=BlockType.PARAGRAPH, text="Introduction.", order=0
        ),
        NormalizedBlock(
            block_id="2", block_type=BlockType.HEADING, text="Main Topic", order=1
        ),
        NormalizedBlock(
            block_id="3", block_type=BlockType.PARAGRAPH, text="Topic details.", order=2
        ),
    ]
    doc = create_doc(blocks)
    strategy = FixedSizeChunkStrategy(max_characters=50)
    collection = strategy.chunk(doc)
    
    # Total chars: 13 + 1 + 10 + 1 + 14 = 39 <= 50. All in one chunk.
    assert collection.total_chunks == 1
    assert "Main Topic" in collection.chunks[0].text
    assert collection.chunks[0].title == "Main Topic"
    assert collection.chunks[0].section_title == "Main Topic"
