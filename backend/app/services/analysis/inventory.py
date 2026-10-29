"""
Deterministic Repository Inventory Analyzer.
Extracts languages, frameworks, manifests, entry points, routes,
database access, authentication mechanisms, and infrastructure configurations
from source code without dynamic code execution.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
import re
from typing import Dict, List, Optional, Set, Tuple

# In Python 3.11+, tomllib is standard library
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore

from app.schemas.analysis import (
    ComponentFinding,
    Dependency,
    LanguageStat,
    RepositoryInventory,
    RouteFinding,
)

logger = logging.getLogger(__name__)

# Files and directories to skip
EXCLUDED_DIRS = {
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
    "target",
    ".next",
    "coverage",
}

# Language mapping by file extension
EXT_TO_LANGUAGE = {
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".go": "Go",
    ".java": "Java",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".cpp": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sql": "SQL",
    ".sh": "Shell",
    ".bash": "Shell",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".json": "JSON",
    ".md": "Markdown",
    ".dockerfile": "Dockerfile",
}

# Framework signatures (in dependencies or files)
FRAMEWORK_RULES = [
    # Python
    ("FastAPI", ["fastapi"], [r"from\s+fastapi\s+import", r"import\s+fastapi"]),
    ("Flask", ["flask"], [r"from\s+flask\s+import", r"import\s+flask"]),
    ("Django", ["django"], [r"from\s+django\s+import", r"import\s+django"]),
    ("Starlette", ["starlette"], [r"from\s+starlette\s+import"]),
    ("Tornado", ["tornado"], [r"from\s+tornado\s+import"]),
    # JavaScript / TypeScript
    ("Express", ["express"], [r"require\(['\"]express['\"]", r"from\s+['\"]express['\"]"]),
    ("Next.js", ["next"], [r"from\s+['\"]next/", r"require\(['\"]next['\"]"]),
    ("NestJS", ["@nestjs/core"], [r"from\s+['\"]@nestjs/"]),
    ("React", ["react"], [r"from\s+['\"]react['\"]", r"require\(['\"]react['\"]"]),
    ("Vue", ["vue"], [r"from\s+['\"]vue['\"]"]),
    ("Fastify", ["fastify"], [r"require\(['\"]fastify['\"]", r"from\s+['\"]fastify['\"]"]),
    # Go
    ("Gin", ["github.com/gin-gonic/gin"], [r"github\.com/gin-gonic/gin"]),
    ("Echo", ["github.com/labstack/echo"], [r"github\.com/labstack/echo"]),
    ("Fiber", ["github.com/gofiber/fiber"], [r"github\.com/gofiber/fiber"]),
    # Java
    ("Spring Boot", ["spring-boot-starter"], [r"org\.springframework\.boot"]),
]

# Database patterns
DATABASE_RULES = [
    ("PostgreSQL", ["psycopg2", "psycopg2-binary", "asyncpg", "pg"], [r"postgres://", r"postgresql://"]),
    ("MySQL", ["mysqlclient", "pymysql", "mysql2"], [r"mysql://"]),
    ("SQLite", ["sqlite3", "aiosqlite"], [r"sqlite://", r"\.sqlite3?\b"]),
    ("MongoDB", ["pymongo", "motor", "mongoose", "mongodb"], [r"mongodb://", r"mongodb\+srv://"]),
    ("Redis", ["redis", "aioredis", "ioredis"], [r"redis://", r"rediss://"]),
    ("SQLAlchemy", ["sqlalchemy"], [r"from\s+sqlalchemy", r"import\s+sqlalchemy"]),
    ("Prisma", ["@prisma/client", "prisma"], [r"@prisma/client"]),
    ("Mongoose", ["mongoose"], [r"require\(['\"]mongoose['\"]", r"from\s+['\"]mongoose['\"]"]),
    ("TypeORM", ["typeorm"], [r"from\s+['\"]typeorm['\"]"]),
]

# Authentication patterns
AUTH_RULES = [
    ("JWT", ["pyjwt", "jsonwebtoken", "jose", "python-jose"], [r"jwt\.sign", r"jwt\.verify", r"jwt\.decode", r"jwt\.encode"]),
    ("OAuth / OIDC", ["authlib", "passport", "next-auth", "oauth2"], [r"OAuth2PasswordBearer", r"passport\.use", r"next-auth"]),
    ("Password Hashing", ["bcrypt", "passlib", "argon2-cffi"], [r"bcrypt\.hash", r"bcrypt\.gensalt", r"CryptContext"]),
    ("Session Auth", ["express-session", "flask-login"], [r"express-session", r"LoginManager"]),
]


class RepositoryAnalyzer:
    """Performs deterministic static analysis on an extracted repository directory."""

    def __init__(self, root_dir: Path, repo_name: str, source_type: str = "github") -> None:
        self.root_dir = root_dir.resolve()
        self.repo_name = repo_name
        self.source_type = source_type
        self.files: List[Path] = []

    def analyze(self) -> RepositoryInventory:
        """Execute all deterministic analyzers and construct the inventory."""
        self._collect_files()

        lang_stats, total_bytes, primary_lang = self._analyze_languages()
        manifests, dependencies = self._parse_manifests()
        frameworks = self._detect_frameworks(dependencies)
        entry_points = self._detect_entry_points()
        routes = self._detect_routes()
        databases = self._detect_databases(dependencies)
        auth_mechanisms = self._detect_authentication(dependencies)
        infrastructure = self._detect_infrastructure()

        summary = self._generate_summary(
            primary_lang, len(self.files), frameworks, routes, databases
        )

        return RepositoryInventory(
            repo_name=self.repo_name,
            source_type=self.source_type,  # type: ignore[arg-type]
            languages=lang_stats,
            primary_language=primary_lang,
            frameworks=frameworks,
            manifests=manifests,
            dependencies=dependencies,
            entry_points=entry_points,
            routes=routes,
            databases=databases,
            authentication=auth_mechanisms,
            infrastructure=infrastructure,
            total_files=len(self.files),
            total_bytes=total_bytes,
            summary=summary,
        )

    def _collect_files(self) -> None:
        """Collect all relevant files while skipping excluded vendor/meta directories."""
        self.files = []
        for path in self.root_dir.rglob("*"):
            if not path.is_file():
                continue
            # Check if any parent component is in EXCLUDED_DIRS
            rel_parts = path.relative_to(self.root_dir).parts
            if any(part in EXCLUDED_DIRS for part in rel_parts):
                continue
            self.files.append(path)

    def _analyze_languages(self) -> Tuple[List[LanguageStat], int, Optional[str]]:
        """Compute language breakdown by extension and byte count."""
        lang_counts: Dict[str, int] = {}
        lang_bytes: Dict[str, int] = {}
        total_code_bytes = 0

        for file_path in self.files:
            ext = file_path.suffix.lower()
            if file_path.name.lower() == "dockerfile":
                lang = "Dockerfile"
            else:
                lang = EXT_TO_LANGUAGE.get(ext)

            if not lang:
                continue

            try:
                size = file_path.stat().st_size
            except OSError:
                size = 0

            lang_counts[lang] = lang_counts.get(lang, 0) + 1
            lang_bytes[lang] = lang_bytes.get(lang, 0) + size
            total_code_bytes += size

        stats: List[LanguageStat] = []
        for lang, byte_count in sorted(lang_bytes.items(), key=lambda item: item[1], reverse=True):
            pct = round((byte_count / total_code_bytes * 100), 1) if total_code_bytes > 0 else 0.0
            stats.append(
                LanguageStat(
                    name=lang,
                    files_count=lang_counts[lang],
                    bytes_count=byte_count,
                    percentage=pct,
                )
            )

        primary = stats[0].name if stats else None
        return stats, total_code_bytes, primary

    def _parse_manifests(self) -> Tuple[List[str], List[Dependency]]:
        """Extract manifests and declared dependencies without package execution."""
        manifest_files: List[str] = []
        dependencies: List[Dependency] = []

        for file_path in self.files:
            rel_path = str(file_path.relative_to(self.root_dir)).replace("\\", "/")
            fname = file_path.name.lower()

            # package.json
            if fname == "package.json":
                manifest_files.append(rel_path)
                dependencies.extend(self._parse_package_json(file_path, rel_path))

            # requirements.txt
            elif fname in ("requirements.txt", "requirements-dev.txt", "requirements.in"):
                manifest_files.append(rel_path)
                dependencies.extend(self._parse_requirements_txt(file_path, rel_path))

            # pyproject.toml
            elif fname == "pyproject.toml":
                manifest_files.append(rel_path)
                dependencies.extend(self._parse_pyproject_toml(file_path, rel_path))

            # go.mod
            elif fname == "go.mod":
                manifest_files.append(rel_path)
                dependencies.extend(self._parse_go_mod(file_path, rel_path))

            # Cargo.toml
            elif fname == "cargo.toml":
                manifest_files.append(rel_path)

            # pom.xml
            elif fname == "pom.xml":
                manifest_files.append(rel_path)

        return sorted(manifest_files), dependencies

    def _parse_package_json(self, path: Path, rel_path: str) -> List[Dependency]:
        deps: List[Dependency] = []
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
            prod = data.get("dependencies", {})
            dev = data.get("devDependencies", {})
            for name, ver in prod.items():
                deps.append(Dependency(name=name, version=str(ver), source_file=rel_path, is_dev=False))
            for name, ver in dev.items():
                deps.append(Dependency(name=name, version=str(ver), source_file=rel_path, is_dev=True))
        except Exception as e:
            logger.debug("Could not parse %s: %s", path, e)
        return deps

    def _parse_requirements_txt(self, path: Path, rel_path: str) -> List[Dependency]:
        deps: List[Dependency] = []
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or line.startswith("-"):
                        continue
                    # split on specifiers
                    match = re.match(r"^([a-zA-Z0-9_\-\.]+)(?:([<>=~!].*))?", line)
                    if match:
                        name, ver = match.group(1), match.group(2)
                        deps.append(Dependency(name=name, version=ver.strip() if ver else None, source_file=rel_path))
        except Exception as e:
            logger.debug("Could not parse %s: %s", path, e)
        return deps

    def _parse_pyproject_toml(self, path: Path, rel_path: str) -> List[Dependency]:
        deps: List[Dependency] = []
        if tomllib is None:
            return deps
        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
            # standard PEP 621 [project.dependencies]
            project_deps = data.get("project", {}).get("dependencies", [])
            for dep_str in project_deps:
                match = re.match(r"^([a-zA-Z0-9_\-\.]+)(?:([<>=~!].*))?", dep_str.strip())
                if match:
                    deps.append(Dependency(name=match.group(1), version=match.group(2), source_file=rel_path))
            # Poetry [tool.poetry.dependencies]
            poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            for name, ver in poetry_deps.items():
                if name.lower() != "python":
                    deps.append(Dependency(name=name, version=str(ver), source_file=rel_path))
        except Exception as e:
            logger.debug("Could not parse %s: %s", path, e)
        return deps

    def _parse_go_mod(self, path: Path, rel_path: str) -> List[Dependency]:
        deps: List[Dependency] = []
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            requires = re.findall(r"require\s*\((.*?)\)", content, re.DOTALL)
            for block in requires:
                for line in block.splitlines():
                    parts = line.strip().split()
                    if len(parts) >= 2 and not parts[0].startswith("//"):
                        deps.append(Dependency(name=parts[0], version=parts[1], source_file=rel_path))
        except Exception as e:
            logger.debug("Could not parse %s: %s", path, e)
        return deps

    def _detect_frameworks(self, dependencies: List[Dependency]) -> List[str]:
        """Detect web and application frameworks from manifests and import statements."""
        detected: Set[str] = set()
        dep_names = {d.name.lower() for d in dependencies}

        # Check by dependency name
        for fw_name, pkg_names, _ in FRAMEWORK_RULES:
            if any(p.lower() in dep_names for p in pkg_names):
                detected.add(fw_name)

        # Check code imports for files in repo
        code_files = [f for f in self.files if f.suffix.lower() in (".py", ".js", ".ts", ".tsx", ".go", ".java")]
        for fpath in code_files[:100]:  # limit scan for performance
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
                for fw_name, _, patterns in FRAMEWORK_RULES:
                    if fw_name not in detected:
                        if any(re.search(pat, content) for pat in patterns):
                            detected.add(fw_name)
            except Exception:
                continue

        return sorted(detected)

    def _detect_entry_points(self) -> List[str]:
        """Identify standard application entry points."""
        entry_points: List[str] = []
        common_entry_names = {
            "main.py",
            "app.py",
            "asgi.py",
            "wsgi.py",
            "manage.py",
            "server.ts",
            "server.js",
            "index.ts",
            "index.js",
            "main.go",
        }

        for fpath in self.files:
            rel = str(fpath.relative_to(self.root_dir)).replace("\\", "/")
            if fpath.name.lower() in common_entry_names:
                entry_points.append(rel)
            elif fpath.name.lower() == "dockerfile":
                entry_points.append(f"{rel} (Container Entrypoint)")

        return sorted(entry_points)

    def _detect_routes(self) -> List[RouteFinding]:
        """Extract HTTP endpoints/routes from Python and JavaScript/TypeScript files."""
        routes: List[RouteFinding] = []
        target_files = [
            f for f in self.files
            if f.suffix.lower() in (".py", ".js", ".ts") and f.stat().st_size < 1_000_000
        ]

        # FastAPI / Flask decorators: @app.get("/path") or @router.post("/path")
        py_route_re = re.compile(
            r"@(?:[a-zA-Z0-9_]+)\.(get|post|put|delete|patch|options|head)\s*\(\s*[\"']([^\"']+)[\"']",
            re.IGNORECASE,
        )
        # Express route declarations: router.get('/path', ...) or app.post('/path', ...)
        js_route_re = re.compile(
            r"\b(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*[\"']([^\"']+)[\"']",
            re.IGNORECASE,
        )

        for fpath in target_files:
            rel = str(fpath.relative_to(self.root_dir)).replace("\\", "/")
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    for line_idx, line in enumerate(f, start=1):
                        # Python routes
                        if fpath.suffix.lower() == ".py":
                            for match in py_route_re.finditer(line):
                                method = match.group(1).upper()
                                path = match.group(2)
                                routes.append(RouteFinding(method=method, path=path, file=rel, line_number=line_idx))
                        # JS / TS routes
                        elif fpath.suffix.lower() in (".js", ".ts"):
                            for match in js_route_re.finditer(line):
                                method = match.group(1).upper()
                                path = match.group(2)
                                routes.append(RouteFinding(method=method, path=path, file=rel, line_number=line_idx))
            except Exception as e:
                logger.debug("Failed reading file for routes %s: %s", fpath, e)

        return routes

    def _detect_databases(self, dependencies: List[Dependency]) -> List[ComponentFinding]:
        """Identify database drivers, connection URI patterns, and ORMs."""
        findings: List[ComponentFinding] = []
        dep_names = {d.name.lower() for d in dependencies}

        for db_name, packages, uri_patterns in DATABASE_RULES:
            matched_packages = [p for p in packages if p.lower() in dep_names]
            matched_files: List[str] = []

            for fpath in self.files[:80]:
                if fpath.suffix.lower() in (".py", ".js", ".ts", ".env", ".example", ".yaml", ".json"):
                    try:
                        content = fpath.read_text(encoding="utf-8", errors="ignore")
                        if any(re.search(pat, content, re.IGNORECASE) for pat in uri_patterns):
                            matched_files.append(str(fpath.relative_to(self.root_dir)).replace("\\", "/"))
                    except Exception:
                        continue

            if matched_packages or matched_files:
                details_parts = []
                if matched_packages:
                    details_parts.append(f"Packages: {', '.join(matched_packages)}")
                if matched_files:
                    details_parts.append(f"URI/schema references in {len(matched_files)} files")

                findings.append(
                    ComponentFinding(
                        category="database",
                        name=db_name,
                        evidence_type="verified_code_evidence",
                        file_references=matched_files[:5],
                        details="; ".join(details_parts) if details_parts else "Detected from codebase patterns",
                    )
                )

        return findings

    def _detect_authentication(self, dependencies: List[Dependency]) -> List[ComponentFinding]:
        """Identify authentication libraries and security mechanisms."""
        findings: List[ComponentFinding] = []
        dep_names = {d.name.lower() for d in dependencies}

        for auth_name, packages, patterns in AUTH_RULES:
            matched_packages = [p for p in packages if p.lower() in dep_names]
            matched_files: List[str] = []

            for fpath in self.files[:80]:
                if fpath.suffix.lower() in (".py", ".js", ".ts"):
                    try:
                        content = fpath.read_text(encoding="utf-8", errors="ignore")
                        if any(re.search(pat, content) for pat in patterns):
                            matched_files.append(str(fpath.relative_to(self.root_dir)).replace("\\", "/"))
                    except Exception:
                        continue

            if matched_packages or matched_files:
                details = f"Identified via {', '.join(matched_packages)}" if matched_packages else "Identified via code patterns"
                findings.append(
                    ComponentFinding(
                        category="authentication",
                        name=auth_name,
                        evidence_type="verified_code_evidence",
                        file_references=matched_files[:5],
                        details=details,
                    )
                )

        return findings

    def _detect_infrastructure(self) -> List[ComponentFinding]:
        """Identify container, orchestration, and CI/CD infrastructure manifests."""
        findings: List[ComponentFinding] = []

        dockerfiles: List[str] = []
        compose_files: List[str] = []
        ci_workflows: List[str] = []
        k8s_files: List[str] = []

        for fpath in self.files:
            rel = str(fpath.relative_to(self.root_dir)).replace("\\", "/")
            lower_rel = rel.lower()

            if fpath.name.lower() == "dockerfile" or lower_rel.endswith(".dockerfile"):
                dockerfiles.append(rel)
            elif "docker-compose" in lower_rel and lower_rel.endswith((".yml", ".yaml")):
                compose_files.append(rel)
            elif ".github/workflows" in lower_rel and lower_rel.endswith((".yml", ".yaml")):
                ci_workflows.append(rel)
            elif ("k8s" in lower_rel or "kubernetes" in lower_rel) and lower_rel.endswith((".yml", ".yaml")):
                k8s_files.append(rel)

        if dockerfiles:
            findings.append(
                ComponentFinding(
                    category="infrastructure",
                    name="Docker Containerization",
                    evidence_type="verified_code_evidence",
                    file_references=dockerfiles,
                    details=f"{len(dockerfiles)} Dockerfile(s) defined",
                )
            )

        if compose_files:
            findings.append(
                ComponentFinding(
                    category="infrastructure",
                    name="Docker Compose",
                    evidence_type="verified_code_evidence",
                    file_references=compose_files,
                    details="Multi-container service definition",
                )
            )

        if ci_workflows:
            findings.append(
                ComponentFinding(
                    category="infrastructure",
                    name="GitHub Actions CI/CD",
                    evidence_type="verified_code_evidence",
                    file_references=ci_workflows,
                    details=f"{len(ci_workflows)} workflow definition(s)",
                )
            )

        if k8s_files:
            findings.append(
                ComponentFinding(
                    category="infrastructure",
                    name="Kubernetes Orchestration",
                    evidence_type="verified_code_evidence",
                    file_references=k8s_files,
                    details="Kubernetes resource manifests detected",
                )
            )

        return findings

    def _generate_summary(
        self,
        primary_lang: Optional[str],
        file_count: int,
        frameworks: List[str],
        routes: List[RouteFinding],
        databases: List[ComponentFinding],
    ) -> str:
        """Create a concise, evidence-grounded summary of the repository structure."""
        parts = []
        if primary_lang:
            parts.append(f"Primarily written in {primary_lang}")
        parts.append(f"{file_count} total analyzed source files")

        if frameworks:
            parts.append(f"built with {', '.join(frameworks)}")
        if routes:
            parts.append(f"exposing {len(routes)} detected HTTP route(s)")
        if databases:
            db_names = [d.name for d in databases]
            parts.append(f"utilizing {', '.join(db_names)}")

        return ". ".join(parts) + "."
