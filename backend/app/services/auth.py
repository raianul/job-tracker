from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.user import User
from app.schemas.user import UserResponse

settings = get_settings()


def get_or_create_user(
    db: Session,
    *,
    email: str,
    name: str | None,
    avatar_url: str | None,
    provider: str,
    provider_id: str,
) -> User:
    email = email.lower().strip()
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.name = name or user.name
        user.avatar_url = avatar_url or user.avatar_url
        user.provider = provider
        user.provider_id = provider_id
        if email in settings.admin_emails_list:
            user.is_admin = True
        db.commit()
        db.refresh(user)
        return user
    is_admin = email in settings.admin_emails_list
    user = User(
        email=email,
        name=name,
        avatar_url=avatar_url,
        provider=provider,
        provider_id=provider_id,
        is_admin=is_admin,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def user_to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        avatar_url=user.avatar_url,
        provider=user.provider,
        is_admin=user.is_admin,
        is_active=user.is_active,
    )
