from datetime import UTC, datetime

import pytest
from knowledge.extractors.fake import FakeKnowledgeExtractor

from content.chunking.chunk import Chunk
from content.chunking.collection import ChunkCollection
from content.chunking.metadata import ChunkMetadata
from content.chunking.statistics import ChunkStatistics


@pytest.fixture
def chunk_collection() -> ChunkCollection:
    chunk = Chunk(
        id="c1",
        document_id="doc1",
        chunk_index=0,
        text="A transformer uses attention.",
        metadata=ChunkMetadata(
            processor="test",
            document_version="1",
            source="test",
            checksum="123",
        ),
        statistics=ChunkStatistics(
            character_count=10,
            line_count=1,
            word_count=5,
            estimated_tokens=2,
            processing_timestamp=datetime.now(UTC),
            confidence=1.0,
        ),
        created_at=datetime.now(UTC),
    )
    return ChunkCollection(chunks=(chunk,))


@pytest.mark.asyncio
async def test_fake_knowledge_extractor(chunk_collection: ChunkCollection) -> None:
    extractor = FakeKnowledgeExtractor(processing_delay_ms=0)
    result = await extractor.extract(chunk_collection)

    assert result.extractor_id == "fake_extractor"
    assert len(result.graph.concepts) == 4
    assert len(result.graph.relationships) == 2

    names = [c.name for c in result.graph.concepts]
    assert "Transformer" in names
    assert "Attention" in names


