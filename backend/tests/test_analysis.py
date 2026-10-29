"""Tests for deterministic repository code analysis."""

from __future__ import annotations

from pathlib import Path

from app.services.analysis.inventory import RepositoryAnalyzer


def test_repository_analyzer_fastapi_fixture(tmp_path: Path) -> None:
    # Set up mock repository structure
    repo_dir = tmp_path / "mock_repo"
    repo_dir.mkdir()

    # Requirements
    reqs = repo_dir / "requirements.txt"
    reqs.write_text("fastapi==0.115.0\nsqlalchemy>=2.0.0\npyjwt>=2.8.0\npsycopg2-binary\n")

    # Main app file
    main_py = repo_dir / "main.py"
    main_py.write_text(
        "from fastapi import FastAPI\n"
        "import jwt\n"
        "import sqlalchemy\n"
        "\n"
        "app = FastAPI()\n"
        "\n"
        "@app.get('/api/users')\n"
        "def get_users():\n"
        "    return []\n"
        "\n"
        "@app.post('/api/auth/login')\n"
        "def login():\n"
        "    return {'token': 'xyz'}\n"
    )

    # Dockerfile
    dockerfile = repo_dir / "Dockerfile"
    dockerfile.write_text("FROM python:3.11\nWORKDIR /app\nCMD ['uvicorn', 'main:app']\n")

    # Docker compose
    compose = repo_dir / "docker-compose.yml"
    compose.write_text("version: '3.8'\nservices:\n  web:\n    build: .\n")

    analyzer = RepositoryAnalyzer(repo_dir, repo_name="mock_fastapi", source_type="zip")
    inventory = analyzer.analyze()

    assert inventory.repo_name == "mock_fastapi"
    assert inventory.source_type == "zip"
    assert inventory.primary_language == "Python"
    assert "FastAPI" in inventory.frameworks
    assert "requirements.txt" in inventory.manifests

    # Dependencies
    dep_names = {d.name for d in inventory.dependencies}
    assert "fastapi" in dep_names
    assert "sqlalchemy" in dep_names
    assert "pyjwt" in dep_names

    # Entry points
    assert "main.py" in inventory.entry_points
    assert any("Dockerfile" in ep for ep in inventory.entry_points)

    # Routes
    route_paths = {r.path for r in inventory.routes}
    assert "/api/users" in route_paths
    assert "/api/auth/login" in route_paths

    # Databases
    db_names = {d.name for d in inventory.databases}
    assert "SQLAlchemy" in db_names
    assert "PostgreSQL" in db_names

    # Authentication
    auth_names = {a.name for a in inventory.authentication}
    assert "JWT" in auth_names

    # Infrastructure
    infra_names = {i.name for i in inventory.infrastructure}
    assert "Docker Containerization" in infra_names
    assert "Docker Compose" in infra_names
