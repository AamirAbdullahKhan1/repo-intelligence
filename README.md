# Repo Intelligence

AI-assisted repository intelligence platform that analyses a software repository, reconstructs its architecture and workflows, identifies potential security threats from code evidence, and generates an evidence-backed security assessment report.

> **Milestone 3 — Architecture & Workflows Complete.** This release reconstructs an interactive component graph and workflow execution pipelines from repository code evidence, integrates Azure OpenAI (GPT-4.1 default, GPT-6 Astra escalation) with deterministic fallback, and provides interactive React Flow diagrams and step-by-step workflow visualizers.

---

## Architecture

```
repo-intelligence/
├── frontend/                        # React · Vite · TypeScript · Tailwind CSS · React Flow
│   ├── src/
│   │   ├── components/              # Reusable UI components
│   │   │   ├── Sidebar.tsx          # Navigation sidebar with active repository context
│   │   │   ├── RepoInputPanel.tsx   # Live GitHub URL / ZIP input with analysis trigger
│   │   │   ├── RepositorySummaryCard.tsx # Code inventory dashboard with tabbed breakdowns
│   │   │   ├── BackendStatusCard.tsx
│   │   │   ├── EmptyState.tsx
│   │   │   ├── PageHeader.tsx
│   │   │   └── StatusBadge.tsx
│   │   ├── pages/                   # Route-level page components
│   │   │   ├── Dashboard.tsx        # Ingestion, status, and repository summary
│   │   │   ├── Architecture.tsx     # Interactive React Flow component graph & inspector
│   │   │   ├── Workflows.tsx        # Step-by-step request, auth, and CI/CD lifecycles
│   │   │   ├── ThreatModel.tsx      # Queued for Milestone 4 (threat findings)
│   │   │   └── Reports.tsx          # Queued for Milestone 5 (PDF export)
│   │   ├── context/
│   │   │   └── AnalysisContext.tsx  # Shared repository & architecture state across routes
│   │   ├── layouts/
│   │   │   └── AppLayout.tsx        # Persistent shell layout
│   │   ├── services/
│   │   │   └── api.ts               # Typed API client with /analyze endpoints
│   │   ├── hooks/
│   │   │   └── useHealth.ts         # Backend health polling hook
│   │   └── types/
│   │       └── index.ts             # Strict TypeScript types & schemas
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts               # Vite + /api proxy to localhost:8000
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── backend/                         # Python · FastAPI · Pydantic · Uvicorn
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── router.py        # Aggregates v1 endpoints
│   │   │       └── endpoints/
│   │   │           ├── health.py    # GET /api/v1/health
│   │   │           ├── capabilities.py # GET /api/v1/capabilities
│   │   │           └── analyze.py   # POST /api/v1/analyze/github & /upload
│   │   ├── core/
│   │   │   ├── errors.py            # AppError hierarchy + exception handlers
│   │   │   └── logging_config.py    # Structured logging setup
│   │   ├── schemas/
│   │   │   ├── common.py            # ErrorResponse
│   │   │   ├── health.py            # HealthResponse
│   │   │   ├── capabilities.py      # CapabilitiesResponse, Capability
│   │   │   ├── analysis.py          # AnalysisResponse, RepositoryInventory
│   │   │   └── architecture.py      # ArchitectureModel, ArchitectureNode, Edge, Workflow
│   │   ├── services/
│   │   │   ├── repository/          # Safe repository ingestion & sandboxing
│   │   │   │   ├── safe_extract.py  # Zip-Slip protection, size limits, symlink filter
│   │   │   │   ├── github_clone.py  # Shallow git clone with hook execution suppression
│   │   │   │   └── workspace.py     # Isolated temporary sandboxes
│   │   │   ├── analysis/            # Deterministic code inventory engine
│   │   │   │   └── inventory.py     # AST/regex & manifest parsing
│   │   │   ├── architecture/        # Architecture model & workflow builder
│   │   │   │   └── builder.py       # Graph nodes, relationship edges, and workflow steps
│   │   │   ├── llm/                 # Azure OpenAI client (GPT-4.1 / GPT-6 Astra)
│   │   │   │   └── client.py        # Evidence-grounded architecture reasoning with fallback
│   │   │   ├── threat_model/        # Planned: evidence-linked threat findings (Milestone 4)
│   │   │   └── reporting/           # Planned: ReportLab PDF generation (Milestone 5)
│   │   ├── main.py                  # FastAPI app, CORS, exception handlers
│   │   └── config.py                # Pydantic Settings (all env vars)
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_health.py
│   │   ├── test_capabilities.py
│   │   ├── test_config.py
│   │   ├── test_safe_extract.py     # Zip-Slip, size bomb, and sanitization tests
│   │   ├── test_github_clone.py     # URL validation and clone security tests
│   │   ├── test_analysis.py         # Deterministic fixture analysis tests
│   │   ├── test_architecture.py     # Graph nodes, edges, and workflow builder tests
│   │   ├── test_llm_client.py       # Dual-model routing and fallback tests
│   │   └── test_api_analyze.py      # Endpoints integration tests
│   ├── requirements.txt
│   └── .env.example
│
├── .gitignore
└── README.md
```

