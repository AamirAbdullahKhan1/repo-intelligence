"""
Component Detector for Architecture Reconstruction V2.
Discovers discrete application components (Next.js apps, MCP servers,
workers, standalone servers, databases, and shared libraries) using package boundaries,
entry point signatures, and deployment manifests.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
import re
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class DiscoveredComponent:
    """Represents a discovered architectural component with evidence metadata."""

    def __init__(
        self,
        id: str,
        name: str,
        type: str,
        category: str,
        technology: str,
        root_dir: str,
        entry_points: List[str],
        file_references: List[str],
        sub_modules: List[str],
        description: str,
        confidence: str = "VERIFIED",
        metadata: Optional[Dict] = None,
    ) -> None:
        self.id = id
        self.name = name
        self.type = type
        self.category = category
        self.technology = technology
        self.root_dir = root_dir
        self.entry_points = entry_points
        self.file_references = file_references
        self.sub_modules = sub_modules
        self.description = description
        self.confidence = confidence
        self.metadata = metadata or {}


class ComponentDetector:
    """Scans repository files and discovers discrete application components."""

    def __init__(self, root_dir: Path, files: List[Path]) -> None:
        self.root_dir = root_dir.resolve()
        self.files = files
        self.rel_files = [str(f.relative_to(self.root_dir)).replace("\\", "/") for f in files]
        self.rel_map = {str(f.relative_to(self.root_dir)).replace("\\", "/"): f for f in files}

    def detect_all(self) -> List[DiscoveredComponent]:
        components: List[DiscoveredComponent] = []

        # 1. Detect Next.js Applications & Routes
        nextjs_comps = self._detect_nextjs()
        components.extend(nextjs_comps)

        # 2. Detect MCP Servers
        mcp_comps = self._detect_mcp_servers()
        components.extend(mcp_comps)

        # 3. Detect Workers (Cloudflare Workers, Background Queue Workers)
        worker_comps = self._detect_workers()
        components.extend(worker_comps)

        # 4. Detect Standalone Servers
        standalone_comps = self._detect_standalone_servers(existing=components)
        components.extend(standalone_comps)

        # 5. Detect Shared Packages / Monorepo Packages
        package_comps = self._detect_monorepo_packages(existing=components)
        components.extend(package_comps)

        # 6. Fallback: If no distinct service components found, create core service
        if not any(c.type in ("frontend_app", "api_service", "mcp_server", "worker") for c in components):
            fallback = self._create_fallback_service()
            if fallback:
                components.append(fallback)

        return components

    def _detect_nextjs(self) -> List[DiscoveredComponent]:
        """Detect Next.js App Router and Pages Router apps."""
        results: List[DiscoveredComponent] = []

        # Look for Next.js indicators
        has_next_config = any("next.config" in f for f in self.rel_files)
        has_app_dir = any(f.startswith("app/") or "/app/" in f or f.startswith("src/app/") for f in self.rel_files)
        has_pages_dir = any(f.startswith("pages/") or "/pages/" in f or f.startswith("src/pages/") for f in self.rel_files)

        if not (has_next_config or has_app_dir or has_pages_dir):
            return results

        # Discover App Router Route Handlers (app/**/route.ts|js)
        route_files = [
            f for f in self.rel_files
            if re.search(r"(?:^|/)app/.*route\.[tj]sx?$", f)
        ]
        # Discover Pages API Route Handlers (pages/api/**/*.ts|js)
        pages_api_files = [
            f for f in self.rel_files
            if re.search(r"(?:^|/)pages/api/.*\.[tj]sx?$", f)
        ]

        sub_modules: List[str] = []
        for rf in route_files:
            # Extract path: app/api/diagram/route.ts -> /api/diagram
            m = re.search(r"(?:^|/)app/(.*?)/route\.[tj]sx?$", rf)
            if m:
                sub_modules.append(f"/{m.group(1)}")
        for pf in pages_api_files:
            m = re.search(r"(?:^|/)pages/api/(.*?)\.[tj]sx?$", pf)
            if m:
                sub_modules.append(f"/api/{m.group(1)}")

        # Distinguish client vs server components
        client_components_count = 0
        for f in self.files:
            if f.suffix in (".tsx", ".jsx", ".ts", ".js") and f.stat().st_size < 500_000:
                try:
                    head = f.read_text(encoding="utf-8", errors="ignore")[:300]
                    if '"use client"' in head or "'use client'" in head:
                        client_components_count += 1
                except Exception:
                    pass

        entry_points = []
        for ep in ("app/layout.tsx", "src/app/layout.tsx", "pages/_app.tsx", "src/pages/_app.tsx", "middleware.ts", "src/middleware.ts"):
            if ep in self.rel_files:
                entry_points.append(ep)

        results.append(
            DiscoveredComponent(
                id="comp-nextjs-app",
                name="Next.js Application",
                type="frontend_app",
                category="application",
                technology="Next.js / React (App Router)",
                root_dir="app" if any(f.startswith("app/") for f in self.rel_files) else "src/app",
                entry_points=entry_points or ["app/layout.tsx"],
                file_references=route_files[:8] + entry_points,
                sub_modules=sorted(list(set(sub_modules)))[:12],
                description=(
                    f"Full-stack Next.js web application exposing {len(sub_modules)} API route handlers "
                    f"and {client_components_count} interactive client components."
                ),
                confidence="VERIFIED",
                metadata={
                    "route_handlers_count": len(sub_modules),
                    "client_components_count": client_components_count,
                    "routes": sub_modules[:10],
                },
            )
        )
        return results

    def _detect_mcp_servers(self) -> List[DiscoveredComponent]:
        """Detect Model Context Protocol (MCP) server implementations."""
        results: List[DiscoveredComponent] = []

        mcp_files = [
            f for f in self.rel_files
            if ("mcp" in f.lower() and "server" in f.lower()) or "server/mcp" in f.lower()
        ]

        # Scan files for McpServer or @modelcontextprotocol
        for rf in self.rel_files:
            if rf.endswith((".ts", ".js")) and ("mcp" in rf.lower() or "server" in rf.lower()):
                fpath = self.rel_map.get(rf)
                if not fpath:
                    continue
                try:
                    content = fpath.read_text(encoding="utf-8", errors="ignore")
                    if "McpServer" in content or "@modelcontextprotocol/sdk" in content or "server.tool(" in content:
                        if rf not in mcp_files:
                            mcp_files.append(rf)
                except Exception:
                    continue

        if not mcp_files:
            return results

        # Find tool definitions
        tools: List[str] = []
        for mf in mcp_files:
            fpath = self.rel_map.get(mf)
            if not fpath:
                continue
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
                for match in re.finditer(r"server\.tool\(\s*[\"']([^\"']+)[\"']", content):
                    tools.append(match.group(1))
            except Exception:
                continue

        results.append(
            DiscoveredComponent(
                id="comp-mcp-server",
                name="MCP Protocol Server",
                type="mcp_server",
                category="compute",
                technology="Model Context Protocol (MCP)",
                root_dir=str(Path(mcp_files[0]).parent).replace("\\", "/"),
                entry_points=[mcp_files[0]],
                file_references=mcp_files,
                sub_modules=[f"Tool: {t}" for t in sorted(set(tools))] if tools else ["Tools & Prompts"],
                description=(
                    f"Model Context Protocol server providing AI tool execution and contextual resources "
                    f"({len(tools)} declared tool handlers)."
                ),
                confidence="VERIFIED",
                metadata={"tools": tools},
            )
        )
        return results

    def _detect_workers(self) -> List[DiscoveredComponent]:
        """Detect Cloudflare Workers, queue workers, or background task runners."""
        results: List[DiscoveredComponent] = []

        # Find worker directories: e.g. workers/render, workers/presence, workers/errors
        worker_dirs: Set[str] = set()
        for rf in self.rel_files:
            m = re.match(r"^(?:workers|services|packages)/([^/]+)/", rf)
            if m:
                top = m.group(0).rstrip("/")
                if any(rf.startswith(f"{top}/") and (rf.endswith("index.ts") or rf.endswith("wrangler.toml") or rf.endswith("server.ts")) for rf in self.rel_files):
                    worker_dirs.add(top)

        for wdir in sorted(worker_dirs):
            w_files = [f for f in self.rel_files if f.startswith(f"{wdir}/")]
            entry = next((f for f in w_files if f.endswith(("src/index.ts", "index.ts", "server.ts"))), w_files[0] if w_files else f"{wdir}/index.ts")
            wrangler_file = next((f for f in w_files if f.endswith("wrangler.toml")), None)

            # Name formatting: workers/render -> Render Worker
            w_name = wdir.split("/")[-1].replace("-", " ").replace("_", " ").title()
            tech = "Cloudflare Worker" if (wrangler_file or any("cloudflare" in f.lower() for f in w_files)) else "Background Worker"

            # Check exported handlers (fetch, queue, scheduled)
            handlers: List[str] = []
            fpath = self.rel_map.get(entry)
            if fpath:
                try:
                    content = fpath.read_text(encoding="utf-8", errors="ignore")
                    if "fetch(" in content or "fetch:" in content:
                        handlers.append("HTTP Fetch Handler")
                    if "queue(" in content or "queue:" in content:
                        handlers.append("Queue Consumer")
                    if "scheduled(" in content or "scheduled:" in content:
                        handlers.append("Cron Scheduler")
                except Exception:
                    pass

            results.append(
                DiscoveredComponent(
                    id=f"comp-worker-{wdir.split('/')[-1]}",
                    name=f"{w_name} Worker",
                    type="worker",
                    category="compute",
                    technology=tech,
                    root_dir=wdir,
                    entry_points=[entry],
                    file_references=([wrangler_file] if wrangler_file else []) + [entry],
                    sub_modules=handlers or ["Worker Request Handler"],
                    description=f"{w_name} independent background worker executing {', '.join(handlers) if handlers else 'asynchronous event handlers'}.",
                    confidence="VERIFIED",
                    metadata={"worker_dir": wdir, "handlers": handlers},
                )
            )

        return results

    def _detect_standalone_servers(self, existing: List[DiscoveredComponent]) -> List[DiscoveredComponent]:
        """Detect separate standalone servers like cloudflare/server.ts."""
        results: List[DiscoveredComponent] = []
        claimed_entries = {ep for c in existing for ep in c.entry_points}

        candidates = [
            f for f in self.rel_files
            if re.search(r"(?:server|service|daemon|gateway)\.[tj]s$", f) and f not in claimed_entries
        ]

        for cand in candidates:
            # Skip if inside an already claimed worker directory
            if any(cand.startswith(f"{c.root_dir}/") for c in existing):
                continue

            name_part = Path(cand).parent.name or "Edge"
            s_name = f"{name_part.title()} Server" if name_part != "." else "Standalone Server"

            results.append(
                DiscoveredComponent(
                    id=f"comp-server-{Path(cand).stem}-{len(results)+1}",
                    name=s_name,
                    type="api_service",
                    category="compute",
                    technology="Node.js / TypeScript Server",
                    root_dir=str(Path(cand).parent).replace("\\", "/"),
                    entry_points=[cand],
                    file_references=[cand],
                    sub_modules=["Server Ingress"],
                    description=f"Standalone service runtime entry point defined in {cand}.",
                    confidence="VERIFIED",
                )
            )

        return results

    def _detect_monorepo_packages(self, existing: List[DiscoveredComponent]) -> List[DiscoveredComponent]:
        """Detect shared packages or libraries in monorepos."""
        results: List[DiscoveredComponent] = []
        claimed_dirs = {c.root_dir for c in existing}

        # Look for packages/* or shared/*
        for rf in self.rel_files:
            if rf.endswith("package.json") and (rf.startswith("packages/") or rf.startswith("shared/") or rf.startswith("libs/")):
                pdir = str(Path(rf).parent).replace("\\", "/")
                if pdir in claimed_dirs:
                    continue

                pname = pdir.split("/")[-1].replace("-", " ").title()
                results.append(
                    DiscoveredComponent(
                        id=f"comp-pkg-{pdir.split('/')[-1]}",
                        name=f"{pname} Package",
                        type="shared_library",
                        category="application",
                        technology="TypeScript Library",
                        root_dir=pdir,
                        entry_points=[rf],
                        file_references=[rf],
                        sub_modules=["Shared Utilities"],
                        description=f"Shared workspace library module located in {pdir}.",
                        confidence="VERIFIED",
                    )
                )

        return results

    def _create_fallback_service(self) -> Optional[DiscoveredComponent]:
        """Create a default core application service when no specialized components match."""
        entry = next((f for f in self.rel_files if f in ("main.py", "app.py", "server.ts", "index.ts", "main.go")), None)
        return DiscoveredComponent(
            id="comp-core-service",
            name="Core Application Service",
            type="api_service",
            category="compute",
            technology="Application Service",
            root_dir=".",
            entry_points=[entry] if entry else [],
            file_references=[entry] if entry else [],
            sub_modules=["API Handlers"],
            description="Core backend application service handling routing and business logic.",
            confidence="VERIFIED" if entry else "INFERRED",
        )
