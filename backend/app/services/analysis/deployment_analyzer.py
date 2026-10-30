"""
Deployment Architecture Analyzer for Architecture Reconstruction Engine V2.
Extracts build, containerization, and CI/CD pipelines into a distinct deployment model.
Guarantees deployment triggers are never conflated with runtime service communications.
"""

from __future__ import annotations

import logging
from pathlib import Path
import re
from typing import List, Tuple

from app.schemas.architecture import ArchitectureEdge, ArchitectureNode, DeploymentModel, EvidenceMeta

logger = logging.getLogger(__name__)


class DeploymentAnalyzer:
    """Analyzes GitHub Actions, Dockerfiles, and Wrangler configs to construct a separate deployment view."""

    def __init__(self, root_dir: Path, files: List[Path], repo_name: str) -> None:
        self.root_dir = root_dir.resolve()
        self.files = files
        self.repo_name = repo_name
        self.rel_files = [str(f.relative_to(self.root_dir)).replace("\\", "/") for f in files]
        self.rel_map = {str(f.relative_to(self.root_dir)).replace("\\", "/"): f for f in files}

    def build_deployment_model(self) -> DeploymentModel:
        nodes: List[ArchitectureNode] = []
        edges: List[ArchitectureEdge] = []
        stages: List[str] = ["Source Checkout"]

        # 1. Source Repository Node
        repo_node_id = "deploy-node-source"
        nodes.append(
            ArchitectureNode(
                id=repo_node_id,
                label=f"Source Repository ({self.repo_name})",
                type="infrastructure",
                category="source_control",
                technology="Git Version Control",
                confidence="VERIFIED",
                description="Source code repository containing branches, tags, and commits.",
            )
        )

        # 2. Check for GitHub Actions Workflows
        workflow_files = [
            f for f in self.rel_files
            if f.startswith(".github/workflows/") and f.endswith((".yml", ".yaml"))
        ]

        ci_node_id = None
        if workflow_files:
            stages.append("Continuous Integration (CI)")
            ci_node_id = "deploy-node-github-actions"
            workflow_names = []
            for wf in workflow_files:
                wf_path = self.rel_map.get(wf)
                if wf_path:
                    try:
                        content = wf_path.read_text(encoding="utf-8", errors="ignore")
                        m = re.search(r"^name:\s*['\"]?([^'\"\n]+)", content, re.MULTILINE)
                        workflow_names.append(m.group(1).strip() if m else Path(wf).stem)
                    except Exception:
                        workflow_names.append(Path(wf).stem)

            nodes.append(
                ArchitectureNode(
                    id=ci_node_id,
                    label="GitHub Actions Workflows",
                    type="infrastructure",
                    category="ci_cd_pipeline",
                    technology="GitHub Actions",
                    file_references=workflow_files,
                    sub_modules=[f"Workflow: {n}" for n in workflow_names],
                    confidence="VERIFIED",
                    evidence=EvidenceMeta(
                        file_path=workflow_files[0],
                        evidence_category="config_manifest",
                        extraction_method="workflow_manifest_scan",
                        confidence="VERIFIED",
                    ),
                    description=f"{len(workflow_files)} CI/CD workflow definition(s) automating test, build, and deploy.",
                )
            )

            # Edge: Source -> GitHub Actions (TRIGGERS_WORKFLOW)
            edges.append(
                ArchitectureEdge(
                    id=f"deploy-edge-{repo_node_id}-{ci_node_id}",
                    source=repo_node_id,
                    target=ci_node_id,
                    label="Commit / PR Push",
                    relationship_type="TRIGGERS_WORKFLOW",
                    confidence="VERIFIED",
                    evidence_file=workflow_files[0],
                    description="Source code updates trigger automated workflow dispatch.",
                )
            )

        # 3. Check for Docker Containerization
        docker_files = [
            f for f in self.rel_files
            if Path(f).name.lower() == "dockerfile" or f.lower().endswith(".dockerfile")
        ]

        docker_node_id = None
        if docker_files:
            stages.append("Container Packaging")
            docker_node_id = "deploy-node-docker"
            base_images: List[str] = []
            for df in docker_files:
                df_path = self.rel_map.get(df)
                if df_path:
                    try:
                        content = df_path.read_text(encoding="utf-8", errors="ignore")
                        for match in re.finditer(r"^FROM\s+([a-zA-Z0-9_\-\./:]+)", content, re.MULTILINE | re.IGNORECASE):
                            base_images.append(match.group(1).strip())
                    except Exception:
                        pass

            nodes.append(
                ArchitectureNode(
                    id=docker_node_id,
                    label="Docker Container Build",
                    type="infrastructure",
                    category="container_packaging",
                    technology="Docker OCI Image",
                    file_references=docker_files,
                    sub_modules=[f"Base: {b}" for b in set(base_images)] if base_images else ["Container Image"],
                    confidence="VERIFIED",
                    evidence=EvidenceMeta(
                        file_path=docker_files[0],
                        evidence_category="config_manifest",
                        extraction_method="dockerfile_manifest_scan",
                        confidence="VERIFIED",
                    ),
                    description=f"Containerized image specification based on {', '.join(set(base_images)) if base_images else 'standard runtimes'}.",
                )
            )

            parent_id = ci_node_id if ci_node_id else repo_node_id
            edges.append(
                ArchitectureEdge(
                    id=f"deploy-edge-{parent_id}-{docker_node_id}",
                    source=parent_id,
                    target=docker_node_id,
                    label="Builds OCI Image",
                    relationship_type="DEPLOYED_AS",
                    confidence="VERIFIED",
                    evidence_file=docker_files[0],
                    description="Packages service runtime into deployable container artifact.",
                )
            )

        # 4. Check for Cloudflare / Serverless Deployment Manifests
        wrangler_files = [f for f in self.rel_files if Path(f).name.lower() == "wrangler.toml"]
        if wrangler_files:
            stages.append("Edge Runtime Deployment")
            cf_node_id = "deploy-node-cloudflare-edge"
            nodes.append(
                ArchitectureNode(
                    id=cf_node_id,
                    label="Cloudflare Workers Edge Target",
                    type="infrastructure",
                    category="deployment_target",
                    technology="Cloudflare Edge Network",
                    file_references=wrangler_files,
                    confidence="VERIFIED",
                    evidence=EvidenceMeta(
                        file_path=wrangler_files[0],
                        evidence_category="config_manifest",
                        extraction_method="wrangler_config_scan",
                        confidence="VERIFIED",
                    ),
                    description="Serverless edge deployment target configured via wrangler.toml.",
                )
            )

            parent_id = ci_node_id if ci_node_id else repo_node_id
            edges.append(
                ArchitectureEdge(
                    id=f"deploy-edge-{parent_id}-{cf_node_id}",
                    source=parent_id,
                    target=cf_node_id,
                    label="Wrangler Edge Deploy",
                    relationship_type="DEPLOYED_AS",
                    confidence="VERIFIED",
                    evidence_file=wrangler_files[0],
                    description="Deploys worker bundles to Cloudflare globally distributed edge.",
                )
            )

        return DeploymentModel(nodes=nodes, edges=edges, pipeline_stages=stages)
