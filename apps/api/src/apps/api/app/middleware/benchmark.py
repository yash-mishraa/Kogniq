import contextvars, time, json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

benchmark_metrics_var = contextvars.ContextVar("benchmark_metrics", default=None)

class BenchmarkMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        metrics = {"calls": [], "req_start": time.perf_counter()}
        token = benchmark_metrics_var.set(metrics)
        
        try:
            response = await call_next(request)
            data = benchmark_metrics_var.get()
            
            # Summarize
            if data and data["calls"]:
                calls = data["calls"]
                total_exec = sum(c["exec_ms"] for c in calls)
                total_queue = sum(c["queue_ms"] for c in calls)
                
                response.headers["X-Benchmark-Provider-Calls"] = str(len(calls))
                response.headers["X-Benchmark-Provider-Exec-Ms"] = f"{total_exec:.3f}"
                response.headers["X-Benchmark-Provider-Queue-Ms"] = f"{total_queue:.3f}"
                
                if calls:
                    response.headers["X-Benchmark-Executor"] = calls[0].get("executor", "Unknown")
                    response.headers["X-Benchmark-Max-Workers"] = str(calls[0].get("max_workers", -1))
                    
            return response
        finally:
            benchmark_metrics_var.reset(token)
