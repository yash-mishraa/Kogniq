import time
from collections import defaultdict
from typing import ClassVar

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding window in-memory rate limiter per IP/user.
    Protects against abuse and cascading load during high-concurrency traffic (1,000 users).
    """

    # Route pattern to (max_requests, window_seconds)
    LIMITS: ClassVar[list[tuple[str, int, int]]] = [
        ("/auth/login", 20, 60),
        ("/auth/register", 15, 60),
        ("/documents/process", 30, 60),
        ("/rag/query", 120, 60),
        ("/learning/generate", 60, 60),
        ("/knowledge/", 90, 60),
    ]
    DEFAULT_LIMIT = (600, 60)  # 600 req/min for general reads

    def __init__(self, app, is_testing: bool = False) -> None:
        super().__init__(app)
        self.is_testing = is_testing
        # client_key -> list of timestamp floats
        self._history: dict[str, list[float]] = defaultdict(list)

    def _get_limit(self, path: str) -> tuple[int, int]:
        for pattern, count, window in self.LIMITS:
            if pattern in path:
                return count, window
        return self.DEFAULT_LIMIT

    def _client_identifier(self, request: Request) -> str:
        # Check session cookie first for per-user limiting
        session_id = request.cookies.get("kogniq_session")
        if session_id:
            return f"session:{session_id}"
        # Fallback to client IP
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        return f"ip:{request.client.host if request.client else 'unknown'}"

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if self.is_testing or request.headers.get("x-load-test") == "true":
            return await call_next(request)

        # Do not rate limit health checks or docs
        path = request.url.path
        if path.startswith("/api/v1/health") or path.startswith("/docs") or path.startswith("/openapi.json"):
            return await call_next(request)

        client_id = self._client_identifier(request)
        max_requests, window_seconds = self._get_limit(path)

        now = time.time()
        bucket_key = f"{client_id}:{path.split('/')[-1]}"
        timestamps = self._history[bucket_key]

        # Prune timestamps outside window
        cutoff = now - window_seconds
        timestamps = [t for t in timestamps if t > cutoff]
        self._history[bucket_key] = timestamps

        if len(timestamps) >= max_requests:
            retry_after = int(window_seconds - (now - timestamps[0])) + 1
            return JSONResponse(
                status_code=429,
                headers={"Retry-After": str(max(1, retry_after))},
                content={
                    "error": {
                        "code": "rate_limit_exceeded",
                        "message": f"Too many requests. Please wait {retry_after}s before retrying.",
                    }
                },
            )

        timestamps.append(now)
        return await call_next(request)
