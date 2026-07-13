from datetime import UTC, datetime

import pytest
from embedding.providers import ProviderCapabilityError
from embedding.providers.local.provider import LocalEmbeddingProvider

from content.chunking import Chunk, ChunkCollection, ChunkMetadata, ChunkStatistics


def make_chunk(cid: str, text: str) -> Chunk:
    meta = ChunkMetadata(processor="test", document_version="1", source="test", checksum="123")
    stats = ChunkStatistics(
        character_count=len(text),
        line_count=1,
        word_count=len(text.split()),
        estimated_tokens=len(text.split()),
        processing_timestamp=datetime.now(UTC),
        confidence=1.0
    )
    return Chunk(
        id=cid, document_id="doc1", chunk_index=0, text=text,
        metadata=meta, statistics=stats, created_at=datetime.now(UTC)
    )


def test_local_provider_lazy_load() -> None:
    provider = LocalEmbeddingProvider()
    assert provider._model is None
    
    _ = provider.info
    assert provider._model is not None
    
    model_instance = provider._model  # type: ignore[unreachable]
    _ = provider.info
    assert provider._model is model_instance


def test_local_provider_single_generation() -> None:
    provider = LocalEmbeddingProvider()
    chunk = make_chunk("c1", "This is a test chunk.")
    
    emb = provider.generate(chunk)
    
    assert emb.id == "c1"
    assert emb.chunk_id == "c1"
    assert len(emb.vector.values) == provider.info.dimensions
    assert emb.vector.dimension == provider.info.dimensions
    assert emb.metadata.provider == "SentenceTransformers"
    assert emb.metadata.normalized is True


def test_local_provider_batch_generation() -> None:
    provider = LocalEmbeddingProvider()
    chunk1 = make_chunk("c1", "Hello world")
    chunk2 = make_chunk("c2", "Second chunk here")
    
    collection = ChunkCollection(chunks=(chunk1, chunk2))
    
    embs = provider.generate_batch(collection)
    
    assert embs.total_embeddings == 2
    assert embs.embeddings[0].chunk_id == "c1"
    assert embs.embeddings[1].chunk_id == "c2"
    assert len(embs.embeddings[0].vector.values) == provider.info.dimensions


def test_local_provider_empty_collection_rejection() -> None:
    provider = LocalEmbeddingProvider()
    collection = ChunkCollection(chunks=())
    with pytest.raises(ProviderCapabilityError):
        provider.generate_batch(collection)
