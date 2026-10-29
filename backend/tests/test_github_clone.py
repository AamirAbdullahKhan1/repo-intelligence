"""Tests for GitHub URL validation and cloning service."""

from __future__ import annotations

import pytest

from app.core.errors import ValidationError
from app.services.repository.github_clone import parse_and_sanitize_github_url


def test_parse_valid_github_urls() -> None:
    cases = [
        ("https://github.com/fastapi/fastapi", "https://github.com/fastapi/fastapi.git", "fastapi", "fastapi"),
        ("https://github.com/facebook/react.git", "https://github.com/facebook/react.git", "facebook", "react"),
        ("http://github.com/pallets/flask/", "https://github.com/pallets/flask.git", "pallets", "flask"),
    ]
    for raw, expected_url, expected_owner, expected_repo in cases:
        canonical, owner, repo = parse_and_sanitize_github_url(raw)
        assert canonical == expected_url
        assert owner == expected_owner
        assert repo == expected_repo


def test_reject_invalid_github_urls() -> None:
    invalid = [
        "https://gitlab.com/owner/repo",
        "git@github.com:owner/repo.git",
        "https://github.com/onlyowner",
        "ftp://github.com/owner/repo",
        "javascript:alert(1)",
        "https://github.com/../evil",
    ]
    for url in invalid:
        with pytest.raises(ValidationError):
            parse_and_sanitize_github_url(url)
