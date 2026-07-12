from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import settings


class RapidAPIMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if settings.rapidapi_proxy_secret:
            proxy_secret = request.headers.get("X-RapidAPI-Proxy-Secret", "")
            if proxy_secret != settings.rapidapi_proxy_secret:
                return JSONResponse(
                    status_code=403,
                    content={"error": "access_denied", "detail": "Valid RapidAPI Proxy Secret required. Use RapidAPI to access this endpoint."},
                )

        plan = request.headers.get("X-RapidAPI-Plan", "free")
        user = request.headers.get("X-RapidAPI-User", "anonymous")
        request.state.rapidapi_plan = plan
        request.state.rapidapi_user = user

        resp = await call_next(request)
        resp.headers["X-RateLimit-Plan"] = plan
        return resp
