"""Composition point for foundational API routes."""

from backend.routers.documents import documents_router
from backend.routers.jobs import jobs_router
from backend.routers.learning import learning_router
from backend.routers.retrieval import retrieval_router
from fastapi import APIRouter

from apps.api.app.routers.auth import router as auth_router
from apps.api.app.routers.health import router as health_router
from apps.api.app.routers.version import router as version_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(health_router)
api_router.include_router(version_router)
api_router.include_router(documents_router)
api_router.include_router(learning_router)
api_router.include_router(retrieval_router)
api_router.include_router(jobs_router)
