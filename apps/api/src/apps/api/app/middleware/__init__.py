"""Middleware registration for the Kogniq API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from apps.api.app.config import APISettings
from apps.api.app.middleware.exceptions import UnhandledExceptionMiddleware
from apps.api.app.middleware.request_id import RequestIDMiddleware
from apps.api.app.middleware.timing import RequestTimingMiddleware


def register_middleware(application: FastAPI, settings: APISettings) -> None:
    """Register middleware in deliberate inner-to-outer order."""
    application.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts,
    )
    if settings.gzip_enabled:
        application.add_middleware(
            GZipMiddleware,
            minimum_size=settings.gzip_minimum_size,
        )
    application.add_middleware(
        RequestTimingMiddleware,
        header_name=settings.process_time_header,
    )
    application.add_middleware(UnhandledExceptionMiddleware)
    application.add_middleware(
        RequestIDMiddleware,
        header_name=settings.request_id_header,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )


__all__ = ["register_middleware"]
