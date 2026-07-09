"""Application health endpoint."""

from time import monotonic

from fastapi import APIRouter, HTTPException, Request

from apps.api.app.db.health import check_database_health
from apps.api.app.dependencies import SettingsDependency
from apps.api.app.schemas.system import HealthResponse

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health", response_model=HealthResponse)
async def health(request: Request, settings: SettingsDependency) -> HealthResponse:
    """Report process health without probing external dependencies."""
    started_at = float(request.app.state.started_at)
    engine = getattr(request.app.state, "engine", None)

    if engine:
        is_db_healthy = await check_database_health(engine)
        if not is_db_healthy:
            raise HTTPException(status_code=503, detail="Database is unavailable")

    return HealthResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.environment,
        uptime_seconds=max(0.0, monotonic() - started_at),
        application=settings.app_name,
    )
