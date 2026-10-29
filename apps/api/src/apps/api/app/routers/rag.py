"""Retrieval and grounded-answer endpoints."""

from __future__ import annotations

from backend.dependencies import get_rag_service
from backend.schemas.rag import (
    RagQueryRequest,
    RagQueryResponse,
    RetrievalOnlyResponse,
)
from backend.services.rag_service import RagService
from fastapi import APIRouter, Depends

from apps.api.app.dependencies.auth import CurrentUserDependency

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/query", response_model=RagQueryResponse)
async def rag_query(
    request: RagQueryRequest,
    current_user: CurrentUserDependency,
    rag_service: RagService = Depends(get_rag_service),  # noqa: B008
) -> RagQueryResponse:
    """Answer a question from authorized, indexed sources with validated citations."""
    return await rag_service.query(request, current_user.user_id)


@router.post("/retrieve", response_model=RetrievalOnlyResponse)
async def rag_retrieve(
    request: RagQueryRequest,
    current_user: CurrentUserDependency,
    rag_service: RagService = Depends(get_rag_service),  # noqa: B008
) -> RetrievalOnlyResponse:
    """Inspect hybrid retrieval without invoking a language model."""
    return await rag_service.retrieve_only(request, current_user.user_id)
