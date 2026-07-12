import time
from collections import defaultdict

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import settings


class InMemoryRateLimiter:
    def __init__(self):
        self._windows: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str, max_requests: int, window_seconds: int = 60) -> bool:
        now = time.monotonic()
        window_start = now - window_seconds
        timestamps = self._windows[key]
        self._windows[key] = [t for t in timestamps if t > window_start]
        if len(self._windows[key]) >= max_requests:
            return False
        self._windows[key].append(now)
        return True


rate_limiter = InMemoryRateLimiter()

PLAN_LIMITS = {
    "free": 10,
    "basic": 60,
    "pro": 300,
    "ultra": 1000,
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi"):
            return await call_next(request)

        plan = getattr(request.state, "rapidapi_plan", "free")
        user = getattr(request.state, "rapidapi_user", request.client.host or "unknown")
        max_reqs = PLAN_LIMITS.get(plan, settings.max_requests_per_minute)

        key = f"{user}:{plan}"
        if not rate_limiter.check(key, max_reqs, 60):
            return JSONResponse(
                status_code=429,
                content={"error": "rate_limit_exceeded", "detail": f"Max {max_reqs} requests per minute for {plan} plan"},
                headers={"Retry-After": "60"},
            )

        resp = await call_next(request)
        resp.headers["X-RateLimit-Limit"] = str(max_reqs)
        resp.headers["X-RateLimit-Remaining"] = str(
            max(0, max_reqs - len(rate_limiter._windows.get(key, [])))
        )
        return resp
