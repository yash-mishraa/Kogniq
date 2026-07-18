import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "embedding" / "src"))

from embedding.collection import EmbeddingCollection
from embedding.embedding import Embedding
from embedding.metadata import EmbeddingMetadata
from embedding.statistics import EmbeddingStatistics
from embedding.vector import EmbeddingVector
from embedding.vectorstores.chroma import ChromaVectorStore


def create_fake_embedding(id_str: str, values: tuple[float, ...]) -> Embedding:
    return Embedding(
        id=id_str,
        chunk_id=f"c_{id_str}",
        vector=EmbeddingVector(values=values, dimension=len(values)),
        metadata=EmbeddingMetadata(
            provider="demo_provider",
            model_name="demo_model",
            model_version="1",
            embedding_version="1",
            dimensions=len(values),
            normalized=True,
            language="en",
            created_at=datetime.now(UTC),
        ),
        statistics=EmbeddingStatistics(processing_time_ms=5.0),
        created_at=datetime.now(UTC),
    )


def main() -> None:
    print("Initializing ChromaVectorStore (Ephemeral Mode)...")
    store = ChromaVectorStore(collection_name="demo_collection")

    print("\nCreating fake embeddings...")
    e1 = create_fake_embedding("emb_1", (1.0, 0.0, 0.0))
    e2 = create_fake_embedding("emb_2", (0.0, 1.0, 0.0))
    e3 = create_fake_embedding("emb_3", (0.7, 0.7, 0.0))

    collection = EmbeddingCollection(embeddings=(e1, e2, e3))

    print(f"Inserting {len(collection.embeddings)} embeddings...")
    store.store_batch(collection)

    count = store.count()
    print(f"Current Vector Count: {count}")

    query_vector = EmbeddingVector(values=(1.0, 0.1, 0.0), dimension=3)
    print("\nExecuting similarity search for vector roughly around (1.0, 0.0, 0.0)...")
    results = store.search(query_vector, limit=3)

    print(f"\nFound {len(results)} results:")
    for result in results:
        emb = result.embedding
        print("-" * 40)
        print(f"Embedding ID : {emb.id}")
        print(f"Similarity   : {result.similarity_score:.4f}")
        print(f"Chunk ID     : {emb.chunk_id}")
        print(f"Provider     : {emb.metadata.provider}")
        print(f"Model        : {emb.metadata.model_name}")

    print("\nClearing collection...")
    store.clear()

    try:
        count_after = store.count()
        print(f"Count after clear: {count_after}")
    except Exception:
        print("Count after clear: 0 (Collection deleted)")


if __name__ == "__main__":
    main()
