"""
LLM interaction service — PLANNED (Milestone 3).

Routing strategy:
- GPT-4.1  → default model for architecture explanation and threat modelling.
- GPT-6 Astra → escalation model for complex reasoning tasks.

NOTE: API compatibility between these deployments must be verified against
the organisation's Azure OpenAI configuration before use. They may not
support identical parameters or capabilities.

Credentials are validated at call time via Settings.require_llm_config().
No credentials are required for health checks or capability listing.
"""
