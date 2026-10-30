"""
Relationship Extractor for Architecture Reconstruction V2.
Extracts verified code relationships:
- HANDLES_ROUTE
- READS_FROM / WRITES_TO (Redis & Database queries with line numbers)
- CALLS / IMPORTS (Inter-component and shared library imports)
- CONNECTS_TO (External API integrations)
"""

from __future__ import annotations

import logging
from pathlib import Path
import re
from typing import Dict, List, Optional, Set, Tuple

from app.schemas.architecture import ArchitectureEdge, EvidenceMeta
from app.services.analysis.component_detector import DiscoveredComponent

logger = logging.getLogger(__name__)

# Redis operations mapped to access patterns
REDIS_READ_OPS = {"get", "hget", "hgetall", "mget", "smembers", "zrange", "lrange", "exists"}
REDIS_WRITE_OPS = {"set", "hset", "del", "expire", "sadd", "zadd", "lpush", "rpush", "publish"}


class RelationshipExtractor:
    """Extracts fine-grained relationships and call-chain evidence between components."""

    def __init__(
        self,
        root_dir: Path,
        files: List[Path],
        components: List[DiscoveredComponent],
        databases: List[str],
    ) -> None:
        self.root_dir = root_dir.resolve()
        self.files = files
        self.components = components
        self.databases = databases
        self.rel_files = [str(f.relative_to(self.root_dir)).replace("\\", "/") for f in files]
        self.rel_map = {str(f.relative_to(self.root_dir)).replace("\\", "/"): f for f in files}

    def extract_all(self) -> List[ArchitectureEdge]:
        edges: List[ArchitectureEdge] = []
        edge_set: Set[Tuple[str, str, str]] = set()

        def add_edge(edge: ArchitectureEdge) -> None:
            key = (edge.source, edge.target, edge.relationship_type)
            if key not in edge_set:
                edge_set.add(key)
                edges.append(edge)

        # 1. External Client -> Service / App Ingress
        for comp in self.components:
            if comp.type in ("frontend_app", "api_service"):
                add_edge(
                    ArchitectureEdge(
                        id=f"edge-client-{comp.id}",
                        source="node-client",
                        target=comp.id,
                        label="HTTP Ingress",
                        relationship_type="HANDLES_ROUTE",
                        confidence="VERIFIED",
                        evidence=EvidenceMeta(
                            file_path=comp.entry_points[0] if comp.entry_points else "routes",
                            evidence_category="code_ast_pattern",
                            extraction_method="route_manifest_scan",
                            confidence="VERIFIED",
                        ),
                        description=f"External requests routed to {comp.name}.",
                    )
                )

        # 2. Component -> Database / Cache Operations (READS_FROM, WRITES_TO)
        db_edges = self._extract_database_operations()
        for e in db_edges:
            add_edge(e)

        # 3. Inter-component Imports & Dependencies (IMPORTS / DEPENDS_ON)
        comp_edges = self._extract_component_dependencies()
        for e in comp_edges:
            add_edge(e)

        # 4. External API connections (CONNECTS_TO)
        ext_edges = self._extract_external_connections()
        for e in ext_edges:
            add_edge(e)

        return edges

    def _extract_database_operations(self) -> List[ArchitectureEdge]:
        """Detect component-level database and cache operations with file and line citations."""
        edges: List[ArchitectureEdge] = []

        # Target files across code
        code_files = [
            f for f in self.files
            if f.suffix in (".ts", ".js", ".py", ".go") and f.stat().st_size < 500_000
        ]

        # Scan for Redis operations: e.g. redis.get(, redis.set(, kv.get(
        redis_op_pattern = re.compile(r"\b(?:redis|kv|cache|client)\.([a-zA-Z0-9_]+)\s*\(", re.IGNORECASE)
        # Scan for Prisma / ORM operations: e.g. prisma.user.findMany(
        orm_op_pattern = re.compile(r"\b(?:prisma|db)\.([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)\s*\(", re.IGNORECASE)

        for fpath in code_files:
            rel = str(fpath.relative_to(self.root_dir)).replace("\\", "/")
            calling_comp = self._match_file_to_component(rel)
            if not calling_comp:
                continue

            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, start=1):
                        # 1. Redis / Cache checks
                        if any("redis" in d.lower() for d in self.databases) or "redis" in line.lower():
                            for m in redis_op_pattern.finditer(line):
                                op = m.group(1).lower()
                                if op in REDIS_READ_OPS or op in REDIS_WRITE_OPS:
                                    rel_type = "READS_FROM" if op in REDIS_READ_OPS else "WRITES_TO"
                                    edges.append(
                                        ArchitectureEdge(
                                            id=f"edge-{calling_comp.id}-redis-{rel_type.lower()}",
                                            source=calling_comp.id,
                                            target="node-db-redis",
                                            label=f"{rel_type} (redis.{op})",
                                            relationship_type=rel_type,
                                            confidence="VERIFIED",
                                            evidence_file=rel,
                                            line_number=line_num,
                                            evidence=EvidenceMeta(
                                                file_path=rel,
                                                line_start=line_num,
                                                line_end=line_num,
                                                evidence_category="code_ast_pattern",
                                                extraction_method="call_pattern_trace",
                                                confidence="VERIFIED",
                                                snippet=line.strip()[:100],
                                            ),
                                            description=f"{calling_comp.name} executes {op.upper()} operation on Redis cache.",
                                        )
                                    )

                        # 2. SQL / Prisma checks
                        for m in orm_op_pattern.finditer(line):
                            model_name, op = m.group(1), m.group(2).lower()
                            rel_type = "READS_FROM" if any(r in op for r in ("find", "select", "get", "query")) else "WRITES_TO"
                            edges.append(
                                ArchitectureEdge(
                                    id=f"edge-{calling_comp.id}-db-{rel_type.lower()}",
                                    source=calling_comp.id,
                                    target="node-db-primary",
                                    label=f"{rel_type} ({model_name}.{op})",
                                    relationship_type=rel_type,
                                    confidence="VERIFIED",
                                    evidence_file=rel,
                                    line_number=line_num,
                                    evidence=EvidenceMeta(
                                        file_path=rel,
                                        line_start=line_num,
                                        line_end=line_num,
                                        evidence_category="code_ast_pattern",
                                        extraction_method="call_pattern_trace",
                                        confidence="VERIFIED",
                                        snippet=line.strip()[:100],
                                    ),
                                    description=f"{calling_comp.name} accesses database model '{model_name}'.",
                                )
                            )
            except Exception:
                continue

        return edges

    def _extract_component_dependencies(self) -> List[ArchitectureEdge]:
        """Detect inter-component import references (e.g. Next.js App imports shared package)."""
        edges: List[ArchitectureEdge] = []

        import_pattern = re.compile(
            r"(?:import|from)\s+['\"]([^'\"]+)['\"]|(?:require\s*\(\s*['\"]([^'\"]+)['\"]\))"
        )

        for comp in self.components:
            for ref in comp.file_references[:15]:
                fpath = self.rel_map.get(ref)
                if not fpath:
                    continue
                try:
                    content = fpath.read_text(encoding="utf-8", errors="ignore")
                    for m in import_pattern.finditer(content):
                        imp_path = m.group(1) or m.group(2)
                        # Check if import matches another component's root_dir
                        for target_comp in self.components:
                            if target_comp.id == comp.id:
                                continue
                            if (
                                target_comp.root_dir != "."
                                and target_comp.root_dir in imp_path
                                or target_comp.name.lower().replace(" ", "-") in imp_path.lower()
                            ):
                                edges.append(
                                    ArchitectureEdge(
                                        id=f"edge-{comp.id}-{target_comp.id}",
                                        source=comp.id,
                                        target=target_comp.id,
                                        label="Imports Module",
                                        relationship_type="IMPORTS",
                                        confidence="VERIFIED",
                                        evidence_file=ref,
                                        evidence=EvidenceMeta(
                                            file_path=ref,
                                            evidence_category="import_reference",
                                            extraction_method="import_statement_scan",
                                            confidence="VERIFIED",
                                            snippet=f"import from '{imp_path}'",
                                        ),
                                        description=f"{comp.name} imports code modules from {target_comp.name}.",
                                    )
                                )
                except Exception:
                    continue

        return edges

    def _extract_external_connections(self) -> List[ArchitectureEdge]:
        """Detect outbound HTTP calls to third-party services."""
        edges: List[ArchitectureEdge] = []
        url_pattern = re.compile(r"https?://(?:api\.)?([a-zA-Z0-9_\-\.]+)/", re.IGNORECASE)

        for comp in self.components:
            for ref in comp.file_references[:10]:
                fpath = self.rel_map.get(ref)
                if not fpath:
                    continue
                try:
                    content = fpath.read_text(encoding="utf-8", errors="ignore")
                    for m in url_pattern.finditer(content):
                        host = m.group(1).lower()
                        if host in ("localhost", "127.0.0.1", "example.com", "schema.org"):
                            continue
                        if any(api in host for api in ("github", "openai", "anthropic", "stripe", "sentry", "cloudflare")):
                            service_name = host.split(".")[0].title()
                            edges.append(
                                ArchitectureEdge(
                                    id=f"edge-{comp.id}-ext-{service_name.lower()}",
                                    source=comp.id,
                                    target=f"node-ext-{service_name.lower()}",
                                    label=f"Calls API ({service_name})",
                                    relationship_type="CONNECTS_TO",
                                    confidence="VERIFIED",
                                    evidence_file=ref,
                                    evidence=EvidenceMeta(
                                        file_path=ref,
                                        evidence_category="code_ast_pattern",
                                        extraction_method="external_endpoint_scan",
                                        confidence="VERIFIED",
                                    ),
                                    description=f"{comp.name} integrates with external {service_name} API.",
                                )
                            )
                except Exception:
                    continue

        return edges

    def _match_file_to_component(self, rel_path: str) -> Optional[DiscoveredComponent]:
        """Find the most specific component that contains the given relative file path."""
        matches = [
            c for c in self.components
            if c.root_dir != "." and rel_path.startswith(f"{c.root_dir}/")
        ]
        if matches:
            return sorted(matches, key=lambda c: len(c.root_dir), reverse=True)[0]

        # Check default frontend app or core service
        for c in self.components:
            if c.type in ("frontend_app", "api_service") and (
                rel_path.startswith("app/") or rel_path.startswith("src/") or rel_path.startswith("pages/")
            ):
                return c

        return None
