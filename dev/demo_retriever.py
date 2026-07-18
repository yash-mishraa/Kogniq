import sys
from datetime import UTC, datetime
from pathlib import Path

# Fix paths to run easily without installation
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "embedding" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "retrieval" / "src"))

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
from retrieval.models import RetrievalQuery
from retrieval.semantic_retriever import SemanticRetriever

from content.chunking import Chunk, ChunkCollection


class DemoEmbeddingProvider(AbstractEmbeddingProvider):
    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            provider_id="demo_provider",
            provider_name="Demo Provider",
            model_name="demo_model",
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
        print(f"  [DemoEmbeddingProvider] Generating vector for chunk '{chunk.text}'")
        return Embedding(
            id=f"e_{chunk.id}",
            chunk_id=chunk.id,
            vector=EmbeddingVector(values=(0.8, 0.1, 0.1), dimension=3),
            metadata=EmbeddingMetadata(
                provider="demo_provider",
                model_name="demo_model",
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


class DemoVectorStore(AbstractVectorStore):
    @property
    def info(self) -> StoreInfo:
        return StoreInfo(
            store_id="demo_store",
            store_name="Demo Store",
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

    def search(self, vector: EmbeddingVector, *, limit: int = 10) -> tuple[SearchResult, ...]:
        print(f"  [DemoVectorStore] Searching for vector {vector.values} (limit={limit})")
        # Return fake matches
        emb1 = Embedding(
            id="e_1",
            chunk_id="c_1",
            vector=EmbeddingVector(values=(0.8, 0.1, 0.1), dimension=3),
            metadata=EmbeddingMetadata(
                provider="demo_provider",
                model_name="demo_model",
                model_version="1",
                embedding_version="1",
                dimensions=3,
                normalized=True,
                created_at=datetime.now(UTC),
            ),
            statistics=EmbeddingStatistics(processing_time_ms=1.0),
            created_at=datetime.now(UTC),
        )
        return (SearchResult(embedding=emb1, similarity_score=0.95),)

    def delete(self, embedding_id: str) -> None:
        pass

    def delete_batch(self, embedding_ids: tuple[str, ...]) -> None:
        pass

    def count(self) -> int:
        return 1

    def clear(self) -> None:
        pass


def main() -> None:
    print("Initializing Demo Components...")
    provider = DemoEmbeddingProvider()
    store = DemoVectorStore()

    config = RetrieverConfig(default_top_k=5, similarity_threshold=0.5)
    retriever = SemanticRetriever(embedding_provider=provider, vector_store=store, config=config)

    query_text = "What is the capital of France?"
    print(f"\nExecuting query: '{query_text}'")
    query = RetrievalQuery(text=query_text, top_k=3)

    results = retriever.retrieve(query)

    print("\nRetrieval Results:")
    for rr in results:
        print("-" * 40)
        print(f"Query ID     : {rr.query_id}")
        print(f"Query Text   : {rr.query_text}")
        print(f"Similarity   : {rr.similarity_score:.4f}")
        print(f"Chunk ID     : {rr.chunk_id}")
        print(f"Provider     : {rr.provider}")
        print(f"Model        : {rr.model}")


if __name__ == "__main__":
    main()
