from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/version")
def version():
    return {"version": "0.1.0"}
