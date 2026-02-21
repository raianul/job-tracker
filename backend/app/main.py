from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api import health, auth, applications, jobs, dashboard, admin

settings = get_settings()

app = FastAPI(
    title="Job Tracker API",
    version="0.1.0",
    description="Central panel to track job applications",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(applications.router)
app.include_router(jobs.router)
app.include_router(dashboard.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"message": "Job Tracker API", "docs": "/docs"}
