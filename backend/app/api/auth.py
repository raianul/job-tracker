from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.httpx_client import AsyncOAuth2Client
from httpx import AsyncClient

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.user import TokenResponse, UserResponse
from app.services.auth import get_or_create_user, user_to_response
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["auth"])


class DevLoginBody(BaseModel):
    email: str = "dev@example.com"


@router.post("/dev-login", response_model=TokenResponse)
def dev_login(
    body: DevLoginBody,
    db: Annotated[Session, Depends(get_db)],
):
    """Create or get a user and return JWT. Only if ADMIN_EMAILS is set (dev mode)."""
    if not settings.admin_emails_list:
        raise HTTPException(status_code=404, detail="Dev login disabled")
    user = get_or_create_user(
        db,
        email=body.email.strip().lower(),
        name="Dev User",
        avatar_url=None,
        provider="google",
        provider_id=body.email,
    )
    access_token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=access_token, user=user_to_response(user))
settings = get_settings()

GOOGLE_AUTHORIZE = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO = "https://www.googleapis.com/oauth2/v2/userinfo"
LINKEDIN_AUTHORIZE = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_USERINFO = "https://api.linkedin.com/v2/userinfo"


@router.get("/me", response_model=UserResponse)
def me(user: Annotated[User, Depends(get_current_user)]):
    return user_to_response(user)


def _backend_callback_url() -> str:
    return f"{settings.backend_origin}/api/auth/callback"


@router.get("/google")
def google_login():
    if not settings.google_client_id:
        raise HTTPException(status_code=503, detail="Google login not configured")
    redirect_uri = _backend_callback_url()
    client = AsyncOAuth2Client(
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        redirect_uri=redirect_uri,
    )
    url, _ = client.create_authorization_url(
        GOOGLE_AUTHORIZE,
        scope="openid email profile",
        state="google",
    )
    return RedirectResponse(url=url)


@router.get("/linkedin")
def linkedin_login():
    if not settings.linkedin_client_id:
        raise HTTPException(status_code=503, detail="LinkedIn login not configured")
    redirect_uri = _backend_callback_url()
    client = AsyncOAuth2Client(
        client_id=settings.linkedin_client_id,
        client_secret=settings.linkedin_client_secret,
        redirect_uri=redirect_uri,
    )
    url, _ = client.create_authorization_url(
        LINKEDIN_AUTHORIZE,
        scope="openid profile email",
        state="linkedin",
    )
    return RedirectResponse(url=url)


@router.get("/callback")
async def auth_callback(
    code: str,
    state: str,
    db: Annotated[Session, Depends(get_db)],
):
    redirect_uri = _backend_callback_url()
    if state == "google":
        if not settings.google_client_id:
            raise HTTPException(status_code=503, detail="Google login not configured")
        client = AsyncOAuth2Client(
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            redirect_uri=redirect_uri,
        )
        token = await client.fetch_token(
            GOOGLE_TOKEN,
            code=code,
            redirect_uri=redirect_uri,
        )
        async with AsyncClient() as http:
            r = await http.get(
                GOOGLE_USERINFO,
                headers={"Authorization": f"Bearer {token['access_token']}"},
            )
            r.raise_for_status()
            data = r.json()
        email = data.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Google")
        user = get_or_create_user(
            db,
            email=email,
            name=data.get("name"),
            avatar_url=data.get("picture"),
            provider="google",
            provider_id=data.get("id", ""),
        )
    elif state == "linkedin":
        if not settings.linkedin_client_id:
            raise HTTPException(status_code=503, detail="LinkedIn login not configured")
        client = AsyncOAuth2Client(
            client_id=settings.linkedin_client_id,
            client_secret=settings.linkedin_client_secret,
            redirect_uri=redirect_uri,
        )
        token = await client.fetch_token(
            LINKEDIN_TOKEN,
            code=code,
            redirect_uri=redirect_uri,
        )
        async with AsyncClient() as http:
            r = await http.get(
                LINKEDIN_USERINFO,
                headers={"Authorization": f"Bearer {token['access_token']}"},
            )
            r.raise_for_status()
            data = r.json()
        email = data.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by LinkedIn")
        user = get_or_create_user(
            db,
            email=email,
            name=data.get("name"),
            avatar_url=data.get("picture"),
            provider="linkedin",
            provider_id=data.get("sub", ""),
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid state")
    access_token = create_access_token(data={"sub": str(user.id)})
    # Redirect to frontend with token in fragment (not sent to server logs)
    return RedirectResponse(
        url=f"{settings.frontend_url}/auth/callback#token={access_token}",
        status_code=302,
    )
