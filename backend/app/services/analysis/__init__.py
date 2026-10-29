"""
Deterministic repository analysis service.
Extracts inventory, components, frameworks, routes, and security-relevant code patterns.
"""

from app.services.analysis.inventory import RepositoryAnalyzer

__all__ = ["RepositoryAnalyzer"]
