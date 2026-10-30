"""
API v1 Endpoints for repository ingestion, deterministic code inventory,
and architecture/workflow model construction.
"""

from __future__ import annotations

import logging
from pathlib import Path
import tempfile

from fastapi import APIRouter, Depends, File, UploadFile

from app.config import Settings, get_settings
from app.core.errors import ValidationError
from app.schemas.analysis import (
    AnalysisResponse,
    AnalyzeGithubRequest,
    RepositoryInventory,
)
from app.schemas.architecture import ArchitectureModel
from app.services.analysis import RepositoryAnalyzer
from app.services.architecture import ArchitectureBuilder
from app.services.llm import AzureLLMService
from app.services.repository import Workspace, clone_github_repo, extract_zip_safely

logger = logging.getLogger(__name__)

router = APIRouter()


def _construct_architecture(
    inventory: RepositoryInventory,
    settings: Settings,
    workspace_dir: Optional[Path] = None,
    escalate: bool = False,
) -> ArchitectureModel:
    """Build the architecture model and attempt evidence-grounded LLM enhancement."""
    builder = ArchitectureBuilder(inventory, workspace_dir=workspace_dir)
    arch_model = builder.build()

    llm = AzureLLMService(settings)
    explanation, llm_enhanced, model_used = llm.enhance_architecture_explanation(
        arch_model, inventory, escalate=escalate
    )
    arch_model.explanation = explanation
    arch_model.llm_enhanced = llm_enhanced
    arch_model.model_used = model_used
    return arch_model


@router.post(
    "/analyze/github",
    response_model=AnalysisResponse,
    summary="Analyze public GitHub repository",
    description=(
        "Clones a public GitHub repository safely, produces a deterministic code inventory, "
        "and constructs a full architecture graph and workflow model."
    ),
)
async def analyze_github(
    payload: AnalyzeGithubRequest,
    settings: Settings = Depends(get_settings),
) -> AnalysisResponse:
    with Workspace(prefix="github_") as workspace_path:
        repo_name = clone_github_repo(payload.url, workspace_path)
        analyzer = RepositoryAnalyzer(workspace_path, repo_name=repo_name, source_type="github")
        inventory = analyzer.analyze()
        arch_model = _construct_architecture(inventory, settings, workspace_dir=workspace_path)
        return AnalysisResponse(status="success", inventory=inventory, architecture=arch_model)


@router.post(
    "/analyze/upload",
    response_model=AnalysisResponse,
    summary="Analyze uploaded ZIP archive",
    description=(
        "Safely extracts a ZIP repository archive with path-traversal protection, "
        "generates a code inventory, and builds the architecture and workflow model."
    ),
)
async def analyze_upload(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
) -> AnalysisResponse:
    filename = file.filename or "archive.zip"
    if not filename.lower().endswith(".zip"):
        raise ValidationError("Only .zip archives are supported.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_file:
        tmp_path = Path(tmp_file.name)
        total_bytes = 0
        try:
            while chunk := await file.read(65536):
                total_bytes += len(chunk)
                if total_bytes > settings.max_upload_size_bytes:
                    raise ValidationError(
                        f"Uploaded file exceeds maximum limit of "
                        f"{settings.max_upload_size_bytes // (1024 * 1024)} MiB."
                    )
                tmp_file.write(chunk)
        except Exception:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
            raise

    try:
        with Workspace(prefix="zip_") as workspace_path:
            extract_zip_safely(
                tmp_path,
                workspace_path,
                max_total_size_bytes=settings.max_upload_size_bytes,
            )
            clean_name = filename.rsplit(".", 1)[0]
            analyzer = RepositoryAnalyzer(workspace_path, repo_name=clean_name, source_type="zip")
            inventory = analyzer.analyze()
            arch_model = _construct_architecture(inventory, settings, workspace_dir=workspace_path)
            return AnalysisResponse(status="success", inventory=inventory, architecture=arch_model)
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
