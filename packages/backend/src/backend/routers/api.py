from fastapi import APIRouter

from backend.routers.documents import documents_router
from backend.routers.health import health_router

api_router = APIRouter(prefix="/api/v1")

# Include sub-routers here as they are developed
api_router.include_router(health_router)
api_router.include_router(documents_router)
