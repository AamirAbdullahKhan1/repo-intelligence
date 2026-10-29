"""GET /api/v1/capabilities — describes platform capabilities and their status."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.capabilities import Capability, CapabilitiesResponse

router = APIRouter()

_CAPABILITIES: list[Capability] = [
    Capability(
        id="health_check",
        name="Health Check",
        description="Liveness endpoint confirming the API is reachable.",
        status="implemented",
    ),
    Capability(
        id="capabilities_discovery",
        name="Capabilities Discovery",
        description="Structured list of implemented and planned platform features.",
        status="implemented",
    ),
    Capability(
        id="github_ingest",
        name="GitHub Repository Ingestion",
        description=(
            "Clone a public GitHub repository into a secure temporary workspace "
            "using single-branch shallow cloning with hooks disabled."
        ),
        status="implemented",
    ),
    Capability(
        id="zip_ingest",
        name="ZIP Archive Ingestion",
        description=(
            "Accept an uploaded ZIP archive, validate file type and size, "
            "and extract it safely with Zip-Slip path-traversal protection."
        ),
        status="implemented",
    ),
    Capability(
        id="repo_inventory",
        name="Repository Inventory",
        description=(
            "Identify languages, frameworks, manifests, entry points, routes, "
            "dependencies, database access, authentication, and infrastructure."
        ),
        status="implemented",
    ),
    Capability(
        id="architecture_model",
        name="Architecture Model Construction",
        description=(
            "Build a structured model of components, relationships, and "
            "data-flow edges from deterministic code analysis."
        ),
        status="planned",
    ),
    Capability(
        id="llm_interpretation",
        name="LLM-Assisted Architecture Explanation",
        description=(
            "Use Azure OpenAI (GPT-4.1 by default; GPT-6 Astra for complex "
            "escalations) to produce a concise, evidence-grounded explanation "
            "of the extracted architecture."
        ),
        status="planned",
    ),
    Capability(
        id="threat_model",
        name="Preliminary Threat Model",
        description=(
            "Generate evidence-linked threats and prioritised SDLC security "
            "recommendations. Findings distinguish verified code evidence, "
            "reasonable inferences, and unknowns."
        ),
        status="planned",
    ),
    Capability(
        id="pdf_report",
        name="PDF Report Export",
        description=(
            "Produce a professionally formatted, evidence-backed PDF security "
            "assessment report using ReportLab."
        ),
        status="planned",
    ),
]


@router.get(
    "/capabilities",
    response_model=CapabilitiesResponse,
    summary="Platform capabilities",
)
async def capabilities() -> CapabilitiesResponse:
    """
    Returns a structured description of all platform capabilities.
    Each capability clearly indicates whether it is already implemented
    or is planned for a future milestone.
    """
    return CapabilitiesResponse(
        service="repo-intelligence-backend",
        capabilities=_CAPABILITIES,
    )
