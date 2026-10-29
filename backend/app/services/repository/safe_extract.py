"""
Safe ZIP archive extraction with path traversal (Zip-Slip) protection,
file size limits, and symlink rejections.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
import zipfile

from app.core.errors import AppError, ValidationError

logger = logging.getLogger(__name__)

# Extensions / paths to exclude from analysis to prevent denial of service
IGNORED_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".idea",
    ".vscode",
    ".pytest_cache",
    ".mypy_cache",
    "dist",
    "build",
}


class ZipExtractionError(AppError):
    status_code = 400
    error_code = "zip_extraction_error"


def extract_zip_safely(
    zip_source: str | Path | zipfile.ZipFile,
    target_dir: Path,
    max_total_size_bytes: int = 52_428_800,  # 50 MiB limit
    max_file_count: int = 5_000,
) -> int:
    """
    Safely extract a ZIP archive into target_dir.

    Protections applied:
    - Path traversal (Zip-Slip): Canonical destination path must reside strictly inside target_dir.
    - Symlinks / Hardlinks: Rejected to prevent reading arbitrary system files.
    - Zip Bomb mitigation: Enforces maximum total uncompressed bytes and maximum file count.
    
    Returns the count of extracted files.
    """
    target_dir = target_dir.resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    def _process_zip(zf: zipfile.ZipFile) -> int:
        total_uncompressed_bytes = 0
        extracted_count = 0

        infolist = zf.infolist()
        if len(infolist) > max_file_count:
            raise ZipExtractionError(
                f"Archive contains {len(infolist)} files, exceeding the limit of {max_file_count}."
            )

        for member in infolist:
            # Check for zip bomb size accumulation
            total_uncompressed_bytes += member.file_size
            if total_uncompressed_bytes > max_total_size_bytes:
                raise ZipExtractionError(
                    f"Archive uncompressed size exceeds limit of {max_total_size_bytes // (1024 * 1024)} MiB."
                )

            # Prevent Zip-Slip: resolve final path and verify prefix
            normalized_name = os.path.normpath(member.filename)
            if normalized_name.startswith("..") or os.path.isabs(normalized_name):
                raise ZipExtractionError(
                    f"Malicious path detected in archive: {member.filename}"
                )

            dest_path = (target_dir / normalized_name).resolve()
            if not str(dest_path).startswith(str(target_dir)):
                raise ZipExtractionError(
                    f"Path traversal attempted in archive entry: {member.filename}"
                )

            # Check for symlinks in zip attributes (Unix file attributes upper 16 bits)
            mode = member.external_attr >> 16
            if mode & 0o120000 == 0o120000:  # S_IFLNK
                logger.warning("Ignoring symlink in zip: %s", member.filename)
                continue

            # Skip entries from unwanted top-level/nested vendor directories
            path_parts = Path(normalized_name).parts
            if any(part in IGNORED_DIRS for part in path_parts):
                continue

            if member.is_dir():
                dest_path.mkdir(parents=True, exist_ok=True)
            else:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as src, open(dest_path, "wb") as dst:
                    # Stream in chunks
                    while chunk := src.read(65536):
                        dst.write(chunk)
                extracted_count += 1

        return extracted_count

    if isinstance(zip_source, zipfile.ZipFile):
        return _process_zip(zip_source)

    try:
        with zipfile.ZipFile(zip_source, "r") as zf:
            return _process_zip(zf)
    except zipfile.BadZipFile as e:
        raise ZipExtractionError(f"Uploaded file is not a valid ZIP archive: {e}") from e
