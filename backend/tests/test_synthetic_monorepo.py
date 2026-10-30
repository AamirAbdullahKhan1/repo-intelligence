"""
Phase 8: Synthetic TypeScript Monorepo Fixture Test.
Tests Architecture Reconstruction Engine V2 against a multi-component TypeScript repository
modeled directly after the GitDiagram topology (Next.js, MCP server, workers, Redis, Docker, GitHub Actions).
"""

from __future__ import annotations

from pathlib import Path
from app.services.analysis.inventory import RepositoryAnalyzer
from app.services.architecture.builder import ArchitectureBuilder


def test_synthetic_ts_monorepo_architecture_reconstruction(tmp_path: Path) -> None:
    repo_dir = tmp_path / "gitdiagram_mock"
    repo_dir.mkdir()

    # 1. Root package.json & Next.js App Router
    (repo_dir / "package.json").write_text(
        '{\n  "name": "gitdiagram",\n  "dependencies": {\n    "next": "^14.2.0",\n    "react": "^18.3.0",\n    "@upstash/redis": "^1.28.0"\n  }\n}\n'
    )
    (repo_dir / "next.config.js").write_text("module.exports = {};\n")

    # Next.js route handlers
    diagram_route = repo_dir / "app" / "api" / "diagram"
    diagram_route.mkdir(parents=True)
    (diagram_route / "route.ts").write_text(
        'import { redis } from "@/lib/redis";\n'
        'import { formatDiagram } from "packages/shared/utils";\n'
        "\n"
        "export async function GET(req: Request) {\n"
        '  const cached = await redis.get("diagram:123");\n'
        "  return Response.json({ cached });\n"
        "}\n"
        "\n"
        "export async function POST(req: Request) {\n"
        '  await redis.set("diagram:123", "rendered_data");\n'
        "  return Response.json({ success: true });\n"
        "}\n"
    )

    auth_route = repo_dir / "app" / "api" / "auth"
    auth_route.mkdir(parents=True)
    (auth_route / "route.ts").write_text(
        "export async function POST(req: Request) {\n"
        "  return Response.json({ token: 'mock' });\n"
        "}\n"
    )

    # 2. Redis Client module
    lib_dir = repo_dir / "src" / "lib"
    lib_dir.mkdir(parents=True)
    (lib_dir / "redis.ts").write_text(
        'import { Redis } from "@upstash/redis";\n'
        "export const redis = new Redis();\n"
    )

    # 3. Model Context Protocol (MCP) Server: src/server/mcp/server.ts
    mcp_dir = repo_dir / "src" / "server" / "mcp"
    mcp_dir.mkdir(parents=True)
    (mcp_dir / "server.ts").write_text(
        'import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";\n'
        'const server = new McpServer({ name: "gitdiagram-mcp", version: "1.0.0" });\n'
        'server.tool("render_diagram", "Renders architecture diagram", () => ({ status: "ok" }));\n'
        'server.tool("get_repo_tree", "Extracts repo file tree", () => ({ tree: [] }));\n'
        "server.start();\n"
    )

    # 4. Cloudflare Standalone Server: cloudflare/server.ts
    cf_dir = repo_dir / "cloudflare"
    cf_dir.mkdir(parents=True)
    (cf_dir / "server.ts").write_text(
        'import { Hono } from "hono";\n'
        "const app = new Hono();\n"
        'app.get("/health", (c) => c.text("ok"));\n'
        "export default app;\n"
    )

    # 5. Multiple Workers: workers/render, workers/presence, workers/errors
    for w_name in ("render", "presence", "errors"):
        w_dir = repo_dir / "workers" / w_name / "src"
        w_dir.mkdir(parents=True)
        (repo_dir / "workers" / w_name / "package.json").write_text(
            f'{{\n  "name": "@gitdiagram/worker-{w_name}"\n}}\n'
        )
        (repo_dir / "workers" / w_name / "wrangler.toml").write_text(
            f'name = "worker-{w_name}"\nmain = "src/index.ts"\ncompatibility_date = "2024-01-01"\n'
        )
        (w_dir / "index.ts").write_text(
            "export default {\n"
            "  async fetch(req: Request, env: any) {\n"
            f'    return new Response("worker {w_name}");\n'
            "  },\n"
            "  async queue(batch: any, env: any) {\n"
            "    // process queue events\n"
            "  }\n"
            "};\n"
        )

    # 6. Shared package
    pkg_dir = repo_dir / "packages" / "shared"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "package.json").write_text('{"name": "@gitdiagram/shared"}\n')
    (pkg_dir / "utils.ts").write_text("export function formatDiagram(d: any) { return d; }\n")

    # 7. Dockerfile
    (repo_dir / "Dockerfile").write_text(
        "FROM node:20-alpine AS builder\n"
        "WORKDIR /app\n"
        "COPY . .\n"
        "RUN npm run build\n"
        "EXPOSE 3000\n"
        'CMD ["npm", "start"]\n'
    )

    # 8. GitHub Actions Workflows
    wf_dir = repo_dir / ".github" / "workflows"
    wf_dir.mkdir(parents=True)
    (wf_dir / "ci.yml").write_text(
        "name: CI Pipeline\n"
        "on: [push, pull_request]\n"
        "jobs:\n"
        "  build:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - uses: actions/checkout@v4\n"
        "      - run: npm test\n"
    )
    (wf_dir / "deploy-workers.yml").write_text(
        "name: Deploy Workers\n"
        "on:\n  push:\n    branches: [main]\n"
        "jobs:\n  deploy:\n    runs-on: ubuntu-latest\n"
    )

    # RUN ANALYSIS
    analyzer = RepositoryAnalyzer(repo_dir, repo_name="gitdiagram-mock", source_type="github")
    inventory = analyzer.analyze()

    # BUILD ARCHITECTURE V2
    builder = ArchitectureBuilder(inventory, workspace_dir=repo_dir)
    arch = builder.build()

    # VERIFY RESULTS
    # 1. Distinct Components Created (No longer collapsed into 1 service!)
    node_ids = {n.id for n in arch.nodes}
    node_labels = {n.label for n in arch.nodes}
    node_types = {n.type for n in arch.nodes}

    assert "comp-nextjs-app" in node_ids
    assert "comp-mcp-server" in node_ids
    assert "comp-worker-render" in node_ids
    assert "comp-worker-presence" in node_ids
    assert "comp-worker-errors" in node_ids
    assert "node-db-redis" in node_ids

    # 2. Component Types Breakdown
    assert "frontend_app" in node_types
    assert "mcp_server" in node_types
    assert "worker" in node_types
    assert "cache" in node_types

    # 3. Next.js App details
    nextjs_node = next(n for n in arch.nodes if n.id == "comp-nextjs-app")
    assert "/api/diagram" in nextjs_node.sub_modules
    assert "/api/auth" in nextjs_node.sub_modules

    # 4. MCP Server details
    mcp_node = next(n for n in arch.nodes if n.id == "comp-mcp-server")
    assert any("render_diagram" in m for m in mcp_node.sub_modules)
    assert any("get_repo_tree" in m for m in mcp_node.sub_modules)

    # 5. Workers details
    render_worker = next(n for n in arch.nodes if n.id == "comp-worker-render")
    assert "HTTP Fetch Handler" in render_worker.sub_modules
    assert "Queue Consumer" in render_worker.sub_modules

    # 6. Fine-grained relationship edges: READS_FROM and WRITES_TO on Redis!
    edge_types = {e.relationship_type for e in arch.edges}
    assert "READS_FROM" in edge_types
    assert "WRITES_TO" in edge_types
    assert "HANDLES_ROUTE" in edge_types

    redis_edges = [e for e in arch.edges if e.target == "node-db-redis"]
    assert len(redis_edges) >= 2
    read_edge = next(e for e in redis_edges if e.relationship_type == "READS_FROM")
    assert read_edge.confidence == "VERIFIED"
    assert "app/api/diagram/route.ts" in (read_edge.evidence_file or "")

    # 7. Deployment Architecture View (Phase 4 Separation)
    assert arch.deployment_view is not None
    deploy_node_ids = {n.id for n in arch.deployment_view.nodes}
    assert "deploy-node-source" in deploy_node_ids
    assert "deploy-node-github-actions" in deploy_node_ids
    assert "deploy-node-docker" in deploy_node_ids

    deploy_edge_types = {e.relationship_type for e in arch.deployment_view.edges}
    assert "TRIGGERS_WORKFLOW" in deploy_edge_types
    assert "DEPLOYED_AS" in deploy_edge_types

    # 8. Workflows
    wf_ids = {w.id for w in arch.workflows}
    assert "wf-http-ingress" in wf_ids
    assert "wf-worker-event" in wf_ids
    assert "wf-mcp-execution" in wf_ids
