import logging
from datetime import UTC, datetime

from embedding.providers.interfaces import AbstractEmbeddingProvider
from embedding.vectorstores.interfaces import AbstractVectorStore

from content.chunking import Chunk, ChunkMetadata, ChunkStatistics
from retrieval.config import RetrieverConfig
from retrieval.exceptions import RetrievalError
from retrieval.interfaces import AbstractRetriever
from retrieval.models import RetrievalQuery, RetrievalResult

logger = logging.getLogger(__name__)


class SemanticRetriever(AbstractRetriever):
    """
    Canonical orchestration layer for semantic retrieval.
    Composes an embedding provider and a vector store to retrieve semantic results.
    Does not implement filtering, reranking, or LLM logic.
    """

    def __init__(
        self,
        embedding_provider: AbstractEmbeddingProvider,
        vector_store: AbstractVectorStore,
        config: RetrieverConfig | None = None,
    ) -> None:
        self._provider = embedding_provider
        self._store = vector_store
        self._config = config or RetrieverConfig()

    def retrieve(self, query: RetrievalQuery) -> tuple[RetrievalResult, ...]:
        """
        Executes semantic retrieval.

        Orchestration flow:
        1. query text -> embedding provider -> embedding vector
        2. embedding vector -> vector store -> search results
        3. search results -> retrieval results
        """
        try:
            # 1. Create a temporary chunk for the query text since EmbeddingProviders expect Chunks
            query_chunk = Chunk(
                id=query.query_id,
                document_id="query",
                chunk_index=0,
                text=query.text,
                metadata=ChunkMetadata(
                    processor="retrieval",
                    document_version="1",
                    source="query",
                    checksum="query",
                ),
                statistics=ChunkStatistics(
                    character_count=len(query.text),
                    line_count=1,
                    word_count=len(query.text.split()),
                    estimated_tokens=len(query.text) // 4,
                    processing_timestamp=datetime.now(UTC),
                    confidence=1.0,
                ),
                created_at=datetime.now(UTC),
            )

            # 2. Generate query embedding
            query_embedding_obj = self._provider.generate(query_chunk)
            query_embedding = query_embedding_obj.vector

            # 3. Search vector store
            limit = query.top_k or self._config.default_top_k
            search_results = self._store.search(query_embedding, limit=limit)

            # 4. Map to RetrievalResult domain models
            retrieval_results = []
            for sr in search_results:
                if sr.similarity_score < self._config.similarity_threshold:
                    continue

                emb = sr.embedding
                rr = RetrievalResult(
                    query_id=query.query_id,
                    query_text=query.text,
                    embedding_id=emb.id,
                    chunk_id=emb.chunk_id,
                    similarity_score=sr.similarity_score,
                    provider=emb.metadata.provider,
                    model=emb.metadata.model_name,
                )
                retrieval_results.append(rr)

            return tuple(retrieval_results)

        except Exception as e:
            # Wrap any downstream errors securely
            msg = f"Failed to execute semantic retrieval for query {query.query_id}: {e}"
            logger.error(msg)
            raise RetrievalError(msg) from e
