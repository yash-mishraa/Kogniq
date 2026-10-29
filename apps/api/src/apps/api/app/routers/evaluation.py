"""Evaluation endpoints."""

from __future__ import annotations

from typing import Any

from backend.dependencies import get_evaluation_service
from backend.schemas.evaluation import (
    EvaluationDataset,
    RunEvaluationRequest,
    RunEvaluationResponse,
    SuggestedCase,
)
from backend.services.evaluation_service import EvaluationService
from fastapi import APIRouter, Depends

from apps.api.app.dependencies.auth import CurrentUserDependency

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@router.get("/datasets", response_model=list[EvaluationDataset])
async def datasets(
    service: EvaluationService = Depends(get_evaluation_service),  # noqa: B008
) -> list[EvaluationDataset]:
    """List available evaluation dataset definitions."""
    return service.datasets()


@router.get("/suggest", response_model=list[SuggestedCase])
async def suggest_cases(
    document_id: str,
    current_user: CurrentUserDependency,
    limit: int = 5,
    service: EvaluationService = Depends(get_evaluation_service),  # noqa: B008
) -> list[SuggestedCase]:
    """Suggest deterministic cases from a document's persisted chunks."""
    return await service.suggest_cases(document_id, current_user.user_id, limit=limit)


@router.post("/run", response_model=RunEvaluationResponse)
async def run_evaluation(
    request: RunEvaluationRequest,
    current_user: CurrentUserDependency,
    service: EvaluationService = Depends(get_evaluation_service),  # noqa: B008
) -> RunEvaluationResponse:
    """Run retrieval (and optionally generation) metrics and persist the result."""
    return await service.run(request, current_user.user_id)


@router.get("/history")
async def evaluation_history(
    current_user: CurrentUserDependency,
    limit: int = 20,
    service: EvaluationService = Depends(get_evaluation_service),  # noqa: B008
) -> dict[str, Any]:
    """List this user's previous evaluation runs."""
    return {"runs": service.history(current_user.user_id, limit=limit)}
