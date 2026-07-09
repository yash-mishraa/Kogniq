"""Composition point for foundational API routes."""

from fastapi import APIRouter

from apps.api.app.routers.health import router as health_router
from apps.api.app.routers.version import router as version_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(version_router)
