import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "embedding" / "src"))

from embedding.collection import EmbeddingCollection
from embedding.embedding import Embedding
from embedding.metadata import EmbeddingMetadata
from embedding.statistics import EmbeddingStatistics
from embedding.vector import EmbeddingVector


def main() -> None:
    print("Building Canonical Embedding Domain Models...\n")

    dim = 4
    provider = "openai"
    model = "text-embedding-3-small"

    vec1 = EmbeddingVector(values=(0.1, 0.2, 0.3, 0.4), dimension=dim)
    vec2 = EmbeddingVector(values=(-0.1, -0.2, -0.3, -0.4), dimension=dim)

    meta = EmbeddingMetadata(
        provider=provider,
        model_name=model,
        model_version="1",
        embedding_version="v1",
        created_at=datetime.now(UTC),
        dimensions=dim,
        normalized=True,
    )
    stats = EmbeddingStatistics(processing_time_ms=150.0, token_count=100)

    emb1 = Embedding(
        id="e1",
        chunk_id="c1",
        vector=vec1,
        metadata=meta,
        statistics=stats,
        created_at=datetime.now(UTC),
    )
    emb2 = Embedding(
        id="e2",
        chunk_id="c2",
        vector=vec2,
        metadata=meta,
        statistics=stats,
        created_at=datetime.now(UTC),
    )

    collection = EmbeddingCollection(embeddings=(emb1, emb2))

    print("-" * 32)
    print("Embedding Collection Summary")
    print(f"Provider    : {collection.provider}")
    print(f"Model       : {emb1.metadata.model_name} (v{emb1.metadata.embedding_version})")
    print(f"Dimensions  : {collection.dimensions}")
    print(f"Count       : {collection.total_embeddings}")
    print(f"Normalized  : {emb1.metadata.normalized}")
    print("-" * 32)

    for i, emb in enumerate(collection.embeddings):
        print(f"\nEmbedding {i + 1}:")
        print(f"  ID        : {emb.id}")
        print(f"  Chunk ID  : {emb.chunk_id}")
        print(f"  Values    : {emb.vector.values}")
        print(f"  Latency   : {emb.statistics.processing_time_ms}ms")


if __name__ == "__main__":
    main()