---

## How to Analyze Any Public GitHub Repository

You can enter any public GitHub repository URL (e.g. `https://github.com/fastapi/fastapi` or `https://github.com/pallets/flask`) into the **Overview** dashboard and immediately get:
1. **Repository Inventory:** Languages breakdown, frameworks, entry points, detected HTTP endpoints, database drivers, and authentication mechanisms.
2. **Architecture Map:** An interactive component node graph (Client, Services, Database, Auth, Infra) rendered with React Flow, with zoom/pan and a component inspection panel.
3. **Workflow Pipelines:** Step-by-step visual execution paths for HTTP ingress, authentication challenges, and CI/CD pipelines with source citations.
4. **Architectural Explanation:** Evidence-grounded narrative produced by Azure OpenAI (or the built-in deterministic synthesizer if Azure keys are not yet configured).

---

## Startup Instructions

### 1. Start Backend Server
```powershell
cd backend
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```
- API is available at `http://localhost:8000`
- Interactive Swagger docs: `http://localhost:8000/docs`

### 2. Start Frontend Dev Server
```powershell
cd frontend
npm run dev
# or: pnpm dev
```
- Open `http://localhost:5173` in your browser.

---

## Running Automated Tests

```bash
cd backend
.venv\Scripts\activate
pytest tests/ -v
```

### Frontend Build & Type-Check
```bash
cd frontend
npx tsc --noEmit
npx vite build
```

---

## Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| FastAPI shell & health check | ✅ Implemented | Production-ready with centralized config |
| Dynamic capabilities discovery | ✅ Implemented | Distinguishes implemented vs. planned |
| Safe GitHub Repository Ingest | ✅ Implemented | Depth=1, hook suppression, URL validation |
| Safe ZIP Archive Ingest | ✅ Implemented | Zip-Slip traversal protection & size bomb checks |
| Deterministic Code Inventory | ✅ Implemented | Languages, manifests, deps, routes, DB, auth |
| Architecture Graph & React Flow | ✅ Implemented | Interactive nodes, edges, and inspector drawer |
| Workflow Sequence Pipeline | ✅ Implemented | Request, auth, and CI/CD execution steps |
| Azure OpenAI Integration | ✅ Implemented | GPT-4.1 default + Astra escalation + fallback |
| Automated Backend Tests | ✅ Implemented | 30/30 Pytest tests passing |
| Frontend Shell & Build | ✅ Implemented | Strict TypeScript & Vite build passing |
| Threat Model Engine | 🔲 Planned (Milestone 4) | Evidence-linked findings & SDLC recommendations |
| PDF Report Export | 🔲 Planned (Milestone 5) | ReportLab PDF generator |
