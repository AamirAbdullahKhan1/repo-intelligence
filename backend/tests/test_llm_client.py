"""Tests for Azure OpenAI client and deterministic fallback behavior."""

from __future__ import annotations

from app.config import Settings
from app.schemas.analysis import RepositoryInventory
from app.services.architecture.builder import ArchitectureBuilder
from app.services.llm.client import AzureLLMService
from tests.test_architecture import _sample_inventory


def test_llm_client_falls_back_when_not_configured() -> None:
    settings = Settings(
        _env_file=None,
        azure_openai_endpoint=None,
        azure_openai_api_key=None,
        azure_openai_api_version=None,
        azure_openai_gpt41_deployment=None,
    )
    inv = _sample_inventory()
    arch = ArchitectureBuilder(inv).build()

    llm = AzureLLMService(settings)
    explanation, enhanced, model_used = llm.enhance_architecture_explanation(arch, inv)

    assert enhanced is False
    assert model_used == "deterministic_synthesizer"
    assert "sample-ecommerce" in explanation


def test_llm_routing_selection() -> None:
    settings = Settings(
        azure_openai_endpoint="https://example.openai.azure.com",
        azure_openai_api_key="mock-key",
        azure_openai_api_version="2024-02-01",
        azure_openai_gpt41_deployment="gpt-41-prod",
        azure_openai_astra_deployment="gpt-6-astra-preview",
    )
    assert settings.llm_configured is True
    assert settings.azure_openai_gpt41_deployment == "gpt-41-prod"
    assert settings.azure_openai_astra_deployment == "gpt-6-astra-preview"

