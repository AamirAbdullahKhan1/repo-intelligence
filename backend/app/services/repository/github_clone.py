"""
Safe GitHub repository cloning service.
Clones only public GitHub repositories using single-branch shallow clones
with strict URL sanitisation and execution prevention.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
import re
import shutil
import subprocess

from app.core.errors import AppError, ValidationError

logger = logging.getLogger(__name__)

# Validates standard public GitHub repository URLs
# Examples:
#   https://github.com/fastapi/fastapi
#   https://github.com/facebook/react.git
#   http://github.com/pallets/flask
GITHUB_URL_PATTERN = re.compile(
    r"^https?://(www\.)?github\.com/(?P<owner>[a-zA-Z0-9_.-]+)/(?P<repo>[a-zA-Z0-9_.-]+?)(?:\.git)?/?$"
)


class GitCloneError(AppError):
    status_code = 400
    error_code = "git_clone_error"


def parse_and_sanitize_github_url(raw_url: str) -> tuple[str, str, str]:
    """
    Validate and sanitize a GitHub repository URL.
    Returns: (canonical_clone_url, owner, repo)
    """
    cleaned = raw_url.strip()
    match = GITHUB_URL_PATTERN.match(cleaned)
    if not match:
        raise ValidationError(
            f"Invalid GitHub repository URL: '{raw_url}'. "
            "Expected format: https://github.com/owner/repository"
        )

    owner = match.group("owner")
    repo = match.group("repo")

    # Guard against invalid path components
    if owner in (".", "..") or repo in (".", ".."):
        raise ValidationError("Invalid repository or owner name.")

    canonical_url = f"https://github.com/{owner}/{repo}.git"
    return canonical_url, owner, repo


def clone_github_repo(
    raw_url: str,
    target_dir: Path,
    timeout_seconds: int = 45,
) -> str:
    """
    Clone a public GitHub repository with shallow depth and security options.
    
    Returns the repository identifier (owner/repo).
    """
    canonical_url, owner, repo = parse_and_sanitize_github_url(raw_url)
    target_dir = target_dir.resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    # Disable git hooks to prevent any arbitrary code execution via repository hooks
    # and disable git credentials prompts (GIT_TERMINAL_PROMPT=0)
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"

    cmd = [
        "git",
        "-c",
        "core.hooksPath=",  # disable repository hooks
        "clone",
        "--depth",
        "1",
        "--single-branch",
        canonical_url,
        str(target_dir),
    ]

    logger.info("Cloning public repository %s/%s into temporary workspace", owner, repo)

    try:
        proc = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        logger.error("Git clone timed out for %s: %s", canonical_url, e)
        raise GitCloneError(
            f"Cloning {owner}/{repo} timed out after {timeout_seconds} seconds. "
            "The repository may be too large or the network connection is slow."
        ) from e
    except FileNotFoundError as e:
        logger.error("Git executable not found: %s", e)
        raise GitCloneError("Git is not installed or not available on the server path.") from e

    if proc.returncode != 0:
        err_msg = proc.stderr.strip()
        logger.warning("Git clone failed (code %d): %s", proc.returncode, err_msg)
        if "Authentication failed" in err_msg or "could not read Username" in err_msg or "Repository not found" in err_msg:
            raise GitCloneError(
                f"Could not clone repository '{owner}/{repo}'. "
                "Ensure the repository is public and the URL is spelled correctly."
            )
        raise GitCloneError(f"Failed to clone repository: {err_msg or 'Unknown error'}")

    # Remove the .git metadata directory from the clone to avoid parsing it as code
    git_meta = target_dir / ".git"
    if git_meta.exists():
        shutil.rmtree(git_meta, ignore_errors=True)

    return f"{owner}/{repo}"

