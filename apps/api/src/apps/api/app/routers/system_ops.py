"""System overview and observability endpoints for the RAG console."""

from __future__ import annotations

from typing import Any

from backend.dependencies import get_system_service
from backend.services.system_service import SystemService
from fastapi import APIRouter, Depends

from apps.api.app.dependencies.auth import CurrentUserDependency

router = APIRouter(prefix="/system", tags=["system"])
observability_router = APIRouter(prefix="/observability", tags=["Observability"])


@router.get("/overview")
async def overview(
    current_user: CurrentUserDependency,
    service: SystemService = Depends(get_system_service),  # noqa: B008
) -> dict[str, Any]:
    """Return document, index, query, and capability telemetry for this user."""
    return await service.overview(current_user.user_id)


@router.get("/ready")
async def ready(
    service: SystemService = Depends(get_system_service),  # noqa: B008
) -> dict[str, Any]:
    """Report dependency readiness without claiming provider availability."""
    return await service.ready()


@observability_router.get("/queries")
async def recent_queries(
    current_user: CurrentUserDependency,
    limit: int = 50,
    service: SystemService = Depends(get_system_service),  # noqa: B008
) -> dict[str, Any]:
    """Return the caller's recent query telemetry. Prompts and source text are not stored."""
    return {
        "queries": service.recent_queries(current_user.user_id, limit=limit),
        "cache_status": "not_supported",
    }
