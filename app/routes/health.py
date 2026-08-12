from fastapi import APIRouter
from app.config import get_settings

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
    }
