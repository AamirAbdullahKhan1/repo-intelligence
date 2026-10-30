"""
Schemas for Architecture Reconstruction Engine V2.
Supports multi-layer graphs, hierarchical drill-down, separated deployment architecture,
fine-grained relationship types, and rich evidence metadata.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

# Component types across the architecture
ArchitectureNodeType = Literal[
    "client",
    "frontend_app",
    "api_service",
    "mcp_server",
    "worker",
    "serverless_function",
    "database",
    "cache",
    "auth",
    "shared_library",
    "infrastructure",
    "external_service",
]

# Code relationship types
ArchitectureEdgeType = Literal[
    "IMPORTS",
    "CALLS",
    "HANDLES_ROUTE",
    "READS_FROM",
    "WRITES_TO",
    "CONNECTS_TO",
    "PUBLISHES_EVENT",
    "CONSUMES_EVENT",
    "DEPLOYED_AS",
    "TRIGGERS_WORKFLOW",
    "DEPENDS_ON",
]

# Evidence confidence ratings
ConfidenceLevel = Literal["VERIFIED", "INFERRED", "UNKNOWN"]

# Evidence categories
EvidenceCategory = Literal[
    "manifest_declaration",
    "code_ast_pattern",
    "import_reference",
    "config_manifest",
    "heuristic_pattern",
]


class EvidenceMeta(BaseModel):
    file_path: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    evidence_category: EvidenceCategory = "code_ast_pattern"
    extraction_method: str = "static_analysis"
    confidence: ConfidenceLevel = "VERIFIED"
    snippet: Optional[str] = None


class ArchitectureNode(BaseModel):
    id: str
    label: str
    type: ArchitectureNodeType
    category: str = Field(
        description="Logical category: application, compute, storage, security, edge, external"
    )
    technology: Optional[str] = None
    level: int = Field(default=1, description="1=System Overview, 2=Component, 3=Module")
    parent_id: Optional[str] = Field(
        default=None, description="Parent component ID for hierarchical drill-down"
    )
    file_references: List[str] = Field(default_factory=list)
    confidence: ConfidenceLevel = "VERIFIED"
    description: Optional[str] = None
    evidence: Optional[EvidenceMeta] = None
    sub_modules: List[str] = Field(
        default_factory=list, description="Internal routes, tools, or handlers"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ArchitectureEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str
    relationship_type: ArchitectureEdgeType
    confidence: ConfidenceLevel = "VERIFIED"
    evidence_file: Optional[str] = None
    line_number: Optional[int] = None
    evidence: Optional[EvidenceMeta] = None
    description: Optional[str] = None


class WorkflowStep(BaseModel):
    step_number: int
    component_id: str
    component_label: str
    action: str
    file_reference: Optional[str] = None
    line_number: Optional[int] = None
    confidence: ConfidenceLevel = "VERIFIED"


class WorkflowModel(BaseModel):
    id: str
    name: str
    description: str
    trigger: str
    steps: List[WorkflowStep]
    components_involved: List[str]


class DeploymentModel(BaseModel):
    nodes: List[ArchitectureNode] = Field(default_factory=list)
    edges: List[ArchitectureEdge] = Field(default_factory=list)
    pipeline_stages: List[str] = Field(default_factory=list)


class ArchitectureModel(BaseModel):
    repo_name: str
    # Runtime Architecture (System Overview & Component Breakdown)
    nodes: List[ArchitectureNode]
    edges: List[ArchitectureEdge]
    # Execution Workflows
    workflows: List[WorkflowModel]
    # Deployment & CI/CD Architecture (Strictly separated from runtime graph)
    deployment_view: DeploymentModel = Field(default_factory=DeploymentModel)
    explanation: str
    llm_enhanced: bool = False
    model_used: Optional[str] = None
