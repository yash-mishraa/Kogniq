from datetime import UTC, datetime

import pytest
from embedding.collection import EmbeddingCollection
from embedding.embedding import Embedding
from embedding.metadata import EmbeddingMetadata
from embedding.statistics import EmbeddingStatistics
from embedding.vector import EmbeddingVector
from embedding.vectorstores import (
    AbstractVectorStore,
    SearchResult,
    StorageResult,
    StoreConfigurationError,
    StoreInfo,
)


class FakeVectorStore(AbstractVectorStore):
    def __init__(self) -> None:
        self._store: dict[str, Embedding] = {}
        self._info = StoreInfo(
            store_id="fake_store",
            store_name="Fake In-Memory Store",
            implementation_version="1.0.0",
            supported_distance_metrics=("cosine",),
            supports_metadata_filtering=False,
            supports_batch_insert=True,
            supports_batch_delete=True,
            maximum_batch_size=100,
        )

    @property
    def info(self) -> StoreInfo:
        return self._info

    def store(self, embedding: Embedding) -> StorageResult:
        self._store[embedding.id] = embedding
        return StorageResult(stored_count=1, collection_name="fake", metadata=None)

    def store_batch(self, embeddings: EmbeddingCollection) -> StorageResult:
        for emb in embeddings.embeddings:
            self._store[emb.id] = emb
        return StorageResult(
            stored_count=len(embeddings.embeddings), collection_name="fake", metadata=None
        )

    def delete(self, embedding_id: str) -> None:
        self._store.pop(embedding_id, None)

    def delete_batch(self, embedding_ids: tuple[str, ...]) -> None:
        for eid in embedding_ids:
            self._store.pop(eid, None)

    def search(self, vector: EmbeddingVector, *, limit: int = 10) -> tuple[SearchResult, ...]:
        _ = vector
        results = [
            SearchResult(embedding=emb, similarity_score=0.99) for emb in self._store.values()
        ]
        return tuple(results[:limit])

    def count(self) -> int:
        return len(self._store)

    def clear(self) -> None:
        self._store.clear()


def test_store_info_validation() -> None:
    with pytest.raises(StoreConfigurationError):
        StoreInfo(
            store_id="invalid",
            store_name="Invalid Store",
            implementation_version="1.0",
            supported_distance_metrics=("cosine",),
            supports_metadata_filtering=False,
            supports_batch_insert=False,
            supports_batch_delete=False,
            maximum_batch_size=0,
        )


def test_abstract_vector_store_implementation() -> None:
    store = FakeVectorStore()
    assert store.info.store_id == "fake_store"
    assert store.count() == 0

    vector = EmbeddingVector(values=(1.0, 2.0), dimension=2)
    meta = EmbeddingMetadata(
        provider="test",
        model_name="test",
        model_version="1",
        embedding_version="1",
        dimensions=2,
        normalized=False,
        created_at=datetime.now(UTC),
    )
    stats = EmbeddingStatistics(
        processing_time_ms=10.0,
    )
    emb = Embedding(
        id="e1",
        chunk_id="c1",
        vector=vector,
        metadata=meta,
        statistics=stats,
        created_at=datetime.now(UTC),
    )

    store.store(emb)
    assert store.count() == 1

    results = store.search(vector)
    assert len(results) == 1
    assert results[0].similarity_score == 0.99
    assert results[0].embedding.id == "e1"

    store.clear()
    assert store.count() == 0
