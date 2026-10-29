from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from content.chunking import Chunk, ChunkCollection, ChunkMetadata, ChunkStatistics
from embedding.providers.gemini.provider import GeminiEmbeddingProvider


def make_chunk(cid: str, text: str) -> Chunk:
    meta = ChunkMetadata(processor="test", document_version="1", source="test", checksum="123")
    stats = ChunkStatistics(
        character_count=len(text),
        line_count=1,
        word_count=len(text.split()),
        estimated_tokens=len(text.split()),
        processing_timestamp=datetime.now(UTC),
        confidence=1.0,
    )
    return Chunk(
        id=cid,
        document_id="doc1",
        chunk_index=0,
        text=text,
        metadata=meta,
        statistics=stats,
        created_at=datetime.now(UTC),
    )


def test_gemini_provider_generation() -> None:
    mock_response = MagicMock()
    mock_response.embeddings = [MagicMock(values=[0.1] * 384)]

    mock_client = MagicMock()
    mock_client.models.embed_content.return_value = mock_response

    provider = GeminiEmbeddingProvider(api_key="test-key")
    provider._client = mock_client

    chunk = make_chunk("c1", "Test formula $E=mc^2$")
    result = provider.generate(chunk)

    assert result.vector.dimension == 384
    assert len(result.vector.values) == 384
    assert result.metadata.provider == "GeminiEmbeddingProvider"
    assert mock_client.models.embed_content.called
