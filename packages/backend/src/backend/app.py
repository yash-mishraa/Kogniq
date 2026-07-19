from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.core.exceptions import BackendError, backend_error_handler
from backend.core.settings import settings
from backend.lifespan import app_lifespan
from backend.routers.api import api_router


class WelcomeResponse(BaseModel):
    name: str
    status: str


def create_app() -> FastAPI:
    """
    Factory function to configure and bootstrap the FastAPI application.
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        debug=settings.debug,
        lifespan=app_lifespan,
    )

    # Middleware Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handlers
    app.add_exception_handler(BackendError, backend_error_handler)  # type: ignore[arg-type]

    # Routing
    app.include_router(api_router)

    @app.get("/", response_model=WelcomeResponse, tags=["Root"])
    async def root() -> WelcomeResponse:
        return WelcomeResponse(name=settings.app_name, status="running")

    return app
