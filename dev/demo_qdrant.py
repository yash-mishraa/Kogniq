import uuid
from datetime import UTC, datetime

from embedding.collection import EmbeddingCollection
from embedding.embedding import Embedding
from embedding.metadata import EmbeddingMetadata
from embedding.statistics import EmbeddingStatistics
from embedding.vector import EmbeddingVector
from embedding.vectorstores.qdrant.client import QdrantClientManager
from embedding.vectorstores.qdrant.store import QdrantVectorStore


def create_demo_embeddings() -> tuple[Embedding, ...]:
    embeddings = []

    # 1. A document about Python
    emb1 = Embedding(
        id=f"doc_{uuid.uuid4().hex}",
        chunk_id="chunk-1",
        vector=EmbeddingVector(values=(0.9, 0.1, 0.0), dimension=3),
        metadata=EmbeddingMetadata(
            provider="demo",
            model_name="demo-model",
            model_version="1",
            embedding_version="1",
            dimensions=3,
            normalized=False,
            language="en",
            created_at=datetime.now(UTC),
        ),
        statistics=EmbeddingStatistics(processing_time_ms=5.0),
        created_at=datetime.now(UTC),
    )
    embeddings.append(emb1)

    # 2. A document about Data Science (similar to Python)
    emb2 = Embedding(
        id=f"doc_{uuid.uuid4().hex}",
        chunk_id="chunk-2",
        vector=EmbeddingVector(values=(0.8, 0.2, 0.0), dimension=3),
        metadata=EmbeddingMetadata(
            provider="demo",
            model_name="demo-model",
            model_version="1",
            embedding_version="1",
            dimensions=3,
            normalized=False,
            language="en",
            created_at=datetime.now(UTC),
        ),
        statistics=EmbeddingStatistics(processing_time_ms=5.0),
        created_at=datetime.now(UTC),
    )
    embeddings.append(emb2)

    # 3. A document about Cars (not similar)
    emb3 = Embedding(
        id=f"doc_{uuid.uuid4().hex}",
        chunk_id="chunk-3",
        vector=EmbeddingVector(values=(0.0, 0.1, 0.9), dimension=3),
        metadata=EmbeddingMetadata(
            provider="demo",
            model_name="demo-model",
            model_version="1",
            embedding_version="1",
            dimensions=3,
            normalized=False,
            language="en",
            created_at=datetime.now(UTC),
        ),
        statistics=EmbeddingStatistics(processing_time_ms=5.0),
        created_at=datetime.now(UTC),
    )
    embeddings.append(emb3)

    return tuple(embeddings)


def main() -> None:
    print("--- Qdrant Vector Store Demo ---")

    # Initialize Manager (using memory for easy demo, change url for docker)
    # To test against local docker: manager = QdrantClientManager(url="http://localhost:6333")
    print("Connecting to Qdrant (in-memory mode for demo)...")
    manager = QdrantClientManager(location=":memory:")

    # Check Health
    print(f"Health check: {manager.health_check()}")

    # Initialize Store
    print("\nInitializing QdrantVectorStore...")
    store = QdrantVectorStore(manager=manager, collection_name="demo_collection")
    print(f"Store Info: {store.info}")

    # Generate mock embeddings
    demo_embeddings = create_demo_embeddings()
    collection = EmbeddingCollection(embeddings=demo_embeddings)

    # Insert batch
    print(f"\nInserting {len(demo_embeddings)} vectors into Qdrant...")
    result = store.store_batch(collection)
    print(f"Stored count: {result.stored_count}")
    print(f"Total count in store: {store.count()}")

    # Perform Search
    print("\nSearching for vectors similar to (1.0, 0.0, 0.0)...")
    query_vector = EmbeddingVector(values=(1.0, 0.0, 0.0), dimension=3)
    search_results = store.search(query_vector, limit=2)

    print("\nSearch Results:")
    for rank, res in enumerate(search_results, 1):
        print(f"  {rank}. ID: {res.embedding.id}")
        print(f"     Chunk ID: {res.embedding.chunk_id}")
        print(f"     Score: {res.similarity_score:.4f}")
        print(f"     Provider: {res.embedding.metadata.provider}")

    # Test Deletion
    target_delete_id = demo_embeddings[0].id
    print(f"\nDeleting vector with ID: {target_delete_id}")
    store.delete(target_delete_id)
    print(f"Total count after deletion: {store.count()}")

    # Test Cleanup
    print("\nClearing vector store collection...")
    store.clear()

    # Check if empty
    print(f"Total count after clear: {store.count()}")

    print("\nDemo completed successfully!")


if __name__ == "__main__":
    main()
