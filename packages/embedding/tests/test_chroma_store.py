import uuid
from datetime import UTC, datetime

import pytest
from embedding.collection import EmbeddingCollection
from embedding.embedding import Embedding
from embedding.metadata import EmbeddingMetadata
from embedding.statistics import EmbeddingStatistics
from embedding.vector import EmbeddingVector
from embedding.vectorstores.chroma import ChromaVectorStore
from embedding.vectorstores.exceptions import StorageError


@pytest.fixture
def ephemeral_store() -> ChromaVectorStore:
    store = ChromaVectorStore(collection_name=f"test_{uuid.uuid4().hex}")
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


def test_chroma_store_info(ephemeral_store: ChromaVectorStore) -> None:
    info = ephemeral_store.info
    assert info.store_id == "chroma"
    assert info.store_name == "ChromaDB"
    assert "cosine" in info.supported_distance_metrics


def test_insert_one_and_count(ephemeral_store: ChromaVectorStore) -> None:
    assert ephemeral_store.count() == 0
    emb = create_test_embedding("e1")
    ephemeral_store.store(emb)
    assert ephemeral_store.count() == 1


def test_insert_batch(ephemeral_store: ChromaVectorStore) -> None:
    emb1 = create_test_embedding("e1")
    emb2 = create_test_embedding("e2")
    collection = EmbeddingCollection(embeddings=(emb1, emb2))

    ephemeral_store.store_batch(collection)
    assert ephemeral_store.count() == 2


def test_batch_limit_validation(ephemeral_store: ChromaVectorStore) -> None:
    limit = ephemeral_store.info.maximum_batch_size
    embeddings = tuple(create_test_embedding(f"e{i}") for i in range(limit + 1))
    collection = EmbeddingCollection(embeddings=embeddings)

    with pytest.raises(StorageError, match="exceeds maximum"):
        ephemeral_store.store_batch(collection)


def test_delete_and_delete_batch(ephemeral_store: ChromaVectorStore) -> None:
    emb1 = create_test_embedding("e1")
    emb2 = create_test_embedding("e2")
    emb3 = create_test_embedding("e3")
    ephemeral_store.store_batch(EmbeddingCollection(embeddings=(emb1, emb2, emb3)))

    assert ephemeral_store.count() == 3

    ephemeral_store.delete("e1")
    assert ephemeral_store.count() == 2

    ephemeral_store.delete_batch(("e2", "e3"))
    assert ephemeral_store.count() == 0


def test_search_and_metadata_persistence(ephemeral_store: ChromaVectorStore) -> None:
    emb = create_test_embedding("target_emb")
    ephemeral_store.store(emb)

    results = ephemeral_store.search(emb.vector, limit=1)

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


def test_clear(ephemeral_store: ChromaVectorStore) -> None:
    ephemeral_store.store(create_test_embedding("e1"))
    assert ephemeral_store.count() == 1
    ephemeral_store.clear()

    # Store should be usable after clear? Or requires re-init?
    # In Chroma, deleting a collection means we have to re-create it.
    # Our implementation uses get_or_create_collection lazily.
    ephemeral_store.store(create_test_embedding("e2"))
    assert ephemeral_store.count() == 1
