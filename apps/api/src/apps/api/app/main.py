"""FastAPI application factory."""

from fastapi import FastAPI

from apps.api.app.api.router import api_router
from apps.api.app.config import APISettings
from apps.api.app.core.errors import register_exception_handlers
from apps.api.app.core.lifecycle import create_lifespan
from apps.api.app.core.metadata import build_contact, build_license, build_servers
from apps.api.app.middleware import register_middleware
from shared.logging import LoggingConfig, configure_logging


def create_app(settings: APISettings | None = None) -> FastAPI:
    """Create an independently configured Kogniq API application."""
    effective_settings = settings or APISettings()
    configure_logging(LoggingConfig(level=effective_settings.log_level))

    application = FastAPI(
        title=effective_settings.app_name,
        summary="Kogniq learning intelligence application API",
        description=effective_settings.openapi_description,
        version=effective_settings.app_version,
        openapi_tags=effective_settings.openapi_tags,
        contact=build_contact(effective_settings),
        license_info=build_license(effective_settings),
        servers=build_servers(effective_settings),
        lifespan=create_lifespan(effective_settings),
    )
    application.state.settings = effective_settings

    register_exception_handlers(application)
    register_middleware(application, effective_settings)
    application.include_router(api_router)

    return application


app = create_app()
