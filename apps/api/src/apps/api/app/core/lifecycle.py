"""Application lifespan construction."""

from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from logging import getLogger
from time import monotonic

from fastapi import FastAPI

from apps.api.app.config import APISettings
from apps.api.app.db.engine import get_engine, get_session_factory

logger = getLogger(__name__)

Lifespan = Callable[[FastAPI], AbstractAsyncContextManager[None]]


def create_lifespan(settings: APISettings) -> Lifespan:
    """Create lifecycle behavior bound to one application configuration."""

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        application.state.started_at = monotonic()
        application.state.is_ready = True

        # Setup Database Engine
        engine = get_engine(settings)
        application.state.engine = engine
        application.state.session_factory = get_session_factory(engine)

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

            # Teardown Database Engine
            await engine.dispose()

            logger.info(
                "application_stopped",
                extra={"application": settings.app_name},
            )

    return lifespan
