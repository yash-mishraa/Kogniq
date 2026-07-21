import asyncio
import logging
import time

from backend.core.exceptions import BackendError
from backend.schemas.retrieval import RetrievalRequest, RetrievalResponse, RetrievalResultItem
from persistence.uow_factory import AbstractUnitOfWorkFactory
from retrieval.exceptions import RetrievalError
from retrieval.interfaces import AbstractRetriever
from retrieval.models import RetrievalQuery

logger = logging.getLogger(__name__)


class RetrievalService:
    """
    Application service orchestrating semantic retrieval.
    Operates strictly via domain interfaces (AbstractRetriever, AbstractChunkRepository).
    """

    def __init__(
        self,
        retriever: AbstractRetriever,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self.retriever = retriever
        self.uow_factory = uow_factory

    async def search(self, request: RetrievalRequest) -> RetrievalResponse:
        start_time = time.perf_counter()
        warnings: list[str] = []

        # 1. Obtain document context (chunks) from repository
        # to ensure doc exists and we can hydrate
        with self.uow_factory.create() as uow:
            chunk_collection = await uow.chunks.get_by_document(request.document_id)

        if not chunk_collection or not chunk_collection.chunks:
            raise BackendError(
                code="document_not_found",
                message=f"No chunks found for document {request.document_id}",
                status_code=404,
            )

        # Map chunk ID to actual chunk for O(1) hydration
        chunk_map = {c.id: c for c in chunk_collection.chunks}

        # 2. Build semantic query
        # Since we use a single collection, we can pass document_id in filters
        # so we only match this doc.
        # Note: If the vector store doesn't support metadata filtering by document_id
        # we will fetch top_k results globally and then filter them down to this document.
        # We fetch a larger limit to allow filtering post-retrieval.
        query = RetrievalQuery(
            text=request.query,
            top_k=request.top_k * 5,  # Fetch more to allow for document_id filtering
            filters={"document_id": request.document_id},
        )

        # 3. Invoke retriever (runs in thread pool to avoid blocking event loop)
        try:
            results = await asyncio.to_thread(self.retriever.retrieve, query)
        except RetrievalError as e:
            logger.error(f"Retriever error: {e}")
            raise BackendError(
                code="retrieval_failed",
                message=f"Semantic retrieval failed: {e}",
                status_code=500,
            ) from e
        except Exception as e:
            logger.error(f"Unexpected retrieval error: {e}")
            raise BackendError(
                code="retrieval_failed",
                message="An unexpected error occurred during semantic retrieval.",
                status_code=500,
            ) from e

        # 4. Filter, Hydrate and map results
        mapped_results: list[RetrievalResultItem] = []
        for r in results:
            if r.chunk_id not in chunk_map:
                # The retriever returned a chunk ID that doesn't exist in the current document.
                # It either belongs to a different document (since we share the Chroma collection)
                # or it was deleted from the repo but not from Chroma.
                continue

            # Apply minimum similarity threshold if requested
            if (
                request.minimum_similarity is not None
                and r.similarity_score < request.minimum_similarity
            ):
                continue

            chunk = chunk_map[r.chunk_id]

            # Extract safe metadata
            safe_meta = {
                "processor": chunk.metadata.processor,
                "source": chunk.metadata.source,
            }

            item = RetrievalResultItem(
                chunk_id=r.chunk_id,
                similarity_score=r.similarity_score,
                chunk_text=chunk.text,
                chunk_index=chunk.chunk_index,
                document_id=request.document_id,
                metadata=safe_meta,
            )
            mapped_results.append(item)

            if len(mapped_results) >= request.top_k:
                break

        if len(results) > len(mapped_results) and len(mapped_results) < request.top_k:
            msg = "Results were found but filtered out (mismatch or threshold)."
            warnings.append(msg)

        end_time = time.perf_counter()
        processing_time_ms = (end_time - start_time) * 1000.0

        return RetrievalResponse(
            query=request.query,
            document_id=request.document_id,
            total_results=len(mapped_results),
            results=mapped_results,
            processing_time_ms=processing_time_ms,
            warnings=warnings,
        )
