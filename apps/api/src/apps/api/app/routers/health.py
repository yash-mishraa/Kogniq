"""Application health endpoint."""

from time import monotonic

from fastapi import APIRouter, Request

from apps.api.app.dependencies import SettingsDependency
from apps.api.app.schemas.system import HealthResponse

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health", response_model=HealthResponse)
async def health(request: Request, settings: SettingsDependency) -> HealthResponse:
    """Report process health without probing external dependencies."""
    started_at = float(request.app.state.started_at)
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.environment,
        uptime_seconds=max(0.0, monotonic() - started_at),
        application=settings.app_name,
    )
