import re

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import get_settings
from app.api import health, auth, applications, jobs, dashboard, admin

settings = get_settings()

app = FastAPI(
    title="Job Tracker API",
    version="0.1.0",
    description="Central panel to track job applications",
)

# Allow these origins for CORS (and regex for *.vercel.app)
_CORS_ORIGIN_REGEX = re.compile(r"^https://[a-z0-9-]+\.vercel\.app$", re.I)

def _cors_allow_origin(origin: str | None) -> str | None:
    if not origin:
        return None
    if origin in ("http://localhost:3000", "http://127.0.0.1:3000"):
        return origin
    if settings.frontend_url and origin.strip() == settings.frontend_url.strip():
        return origin
    if _CORS_ORIGIN_REGEX.match(origin):
        return origin
    return None


class OptionPreflightMiddleware(BaseHTTPMiddleware):
    """Respond to OPTIONS (CORS preflight) with 200 and CORS headers so preflight never hits the router."""
    async def dispatch(self, request: Request, call_next):
        if request.method != "OPTIONS":
            return await call_next(request)
        origin = request.headers.get("origin")
        allow = _cors_allow_origin(origin) if origin else None
        headers = {
            "Access-Control-Max-Age": "86400",
            "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
        if allow:
            headers["Access-Control-Allow-Origin"] = allow
        return Response(status_code=200, headers=headers)


# Build CORS origins for non-OPTIONS responses
_cors_origins = [o.strip() for o in [settings.frontend_url, "http://localhost:3000"] if o and o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
# Run first (added last = outermost): handle OPTIONS so preflight never hits the router
app.add_middleware(OptionPreflightMiddleware)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(applications.router)
app.include_router(jobs.router)
app.include_router(dashboard.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"message": "Job Tracker API", "docs": "/docs"}
