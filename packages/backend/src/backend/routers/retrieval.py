from fastapi import APIRouter

from backend.dependencies import RetrievalDependency
from backend.schemas.retrieval import RetrievalRequest, RetrievalResponse

retrieval_router = APIRouter(prefix="/retrieval", tags=["retrieval"])


@retrieval_router.post("/search", response_model=RetrievalResponse)
async def semantic_search(
    request: RetrievalRequest,
    retrieval_service: RetrievalDependency,
) -> RetrievalResponse:
    """
    Executes a semantic search over a specific processed document.
    Returns ranked chunks with similarity scores.
    """
    return await retrieval_service.search(request)
