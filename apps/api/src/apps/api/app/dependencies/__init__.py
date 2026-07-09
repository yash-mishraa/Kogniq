"""Generic FastAPI dependency exports."""

from apps.api.app.dependencies.request import (
    RequestIDDependency,
    SettingsDependency,
    get_request_id,
    get_settings,
)

__all__ = [
    "RequestIDDependency",
    "SettingsDependency",
    "get_request_id",
    "get_settings",
]
