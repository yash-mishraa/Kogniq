"""FastAPI application factory."""

from fastapi import FastAPI

from apps.api.app.api.router import api_router
from apps.api.app.config import APISettings
from apps.api.app.core.errors import register_exception_handlers
from apps.api.app.core.lifecycle import create_lifespan
from apps.api.app.core.metadata import build_contact, build_license, build_servers
from apps.api.app.middleware import register_middleware
from shared.logging import LoggingConfig, configure_logging



from fastapi import Request
import threading, time

class GlobalMetrics:
    def __init__(self):
        self.lock = threading.Lock()
        self.http_in_flight = 0
        self.max_http_in_flight = 0
        self.embed_waiters = 0
        self.max_embed_waiters = 0
        self.embed_executing = 0
        self.max_embed_executing = 0
        self.total_embed_calls = 0
        self.provider_executing = 0
        self.max_provider_executing = 0
        self.embed_wait_times = []
        self.embed_exec_times = []

global_metrics = GlobalMetrics()

def create_app(settings: APISettings | None = None) -> FastAPI:
    """Create an independently configured Kogniq API application."""
    effective_settings = settings or APISettings()
    configure_logging(LoggingConfig(level=effective_settings.log_level, format_type=effective_settings.log_format))

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
        swagger_ui_parameters={"withCredentials": True},
    )
    application.state.settings = effective_settings

    register_exception_handlers(application)
    register_middleware(application, effective_settings)

    @application.middleware("http")
    async def track_http(request: Request, call_next):
        if request.url.path.startswith("/_benchmark"):
            return await call_next(request)
        with global_metrics.lock:
            global_metrics.http_in_flight += 1
            if global_metrics.http_in_flight > global_metrics.max_http_in_flight:
                global_metrics.max_http_in_flight = global_metrics.http_in_flight
        try:
            return await call_next(request)
        finally:
            with global_metrics.lock:
                global_metrics.http_in_flight -= 1

    @application.get("/_benchmark/report")
    def get_metrics():
        import numpy as np
        return {
            "A_max_http_in_flight": global_metrics.max_http_in_flight,
            "B_max_embed_waiters": global_metrics.max_embed_waiters,
            "C_max_embed_executing": global_metrics.max_embed_executing,
            "D_total_embed_calls": global_metrics.total_embed_calls,
            "E_max_provider_executing": global_metrics.max_provider_executing,
            "G_embed_wait_p95": np.percentile(global_metrics.embed_wait_times, 95) if global_metrics.embed_wait_times else 0,
            "H_embed_exec_p95": np.percentile(global_metrics.embed_exec_times, 95) if global_metrics.embed_exec_times else 0,
        }

    
    if effective_settings.environment.value == "benchmark":
        from apps.api.app.middleware.benchmark import BenchmarkMiddleware
        from apps.api.app.routers.benchmark import benchmark_router
        application.add_middleware(BenchmarkMiddleware)
        application.include_router(benchmark_router)
        
    application.include_router(api_router)

    @application.get("/", tags=["system"])
    async def root() -> dict[str, str]:
        return {"name": application.title, "status": "running"}

    return application


app = create_app()
