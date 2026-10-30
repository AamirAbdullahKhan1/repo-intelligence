"""
Azure OpenAI service client for architecture explanation and threat interpretation.
Implements dual-model routing (GPT-4.1 default, GPT-6 Astra escalation)
with strict evidence groundings, credential validation, and graceful deterministic fallback.
"""

from __future__ import annotations

import json
import logging
from typing import Optional, Tuple

from openai import AzureOpenAI

from app.config import Settings, get_settings
from app.schemas.analysis import RepositoryInventory
from app.schemas.architecture import ArchitectureModel

logger = logging.getLogger(__name__)


class AzureLLMService:
    """Manages Azure OpenAI requests for architecture reasoning and threat modeling."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()

    def enhance_architecture_explanation(
        self,
        arch_model: ArchitectureModel,
        inventory: RepositoryInventory,
        escalate: bool = False,
    ) -> Tuple[str, bool, str]:
        """
        Produce a concise, evidence-grounded explanation of the extracted architecture.
        Uses GPT-4.1 by default, or escalates to GPT-6 Astra for complex multi-tier topologies.
        
        Falls back gracefully to the deterministic synthesis if Azure credentials
        are unconfigured or if the remote endpoint is unavailable.
        """
        if not self.settings.llm_configured:
            logger.info("Azure OpenAI credentials not configured; using deterministic baseline.")
            return arch_model.explanation, False, "deterministic_synthesizer"

        deployment = (
            self.settings.azure_openai_astra_deployment
            if escalate and self.settings.azure_openai_astra_deployment
            else self.settings.azure_openai_gpt41_deployment
        )

        if not deployment:
            deployment = self.settings.azure_openai_gpt41_deployment or "gpt-4.1"

        # Prepare sanitized, evidence-grounded payload (no raw secrets, source code, or env variables)
        summary_payload = {
            "repository": inventory.repo_name,
            "primary_language": inventory.primary_language,
            "frameworks": inventory.frameworks,
            "components": [
                {
                    "id": n.id,
                    "label": n.label,
                    "type": n.type,
                    "technology": n.technology,
                    "confidence": n.confidence,
                }
                for n in arch_model.nodes
            ],
            "relationships": [
                {
                    "source": e.source,
                    "target": e.target,
                    "relationship": e.relationship_type,
                    "label": e.label,
                }
                for e in arch_model.edges
            ],
            "routes_sample": [
                {"method": r.method, "path": r.path} for r in inventory.routes[:15]
            ],
            "databases": [d.name for d in inventory.databases],
            "authentication": [a.name for a in inventory.authentication],
            "infrastructure": [i.name for i in inventory.infrastructure],
        }

        system_prompt = (
            "You are a senior software architect and application security engineer. "
            "Explain the architecture of the software repository based STRICTLY on the "
            "provided verified code evidence. "
            "Rules:\n"
            "1. Distinguish verified facts (manifests, routes, drivers) from reasonable inferences.\n"
            "2. Never claim an import relationship alone proves a dynamic execution path.\n"
            "3. Clearly highlight trust boundaries, ingress entry points, and data persistence layers.\n"
            "4. Keep the explanation concise, professional, and formatted in clear markdown.\n"
            "5. Do NOT invent components not present in the provided evidence."
        )

        user_prompt = (
            f"Here is the extracted architecture evidence for repository '{inventory.repo_name}':\n\n"
            f"```json\n{json.dumps(summary_payload, indent=2)}\n```\n\n"
            "Please provide a structured architectural explanation covering:\n"
            "1. Architectural Pattern & Topology\n"
            "2. Ingress & Component Responsibilities\n"
            "3. Data Flow & Security Boundaries\n"
            "4. Key Inferences vs Verified Evidence"
        )

        try:
            client = AzureOpenAI(
                azure_endpoint=self.settings.azure_openai_endpoint or "",
                api_key=self.settings.azure_openai_api_key or "",
                api_version=self.settings.azure_openai_api_version or "2024-02-01",
                timeout=25.0,
            )

            logger.info("Calling Azure OpenAI deployment '%s' for repository '%s'", deployment, inventory.repo_name)
            response = client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=900,
            )

            content = response.choices[0].message.content
            if content and content.strip():
                return content.strip(), True, deployment

        except Exception as e:
            logger.warning("Azure OpenAI call failed; falling back to deterministic explanation: %s", e)

        return arch_model.explanation, False, "deterministic_synthesizer"
