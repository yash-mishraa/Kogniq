"""Application version endpoint."""

from fastapi import APIRouter

from apps.api.app.dependencies import SettingsDependency
from apps.api.app.schemas.system import VersionResponse

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/version", response_model=VersionResponse)
async def version(settings: SettingsDependency) -> VersionResponse:
    """Report build metadata without exposing runtime secrets."""
    return VersionResponse(
        application=settings.app_name,
        version=settings.app_version,
        build=settings.build,
        commit=settings.commit,
        api_version=settings.api_version,
    )
