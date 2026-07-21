from datetime import UTC, datetime

from content.chunking.collection import ChunkCollection
from content.chunking.engine import HybridChunkEngine
from content.chunking.strategies.base import AbstractChunkStrategy
from content.normalized.block import NormalizedBlock
from content.normalized.document import NormalizedDocument
from content.normalized.enums import BlockType
from content.normalized.page import NormalizedPage


class MockStrategy(AbstractChunkStrategy):
    def __init__(self, name: str) -> None:
        self.name = name
        self.called = False

    def chunk(self, document: NormalizedDocument) -> ChunkCollection:
        self.called = True
        return ChunkCollection(chunks=())


def create_doc(blocks: list[NormalizedBlock]) -> NormalizedDocument:
    pages = (NormalizedPage(page_number=1, blocks=tuple(blocks)),)

    return NormalizedDocument(
        id="doc-1",
        title="Test Doc",
        pages=pages,
        source="test",
        checksum="123",
        version="1.0",
        created_at=datetime.now(UTC),
    )


def test_document_with_headings() -> None:
    blocks = [
        NormalizedBlock(block_id="1", block_type=BlockType.PARAGRAPH, text="Intro", order=0),
        NormalizedBlock(block_id="2", block_type=BlockType.HEADING, text="H1", order=1),
    ]
    doc = create_doc(blocks)
    engine = HybridChunkEngine()

    engine.chunk(doc)
    assert engine.last_selected_strategy == "StructuralChunkStrategy"


def test_document_without_headings() -> None:
    blocks = [
        NormalizedBlock(block_id="1", block_type=BlockType.PARAGRAPH, text="P1", order=0),
        NormalizedBlock(block_id="2", block_type=BlockType.PARAGRAPH, text="P2", order=1),
    ]
    doc = create_doc(blocks)
    engine = HybridChunkEngine()

    engine.chunk(doc)
    assert engine.last_selected_strategy == "FixedSizeChunkStrategy"

    engine.chunk(doc)
    assert engine.last_selected_strategy == "FixedSizeChunkStrategy"


def test_deeply_nested_heading_blocks() -> None:
    heading_block = NormalizedBlock(
        block_id="4", block_type=BlockType.HEADING, text="Nested", order=0
    )
    nested_layer_2 = NormalizedBlock(
        block_id="3",
        block_type=BlockType.PARAGRAPH,
        text="Wrapper 2",
        order=0,
        children=(heading_block,),
    )
    nested_layer_1 = NormalizedBlock(
        block_id="2",
        block_type=BlockType.PARAGRAPH,
        text="Wrapper 1",
        order=0,
        children=(nested_layer_2,),
    )

    blocks = [
        NormalizedBlock(
            block_id="1",
            block_type=BlockType.PARAGRAPH,
            text="Root",
            order=0,
            children=(nested_layer_1,),
        )
    ]
    doc = create_doc(blocks)
    engine = HybridChunkEngine()

    engine.chunk(doc)
    assert engine.last_selected_strategy == "StructuralChunkStrategy"


def test_strategy_injection_and_delegation() -> None:
    mock_structural = MockStrategy("MockStructural")
    mock_fixed = MockStrategy("MockFixed")

    engine = HybridChunkEngine(structural_strategy=mock_structural, fixed_strategy=mock_fixed)

    doc_with_headings = create_doc(
        [NormalizedBlock(block_id="1", block_type=BlockType.HEADING, text="H1", order=0)]
    )
    engine.chunk(doc_with_headings)

    assert mock_structural.called is True
    assert mock_fixed.called is False
    assert engine.last_selected_strategy == "MockStrategy"

    # Reset
    mock_structural.called = False
    mock_fixed.called = False

    doc_without_headings = create_doc(
        [NormalizedBlock(block_id="1", block_type=BlockType.PARAGRAPH, text="P1", order=0)]
    )
    engine.chunk(doc_without_headings)

    assert mock_structural.called is False
    assert mock_fixed.called is True
    assert engine.last_selected_strategy == "MockStrategy"


def test_determinism() -> None:
    blocks = [
        NormalizedBlock(block_id="1", block_type=BlockType.PARAGRAPH, text="P1", order=0),
    ]
    doc = create_doc(blocks)
    engine = HybridChunkEngine()

    collection1 = engine.chunk(doc)
    strategy1 = engine.last_selected_strategy

    collection2 = engine.chunk(doc)
    strategy2 = engine.last_selected_strategy

    assert strategy1 == strategy2
    assert collection1.total_chunks == collection2.total_chunks
