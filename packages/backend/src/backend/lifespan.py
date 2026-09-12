from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.core.logging import logger


@asynccontextmanager
async def app_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manages global application startup and shutdown events.
    """
    _ = app  # Unused for now, but signature matches FastAPI requirements

    logger.info("Starting Kogniq Backend")
    
    from backend.core.settings import settings
    provider_name = settings.learning_generation_provider.capitalize()
    logger.info(f"Learning Generation Provider: {provider_name}")


    # Example placeholder: Initialize database connections, load models, etc.
    logger.info("Backend Ready")

    yield

    logger.info("Stopping Backend...")
    # Example placeholder: Close connections, clean up resources, etc.
    logger.info("Backend Shutdown Complete")
