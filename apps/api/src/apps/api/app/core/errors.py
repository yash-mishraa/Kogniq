"""Application-level exceptions and reusable FastAPI handlers."""

from collections.abc import Mapping, Sequence

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from apps.api.app.schemas.errors import ErrorDetail, ErrorResponse, ValidationIssue
from shared.exceptions import KogniqError


class APIError(KogniqError):
    """Expected application-edge error with a stable public code."""

    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.headers = headers


def register_exception_handlers(application: FastAPI) -> None:
    """Register standardized handlers for expected framework and API errors."""
    application.add_exception_handler(APIError, api_error_handler)
    application.add_exception_handler(RequestValidationError, validation_error_handler)
    application.add_exception_handler(StarletteHTTPException, http_error_handler)


async def api_error_handler(request: Request, error: Exception) -> JSONResponse:
    """Convert an expected API error to the public error envelope."""
    if not isinstance(error, APIError):
        raise error
    return _error_response(
        request=request,
        status_code=error.status_code,
        code=error.code,
        message=error.message,
        headers=error.headers,
    )


async def validation_error_handler(request: Request, error: Exception) -> JSONResponse:
    """Return safe validation details without echoing submitted values."""
    if not isinstance(error, RequestValidationError):
        raise error
    issues = [
        ValidationIssue(
            location=[str(part) for part in item["loc"]],
            message=str(item["msg"]),
            type=str(item["type"]),
        )
        for item in error.errors()
    ]
    return _error_response(
        request=request,
        status_code=422,
        code="request_validation_failed",
        message="The request could not be validated.",
        issues=issues,
    )


async def http_error_handler(request: Request, error: Exception) -> JSONResponse:
    """Normalize Starlette and FastAPI HTTP exceptions."""
    if not isinstance(error, StarletteHTTPException):
        raise error
    message = error.detail if isinstance(error.detail, str) else "The request failed."
    return _error_response(
        request=request,
        status_code=error.status_code,
        code=f"http_{error.status_code}",
        message=message,
        headers=error.headers,
    )


def _error_response(
    *,
    request: Request,
    status_code: int,
    code: str,
    message: str,
    headers: Mapping[str, str] | None = None,
    issues: Sequence[ValidationIssue] | None = None,
) -> JSONResponse:
    payload = ErrorResponse(
        error=ErrorDetail(
            code=code,
            message=message,
            issues=list(issues) if issues else None,
        ),
        request_id=getattr(request.state, "request_id", None),
    )
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(mode="json", exclude_none=True),
        headers=headers,
    )
