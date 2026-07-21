import logging
import uuid
from typing import Any

from qdrant_client.http import models

from embedding.collection import EmbeddingCollection
from embedding.embedding import Embedding
from embedding.vector import EmbeddingVector
from embedding.vectorstores.exceptions import DeletionError, SearchError, StorageError
from embedding.vectorstores.interfaces import AbstractVectorStore
from embedding.vectorstores.search_result import SearchResult
from embedding.vectorstores.storage_result import StorageResult
from embedding.vectorstores.store_info import StoreInfo

from .client import QdrantClientManager

logger = logging.getLogger(__name__)


def _generate_uuid_from_string(id_str: str) -> str:
    """Generates a stable UUID5 from an arbitrary string ID."""
    return str(uuid.uuid5(uuid.NAMESPACE_OID, id_str))


class QdrantVectorStore(AbstractVectorStore):
    """
    Concrete implementation of AbstractVectorStore using Qdrant.
    This encapsulates all Qdrant-specific logic to prevent framework leakage.
    """

    def __init__(
        self, manager: QdrantClientManager, collection_name: str = "kogniq_documents"
    ) -> None:
        self.manager = manager
        self.collection_name = collection_name
        self._initialized_dimensions: int | None = None

    @property
    def info(self) -> StoreInfo:
        return StoreInfo(
            store_id="qdrant",
            store_name="Qdrant",
            implementation_version="1.0",
            supported_distance_metrics=("cosine",),
            supports_metadata_filtering=True,
            supports_batch_insert=True,
            supports_batch_delete=True,
            maximum_batch_size=1000,
        )

    def _ensure_collection_for_embedding(self, dimension: int) -> None:
        if self._initialized_dimensions != dimension:
            self.manager.ensure_collection(
                collection_name=self.collection_name,
                vector_size=dimension,
                distance=models.Distance.COSINE,
            )
            self._initialized_dimensions = dimension

    def _extract_payload(self, embedding: Embedding) -> dict[str, Any]:
        """Convert Embedding domain metadata into flat dictionary for Qdrant payload."""
        payload = {
            "original_id": embedding.id,  # store the actual ID since Qdrant uses UUID
            "chunk_id": embedding.chunk_id,
            "provider": embedding.metadata.provider,
            "model_name": embedding.metadata.model_name,
            "embedding_version": embedding.metadata.embedding_version,
            "dimensions": embedding.metadata.dimensions,
            "normalized": embedding.metadata.normalized,
        }

        if embedding.metadata.language is not None:
            payload["language"] = embedding.metadata.language

        return payload

    def store(self, embedding: Embedding) -> StorageResult:
        self._ensure_collection_for_embedding(embedding.vector.dimension)
        client = self.manager.connect()
        try:
            point_id = _generate_uuid_from_string(embedding.id)
            client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=point_id,
                        vector=list(embedding.vector.values),
                        payload=self._extract_payload(embedding),
                    )
                ],
            )
            return StorageResult(
                stored_count=1,
                collection_name=self.collection_name,
                metadata={"provider": "qdrant", "ids": [embedding.id]},
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
                collection_name=self.collection_name,
                metadata={"provider": "qdrant", "ids": []},
            )

        self._ensure_collection_for_embedding(embeddings.embeddings[0].vector.dimension)
        client = self.manager.connect()
        try:
            points = []
            ids = []
            for emb in embeddings.embeddings:
                points.append(
                    models.PointStruct(
                        id=_generate_uuid_from_string(emb.id),
                        vector=list(emb.vector.values),
                        payload=self._extract_payload(emb),
                    )
                )
                ids.append(emb.id)

            client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
            return StorageResult(
                stored_count=len(ids),
                collection_name=self.collection_name,
                metadata={"provider": "qdrant", "ids": ids},
            )
        except Exception as e:
            raise StorageError(f"Failed to store batch of embeddings: {e}") from e

    def search(self, vector: EmbeddingVector, *, limit: int = 10) -> tuple[SearchResult, ...]:
        # Fast exit if we never initialized (collection might not exist locally in memory tests)
        # But Qdrant client will throw if we search missing collection, so ensure it.
        # However, to ensure it we need the dimension.
        self._ensure_collection_for_embedding(vector.dimension)
        client = self.manager.connect()
        try:
            results = client.query_points(
                collection_name=self.collection_name,
                query=list(vector.values),
                limit=limit,
                with_payload=True,
                with_vectors=True,
            ).points

            if not results:
                return ()

            search_results = []
            for hit in results:
                payload = hit.payload or {}
                # Qdrant cosine distance score is directly cosine similarity ([-1, 1]).
                # We normalize it to [0.0, 1.0] if we want, or just clamp to [0.0, 1.0]
                # Actually, Qdrant cosine similarity is natively [0.0, 1.0] for positive vectors,
                # but standard cosine similarity is [-1, 1]. Score 1.0 is exact match.
                similarity = max(0.0, min(1.0, hit.score))

                from datetime import UTC, datetime

                from embedding.metadata import EmbeddingMetadata
                from embedding.statistics import EmbeddingStatistics

                metadata = EmbeddingMetadata(
                    provider=payload["provider"],
                    model_name=payload["model_name"],
                    model_version="unknown",
                    embedding_version=payload["embedding_version"],
                    dimensions=payload["dimensions"],
                    normalized=payload.get("normalized", False),
                    language=payload.get("language"),
                    created_at=datetime.now(UTC),
                )

                stats = EmbeddingStatistics(
                    processing_time_ms=0.0,
                )

                from typing import cast
                # Recover vector values
                vec_values_raw = hit.vector if hit.vector is not None else []
                if isinstance(vec_values_raw, dict):
                    # In some qdrant versions, named vectors might return a dict. 
                    # Assuming default unnamed vector:
                    vec_values = vec_values_raw.get("", [])
                else:
                    vec_values = vec_values_raw
                
                # Make mypy happy by ensuring we pass a sequence of floats
                if (
                    isinstance(vec_values, list)
                    and len(vec_values) > 0
                    and isinstance(vec_values[0], list)
                ):
                    final_values = vec_values[0]
                else:
                    final_values = cast(list[float], vec_values)

                recovered_emb = Embedding(
                    id=payload["original_id"],
                    chunk_id=payload["chunk_id"],
                    vector=EmbeddingVector(
                        values=tuple(final_values), dimension=payload["dimensions"]
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
        client = self.manager.connect()
        try:
            client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=[_generate_uuid_from_string(embedding_id)]
                ),
            )
        except Exception as e:
            raise DeletionError(f"Failed to delete embedding {embedding_id}: {e}") from e

    def delete_batch(self, embedding_ids: tuple[str, ...]) -> None:
        if not embedding_ids:
            return
        client = self.manager.connect()
        try:
            client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=[_generate_uuid_from_string(eid) for eid in embedding_ids]
                ),
            )
        except Exception as e:
            raise DeletionError(f"Failed to delete batch: {e}") from e

    def count(self) -> int:
        client = self.manager.connect()
        try:
            if not client.collection_exists(collection_name=self.collection_name):
                return 0
            return client.count(collection_name=self.collection_name).count
        except Exception as e:
            raise StorageError(f"Failed to count embeddings: {e}") from e

    def clear(self) -> None:
        client = self.manager.connect()
        try:
            if client.collection_exists(collection_name=self.collection_name):
                client.delete_collection(collection_name=self.collection_name)
            self._initialized_dimensions = None
        except Exception as e:
            raise DeletionError(f"Failed to clear vector store: {e}") from e
