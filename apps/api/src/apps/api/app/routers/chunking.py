"""Chunking laboratory endpoints."""

from __future__ import annotations

from backend.dependencies import get_chunking_service
from backend.schemas.chunking import (
    ChunkCompareRequest,
    ChunkCompareResponse,
    ChunkPreviewRequest,
    ChunkPreviewResponse,
)
from backend.services.chunking_service import ChunkingService
from fastapi import APIRouter, Depends

from apps.api.app.dependencies.auth import CurrentUserDependency

router = APIRouter(prefix="/chunking", tags=["Chunking"])


@router.post("/preview", response_model=ChunkPreviewResponse)
async def preview_chunks(
    request: ChunkPreviewRequest,
    current_user: CurrentUserDependency,
    service: ChunkingService = Depends(get_chunking_service),  # noqa: B008
) -> ChunkPreviewResponse:
    """Preview the exact fixed-size chunker used by ingestion."""
    return await service.preview(request, current_user.user_id)


@router.post("/compare", response_model=ChunkCompareResponse)
async def compare_chunking(
    request: ChunkCompareRequest,
    current_user: CurrentUserDependency,
    service: ChunkingService = Depends(get_chunking_service),  # noqa: B008
) -> ChunkCompareResponse:
    """Compare two to five chunking configurations over the same source."""
    return await service.compare(request, current_user.user_id)
