from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Job(Base):
    """One row per unique job URL. Shared across users; we fetch once and reuse."""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_url = Column(String(2048), unique=True, nullable=False, index=True)
    title = Column(String(512), nullable=True)
    company = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    source_domain = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    applications = relationship("JobApplication", back_populates="job")
