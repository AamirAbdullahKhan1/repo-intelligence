"""
Centralised error types and FastAPI exception handlers.

All handled application errors return a consistent JSON envelope:
  { "error": "<short code>", "detail": "<human-readable message>" }
"""

from __future__ import annotations

import logging

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base class for application-defined errors."""

    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class NotFoundError(AppError):
    status_code = 404
    error_code = "not_found"


class ValidationError(AppError):
    status_code = 422
    error_code = "validation_error"


class LLMNotConfiguredError(AppError):
    status_code = 503
    error_code = "llm_not_configured"

    def __init__(self) -> None:
        super().__init__(
            "Azure OpenAI credentials are not configured on this server. "
            "Set the required environment variables and restart the service."
        )


def _error_body(error_code: str, detail: str) -> dict:
    return {"error": error_code, "detail": detail}


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    logger.warning("Handled application error [%s]: %s", exc.error_code, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.error_code, exc.detail),
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content=_error_body("internal_error", "An unexpected error occurred."),
    )
