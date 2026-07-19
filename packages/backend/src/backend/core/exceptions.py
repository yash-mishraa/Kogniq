from fastapi import Request
from fastapi.responses import JSONResponse


class BackendError(Exception):
    """Base class for all application-level errors."""

    def __init__(self, code: str, message: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


async def backend_error_handler(request: Request, exc: BackendError) -> JSONResponse:
    """
    Global exception handler ensuring every application exception
    serializes consistently into a standard JSON schema.
    """
    _ = request
    return JSONResponse(
        status_code=exc.status_code, content={"error": {"code": exc.code, "message": exc.message}}
    )
