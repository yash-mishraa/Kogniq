"""Stable error response schemas."""

from pydantic import BaseModel


class ValidationIssue(BaseModel):
    """Safe description of one request validation failure."""

    location: list[str]
    message: str
    type: str


class ErrorDetail(BaseModel):
    """Machine-readable error code and human-readable message."""

    code: str
    message: str
    issues: list[ValidationIssue] | None = None


class ErrorResponse(BaseModel):
    """Standard public error envelope."""

    error: ErrorDetail
    request_id: str | None = None
