"""
Workspace manager for temporary repository storage.
Provides clean temporary sandboxes that are reliably cleaned up after analysis.
"""

from __future__ import annotations

import logging
from pathlib import Path
import shutil
import tempfile
import uuid

logger = logging.getLogger(__name__)


class Workspace:
    """Manages an isolated temporary directory for repository analysis."""

    def __init__(self, prefix: str = "repo_intel_") -> None:
        self.workspace_id = str(uuid.uuid4())[:8]
        self._temp_dir: Path | None = None
        self._prefix = f"{prefix}{self.workspace_id}_"

    def __enter__(self) -> Path:
        base_dir = Path(tempfile.gettempdir()) / "repo_intelligence_workspaces"
        base_dir.mkdir(parents=True, exist_ok=True)
        self._temp_dir = Path(tempfile.mkdtemp(prefix=self._prefix, dir=str(base_dir)))
        logger.debug("Created temporary workspace at %s", self._temp_dir)
        return self._temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._temp_dir and self._temp_dir.exists():
            try:
                shutil.rmtree(self._temp_dir, ignore_errors=True)
                logger.debug("Cleaned up temporary workspace at %s", self._temp_dir)
            except Exception as e:
                logger.warning("Failed to clean up workspace %s: %e", self._temp_dir, e)
