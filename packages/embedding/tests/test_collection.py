from datetime import UTC, datetime

import pytest
from embedding.collection import EmbeddingCollection
from embedding.embedding import Embedding
from embedding.exceptions import InvalidEmbeddingError
from embedding.metadata import EmbeddingMetadata
from embedding.statistics import EmbeddingStatistics
from embedding.vector import EmbeddingVector


def create_meta(provider: str, model_name: str, dim: int) -> EmbeddingMetadata:
    return EmbeddingMetadata(
        provider=provider,
        model_name=model_name,
        model_version="1",
        embedding_version="v1",
        created_at=datetime.now(UTC),
        dimensions=dim,
        normalized=True
    )

def test_collection_creation() -> None:
    vec1 = EmbeddingVector(values=(1.0,), dimension=1)
    vec2 = EmbeddingVector(values=(2.0,), dimension=1)
    meta = create_meta("test", "model-a", 1)
    stats = EmbeddingStatistics(processing_time_ms=1.0)
    
    emb1 = Embedding(
        id="1",
        chunk_id="c1",
        vector=vec1,
        metadata=meta,
        statistics=stats,
        created_at=datetime.now(UTC),
    )
    emb2 = Embedding(
        id="2",
        chunk_id="c2",
        vector=vec2,
        metadata=meta,
        statistics=stats,
        created_at=datetime.now(UTC),
    )
    
    col = EmbeddingCollection(embeddings=(emb1, emb2))
    assert col.total_embeddings == 2
    assert col.dimensions == 1
    assert col.provider == "test"

def test_collection_mismatched_dimensions() -> None:
    vec1 = EmbeddingVector(values=(1.0,), dimension=1)
    vec2 = EmbeddingVector(values=(2.0, 3.0), dimension=2)
    meta1 = create_meta("test", "model-a", 1)
    meta2 = create_meta("test", "model-a", 2)
    stats = EmbeddingStatistics(processing_time_ms=1.0)
    
    emb1 = Embedding(
        id="1",
        chunk_id="c1",
        vector=vec1,
        metadata=meta1,
        statistics=stats,
        created_at=datetime.now(UTC),
    )
    emb2 = Embedding(
        id="2",
        chunk_id="c2",
        vector=vec2,
        metadata=meta2,
        statistics=stats,
        created_at=datetime.now(UTC),
    )
    
    with pytest.raises(InvalidEmbeddingError, match="Mismatched dimensions"):
        EmbeddingCollection(embeddings=(emb1, emb2))

def test_collection_mismatched_providers() -> None:
    vec = EmbeddingVector(values=(1.0,), dimension=1)
    meta1 = create_meta("test1", "model-a", 1)
    meta2 = create_meta("test2", "model-a", 1)
    stats = EmbeddingStatistics(processing_time_ms=1.0)
    
    emb1 = Embedding(
        id="1",
        chunk_id="c1",
        vector=vec,
        metadata=meta1,
        statistics=stats,
        created_at=datetime.now(UTC),
    )
    emb2 = Embedding(
        id="2",
        chunk_id="c2",
        vector=vec,
        metadata=meta2,
        statistics=stats,
        created_at=datetime.now(UTC),
    )
    
    with pytest.raises(InvalidEmbeddingError, match="Mismatched provider"):
        EmbeddingCollection(embeddings=(emb1, emb2))

def test_collection_mismatched_model_names() -> None:
    vec = EmbeddingVector(values=(1.0,), dimension=1)
    meta1 = create_meta("test", "model-a", 1)
    meta2 = create_meta("test", "model-b", 1)
    stats = EmbeddingStatistics(processing_time_ms=1.0)
    
    emb1 = Embedding(
        id="1",
        chunk_id="c1",
        vector=vec,
        metadata=meta1,
        statistics=stats,
        created_at=datetime.now(UTC),
    )
    emb2 = Embedding(
        id="2",
        chunk_id="c2",
        vector=vec,
        metadata=meta2,
        statistics=stats,
        created_at=datetime.now(UTC),
    )
    
    with pytest.raises(InvalidEmbeddingError, match="Mismatched model"):
        EmbeddingCollection(embeddings=(emb1, emb2))

def test_collection_empty() -> None:
    col = EmbeddingCollection(embeddings=())
    assert col.total_embeddings == 0
    assert col.dimensions == 0
    assert col.provider is None
