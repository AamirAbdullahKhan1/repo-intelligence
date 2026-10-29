"""GET /api/v1/health — lightweight liveness check."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.schemas.health import HealthResponse

router = APIRouter()

APP_VERSION = "0.1.0"


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """
    Returns HTTP 200 with a brief service descriptor when the application is
    running.  Does not require Azure OpenAI credentials to succeed.
    """
    return HealthResponse(
        service="repo-intelligence-backend",
        status="ok",
        version=APP_VERSION,
        environment=settings.app_env,
    )
