"""
Azure OpenAI interaction service.
Provides model routing between GPT-4.1 (default) and GPT-6 Astra (escalation)
with strict evidence groundings and deterministic fallback.
"""

from app.services.llm.client import AzureLLMService

__all__ = ["AzureLLMService"]
