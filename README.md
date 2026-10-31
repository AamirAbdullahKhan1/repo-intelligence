# Repo Intelligence

A local, AI-independent TypeScript/JavaScript repository analysis MVP. Submit a public GitHub repository or ZIP, save a validated static graph in SQLite, and explore system architecture or a bounded internal call graph with source evidence.

The project does not execute target scripts, install target dependencies, or invoke a model. Framework support is incremental. Read [security and analysis limits](docs/implementation/security-and-limits.md) before using untrusted inputs.

## Run locally on Windows

Prerequisites: Python 3.12, Node.js 22, pnpm. Run these trusted application setup commands; the analyzer never runs them inside submitted repositories.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
cd workers/typescript
npm ci --ignore-scripts --no-audit --no-fund
cd ../..
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In another terminal, from the project root:

```powershell
cd frontend
pnpm install --frozen-lockfile --ignore-scripts
pnpm run dev --host 127.0.0.1
```

Open the Vite address printed in that terminal (normally `http://127.0.0.1:5173`). The development proxy sends `/api` to `127.0.0.1:8000`. API documentation: `http://127.0.0.1:8000/docs`.

For another local backend port, set `REPO_INTELLIGENCE_API` before starting Vite. For development reload, restrict watched directories to trusted application source. Extracted client snapshots use OS temporary directories outside the project tree.

No provider settings are required. Defaults place local results in `data/analysis.sqlite`; optional backend settings are in `backend/.env.example`. Keep the API on loopback with one worker process. The queue is not designed for multiple uvicorn workers.

## Architecture exploration

The default diagram shows major modules, source boundaries and integration groups. Use the explorer to move from repository to packages, modules, and functions/classes. System architecture stays abstract; Core workflow follows a selected source entry. Evidence and scoped unresolved references are available separately from detailed compiler diagnostics.

See the [usability implementation and reconciled tool audit](docs/implementation/architecture-usability.md). Browser checks over the saved GitDiagram graph are in `scripts/verify_exploration.cjs`; `scripts/verify_ui.cjs` also retains the ZIP-upload regression. Set `APP_URL` to the running frontend address (the current preview is port 5175). These checks use the existing snapshot and local Playwright/Chrome environment described below.

## Use

1. Enter a root public GitHub URL or upload a ZIP without vendored dependencies/build outputs. Progress and cancellation appear in the sidebar.
2. Open a saved snapshot. The system view offers source boundaries/usage, infrastructure declarations, or both layers.
3. Switch to core workflow, choose an entry, and adjust depth/node budget. Nested definitions and dependencies are optional and distinct from calls.
4. Select a component or connection for file/line/hash evidence. Select a function and choose **Explore calls from this function** to drill down.
5. Review coverage and paginated unresolved relationships. A missing arrow is not proof that no relationship exists.

The UI renders backend projections. ELK computes node positions and orthogonal edge routing in a browser Web Worker; React Flow provides zoom, pan and selection. The browser does not infer relationships.

## Structure

```text
backend/app/
  api/             HTTP endpoints and response contracts
  ingestion/       public GitHub archive acquisition, safe ZIP extraction, snapshots
  analysis/        Python orchestration and narrow configuration adapters
  evidence/        source validation and limited metadata redaction
  graph/           system/workflow projections from the same graph
  persistence/     SQLite jobs and canonical graph storage
  contracts.py     worker/API Pydantic models
  jobs.py          bounded local execution queue
backend/workers/typescript/
  index.cjs        trusted TypeScript Compiler API analysis
  adapters/        Next, Express and Wrangler rules
  guard.cjs        worker API guard (not an OS sandbox)
frontend/src/
  components/{repository,diagrams,evidence}/
  hooks/           submission/job/snapshot state
  pages/           architecture workspace and filters
  services/        typed API client
shared/            frontend contracts and generated backend JSON/OpenAPI schemas
samples/           static fixtures; never install or execute them
scripts/           contract generation, CLI and acceptance checks
backend/tests/     compiler, framework, ingestion and API regressions
docs/implementation/  audit, handover, tool matrix and limitations
```

`data/`, `tmp/` and `output/` contain private/generated state and are ignored by Git. Historical research/POC outputs in `output/` are retained as artifacts; the obsolete second POC runtime and static-public graph have been removed.

## Verify

From the project root:

```powershell
.\backend\.venv\Scripts\python.exe -m pytest backend/tests -q
.\backend\.venv\Scripts\python.exe scripts/export_contracts.py --check
.\backend\.venv\Scripts\python.exe scripts/tool_status.py
cd frontend
pnpm run build
pnpm run format:check
```

Regenerate schemas with `scripts/export_contracts.py` after backend contract changes. TypeScript definitions are centralized in `shared/contracts/analysis.ts`; JSON/OpenAPI schemas are generated from backend models. Keep both in review when changing an API contract.

For live API checks: `scripts/verify_live.py --source <public-test-repo-folder> --github https://github.com/octocat/Hello-World` packages the folder and submits it through the real ZIP API. `scripts/verify_ui.cjs` uses Playwright from `PLAYWRIGHT_MODULE` (or an installed `playwright` package) and local Chrome; it expects the GitDiagram acceptance snapshot and `tmp/known-system.zip`. See the [implementation handover](docs/implementation/handover.md) for exact verification scope and artifacts.

Optional tools such as Syft, Semgrep and Gitleaks are not prerequisites. Their actual installed/integrated status is recorded in the handover; package inventory is currently manifest-based, not a complete SBOM.
