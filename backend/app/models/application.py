from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    applied_at = Column(Date, nullable=False)
    status = Column(String(32), default="applied", nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    interview_sessions = relationship(
        "InterviewSession",
        back_populates="application",
        order_by="InterviewSession.scheduled_at",
        cascade="all, delete-orphan",
    )


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_application_id = Column(Integer, ForeignKey("job_applications.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sort_order = Column(Integer, default=0, nullable=True)
    notes = Column(Text, nullable=True)

    application = relationship("JobApplication", back_populates="interview_sessions")
