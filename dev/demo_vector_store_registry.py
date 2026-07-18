import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "embedding" / "src"))

from embedding.collection import EmbeddingCollection
from embedding.embedding import Embedding
from embedding.vector import EmbeddingVector
from embedding.vectorstores import (
    AbstractVectorStore,
    SearchResult,
    StorageResult,
    StoreInfo,
    VectorStoreRegistry,
)


class MockPinecone(AbstractVectorStore):
    @property
    def info(self) -> StoreInfo:
        return StoreInfo(
            store_id="pinecone",
            store_name="Mock Pinecone Database",
            implementation_version="1.0",
            supported_distance_metrics=("cosine", "euclidean", "dot_product"),
            supports_metadata_filtering=True,
            supports_batch_insert=True,
            supports_batch_delete=True,
            maximum_batch_size=1000,
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

    def delete(self, embedding_id: str) -> None:
        pass

    def delete_batch(self, embedding_ids: tuple[str, ...]) -> None:
        pass

    def search(self, vector: EmbeddingVector, *, limit: int = 10) -> tuple[SearchResult, ...]:
        _ = vector
        _ = limit
        return ()

    def count(self) -> int:
        return 0

    def clear(self) -> None:
        pass


class MockQdrant(AbstractVectorStore):
    @property
    def info(self) -> StoreInfo:
        return StoreInfo(
            store_id="qdrant",
            store_name="Mock Qdrant Database",
            implementation_version="1.1",
            supported_distance_metrics=("cosine", "euclidean", "dot_product", "manhattan"),
            supports_metadata_filtering=True,
            supports_batch_insert=True,
            supports_batch_delete=True,
            maximum_batch_size=5000,
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

    def delete(self, embedding_id: str) -> None:
        pass

    def delete_batch(self, embedding_ids: tuple[str, ...]) -> None:
        pass

    def search(self, vector: EmbeddingVector, *, limit: int = 10) -> tuple[SearchResult, ...]:
        _ = vector
        _ = limit
        return ()

    def count(self) -> int:
        return 0

    def clear(self) -> None:
        pass


def main() -> None:
    print("Initializing Vector Store Registry...")
    registry = VectorStoreRegistry()

    registry.register(MockPinecone())
    registry.register(MockQdrant())

    print(f"\nRegistry Count: {registry.store_count()}")

    print("\nAvailable Stores:")
    for store in registry.available_stores():
        info = store.info
        print("----------------------------------------")
        print(f"Store ID   : {info.store_id}")
        print(f"Store Name : {info.store_name}")
        print(f"Metrics    : {', '.join(info.supported_distance_metrics)}")
        print(f"Metadata Filtering: {'Yes' if info.supports_metadata_filtering else 'No'}")


if __name__ == "__main__":
    main()
