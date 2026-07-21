import logging
from typing import Any

try:
    import chromadb
    from chromadb.api import ClientAPI
except ImportError as e:
    raise ImportError("ChromaDB is not installed. Please run `uv sync` to install it.") from e

from embedding.collection import EmbeddingCollection
from embedding.embedding import Embedding
from embedding.vector import EmbeddingVector
from embedding.vectorstores.exceptions import DeletionError, SearchError, StorageError
from embedding.vectorstores.interfaces import AbstractVectorStore
from embedding.vectorstores.search_result import SearchResult
from embedding.vectorstores.storage_result import StorageResult
from embedding.vectorstores.store_info import StoreInfo

logger = logging.getLogger(__name__)


class ChromaVectorStore(AbstractVectorStore):
    """
    Concrete implementation of AbstractVectorStore using ChromaDB.
    This encapsulates all ChromaDB-specific logic to prevent framework leakage.
    """

    def __init__(
        self, collection_name: str = "kogniq", persist_directory: str | None = None
    ) -> None:
        self._collection_name = collection_name
        self._persist_directory = persist_directory
        self._client: ClientAPI | None = None
        self._collection: Any | None = None

    @property
    def info(self) -> StoreInfo:
        return StoreInfo(
            store_id="chroma",
            store_name="ChromaDB",
            implementation_version="1.0",
            supported_distance_metrics=("cosine",),
            supports_metadata_filtering=True,
            supports_batch_insert=True,
            supports_batch_delete=True,
            maximum_batch_size=1000,
        )

    def _get_collection(self) -> Any:
        if self._collection is not None:
            return self._collection

        try:
            if self._persist_directory is not None:
                logger.info(f"Initializing persistent ChromaDB at {self._persist_directory}")
                self._client = chromadb.PersistentClient(path=self._persist_directory)
            else:
                logger.info("Initializing ephemeral ChromaDB")
                self._client = chromadb.EphemeralClient()

            # We explicitly enforce cosine similarity as per store info
            self._collection = self._client.get_or_create_collection(
                name=self._collection_name, metadata={"hnsw:space": "cosine"}
            )
            return self._collection
        except Exception as e:
            raise StorageError(f"Failed to initialize ChromaDB collection: {e}") from e

    def _extract_metadata(self, embedding: Embedding) -> dict[str, Any]:
        """Convert Embedding domain metadata into flat dictionary for Chroma."""
        meta = {
            "chunk_id": embedding.chunk_id,
            "provider": embedding.metadata.provider,
            "model_name": embedding.metadata.model_name,
            "embedding_version": embedding.metadata.embedding_version,
            "dimensions": embedding.metadata.dimensions,
            "normalized": embedding.metadata.normalized,
        }

        if embedding.metadata.language is not None:
            meta["language"] = embedding.metadata.language

        return meta

    def store(self, embedding: Embedding) -> StorageResult:
        collection = self._get_collection()
        try:
            collection.add(
                ids=[embedding.id],
                embeddings=[list(embedding.vector.values)],
                metadatas=[self._extract_metadata(embedding)],
            )
            return StorageResult(
                stored_count=1,
                collection_name=self._collection_name,
                metadata={"provider": "chroma", "ids": [embedding.id]},
            )
        except Exception as e:
            raise StorageError(f"Failed to store embedding {embedding.id}: {e}") from e

    def store_batch(self, embeddings: EmbeddingCollection) -> StorageResult:
        if len(embeddings.embeddings) > self.info.maximum_batch_size:
            msg = (
                f"Batch size {len(embeddings.embeddings)} exceeds "
                f"maximum {self.info.maximum_batch_size}"
            )
            raise StorageError(msg)

        if len(embeddings.embeddings) == 0:
            return StorageResult(
                stored_count=0,
                collection_name=self._collection_name,
                metadata={"provider": "chroma", "ids": []},
            )

        collection = self._get_collection()
        try:
            ids = [emb.id for emb in embeddings.embeddings]
            vectors = [list(emb.vector.values) for emb in embeddings.embeddings]
            metadatas = [self._extract_metadata(emb) for emb in embeddings.embeddings]

            collection.add(ids=ids, embeddings=vectors, metadatas=metadatas)
            return StorageResult(
                stored_count=len(ids),
                collection_name=self._collection_name,
                metadata={"provider": "chroma", "ids": ids},
            )
        except Exception as e:
            raise StorageError(f"Failed to store batch of embeddings: {e}") from e

    def search(self, vector: EmbeddingVector, *, limit: int = 10) -> tuple[SearchResult, ...]:
        collection = self._get_collection()
        try:
            # Query returns distances. For cosine space, Chroma returns cosine distance.
            # Cosine distance = 1 - cosine similarity.
            # We want similarity_score from 0.0 to 1.0, so we do 1.0 - distance.
            results = collection.query(
                query_embeddings=[list(vector.values)],
                n_results=limit,
                include=["embeddings", "metadatas", "distances"],
            )

            if not results["ids"] or not results["ids"][0]:
                return ()

            search_results = []
            for i in range(len(results["ids"][0])):
                eid = results["ids"][0][i]
                emb_values = results["embeddings"][0][i]
                meta_dict = results["metadatas"][0][i]
                distance = results["distances"][0][i]

                # Chroma distance for cosine is (1 - cosine_similarity).
                # Normalizing to 0.0 - 1.0 range where 1.0 is exact match.
                # In case floating point error makes it negative or > 1, clamp it.
                similarity = 1.0 - distance
                similarity = max(0.0, min(1.0, similarity))

                from datetime import UTC, datetime

                from embedding.metadata import EmbeddingMetadata
                from embedding.statistics import EmbeddingStatistics

                # Recover standard domain models
                metadata = EmbeddingMetadata(
                    provider=meta_dict["provider"],
                    model_name=meta_dict["model_name"],
                    model_version="unknown",  # We didn't serialize model_version, but wait...
                    embedding_version=meta_dict["embedding_version"],
                    dimensions=meta_dict["dimensions"],
                    normalized=meta_dict.get("normalized", False),
                    language=meta_dict.get("language"),
                    created_at=datetime.now(UTC),  # Fallback since we don't serialize this yet
                )

                # We need a dummy stats because we don't persist it.
                stats = EmbeddingStatistics(
                    processing_time_ms=0.0,
                )

                recovered_emb = Embedding(
                    id=eid,
                    chunk_id=meta_dict["chunk_id"],
                    vector=EmbeddingVector(
                        values=tuple(emb_values), dimension=meta_dict["dimensions"]
                    ),
                    metadata=metadata,
                    statistics=stats,
                    created_at=datetime.now(UTC),
                )

                search_results.append(
                    SearchResult(embedding=recovered_emb, similarity_score=similarity)
                )

            return tuple(search_results)

        except Exception as e:
            raise SearchError(f"Failed to execute similarity search: {e}") from e

    def delete(self, embedding_id: str) -> None:
        collection = self._get_collection()
        try:
            collection.delete(ids=[embedding_id])
        except Exception as e:
            raise DeletionError(f"Failed to delete embedding {embedding_id}: {e}") from e

    def delete_batch(self, embedding_ids: tuple[str, ...]) -> None:
        if not embedding_ids:
            return
        collection = self._get_collection()
        try:
            collection.delete(ids=list(embedding_ids))
        except Exception as e:
            raise DeletionError(f"Failed to delete batch: {e}") from e

    def count(self) -> int:
        collection = self._get_collection()
        try:
            return int(collection.count())
        except Exception as e:
            raise StorageError(f"Failed to count embeddings: {e}") from e

    def clear(self) -> None:
        if self._collection is None:
            return
        try:
            if self._client is not None:
                self._client.delete_collection(name=self._collection_name)
            self._collection = None
        except Exception as e:
            raise DeletionError(f"Failed to clear vector store: {e}") from e
