"""Tests for /api/v1/analyze endpoints."""

from __future__ import annotations

import io
import zipfile
from fastapi.testclient import TestClient


def test_analyze_upload_success(client: TestClient) -> None:
    # Create sample zip
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(
            "main.py",
            "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/health')\ndef h(): return {'ok': True}\n",
        )
        zf.writestr("requirements.txt", "fastapi==0.115.0\n")
    buf.seek(0)

    files = {"file": ("test_project.zip", buf, "application/zip")}
    response = client.post("/api/v1/analyze/upload", files=files)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    inv = data["inventory"]
    assert inv["repo_name"] == "test_project"
    assert inv["source_type"] == "zip"
    assert inv["primary_language"] == "Python"
    assert "FastAPI" in inv["frameworks"]
    assert len(inv["routes"]) == 1
    assert inv["routes"][0]["path"] == "/health"


def test_analyze_upload_reject_non_zip(client: TestClient) -> None:
    files = {"file": ("malicious.exe", io.BytesIO(b"binary"), "application/octet-stream")}
    response = client.post("/api/v1/analyze/upload", files=files)
    assert response.status_code == 422
    assert "Only .zip archives are supported" in response.json()["detail"]


def test_analyze_github_reject_invalid_url(client: TestClient) -> None:
    response = client.post(
        "/api/v1/analyze/github",
        json={"url": "https://notgithub.com/owner/repo"},
    )
    assert response.status_code == 422
    assert "Invalid GitHub repository URL" in response.json()["detail"]
