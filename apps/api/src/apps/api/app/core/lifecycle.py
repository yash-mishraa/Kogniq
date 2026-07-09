"""Application lifespan construction."""

from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from logging import getLogger
from time import monotonic

from fastapi import FastAPI

from apps.api.app.config import APISettings

logger = getLogger(__name__)

Lifespan = Callable[[FastAPI], AbstractAsyncContextManager[None]]


def create_lifespan(settings: APISettings) -> Lifespan:
    """Create lifecycle behavior bound to one application configuration."""

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        application.state.started_at = monotonic()
        application.state.is_ready = True
        logger.info(
            "application_started",
            extra={
                "application": settings.app_name,
                "environment": settings.environment.value,
                "version": settings.app_version,
            },
        )
        try:
            yield
        finally:
            application.state.is_ready = False
            logger.info(
                "application_stopped",
                extra={"application": settings.app_name},
            )

    return lifespan
