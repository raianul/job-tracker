from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.application import JobApplication, InterviewSession
from app.models.job import Job

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
def dashboard_stats(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Return cumulative job stats stored on the user (total_applied, total_rejected, total_success)."""
    u = db.query(User).filter(User.id == user.id).first()
    if not u:
        return {"applied": 0, "rejected": 0, "success": 0}
    return {
        "applied": u.total_applied or 0,
        "rejected": u.total_rejected or 0,
        "success": u.total_success or 0,
    }


@router.get("/upcoming-interviews")
def upcoming_interviews(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(5, ge=1, le=50),
):
    now = datetime.now(timezone.utc)
    sessions = (
        db.query(InterviewSession)
        .join(JobApplication)
        .options(joinedload(InterviewSession.application).joinedload(JobApplication.job))
        .filter(
            JobApplication.user_id == user.id,
            InterviewSession.scheduled_at.isnot(None),
            InterviewSession.scheduled_at >= now,
        )
        .order_by(InterviewSession.scheduled_at.asc())
        .limit(limit)
        .all()
    )
    out = []
    for s in sessions:
        app = s.application
        job = app.job
        out.append({
            "application_id": app.id,
            "session_id": s.id,
            "session_name": s.name,
            "scheduled_at": s.scheduled_at.isoformat() if s.scheduled_at else None,
            "job_title": job.title if job else None,
            "company": job.company if job else None,
        })
    return out
