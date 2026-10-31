"""Presentation responses, independent of the immutable analyzer IPC contract."""
from typing import Any
from pydantic import BaseModel, Field
from app.contracts import Entity

class EntityPage(BaseModel):
    snapshot_id: str
    parent_id: str | None = None
    total: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1,le=60)
    items: list[Entity] = Field(max_length=60)

class RepositoryOverview(BaseModel):
    snapshot_id: str
    languages: dict[str,int]
    frameworks: list[str]
    packages: list[Entity] = Field(max_length=20)
    package_count: int
    packages_truncated: bool
    module_count: int
    entry_point_count: int
    integrations: list[Entity] = Field(max_length=30)
    storage: list[Entity] = Field(max_length=30)
    integration_count: int
    storage_count: int
    infrastructure_count: int
    supported_relationships: int
    unresolved_references: int
    relationship_statuses: dict[str,int]
    coverage: dict[str,int]
    limitations: list[str]

class ToolReport(BaseModel):
    interpreter: str
    prefix: str
    base_prefix: str
    meaning: str
    syft_role: str
    tools: dict[str,dict[str,Any]]
