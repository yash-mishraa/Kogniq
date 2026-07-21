import uuid
from datetime import UTC, datetime

import pytest
from embedding.collection import EmbeddingCollection
from embedding.embedding import Embedding
from embedding.metadata import EmbeddingMetadata
from embedding.statistics import EmbeddingStatistics
from embedding.vector import EmbeddingVector
from embedding.vectorstores.exceptions import StorageError
from embedding.vectorstores.qdrant.client import QdrantClientManager
from embedding.vectorstores.qdrant.store import QdrantVectorStore


@pytest.fixture
def memory_manager() -> QdrantClientManager:
    return QdrantClientManager(location=":memory:")


@pytest.fixture
def qdrant_store(memory_manager: QdrantClientManager) -> QdrantVectorStore:
    store = QdrantVectorStore(manager=memory_manager, collection_name=f"test_{uuid.uuid4().hex}")
    return store


def create_test_embedding(eid: str, dim: int = 2) -> Embedding:
    return Embedding(
        id=eid,
        chunk_id=f"c_{eid}",
        vector=EmbeddingVector(values=tuple(float(i) for i in range(dim)), dimension=dim),
        metadata=EmbeddingMetadata(
            provider="test",
            model_name="test_model",
            model_version="1",
            embedding_version="1",
            dimensions=dim,
            normalized=False,
            language="en",
            created_at=datetime.now(UTC),
        ),
        statistics=EmbeddingStatistics(processing_time_ms=5.0),
        created_at=datetime.now(UTC),
    )


def test_qdrant_store_info(qdrant_store: QdrantVectorStore) -> None:
    info = qdrant_store.info
    assert info.store_id == "qdrant"
    assert info.store_name == "Qdrant"
    assert "cosine" in info.supported_distance_metrics


def test_insert_one_and_count(qdrant_store: QdrantVectorStore) -> None:
    qdrant_store.store(create_test_embedding("e1"))
    assert qdrant_store.count() == 1


def test_insert_batch(qdrant_store: QdrantVectorStore) -> None:
    emb1 = create_test_embedding("e1")
    emb2 = create_test_embedding("e2")
    collection = EmbeddingCollection(embeddings=(emb1, emb2))

    qdrant_store.store_batch(collection)
    assert qdrant_store.count() == 2


def test_duplicate_ids(qdrant_store: QdrantVectorStore) -> None:
    emb1 = create_test_embedding("e1")
    emb1_dup = create_test_embedding("e1")

    # Qdrant upserts by ID, so it overrides
    qdrant_store.store(emb1)
    assert qdrant_store.count() == 1

    qdrant_store.store(emb1_dup)
    assert qdrant_store.count() == 1


def test_batch_limit_validation(qdrant_store: QdrantVectorStore) -> None:
    limit = qdrant_store.info.maximum_batch_size
    embeddings = tuple(create_test_embedding(f"e{i}") for i in range(limit + 1))
    collection = EmbeddingCollection(embeddings=embeddings)

    with pytest.raises(StorageError, match="exceeds maximum"):
        qdrant_store.store_batch(collection)


def test_delete_and_delete_batch(qdrant_store: QdrantVectorStore) -> None:
    emb1 = create_test_embedding("e1")
    emb2 = create_test_embedding("e2")
    emb3 = create_test_embedding("e3")
    qdrant_store.store_batch(EmbeddingCollection(embeddings=(emb1, emb2, emb3)))

    assert qdrant_store.count() == 3

    qdrant_store.delete("e1")
    assert qdrant_store.count() == 2

    qdrant_store.delete_batch(("e2", "e3"))
    assert qdrant_store.count() == 0


def test_search_and_metadata_persistence(qdrant_store: QdrantVectorStore) -> None:
    emb = create_test_embedding("target_emb")
    qdrant_store.store(emb)

    results = qdrant_store.search(emb.vector, limit=1)

    assert len(results) == 1
    result = results[0]

    assert result.embedding.id == "target_emb"
    assert result.similarity_score >= 0.0 and result.similarity_score <= 1.0

    # Check metadata persistence
    meta = result.embedding.metadata
    assert meta.provider == "test"
    assert meta.model_name == "test_model"
    assert meta.dimensions == 2
    assert meta.language == "en"


def test_similarity_ordering(qdrant_store: QdrantVectorStore) -> None:
    emb1 = create_test_embedding("e1")
    emb1_new = Embedding(
        id=emb1.id,
        chunk_id=emb1.chunk_id,
        vector=EmbeddingVector(values=(1.0, 0.0), dimension=2),
        metadata=emb1.metadata,
        statistics=emb1.statistics,
        created_at=emb1.created_at,
    )

    emb2 = create_test_embedding("e2")
    emb2_new = Embedding(
        id=emb2.id,
        chunk_id=emb2.chunk_id,
        vector=EmbeddingVector(values=(0.0, 1.0), dimension=2),
        metadata=emb2.metadata,
        statistics=emb2.statistics,
        created_at=emb2.created_at,
    )

    qdrant_store.store_batch(EmbeddingCollection(embeddings=(emb1_new, emb2_new)))

    query_vector = EmbeddingVector(values=(1.0, 0.0), dimension=2)
    results = qdrant_store.search(query_vector, limit=2)

    assert len(results) == 2
    assert results[0].embedding.id == "e1"  # Closest match
    assert results[1].embedding.id == "e2"
    assert results[0].similarity_score > results[1].similarity_score


def test_empty_collection(qdrant_store: QdrantVectorStore) -> None:
    # Attempting to search an empty/uninitialized collection should return empty
    # if it hasn't been created, or return empty if it's 0 vectors.
    qdrant_store.store(create_test_embedding("e1"))
    qdrant_store.delete("e1")

    query_vector = EmbeddingVector(values=(1.0, 0.0), dimension=2)
    results = qdrant_store.search(query_vector, limit=1)
    assert len(results) == 0


def test_clear(qdrant_store: QdrantVectorStore) -> None:
    qdrant_store.store(create_test_embedding("e1"))
    assert qdrant_store.count() == 1
    qdrant_store.clear()

    # Should recreate correctly
    qdrant_store.store(create_test_embedding("e2"))
    assert qdrant_store.count() == 1
