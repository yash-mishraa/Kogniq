"""Request duration measurement."""

from time import perf_counter

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class RequestTimingMiddleware:
    """Measure server processing duration and expose milliseconds."""

    def __init__(self, application: ASGIApp, header_name: str) -> None:
        self._application = application
        self._header_name = header_name

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._application(scope, receive, send)
            return

        started_at = perf_counter()

        async def add_timing(message: Message) -> None:
            if message["type"] == "http.response.start":
                elapsed_ms = (perf_counter() - started_at) * 1_000
                headers = MutableHeaders(scope=message)
                headers[self._header_name] = f"{elapsed_ms:.3f}"
            await send(message)

        await self._application(scope, receive, add_timing)
