from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, HttpUrl

from app.api.deps import get_current_user
from app.models.user import User
from app.services.job_fetch import fetch_job_from_url

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


class FetchJobBody(BaseModel):
    url: HttpUrl


@router.post("/fetch")
async def fetch_job(
    body: FetchJobBody,
    user: Annotated[User, Depends(get_current_user)],
):
    result = await fetch_job_from_url(str(body.url))
    return result
