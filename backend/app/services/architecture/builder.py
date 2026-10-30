"""
Deterministic Architecture Model & Workflow Builder.
Constructs component nodes, relationship edges, and workflows from code inventory.
"""

from __future__ import annotations

import logging
from typing import List, Tuple

from app.schemas.analysis import RepositoryInventory
from app.schemas.architecture import (
    ArchitectureEdge,
    ArchitectureModel,
    ArchitectureNode,
    WorkflowModel,
    WorkflowStep,
)

logger = logging.getLogger(__name__)


class ArchitectureBuilder:
    """Transforms a deterministic repository inventory into an architectural graph and workflows."""

    def __init__(self, inventory: RepositoryInventory) -> None:
        self.inventory = inventory

    def build(self) -> ArchitectureModel:
        """Construct the complete architecture graph, workflows, and rule-based baseline explanation."""
        nodes, edges = self._build_graph()
        workflows = self._build_workflows()
        explanation = self._build_baseline_explanation(nodes, edges, workflows)

        return ArchitectureModel(
            repo_name=self.inventory.repo_name,
            nodes=nodes,
            edges=edges,
            workflows=workflows,
            explanation=explanation,
            llm_enhanced=False,
            model_used="deterministic_synthesizer",
        )

    def _build_graph(self) -> Tuple[List[ArchitectureNode], List[ArchitectureEdge]]:
        nodes: List[ArchitectureNode] = []
        edges: List[ArchitectureEdge] = []

        # 1. External Client Node
        client_id = "node-client"
        nodes.append(
            ArchitectureNode(
                id=client_id,
                label="External Client / User",
                type="client",
                category="client",
                technology="HTTP / Web Browser",
                confidence="reasonable_inference",
                description="End-user web browser, mobile client, or external consumer initiating requests.",
            )
        )

        # 2. Main API Service / Web Application Node
        service_id = "node-api-service"
        framework_label = (
            ", ".join(self.inventory.frameworks)
            if self.inventory.frameworks
            else (self.inventory.primary_language or "Application Service")
        )
        service_desc = (
            f"Core service handling HTTP routing and application logic. "
            f"Exposes {len(self.inventory.routes)} discovered routes."
        )
        nodes.append(
            ArchitectureNode(
                id=service_id,
                label=f"{self.inventory.repo_name} Service",
                type="service",
                category="backend_service",
                technology=framework_label,
                file_references=self.inventory.entry_points[:5],
                confidence="verified_code_evidence",
                description=service_desc,
                metadata={
                    "routes_count": len(self.inventory.routes),
                    "entry_points": self.inventory.entry_points,
                    "primary_language": self.inventory.primary_language,
                },
            )
        )

        # Edge: Client -> API Service
        edges.append(
            ArchitectureEdge(
                id=f"edge-{client_id}-{service_id}",
                source=client_id,
                target=service_id,
                label="HTTP Ingress",
                relationship_type="calls",
                confidence="verified_code_evidence" if self.inventory.routes else "reasonable_inference",
                description=f"Inbound requests dispatched to {len(self.inventory.routes)} routes.",
            )
        )

        # 3. Authentication Node (if detected)
        auth_id = None
        if self.inventory.authentication:
            auth_id = "node-auth"
            auth_names = [a.name for a in self.inventory.authentication]
            auth_files = [f for a in self.inventory.authentication for f in a.file_references]
            nodes.append(
                ArchitectureNode(
                    id=auth_id,
                    label="Authentication & Identity",
                    type="auth",
                    category="security_control",
                    technology=", ".join(auth_names),
                    file_references=list(set(auth_files))[:5],
                    confidence="verified_code_evidence",
                    description=f"Token verification and credential handling ({', '.join(auth_names)}).",
                )
            )

            # Edge: API Service -> Auth Node
            edges.append(
                ArchitectureEdge(
                    id=f"edge-{service_id}-{auth_id}",
                    source=service_id,
                    target=auth_id,
                    label="Authenticates Request",
                    relationship_type="authenticates_with",
                    confidence="verified_code_evidence",
                    evidence_file=auth_files[0] if auth_files else None,
                    description="Middleware or route dependencies enforce token or session validation.",
                )
            )

        # 4. Database Nodes
        for idx, db in enumerate(self.inventory.databases):
            db_id = f"node-db-{idx + 1}"
            nodes.append(
                ArchitectureNode(
                    id=db_id,
                    label=f"{db.name} Store",
                    type="database",
                    category="data_store",
                    technology=db.name,
                    file_references=db.file_references[:5],
                    confidence="verified_code_evidence",
                    description=db.details or f"Persistent storage for application models and state.",
                )
            )

            # Edge: API Service -> Database
            edges.append(
                ArchitectureEdge(
                    id=f"edge-{service_id}-{db_id}",
                    source=service_id,
                    target=db_id,
                    label="Queries & Persists",
                    relationship_type="reads_writes",
                    confidence="verified_code_evidence",
                    evidence_file=db.file_references[0] if db.file_references else None,
                    description=f"Direct database queries and transactions over {db.name}.",
                )
            )

        # 5. Infrastructure Nodes (Containers / CI-CD)
        for idx, inf in enumerate(self.inventory.infrastructure):
            inf_id = f"node-infra-{idx + 1}"
            nodes.append(
                ArchitectureNode(
                    id=inf_id,
                    label=inf.name,
                    type="infrastructure",
                    category="infrastructure",
                    technology=inf.name,
                    file_references=inf.file_references[:5],
                    confidence="verified_code_evidence",
                    description=inf.details or "Infrastructure definition.",
                )
            )

            # Edge: Infrastructure -> Service
            edges.append(
                ArchitectureEdge(
                    id=f"edge-{inf_id}-{service_id}",
                    source=inf_id,
                    target=service_id,
                    label="Deploys / Manages",
                    relationship_type="deploys_to",
                    confidence="verified_code_evidence",
                    evidence_file=inf.file_references[0] if inf.file_references else None,
                    description=f"Specifies build and runtime deployment for {self.inventory.repo_name}.",
                )
            )

        return nodes, edges

    def _build_workflows(self) -> List[WorkflowModel]:
        workflows: List[WorkflowModel] = []
        repo_name = self.inventory.repo_name
        service_label = f"{repo_name} Service"

        # Workflow 1: Standard HTTP Request Execution Flow
        req_steps = [
            WorkflowStep(
                step_number=1,
                component_id="node-client",
                component_label="External Client",
                action="Client dispatches HTTP request to application ingress.",
                confidence="reasonable_inference",
            ),
            WorkflowStep(
                step_number=2,
                component_id="node-api-service",
                component_label=service_label,
                action=(
                    f"Router parses path and method across {len(self.inventory.routes)} registered route(s)."
                ),
                file_reference=self.inventory.entry_points[0] if self.inventory.entry_points else None,
                confidence="verified_code_evidence" if self.inventory.routes else "reasonable_inference",
            ),
        ]

        if self.inventory.authentication:
            auth_name = self.inventory.authentication[0].name
            auth_file = self.inventory.authentication[0].file_references[0] if self.inventory.authentication[0].file_references else None
            req_steps.append(
                WorkflowStep(
                    step_number=len(req_steps) + 1,
                    component_id="node-auth",
                    component_label="Authentication & Identity",
                    action=f"Validates caller credentials or bearer token ({auth_name}).",
                    file_reference=auth_file,
                    confidence="verified_code_evidence",
                )
            )

        if self.inventory.databases:
            db_name = self.inventory.databases[0].name
            db_file = self.inventory.databases[0].file_references[0] if self.inventory.databases[0].file_references else None
            req_steps.append(
                WorkflowStep(
                    step_number=len(req_steps) + 1,
                    component_id="node-db-1",
                    component_label=f"{db_name} Store",
                    action=f"Executes query / transactional update against {db_name}.",
                    file_reference=db_file,
                    confidence="verified_code_evidence",
                )
            )

        req_steps.append(
            WorkflowStep(
                step_number=len(req_steps) + 1,
                component_id="node-api-service",
                component_label=service_label,
                action="Serializes response payload and returns HTTP response to client.",
                confidence="reasonable_inference",
            )
        )

        workflows.append(
            WorkflowModel(
                id="wf-http-request",
                name="HTTP Ingress & Request Lifecycle",
                description="Standard request lifecycle from external ingress through routing, security verification, and data persistence.",
                trigger="Inbound HTTP Request",
                steps=req_steps,
                components_involved=[s.component_label for s in req_steps],
            )
        )

        # Workflow 2: Authentication Flow (if auth patterns present)
        if self.inventory.authentication:
            auth_findings = self.inventory.authentication[0]
            workflows.append(
                WorkflowModel(
                    id="wf-auth",
                    name="Identity & Access Lifecycle",
                    description="Handles authentication requests, token verification, and security boundary enforcement.",
                    trigger="Authentication Credential Challenge",
                    steps=[
                        WorkflowStep(
                            step_number=1,
                            component_id="node-client",
                            component_label="External Client",
                            action="Submits credentials or session authorization header.",
                            confidence="reasonable_inference",
                        ),
                        WorkflowStep(
                            step_number=2,
                            component_id="node-api-service",
                            component_label=service_label,
                            action="Interceps request via middleware / dependency injection.",
                            confidence="reasonable_inference",
                        ),
                        WorkflowStep(
                            step_number=3,
                            component_id="node-auth",
                            component_label="Authentication & Identity",
                            action=f"Validates cryptographic signature or password hash using {auth_findings.name}.",
                            file_reference=auth_findings.file_references[0] if auth_findings.file_references else None,
                            confidence="verified_code_evidence",
                        ),
                    ],
                    components_involved=["External Client", service_label, "Authentication & Identity"],
                )
            )

        # Workflow 3: CI/CD & Deployment Pipeline (if Docker/Actions detected)
        if self.inventory.infrastructure:
            workflows.append(
                WorkflowModel(
                    id="wf-deployment",
                    name="Continuous Integration & Deployment Pipeline",
                    description="Automated build, test verification, containerization, and deployment lifecycle.",
                    trigger="Git Commit / Branch Merge",
                    steps=[
                        WorkflowStep(
                            step_number=1,
                            component_id="node-infra-1",
                            component_label="Infrastructure / CI",
                            action="Automated CI pipeline triggers on repository changes.",
                            file_reference=self.inventory.infrastructure[0].file_references[0] if self.inventory.infrastructure[0].file_references else None,
                            confidence="verified_code_evidence",
                        ),
                        WorkflowStep(
                            step_number=2,
                            component_id="node-api-service",
                            component_label=service_label,
                            action="Builds container image and packages application dependencies.",
                            confidence="verified_code_evidence",
                        ),
                    ],
                    components_involved=["Infrastructure / CI", service_label],
                )
            )

        return workflows

    def _build_baseline_explanation(
        self,
        nodes: List[ArchitectureNode],
        edges: List[ArchitectureEdge],
        workflows: List[WorkflowModel],
    ) -> str:
        """Produce an evidence-grounded architectural narrative without LLM hallucination."""
        fw_text = (
            ", ".join(self.inventory.frameworks)
            if self.inventory.frameworks
            else self.inventory.primary_language or "custom software"
        )
        db_text = (
            f"with persistent storage managed by {', '.join(d.name for d in self.inventory.databases)}"
            if self.inventory.databases
            else "with no dedicated database driver explicitly identified"
        )
        auth_text = (
            f"Authentication controls are backed by {', '.join(a.name for a in self.inventory.authentication)}."
            if self.inventory.authentication
            else "No standard centralized authentication middleware was detected in manifests."
        )

        lines = [
            f"### Architecture Overview for {self.inventory.repo_name}",
            f"The repository is structured as a {self.inventory.primary_language or 'multi-language'} service built primarily with {fw_text}, {db_text}.",
            "",
            "#### Discovered Components & Trust Boundaries:",
            f"- **Core Service:** `{self.inventory.repo_name} Service` handles inbound traffic across {len(self.inventory.routes)} discovered HTTP endpoints.",
            f"- **Security & Access Control:** {auth_text}",
            f"- **Data Layer:** Identified {len(self.inventory.databases)} data store component(s).",
            f"- **Infrastructure:** {len(self.inventory.infrastructure)} infrastructure configuration(s) identified for containerization and CI/CD.",
            "",
            "#### Primary Workflow Execution:",
            f"The primary request workflow traverses from external clients into the application routing layer, invoking security validation and data persistence before dispatching responses.",
            "",
            "> **Evidence Basis:** Grounded directly in static manifest entries, AST patterns, and file declarations. Import relationships indicate code dependencies, not dynamic runtime paths.",
        ]
        return "\n".join(lines)
