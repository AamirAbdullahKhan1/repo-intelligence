"""
Centralised application settings loaded from environment variables.

LLM credentials are optional at startup. The health endpoint works without
them. LLM-dependent features validate credentials at call time.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    app_env: str = Field(default="development", description="Runtime environment")
    log_level: str = Field(default="INFO", description="Python log level")
    allowed_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="Comma-separated CORS allowed origins",
    )

    # ── Upload limits ─────────────────────────────────────────────────────────
    max_upload_size_bytes: int = Field(
        default=52_428_800,  # 50 MiB
        description="Maximum ZIP upload size in bytes",
    )

    # ── Azure OpenAI (all optional; validated when LLM features are invoked) ─
    azure_openai_endpoint: Optional[str] = Field(default=None)
    azure_openai_api_key: Optional[str] = Field(default=None)
    azure_openai_api_version: Optional[str] = Field(default=None)
    # GPT-4.1 is the default analysis model.
    azure_openai_gpt41_deployment: Optional[str] = Field(default=None)
    # GPT-6 Astra is reserved for complex escalation tasks.
    # API compatibility with the organisation's deployment must be verified
    # before use; it may not share the same parameters as GPT-4.1.
    azure_openai_astra_deployment: Optional[str] = Field(default=None)

    @field_validator("log_level")
    @classmethod
    def _validate_log_level(cls, v: str) -> str:
        level = v.upper()
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if level not in valid:
            raise ValueError(f"log_level must be one of {valid}, got {v!r}")
        return level

    @property
    def parsed_allowed_origins(self) -> List[str]:
        """Return allowed origins as a list."""
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def llm_configured(self) -> bool:
        """True only when all required LLM credentials are present."""
        return all(
            [
                self.azure_openai_endpoint,
                self.azure_openai_api_key,
                self.azure_openai_api_version,
                self.azure_openai_gpt41_deployment,
            ]
        )

    def require_llm_config(self) -> None:
        """Raise RuntimeError if LLM credentials are not fully configured."""
        if not self.llm_configured:
            missing = [
                name
                for name, val in {
                    "AZURE_OPENAI_ENDPOINT": self.azure_openai_endpoint,
                    "AZURE_OPENAI_API_KEY": self.azure_openai_api_key,
                    "AZURE_OPENAI_API_VERSION": self.azure_openai_api_version,
                    "AZURE_OPENAI_GPT41_DEPLOYMENT": self.azure_openai_gpt41_deployment,
                }.items()
                if not val
            ]
            raise RuntimeError(
                f"LLM feature requested but these env vars are not set: {missing}"
            )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings singleton."""
    settings = Settings()
    logging.basicConfig(level=settings.log_level)
    logger.info("Settings loaded. Environment: %s", settings.app_env)
    if not settings.llm_configured:
        logger.warning(
            "Azure OpenAI credentials are not configured. "
            "LLM-dependent features will be unavailable until they are set."
        )
    return settings
