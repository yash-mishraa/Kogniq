from fastapi import APIRouter
from pydantic import BaseModel

from backend.core.settings import settings


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str


health_router = APIRouter(tags=["Health"])


@health_router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Standard health check endpoint for uptime monitoring and load balancers.
    """
    return HealthResponse(
        status="healthy",
        service="kogniq-backend",
        version=settings.version,
        environment=settings.environment,
    )
