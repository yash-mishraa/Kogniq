from fastapi import APIRouter, Request

benchmark_router = APIRouter(prefix="/_benchmark", tags=["Benchmark"])

@benchmark_router.get("/lag")
async def get_lag(request: Request) -> dict:
    if not hasattr(request.app.state, "event_loop_lag_ms"):
        return {"max_lag_ms": 0.0}
    
    # Atomic read and reset
    lag = request.app.state.event_loop_lag_ms
    request.app.state.event_loop_lag_ms = 0.0
    return {"max_lag_ms": lag}
