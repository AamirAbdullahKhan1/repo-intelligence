"""API v1 root router — aggregates all v1 endpoint modules."""

from fastapi import APIRouter

from app.api.v1.endpoints import health, capabilities

router = APIRouter(prefix="/api/v1")
router.include_router(health.router, tags=["Health"])
router.include_router(capabilities.router, tags=["Capabilities"])
