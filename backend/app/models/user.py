from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    avatar_url = Column(String(512), nullable=True)
    provider = Column(String(32), nullable=False)  # google | linkedin
    provider_id = Column(String(255), nullable=False, index=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    total_applied = Column(Integer, default=0, nullable=False)
    total_rejected = Column(Integer, default=0, nullable=False)
    total_success = Column(Integer, default=0, nullable=False)

    applications = relationship("JobApplication", back_populates="user", cascade="all, delete-orphan")
