"""Tests for application configuration and settings."""

from __future__ import annotations

import pytest

from app.config import Settings


def test_default_settings_are_valid() -> None:
    s = Settings()
    assert s.app_env == "development"
    assert s.log_level == "INFO"
    assert s.max_upload_size_bytes == 52_428_800


def test_parsed_allowed_origins() -> None:
    s = Settings(allowed_origins="http://localhost:5173,http://localhost:3000")
    origins = s.parsed_allowed_origins
    assert "http://localhost:5173" in origins
    assert "http://localhost:3000" in origins


def test_llm_not_configured_by_default() -> None:
    s = Settings(
        _env_file=None,
        azure_openai_endpoint=None,
        azure_openai_api_key=None,
        azure_openai_api_version=None,
        azure_openai_gpt41_deployment=None,
        azure_openai_astra_deployment=None,
    )
    assert s.llm_configured is False


def test_llm_configured_when_all_vars_set() -> None:
    s = Settings(
        _env_file=None,
        azure_openai_endpoint="https://example.openai.azure.com",
        azure_openai_api_key="test-key",
        azure_openai_api_version="2024-02-01",
        azure_openai_gpt41_deployment="gpt-41",
    )
    assert s.llm_configured is True


def test_require_llm_config_raises_when_not_configured() -> None:
    s = Settings(
        _env_file=None,
        azure_openai_endpoint=None,
        azure_openai_api_key=None,
        azure_openai_api_version=None,
        azure_openai_gpt41_deployment=None,
    )
    with pytest.raises(RuntimeError, match="env vars are not set"):
        s.require_llm_config()


def test_invalid_log_level_raises() -> None:
    with pytest.raises(Exception):
        Settings(log_level="INVALID")


def test_log_level_is_case_insensitive() -> None:
    s = Settings(log_level="debug")
    assert s.log_level == "DEBUG"
