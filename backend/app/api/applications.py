from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.job import Job
from app.models.application import JobApplication, InterviewSession
from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    ApplicationListResponse,
    JobResponse,
    InterviewSessionCreate,
    InterviewSessionUpdate,
    InterviewSessionResponse,
)
from app.services.job_service import get_or_create_job

router = APIRouter(prefix="/api/applications", tags=["applications"])


def _to_response(app: JobApplication) -> ApplicationResponse:
    job = app.job
    return ApplicationResponse(
        id=app.id,
        user_id=app.user_id,
        job_id=app.job_id,
        applied_at=app.applied_at,
        status=app.status,
        notes=app.notes,
        created_at=app.created_at,
        updated_at=app.updated_at,
        job=JobResponse(
            id=job.id,
            source_url=job.source_url,
            title=job.title,
            company=job.company,
            description=job.description,
            location=job.location,
            source_domain=job.source_domain,
        ),
        interview_sessions=[
            InterviewSessionResponse(
                id=s.id,
                job_application_id=s.job_application_id,
                name=s.name,
                scheduled_at=s.scheduled_at,
                sort_order=s.sort_order,
                notes=s.notes,
            )
            for s in app.interview_sessions
        ],
    )


@router.get("", response_model=list[ApplicationListResponse])
def list_applications(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    status_filter: str | None = Query(None, alias="status"),
    search: str | None = Query(None),
    sort: str = Query("-applied_at"),
):
    q = (
        db.query(JobApplication)
        .options(joinedload(JobApplication.job))
        .filter(JobApplication.user_id == user.id)
    )
    if status_filter:
        q = q.filter(JobApplication.status == status_filter)
    if search:
        search_term = f"%{search}%"
        q = q.join(Job).filter(
            (JobApplication.job_id == Job.id)
            & ((Job.title.ilike(search_term)) | (Job.company.ilike(search_term)))
        ).distinct()
    if sort == "-applied_at":
        q = q.order_by(JobApplication.applied_at.desc())
    elif sort == "applied_at":
        q = q.order_by(JobApplication.applied_at.asc())
    apps = q.all()
    return [
        ApplicationListResponse(
            id=app.id,
            job_id=app.job_id,
            applied_at=app.applied_at,
            status=app.status,
            created_at=app.created_at,
            source_url=app.job.source_url,
            title=app.job.title,
            company=app.job.company,
            source_domain=app.job.source_domain,
        )
        for app in apps
    ]


ACTIVE_STATUSES = ("applied", "in_progress")


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    body: ApplicationCreate,
):
    job = get_or_create_job(
        db,
        source_url=body.source_url,
        title=body.title,
        company=body.company,
        description=body.description,
        source_domain=body.source_domain,
    )
    existing = (
        db.query(JobApplication)
        .filter(
            JobApplication.user_id == user.id,
            JobApplication.job_id == job.id,
            JobApplication.status.in_(ACTIVE_STATUSES),
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have an active application for this job (Applied or In progress). Update the existing one or set its status to Done/Rejected first.",
        )
    app = JobApplication(
        user_id=user.id,
        job_id=job.id,
        applied_at=body.applied_at,
        status=body.status,
    )
    db.add(app)
    u = db.query(User).filter(User.id == user.id).first()
    if u:
        u.total_applied = (u.total_applied or 0) + 1
    db.commit()
    db.refresh(app)
    app = (
        db.query(JobApplication)
        .options(
            joinedload(JobApplication.job),
            joinedload(JobApplication.interview_sessions),
        )
        .filter(JobApplication.id == app.id)
        .first()
    )
    return _to_response(app)


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: int,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    app = (
        db.query(JobApplication)
        .options(
            joinedload(JobApplication.job),
            joinedload(JobApplication.interview_sessions),
        )
        .filter(JobApplication.id == application_id, JobApplication.user_id == user.id)
        .first()
    )
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return _to_response(app)


@router.patch("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: int,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    body: ApplicationUpdate,
):
    app = (
        db.query(JobApplication)
        .options(joinedload(JobApplication.job), joinedload(JobApplication.interview_sessions))
        .filter(JobApplication.id == application_id, JobApplication.user_id == user.id)
        .first()
    )
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if body.applied_at is not None:
        app.applied_at = body.applied_at
    if body.status is not None:
        old_status = app.status
        app.status = body.status
        if old_status != body.status:
            u = db.query(User).filter(User.id == user.id).first()
            if u:
                if body.status == "rejected":
                    u.total_rejected = (u.total_rejected or 0) + 1
                elif body.status == "got_offer":
                    u.total_success = (u.total_success or 0) + 1
    if body.notes is not None:
        app.notes = body.notes
    if body.title is not None or body.company is not None or body.description is not None or body.location is not None or body.source_domain is not None:
        job = app.job
        if body.title is not None:
            job.title = body.title
        if body.company is not None:
            job.company = body.company
        if body.description is not None:
            job.description = body.description
        if body.location is not None:
            job.location = body.location
        if body.source_domain is not None:
            job.source_domain = body.source_domain
    db.commit()
    db.refresh(app)
    return _to_response(app)


@router.post("/{application_id}/sessions", response_model=InterviewSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    application_id: int,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    body: InterviewSessionCreate,
):
    app = db.query(JobApplication).filter(
        JobApplication.id == application_id, JobApplication.user_id == user.id
    ).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app.status not in ("applied", "in_progress"):
        raise HTTPException(
            status_code=400,
            detail="Interview sessions can only be added when status is Applied or In progress",
        )
    session = InterviewSession(
        job_application_id=app.id,
        name=body.name,
        scheduled_at=body.scheduled_at,
        sort_order=body.sort_order or 0,
        notes=body.notes,
    )
    db.add(session)
    if app.status == "applied":
        app.status = "in_progress"
    db.commit()
    db.refresh(session)
    return InterviewSessionResponse(
        id=session.id,
        job_application_id=session.job_application_id,
        name=session.name,
        scheduled_at=session.scheduled_at,
        sort_order=session.sort_order,
        notes=session.notes,
    )


@router.patch("/{application_id}/sessions/{session_id}", response_model=InterviewSessionResponse)
def update_session(
    application_id: int,
    session_id: int,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    body: InterviewSessionUpdate,
):
    session = (
        db.query(InterviewSession)
        .join(JobApplication)
        .filter(
            InterviewSession.id == session_id,
            InterviewSession.job_application_id == application_id,
            JobApplication.user_id == user.id,
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if body.name is not None:
        session.name = body.name
    if body.scheduled_at is not None:
        session.scheduled_at = body.scheduled_at
    if body.sort_order is not None:
        session.sort_order = body.sort_order
    if body.notes is not None:
        session.notes = body.notes
    db.commit()
    db.refresh(session)
    return InterviewSessionResponse(
        id=session.id,
        job_application_id=session.job_application_id,
        name=session.name,
        scheduled_at=session.scheduled_at,
        sort_order=session.sort_order,
        notes=session.notes,
    )


@router.delete("/{application_id}/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    application_id: int,
    session_id: int,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    session = (
        db.query(InterviewSession)
        .join(JobApplication)
        .filter(
            InterviewSession.id == session_id,
            InterviewSession.job_application_id == application_id,
            JobApplication.user_id == user.id,
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
