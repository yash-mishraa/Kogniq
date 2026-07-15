from datetime import UTC, datetime

import pytest
from embedding.collection import EmbeddingCollection
from embedding.embedding import Embedding
from embedding.metadata import EmbeddingMetadata
from embedding.providers.interfaces import AbstractEmbeddingProvider
from embedding.providers.provider_info import ProviderInfo
from embedding.statistics import EmbeddingStatistics
from embedding.vector import EmbeddingVector
from embedding.vectorstores.interfaces import AbstractVectorStore
from embedding.vectorstores.search_result import SearchResult
from embedding.vectorstores.storage_result import StorageResult
from embedding.vectorstores.store_info import StoreInfo
from retrieval.config import RetrieverConfig
from retrieval.exceptions import RetrievalError
from retrieval.models import RetrievalQuery
from retrieval.semantic_retriever import SemanticRetriever

from content.chunking import Chunk, ChunkCollection


class FakeEmbeddingProvider(AbstractEmbeddingProvider):
    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            provider_id="fake",
            provider_name="Fake Provider",
            model_name="fake_model",
            model_version="1",
            embedding_version="1",
            dimensions=3,
            supports_batch_generation=True,
            supports_async_generation=False,
            maximum_batch_size=10,
            maximum_tokens=100,
            normalized_output=True,
        )

    def generate(self, chunk: Chunk) -> Embedding:
        return Embedding(
            id=f"e_{chunk.id}",
            chunk_id=chunk.id,
            vector=EmbeddingVector(values=(1.0, 0.0, 0.0), dimension=3),
            metadata=EmbeddingMetadata(
                provider="fake_provider",
                model_name="fake_model",
                model_version="1",
                embedding_version="1",
                dimensions=3,
                normalized=True,
                created_at=datetime.now(UTC),
            ),
            statistics=EmbeddingStatistics(processing_time_ms=1.0),
            created_at=datetime.now(UTC),
        )

    def generate_batch(self, chunks: ChunkCollection) -> EmbeddingCollection:
        return EmbeddingCollection(
            embeddings=tuple(self.generate(c) for c in chunks.chunks),
        )


class FakeVectorStore(AbstractVectorStore):
    def __init__(self, mock_results: tuple[SearchResult, ...]) -> None:
        self.mock_results = mock_results

    @property
    def info(self) -> StoreInfo:
        return StoreInfo(
            store_id="fake_store",
            store_name="Fake Store",
            implementation_version="1",
            supported_distance_metrics=("cosine",),
            supports_metadata_filtering=False,
            supports_batch_insert=False,
            supports_batch_delete=False,
            maximum_batch_size=10,
        )

    def store(self, embedding: Embedding) -> StorageResult:
        _ = embedding
        from embedding.vectorstores.storage_result import StorageResult
        return StorageResult(stored_count=1, collection_name="fake", metadata=None)

    def store_batch(self, embeddings: EmbeddingCollection) -> StorageResult:
        from embedding.vectorstores.storage_result import StorageResult
        return StorageResult(
            stored_count=len(embeddings.embeddings), collection_name="fake", metadata=None
        )

    def search(self, _vector: EmbeddingVector, *, limit: int = 10) -> tuple[SearchResult, ...]:
        return self.mock_results[:limit]

    def delete(self, embedding_id: str) -> None:
        pass

    def delete_batch(self, embedding_ids: tuple[str, ...]) -> None:
        pass

    def count(self) -> int:
        return len(self.mock_results)

    def clear(self) -> None:
        pass


def create_fake_search_result(score: float, chunk_id: str) -> SearchResult:
    emb = Embedding(
        id=f"e_{chunk_id}",
        chunk_id=chunk_id,
        vector=EmbeddingVector(values=(1.0, 0.0, 0.0), dimension=3),
        metadata=EmbeddingMetadata(
            provider="fake_provider",
            model_name="fake_model",
            model_version="1",
            embedding_version="1",
            dimensions=3,
            normalized=True,
            created_at=datetime.now(UTC),
        ),
        statistics=EmbeddingStatistics(processing_time_ms=1.0),
        created_at=datetime.now(UTC),
    )
    return SearchResult(embedding=emb, similarity_score=score)


def test_semantic_retriever_success() -> None:
    # Arrange
    results = (
        create_fake_search_result(0.9, "chunk_1"),
        create_fake_search_result(0.8, "chunk_2"),
        create_fake_search_result(0.2, "chunk_3"),  # Below threshold
    )
    
    provider = FakeEmbeddingProvider()
    store = FakeVectorStore(mock_results=results)
    
    # We set a threshold of 0.5 to filter out chunk_3
    config = RetrieverConfig(default_top_k=5, similarity_threshold=0.5)
    retriever = SemanticRetriever(embedding_provider=provider, vector_store=store, config=config)
    
    query = RetrievalQuery(text="test query", top_k=2)

    # Act
    retrievals = retriever.retrieve(query)

    # Assert
    assert len(retrievals) == 2
    
    assert retrievals[0].query_text == "test query"
    assert retrievals[0].chunk_id == "chunk_1"
    assert retrievals[0].similarity_score == 0.9
    assert retrievals[0].provider == "fake_provider"
    assert retrievals[0].model == "fake_model"

    assert retrievals[1].chunk_id == "chunk_2"
    assert retrievals[1].similarity_score == 0.8


class FailingEmbeddingProvider(FakeEmbeddingProvider):
    def generate(self, _chunk: Chunk) -> Embedding:
        raise ValueError("Provider failure")


def test_semantic_retriever_failure_wrapping() -> None:
    provider = FailingEmbeddingProvider()
    store = FakeVectorStore(mock_results=())
    retriever = SemanticRetriever(embedding_provider=provider, vector_store=store)
    
    query = RetrievalQuery(text="fail")
    
    with pytest.raises(RetrievalError, match="Failed to execute semantic retrieval"):
        retriever.retrieve(query)
