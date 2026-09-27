"""Application lifespan construction."""

import asyncio
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from logging import getLogger
from time import monotonic, perf_counter
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI

from apps.api.app.config import APISettings

logger = getLogger(__name__)

Lifespan = Callable[[FastAPI], AbstractAsyncContextManager[None]]

async def event_loop_monitor(application: FastAPI) -> None:
    application.state.event_loop_lag_ms = 0.0
    try:
        while True:
            start = perf_counter()
            await asyncio.sleep(0.01)
            elapsed = perf_counter() - start
            lag = max(0.0, (elapsed - 0.01) * 1000.0)
            if lag > application.state.event_loop_lag_ms:
                application.state.event_loop_lag_ms = lag
    except asyncio.CancelledError:
        pass

def create_lifespan(settings: APISettings) -> Lifespan:
    """Create lifecycle behavior bound to one application configuration."""


    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        application.state.started_at = monotonic()
        application.state.is_ready = True
        
        # Globally configure the asyncio thread pool to handle high concurrency of synchronous provider/retrieval calls
        global_executor = ThreadPoolExecutor(max_workers=50)
        asyncio.get_running_loop().set_default_executor(global_executor)


        monitor_task = None
        benchmark_executor = None
        if settings.environment.value == "benchmark":
            monitor_task = asyncio.create_task(event_loop_monitor(application))
            benchmark_executor = ThreadPoolExecutor(max_workers=50)
            loop = asyncio.get_running_loop()
            loop.set_default_executor(benchmark_executor)


        from backend.dependencies import (
            get_authentication_service,
            get_authorization_service,
            get_permission_repository,
            get_role_repository,
        )
        from backend.security.bootstrap import bootstrap_authorization, bootstrap_development_demo
        from application.auth.register_user import RegisterUserUseCase

        await bootstrap_authorization(get_role_repository(), get_permission_repository())

        if settings.environment.value in ("development", "test", "benchmark"):
            auth_service = await get_authentication_service()
            authorization_service = await get_authorization_service()
            use_case = RegisterUserUseCase(
                auth_service=auth_service,  # type: ignore
                authorization_service=authorization_service,  # type: ignore
            )
            await bootstrap_development_demo(use_case)

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
            
            if monitor_task:
                monitor_task.cancel()
                try:
                    await monitor_task
                except asyncio.CancelledError:
                    pass
            if benchmark_executor:
                benchmark_executor.shutdown(wait=True)
            global_executor.shutdown(wait=True)


            logger.info(
                "application_stopped",
                extra={"application": settings.app_name},
            )

    return lifespan
