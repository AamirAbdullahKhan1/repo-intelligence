"""Tests for GET /api/v1/health."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_returns_200(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_response_schema(client: TestClient) -> None:
    data = client.get("/api/v1/health").json()
    assert data["service"] == "repo-intelligence-backend"
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data


def test_health_does_not_require_llm_credentials(client: TestClient) -> None:
    """Health check must succeed even without Azure OpenAI env vars set."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
