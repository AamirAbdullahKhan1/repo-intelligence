"""Versioned worker records and API contracts; JSON Schema is generated from here."""
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

class Record(BaseModel):
    model_config = ConfigDict(extra='allow')
    id: str

class Entity(Record):
    kind: str
    label: str
    evidence_ids: list[str] = Field(default_factory=list)

class Evidence(Record):
    file: str
    start: int = Field(ge=0)
    end: int = Field(ge=0)
    line: int = Field(ge=1)
    column: int = Field(ge=1)
    sha256: str = Field(pattern=r'^[a-f0-9]{64}$')
    rule: str

class Edge(Record):
    source: str
    target: str
    kind: str
    evidence_ids: list[str] = Field(min_length=1)

class Graph(BaseModel):
    model_config = ConfigDict(extra='allow')
    schema_version: Literal['repo-intelligence-1']
    snapshot_id: str = Field(pattern=r'^[a-f0-9]{64}$')
    repository: str
    entities: list[Entity] = Field(max_length=150000)
    edges: list[Edge] = Field(max_length=150000)
    evidence: list[Evidence] = Field(max_length=300000)
    unknowns: list[dict[str, Any]]
    coverage: dict[str, Any]

class GithubInput(BaseModel):
    url: str = Field(max_length=300)

class Job(BaseModel):
    id: str
    status: Literal['queued', 'running', 'complete', 'failed', 'cancelled']
    phase: str
    progress: int
    created_at: str
    snapshot_id: str | None = None
    error: str | None = None

class Analysis(BaseModel):
    snapshot_id: str
    repository: str
    created_at: str
    provenance: dict[str, Any]
    coverage: dict[str, Any]
    counts: dict[str, int]
    unknown_counts: dict[str, int]
    scope: dict[str, Any]
    tools: dict[str, Any]
    inventory: dict[str, Any]
    diagnostics: list[dict[str, Any]]

class View(BaseModel):
    snapshot_id: str
    kind: Literal['system', 'workflow']
    nodes: list[Entity]
    edges: list[Edge]
    metadata: dict[str, Any]

class EvidenceResponse(BaseModel):
    snapshot_id: str
    record: dict[str, Any]
    evidence: list[Evidence]
    truncated: bool
