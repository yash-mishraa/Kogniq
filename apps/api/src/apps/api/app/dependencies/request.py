"""Request-scoped foundational dependencies."""

from typing import Annotated, cast

from fastapi import Depends, Request

from apps.api.app.config import APISettings


def get_settings(request: Request) -> APISettings:
    """Return the immutable settings bound to the current application."""
    return cast(APISettings, request.app.state.settings)


def get_request_id(request: Request) -> str:
    """Return the request identifier assigned by middleware."""
    return cast(str, request.state.request_id)


SettingsDependency = Annotated[APISettings, Depends(get_settings)]
RequestIDDependency = Annotated[str, Depends(get_request_id)]
