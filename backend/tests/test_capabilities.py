"""Tests for GET /api/v1/capabilities."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_capabilities_returns_200(client: TestClient) -> None:
    response = client.get("/api/v1/capabilities")
    assert response.status_code == 200


def test_capabilities_response_schema(client: TestClient) -> None:
    data = client.get("/api/v1/capabilities").json()
    assert data["service"] == "repo-intelligence-backend"
    assert isinstance(data["capabilities"], list)
    assert len(data["capabilities"]) > 0


def test_capabilities_have_required_fields(client: TestClient) -> None:
    capabilities = client.get("/api/v1/capabilities").json()["capabilities"]
    for cap in capabilities:
        assert "id" in cap
        assert "name" in cap
        assert "description" in cap
        assert cap["status"] in ("implemented", "planned")


def test_implemented_capabilities_present(client: TestClient) -> None:
    capabilities = client.get("/api/v1/capabilities").json()["capabilities"]
    implemented_ids = {c["id"] for c in capabilities if c["status"] == "implemented"}
    assert "health_check" in implemented_ids
    assert "capabilities_discovery" in implemented_ids


def test_planned_capabilities_present(client: TestClient) -> None:
    capabilities = client.get("/api/v1/capabilities").json()["capabilities"]
    planned_ids = {c["id"] for c in capabilities if c["status"] == "planned"}
    assert "github_ingest" in planned_ids
    assert "threat_model" in planned_ids
    assert "pdf_report" in planned_ids
