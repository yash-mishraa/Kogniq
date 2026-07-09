"""Last-resort handling for unexpected HTTP request failures."""

from logging import getLogger
from typing import cast

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from apps.api.app.schemas.errors import ErrorDetail, ErrorResponse

logger = getLogger(__name__)


class UnhandledExceptionMiddleware:
    """Convert unexpected pre-response exceptions to a safe error envelope."""

    def __init__(self, application: ASGIApp) -> None:
        self._application = application

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._application(scope, receive, send)
            return

        response_started = False

        async def observe_send(message: Message) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self._application(scope, receive, observe_send)
        except Exception:
            logger.exception("unhandled_request_exception")
            if response_started:
                raise

            state = cast(dict[str, object], scope.get("state", {}))
            request_id = state.get("request_id")
            payload = ErrorResponse(
                error=ErrorDetail(
                    code="internal_server_error",
                    message="An unexpected error occurred.",
                ),
                request_id=request_id if isinstance(request_id, str) else None,
            )
            response = JSONResponse(
                status_code=500,
                content=payload.model_dump(mode="json", exclude_none=True),
            )
            await response(scope, receive, send)
