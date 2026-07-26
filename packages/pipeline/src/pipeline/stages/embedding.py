from typing import Any

from embedding.providers.interfaces import AbstractEmbeddingProvider
from embedding.vectorstores.interfaces import AbstractVectorStore

from content.chunking.collection import ChunkCollection
from pipeline.interfaces import PipelineContext, RetryPolicy, StageResult


class EmbeddingRetryPolicy:
    @property
    def max_retries(self) -> int:
        return 2

    @property
    def delay_seconds(self) -> int:
        return 2


class EmbeddingStageResult:
    def __init__(self, success: bool, data: dict[str, Any], error: str | None = None) -> None:
        self._success = success
        self._data = data
        self._error = error

    @property
    def success(self) -> bool:
        return self._success

    @property
    def data(self) -> dict[str, Any]:
        return self._data

    @property
    def error(self) -> str | None:
        return self._error


class EmbeddingStage:
    def __init__(
        self,
        provider: AbstractEmbeddingProvider,
        vector_store: AbstractVectorStore,
    ) -> None:
        self.provider = provider
        self.vector_store = vector_store
        self._retry_policy = EmbeddingRetryPolicy()

    @property
    def stage_name(self) -> str:
        return "Embedding"

    async def can_skip(self, context: PipelineContext) -> bool:
        # In this option (Option D), we do chunk-level deduplication inside the provider,
        # so we don't skip the stage at a document level unless chunk_collection is empty.
        chunk_collection: ChunkCollection | None = context.get("chunk_collection")
        return not chunk_collection or not chunk_collection.chunks

    async def execute(self, context: PipelineContext) -> StageResult:
        chunk_collection: ChunkCollection | None = context.get("chunk_collection")
        if not chunk_collection:
            return EmbeddingStageResult(False, {}, "No chunk_collection provided in context")

        if not chunk_collection.chunks:
            return EmbeddingStageResult(True, {"message": "No chunks to embed"})

        try:
            # 1. Generate embeddings using generate_batch (handles hashing and caching internally)
            embeddings = self.provider.generate_batch(chunk_collection)
            
            # 2. Store in vector database
            storage_result = self.vector_store.store_batch(embeddings)

            return EmbeddingStageResult(
                success=True,
                data={
                    "total_embeddings": len(embeddings.embeddings),
                    "stored_count": storage_result.stored_count,
                    "provider": self.provider.info.provider_name,
                    "vector_store": self.vector_store.info.store_name,
                },
            )
        except Exception as e:
            return EmbeddingStageResult(False, {}, str(e))

    def retry_policy(self) -> RetryPolicy:
        return self._retry_policy
