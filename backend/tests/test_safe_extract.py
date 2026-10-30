"""Tests for safe ZIP archive extraction and path-traversal protection."""

from __future__ import annotations

import io
from pathlib import Path
import zipfile
import pytest

from app.services.repository.safe_extract import ZipExtractionError, extract_zip_safely


def test_extract_valid_zip(tmp_path: Path) -> None:
    # Build in-memory valid zip
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("src/main.py", "print('hello world')\n")
        zf.writestr("README.md", "# Test Repo\n")
    buf.seek(0)

    target = tmp_path / "extracted"
    count = extract_zip_safely(buf, target)
    assert count == 2
    assert (target / "src" / "main.py").exists()
    assert (target / "README.md").exists()
    assert (target / "src" / "main.py").read_text() == "print('hello world')\n"


def test_reject_zip_slip_path_traversal(tmp_path: Path) -> None:
    # Build zip with traversal path
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        # Zip slip attack attempt
        zf.writestr("../evil.txt", "malicious payload")
    buf.seek(0)

    target = tmp_path / "extracted"
    with pytest.raises(ZipExtractionError, match="Malicious path|Path traversal"):
        extract_zip_safely(buf, target)


def test_reject_size_bomb(tmp_path: Path) -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        # 1 MiB file
        zf.writestr("large.txt", "a" * (1024 * 1024))
    buf.seek(0)

    target = tmp_path / "extracted"
    # Set limit to 500 KiB
    with pytest.raises(ZipExtractionError, match="uncompressed size exceeds limit"):
        extract_zip_safely(buf, target, max_total_size_bytes=500 * 1024)


def test_skip_vendor_and_ignored_directories(tmp_path: Path) -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("app/main.py", "import os")
        zf.writestr("node_modules/pkg/index.js", "ignored")
        zf.writestr(".git/HEAD", "ignored")
    buf.seek(0)

    target = tmp_path / "extracted"
    count = extract_zip_safely(buf, target)
    assert count == 1
    assert (target / "app" / "main.py").exists()
    assert not (target / "node_modules").exists()
    assert not (target / ".git").exists()

