"""Tests for architecture model construction and workflow generation."""

from __future__ import annotations

from app.schemas.analysis import (
    ComponentFinding,
    Dependency,
    LanguageStat,
    RepositoryInventory,
    RouteFinding,
)
from app.services.architecture.builder import ArchitectureBuilder


def _sample_inventory() -> RepositoryInventory:
    return RepositoryInventory(
        repo_name="sample-ecommerce",
        source_type="github",
        languages=[
            LanguageStat(name="Python", files_count=10, bytes_count=10000, percentage=80.0),
            LanguageStat(name="Dockerfile", files_count=1, bytes_count=500, percentage=20.0),
        ],
        primary_language="Python",
        frameworks=["FastAPI"],
        manifests=["requirements.txt"],
        dependencies=[
            Dependency(name="fastapi", version="0.115.0", source_file="requirements.txt"),
            Dependency(name="sqlalchemy", version="2.0.0", source_file="requirements.txt"),
            Dependency(name="pyjwt", version="2.8.0", source_file="requirements.txt"),
        ],
        entry_points=["app/main.py"],
        routes=[
            RouteFinding(method="GET", path="/items", file="app/main.py", line_number=10),
            RouteFinding(method="POST", path="/login", file="app/main.py", line_number=20),
        ],
        databases=[
            ComponentFinding(
                category="database",
                name="PostgreSQL",
                evidence_type="verified_code_evidence",
                file_references=["app/db.py"],
                details="PostgreSQL driver detected",
            )
        ],
        authentication=[
            ComponentFinding(
                category="authentication",
                name="JWT",
                evidence_type="verified_code_evidence",
                file_references=["app/auth.py"],
                details="pyjwt package",
            )
        ],
        infrastructure=[
            ComponentFinding(
                category="infrastructure",
                name="Docker Containerization",
                evidence_type="verified_code_evidence",
                file_references=["Dockerfile"],
                details="Container definition",
            )
        ],
        total_files=11,
        total_bytes=10500,
        summary="Sample FastAPI service with PostgreSQL and JWT.",
    )


def test_architecture_builder_nodes_and_edges() -> None:
    inv = _sample_inventory()
    builder = ArchitectureBuilder(inv)
    arch = builder.build()

    assert arch.repo_name == "sample-ecommerce"
    node_types = {n.type for n in arch.nodes}
    assert "client" in node_types
    assert "service" in node_types
    assert "database" in node_types
    assert "auth" in node_types
    assert "infrastructure" in node_types

    edge_types = {e.relationship_type for e in arch.edges}
    assert "calls" in edge_types
    assert "reads_writes" in edge_types
    assert "authenticates_with" in edge_types
    assert "deploys_to" in edge_types

    # Verified evidence flags
    db_node = next(n for n in arch.nodes if n.type == "database")
    assert db_node.confidence == "verified_code_evidence"
    assert "app/db.py" in db_node.file_references


def test_architecture_builder_workflows() -> None:
    inv = _sample_inventory()
    builder = ArchitectureBuilder(inv)
    arch = builder.build()

    wf_ids = {w.id for w in arch.workflows}
    assert "wf-http-request" in wf_ids
    assert "wf-auth" in wf_ids
    assert "wf-deployment" in wf_ids

    http_wf = next(w for w in arch.workflows if w.id == "wf-http-request")
    assert len(http_wf.steps) >= 4
    step_actions = [s.action for s in http_wf.steps]
    assert any("ingress" in a.lower() for a in step_actions)
    assert any("jwt" in a.lower() or "bearer" in a.lower() for a in step_actions)
    assert any("postgresql" in a.lower() for a in step_actions)


def test_baseline_explanation_contains_evidence_basis() -> None:
    inv = _sample_inventory()
    builder = ArchitectureBuilder(inv)
    arch = builder.build()

    assert "Evidence Basis" in arch.explanation
    assert "FastAPI" in arch.explanation
    assert "sample-ecommerce" in arch.explanation
