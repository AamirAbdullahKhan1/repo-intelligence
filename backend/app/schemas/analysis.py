"""
Schemas for repository analysis and deterministic code inventory.
"""

from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class AnalyzeGithubRequest(BaseModel):
    url: str = Field(
        ...,
        description="Public GitHub repository URL (e.g., https://github.com/owner/repo)",
        json_schema_extra={"example": "https://github.com/fastapi/fastapi"},
    )


class LanguageStat(BaseModel):
    name: str
    files_count: int
    bytes_count: int
    percentage: float = Field(description="Percentage of total code bytes (0-100)")


class Dependency(BaseModel):
    name: str
    version: Optional[str] = None
    source_file: str
    is_dev: bool = False


class RouteFinding(BaseModel):
    method: str
    path: str
    file: str
    line_number: Optional[int] = None


class ComponentFinding(BaseModel):
    category: str = Field(description="framework, database, authentication, infrastructure")
    name: str
    evidence_type: Literal["verified_code_evidence", "reasonable_inference", "unknown"] = (
        "verified_code_evidence"
    )
    file_references: List[str] = Field(default_factory=list)
    details: Optional[str] = None


class RepositoryInventory(BaseModel):
    repo_name: str
    source_type: Literal["github", "zip"]
    languages: List[LanguageStat]
    primary_language: Optional[str] = None
    frameworks: List[str]
    manifests: List[str]
    dependencies: List[Dependency]
    entry_points: List[str]
    routes: List[RouteFinding]
    databases: List[ComponentFinding]
    authentication: List[ComponentFinding]
    infrastructure: List[ComponentFinding]
    total_files: int
    total_bytes: int
    summary: str


from app.schemas.architecture import ArchitectureModel


class AnalysisResponse(BaseModel):
    status: Literal["success"] = "success"
    inventory: RepositoryInventory
    architecture: ArchitectureModel
