from datetime import UTC, datetime

from embedding.embedding import Embedding
from embedding.metadata import EmbeddingMetadata
from embedding.statistics import EmbeddingStatistics
from embedding.vector import EmbeddingVector


def test_embedding_creation() -> None:
    vec = EmbeddingVector(values=(0.5, 0.5), dimension=2)
    meta = EmbeddingMetadata(
        provider="openai",
        model_name="text-embedding-3-small",
        model_version="1",
        embedding_version="v1",
        created_at=datetime.now(UTC),
        dimensions=2,
        normalized=True,
    )
    stats = EmbeddingStatistics(processing_time_ms=10.5)

    emb = Embedding(
        id="emb-1",
        chunk_id="chunk-1",
        vector=vec,
        metadata=meta,
        statistics=stats,
        created_at=datetime.now(UTC),
    )

    assert emb.id == "emb-1"
    assert emb.vector.dimension == 2
    assert emb.metadata.provider == "openai"
