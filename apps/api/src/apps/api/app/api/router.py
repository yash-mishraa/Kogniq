"""Composition point for foundational API routes."""

from fastapi import APIRouter

from apps.api.app.routers.agent import agent_router
from apps.api.app.routers.analytics import analytics_router
from apps.api.app.routers.auth import router as auth_router
from apps.api.app.routers.documents import router as documents_router
from apps.api.app.routers.health import router as health_router
from apps.api.app.routers.jobs import jobs_router
from apps.api.app.routers.knowledge import knowledge_router
from apps.api.app.routers.learning import learning_router
from apps.api.app.routers.resources import router as resources_router
from apps.api.app.routers.retrieval import router as retrieval_router
from apps.api.app.routers.student import student_router
from apps.api.app.routers.version import router as version_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(health_router)
api_router.include_router(version_router)
api_router.include_router(documents_router)
api_router.include_router(learning_router)
api_router.include_router(retrieval_router)
api_router.include_router(jobs_router)
api_router.include_router(knowledge_router)
api_router.include_router(analytics_router)
api_router.include_router(resources_router)
api_router.include_router(student_router)
api_router.include_router(agent_router)

from apps.api.app.routers.notebook import notebook_router
api_router.include_router(notebook_router)
