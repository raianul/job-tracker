from datetime import date, datetime
from typing import List

from pydantic import BaseModel


# Job (shared) - from fetch or manual
class JobResponse(BaseModel):
    id: int
    source_url: str
    title: str | None
    company: str | None
    description: str | None
    location: str | None
    source_domain: str | None

    class Config:
        from_attributes = True


# Interview session
class InterviewSessionBase(BaseModel):
    name: str
    scheduled_at: datetime | None = None
    sort_order: int | None = 0
    notes: str | None = None


class InterviewSessionCreate(InterviewSessionBase):
    pass


class InterviewSessionUpdate(BaseModel):
    name: str | None = None
    scheduled_at: datetime | None = None
    sort_order: int | None = None
    notes: str | None = None


class InterviewSessionResponse(InterviewSessionBase):
    id: int
    job_application_id: int

    class Config:
        from_attributes = True


# Application
class ApplicationCreate(BaseModel):
    source_url: str
    applied_at: date
    status: str = "applied"
    # Optional: pre-fetched details to upsert into Job (when creating new Job)
    title: str | None = None
    company: str | None = None
    description: str | None = None
    source_domain: str | None = None


class ApplicationUpdate(BaseModel):
    applied_at: date | None = None
    status: str | None = None
    notes: str | None = None
    # Optional: update the shared Job's display fields
    title: str | None = None
    company: str | None = None
    description: str | None = None
    location: str | None = None
    source_domain: str | None = None


class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    job_id: int
    applied_at: date
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime | None
    job: JobResponse
    interview_sessions: List[InterviewSessionResponse] = []

    class Config:
        from_attributes = True


class ApplicationListResponse(BaseModel):
    id: int
    job_id: int
    applied_at: date
    status: str
    created_at: datetime
    source_url: str
    title: str | None
    company: str | None
    source_domain: str | None

    class Config:
        from_attributes = True
