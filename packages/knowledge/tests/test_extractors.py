from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from knowledge.extractors.fake import FakeKnowledgeExtractor
from knowledge.extractors.openrouter.extractor import OpenRouterKnowledgeExtractor

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


@pytest.mark.asyncio
async def test_openrouter_knowledge_extractor(chunk_collection: ChunkCollection) -> None:
    extractor = OpenRouterKnowledgeExtractor(api_key="test_key", model_name="test_model")

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content='{"concepts": [], "relationships": []}'))
    ]

    with patch.object(
        extractor._client.chat.completions, "create", new_callable=AsyncMock
    ) as mock_create:
        mock_create.return_value = mock_response

        result = await extractor.extract(chunk_collection)

        assert result.extractor_id == "openrouter_test_model"
        assert len(result.graph.concepts) == 0
        assert len(result.graph.relationships) == 0
        mock_create.assert_called_once()
