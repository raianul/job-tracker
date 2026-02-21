from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.models.user import User
from app.models.settings import SiteSettings
from app.schemas.admin import (
    SiteSettingsResponse,
    SiteSettingsUpdate,
    UserListResponse,
    UserUpdateBody,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _get_setting(db: Session, key: str) -> str | None:
    row = db.query(SiteSettings).filter(SiteSettings.key == key).first()
    return row.value if row else None


def _set_setting(db: Session, key: str, value: str | None) -> None:
    row = db.query(SiteSettings).filter(SiteSettings.key == key).first()
    if row:
        row.value = value
    else:
        db.add(SiteSettings(key=key, value=value))
    db.commit()


@router.get("/settings", response_model=SiteSettingsResponse)
def get_settings(
    _admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    site_name = _get_setting(db, "site_name") or None
    maintenance = _get_setting(db, "maintenance_mode")
    return SiteSettingsResponse(
        site_name=site_name,
        maintenance_mode=maintenance == "true",
    )


@router.patch("/settings", response_model=SiteSettingsResponse)
def update_settings(
    _admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
    body: SiteSettingsUpdate,
):
    if body.site_name is not None:
        _set_setting(db, "site_name", body.site_name or "")
    if body.maintenance_mode is not None:
        _set_setting(db, "maintenance_mode", "true" if body.maintenance_mode else "false")
    return get_settings(_admin, db)


@router.get("/users", response_model=list[UserListResponse])
def list_users(
    _admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    users = db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return [
        UserListResponse(
            id=u.id,
            email=u.email,
            name=u.name,
            is_admin=u.is_admin,
            is_active=u.is_active,
            created_at=u.created_at.isoformat() if u.created_at else "",
        )
        for u in users
    ]


@router.patch("/users/{user_id}", response_model=UserListResponse)
def update_user(
    user_id: int,
    _admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
    body: UserUpdateBody,
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if body.is_admin is not None:
        user.is_admin = body.is_admin
    if body.is_active is not None:
        user.is_active = body.is_active
    db.commit()
    db.refresh(user)
    return UserListResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        is_admin=user.is_admin,
        is_active=user.is_active,
        created_at=user.created_at.isoformat() if user.created_at else "",
    )
