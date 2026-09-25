import asyncio
import logging
import re
import time

from backend.core.exceptions import BackendError
from backend.schemas.retrieval import RetrievalRequest, RetrievalResponse, RetrievalResultItem
from persistence.uow_factory import AbstractUnitOfWorkFactory
from retrieval.exceptions import RetrievalError
from retrieval.interfaces import AbstractRetriever
from retrieval.models import RetrievalQuery

logger = logging.getLogger(__name__)


def _extract_snippet(text: str, query: str) -> str:
    """Extracts 2-3 relevant sentences from the chunk text."""
    # Split text into sentences using basic punctuation logic
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if not sentences:
        return text

    query_terms = [t.lower() for t in query.split() if len(t) > 2]

    # 1. Search for query tokens
    if query_terms:
        for i, sentence in enumerate(sentences):
            lower_sentence = sentence.lower()
            if any(term in lower_sentence for term in query_terms):
                start = max(0, i - 1)
                end = min(len(sentences), i + 2)
                return " ".join(sentences[start:end])

    # 2. Otherwise return the beginning of the chunk (up to 3 sentences)
    return " ".join(sentences[:3])


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
        scope = "document" if request.document_id else "global"
        logger.info(
            "retrieval_started",
            extra={
                "scope": scope
            }
        )
        warnings: list[str] = []

        # 1. Verify document exists if document_id is provided
        authorized_document_ids = None
        user_id = getattr(request, "user_id", None)
        
        if request.document_id:
            with self.uow_factory.create() as uow:
                doc = await uow.documents.get(request.document_id)
                if not doc:
                    raise BackendError(
                        code="document_not_found",
                        message=f"Document '{request.document_id}' not found.",
                        status_code=404,
                    )
                if doc.user_id and doc.user_id != user_id:
                    raise BackendError(
                        code="unauthorized",
                        message="Not authorized to access this document",
                        status_code=403,
                    )
                authorized_document_ids = {request.document_id}
        else:
            if not user_id:
                raise BackendError(
                    code="unauthorized",
                    message="Global search requires an authenticated user.",
                    status_code=401,
                )
            with self.uow_factory.create() as uow:
                user_docs = await uow.documents.list(user_id=user_id)
                authorized_document_ids = {d.id for d in user_docs}

        # 2. Build semantic query
        filters = {}
        if request.document_id:
            filters["document_id"] = request.document_id
        elif user_id:
            # We add user_id filter to allow vector DBs that support it to pre-filter
            filters["user_id"] = user_id

        query = RetrievalQuery(
            text=request.query,
            # We fetch a larger limit for both global and document searches to allow post-retrieval filtering
            top_k=request.top_k * 5,
            filters=filters or None,
        )

        # 2. Invoke retriever (runs in thread pool to avoid blocking event loop)
        try:
            results = await asyncio.to_thread(self.retriever.retrieve, query)
        except RetrievalError as e:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error("retrieval_failed", extra={"duration_ms": duration_ms, "status": "failure", "failure_category": "retrieval_error", "scope": scope})
            raise BackendError(
                code="retrieval_failed",
                message=f"Semantic retrieval failed: {e}",
                status_code=500,
            ) from e
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error("retrieval_failed", extra={"duration_ms": duration_ms, "status": "failure", "failure_category": "unknown_error", "scope": scope})
            raise BackendError(
                code="retrieval_failed",
                message="An unexpected error occurred during semantic retrieval.",
                status_code=500,
            ) from e

        if not results:
            return RetrievalResponse(
                query=request.query,
                document_id=request.document_id or "global",
                total_results=0,
                results=[],
                processing_time_ms=(time.perf_counter() - start_time) * 1000.0,
                warnings=[],
            )

        # 3. Hydrate matching chunks from SQLite
        chunk_ids = [r.chunk_id for r in results]
        with self.uow_factory.create() as uow:
            hydrated_chunks = await uow.chunks.get_by_ids(chunk_ids)

        chunk_map = {c.id: c for c in hydrated_chunks}

        # 4. Filter and map results
        mapped_results: list[RetrievalResultItem] = []
        for r in results:
            if r.chunk_id not in chunk_map:
                # The retriever returned a chunk ID that doesn't exist in the current document.
                # It either belongs to a different document (since we share the Chroma collection)
                # or it was deleted from the repo but not from Chroma.
                continue
            
            chunk = chunk_map[r.chunk_id]
            
            # M10 Security: Strictly reject chunks not belonging to the authorized user's documents
            if authorized_document_ids is not None and chunk.document_id not in authorized_document_ids:
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
                "title": chunk.title,
                "section_title": chunk.section_title,
                "page_number": chunk.page_number,
            }

            item = RetrievalResultItem(
                chunk_id=r.chunk_id,
                similarity_score=r.similarity_score,
                chunk_text=_extract_snippet(chunk.text, request.query),
                chunk_index=chunk.chunk_index,
                document_id=chunk.document_id,
                metadata=safe_meta,
            )
            mapped_results.append(item)
            logger.info(
                f"Retrieved Result: doc_id={chunk.document_id}, "
                f"chunk_index={chunk.chunk_index}, "
                f"similarity={r.similarity_score:.4f}"
            )

            if len(mapped_results) >= request.top_k:
                break

        if len(results) > len(mapped_results) and len(mapped_results) < request.top_k:
            msg = "Results were found but filtered out (mismatch or threshold)."
            warnings.append(msg)

        end_time = time.perf_counter()
        processing_time_ms = (end_time - start_time) * 1000.0
        
        logger.info(
            "retrieval_completed",
            extra={
                "duration_ms": processing_time_ms,
                "result_count": len(mapped_results),
                "scope": scope,
                "status": "success",
            }
        )

        return RetrievalResponse(
            query=request.query,
            document_id=request.document_id or "global",
            total_results=len(mapped_results),
            results=mapped_results,
            processing_time_ms=processing_time_ms,
            warnings=warnings,
        )
