from backend.core.exceptions import BackendError
from backend.dependencies import get_retrieve_use_case
from backend.schemas.retrieval import RetrievalRequest, RetrievalResponse, RetrievalResultItem
from fastapi import APIRouter, Depends

from application.retrieval.commands import RetrievalCommand
from application.retrieval.retrieve import RetrieveUseCase
from apps.api.app.core.errors import APIError
from apps.api.app.dependencies.auth import CurrentUserDependency

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


@router.post("/search", response_model=RetrievalResponse)
async def semantic_search(
    request: RetrievalRequest,
    current_user: CurrentUserDependency,
    use_case: RetrieveUseCase = Depends(get_retrieve_use_case),  # noqa: B008
) -> RetrievalResponse:
    """
    Executes a semantic search over a specific processed document.
    Returns ranked chunks with similarity scores.
    """
    command = RetrievalCommand(
        user_id=current_user.user_id,
        query=request.query,
        document_id=request.document_id,
        top_k=request.top_k,
        minimum_similarity=getattr(request, "minimum_similarity", None),
    )
    
    try:
        result = await use_case.execute(command)
    except BackendError as e:
        raise APIError(status_code=e.status_code, code=e.code, message=e.message) from e

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
