from fastapi import APIRouter, Depends, Header

from application.retrieval.commands import RetrievalCommand
from application.retrieval.retrieve import RetrieveUseCase
from backend.dependencies import get_retrieve_use_case
from backend.schemas.retrieval import RetrievalRequest, RetrievalResponse, RetrievalResultItem

retrieval_router = APIRouter(prefix="/retrieval", tags=["retrieval"])


@retrieval_router.post("/search", response_model=RetrievalResponse)
async def semantic_search(
    request: RetrievalRequest,
    x_user_id: str = Header("demo-user-1", alias="X-User-Id"),
    use_case: RetrieveUseCase = Depends(get_retrieve_use_case),  # noqa: B008
) -> RetrievalResponse:
    """
    Executes a semantic search over a specific processed document.
    Returns ranked chunks with similarity scores.
    """
    command = RetrievalCommand(
        user_id=x_user_id,
        query=request.query,
        document_id=request.document_id,
        top_k=request.top_k,
        minimum_similarity=getattr(request, "minimum_similarity", None),
    )
    result = await use_case.execute(command)
    return RetrievalResponse(
        status=result.status,
        query=result.query,
        document_id=result.document_id,
        total_results=result.total_results,
        processing_time_ms=result.processing_time_ms,
        warnings=result.warnings,
        results=[
            RetrievalResultItem(
                chunk_id=r.chunk_id,
                similarity_score=r.score,
                chunk_text=r.content,
                chunk_index=r.chunk_index,
                metadata=r.metadata,
                document_id=r.document_id,
            )
            for r in result.results
        ],
    )
