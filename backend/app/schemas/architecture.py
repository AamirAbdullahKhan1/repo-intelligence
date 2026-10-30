"""
Schemas for architecture graphs, component nodes, relationships, and workflows.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class ArchitectureNode(BaseModel):
    id: str
    label: str
    type: Literal[
        "client",
        "api_gateway",
        "service",
        "database",
        "auth",
        "worker",
        "infrastructure",
        "external",
    ]
    category: str
    technology: Optional[str] = None
    file_references: List[str] = Field(default_factory=list)
    confidence: Literal["verified_code_evidence", "reasonable_inference", "unknown"] = (
        "verified_code_evidence"
    )
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ArchitectureEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str
    relationship_type: Literal[
        "calls",
        "authenticates_with",
        "reads_writes",
        "depends_on",
        "deploys_to",
    ]
    confidence: Literal["verified_code_evidence", "reasonable_inference", "unknown"] = (
        "verified_code_evidence"
    )
    evidence_file: Optional[str] = None
    description: Optional[str] = None


class WorkflowStep(BaseModel):
    step_number: int
    component_id: str
    component_label: str
    action: str
    file_reference: Optional[str] = None
    confidence: Literal["verified_code_evidence", "reasonable_inference", "unknown"] = (
        "verified_code_evidence"
    )


class WorkflowModel(BaseModel):
    id: str
    name: str
    description: str
    trigger: str
    steps: List[WorkflowStep]
    components_involved: List[str]


class ArchitectureModel(BaseModel):
    repo_name: str
    nodes: List[ArchitectureNode]
    edges: List[ArchitectureEdge]
    workflows: List[WorkflowModel]
    explanation: str
    llm_enhanced: bool = False
    model_used: Optional[str] = None

