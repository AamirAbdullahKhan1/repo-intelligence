# Repo Intelligence

AI-assisted repository intelligence platform that analyses a software repository, reconstructs its architecture and workflows, identifies potential security threats from code evidence, and generates an evidence-backed security assessment report.

> **Milestone 2 — Repository Ingestion & Code Inventory.** This release delivers safe GitHub repository cloning and ZIP archive ingestion, isolated sandboxed workspaces, deterministic code inventory (languages, frameworks, manifests, dependencies, HTTP routes, databases, authentication, and infrastructure), and live dashboard visualization.

---

## Architecture

```
repo-intelligence/
├── frontend/                        # React · Vite · TypeScript · Tailwind CSS
│   ├── src/
│   │   ├── components/              # Reusable UI components
│   │   │   ├── Sidebar.tsx          # Navigation sidebar with backend status
│   │   │   ├── RepoInputPanel.tsx   # GitHub URL / ZIP input with real analysis trigger
│   │   │   ├── RepositorySummaryCard.tsx # Code inventory dashboard with tabbed breakdowns
│   │   │   ├── BackendStatusCard.tsx
│   │   │   ├── EmptyState.tsx
│   │   │   ├── PageHeader.tsx
│   │   │   └── StatusBadge.tsx
│   │   ├── pages/                   # Route-level page components
│   │   │   ├── Dashboard.tsx        # Ingestion, status, and active repository summary
│   │   │   ├── Architecture.tsx     # Queued for Milestone 3 (React Flow diagram)
│   │   │   ├── Workflows.tsx        # Queued for Milestone 3 (workflow sequences)
│   │   │   ├── ThreatModel.tsx      # Queued for Milestone 4 (threat findings)
│   │   │   └── Reports.tsx          # Queued for Milestone 5 (PDF export)
│   │   ├── layouts/
│   │   │   └── AppLayout.tsx        # Sidebar + main content layout
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
│   │   │   └── analysis.py          # AnalysisResponse, RepositoryInventory, etc.
│   │   ├── services/
│   │   │   ├── repository/          # Safe repository ingestion & sandboxing
│   │   │   │   ├── safe_extract.py  # Zip-Slip protection, size limits, symlink filter
│   │   │   │   ├── github_clone.py  # Shallow git clone with hook execution suppression
│   │   │   │   └── workspace.py     # Isolated temporary sandboxes
│   │   │   ├── analysis/            # Deterministic code inventory engine
│   │   │   │   └── inventory.py     # AST/regex & manifest parsing
│   │   │   ├── architecture/        # Planned: component model builder (Milestone 3)
│   │   │   ├── llm/                 # Planned: Azure OpenAI routing (Milestone 3)
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
│   │   └── test_api_analyze.py      # Endpoints integration tests
│   ├── requirements.txt
│   └── .env.example
│
├── .gitignore
└── README.md
```

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.11+ | For the backend |
| Node.js | 18+ | For the frontend |
| pnpm / npm | 9+ | Package management |
| Git | 2.x+ | Available on PATH for repository ingestion |

---

## Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the development server
uvicorn app.main:app --reload --port 8000
```

The API is available at **http://localhost:8000**.  
Interactive documentation: **http://localhost:8000/docs**

---

## Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install
# or: npm install

# Start the development server
pnpm dev
# or: npm run dev
```

The frontend is available at **http://localhost:5173**.  
Vite proxies all `/api` requests to `http://localhost:8000`.

---

## API Endpoints

### 1. `GET /api/v1/health`
Liveness check. Returns HTTP 200 without requiring Azure OpenAI credentials.

### 2. `GET /api/v1/capabilities`
Lists platform capabilities distinguishing `implemented` from `planned`.

### 3. `POST /api/v1/analyze/github`
Safe shallow clone of a public GitHub repository. Sanitizes URL, suppresses git hooks, and produces deterministic code inventory.
```json
{
  "url": "https://github.com/fastapi/fastapi"
}
```

### 4. `POST /api/v1/analyze/upload`
Accepts a `multipart/form-data` upload with field `file: <archive.zip>`. Enforces 50 MiB limits and Zip-Slip traversal protection.

---

## Running Tests

### Backend Unit & Integration Tests (25 tests)
```bash
cd backend
.venv\Scripts\activate
pytest tests/ -v
```

### Frontend Type-Check & Build
```bash
cd frontend
npx tsc --noEmit
npx vite build
```

---

## Current Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| FastAPI application shell | ✅ Implemented | Production-ready with centralized config |
| `GET /api/v1/health` | ✅ Implemented | Liveness check |
| `GET /api/v1/capabilities` | ✅ Implemented | Dynamic discovery |
| CORS for local Vite dev server | ✅ Implemented | Reverse-proxied via Vite |
| Safe GitHub Repository Ingest | ✅ Implemented | Depth=1, hook suppression, URL validation |
| Safe ZIP Archive Ingest | ✅ Implemented | Zip-Slip traversal protection & size bomb checks |
| Deterministic Code Inventory | ✅ Implemented | Language metrics, manifests, deps, routes, DB, auth |
| Live Dashboard Visualizer | ✅ Implemented | Tabbed breakdown with verified code evidence pill |
| Automated Backend Tests | ✅ Implemented | 25/25 Pytest tests passing |
| Frontend Shell & Build | ✅ Implemented | Strict TypeScript & Vite build passing |
| Architecture Model & Diagram | 🔲 Planned (Milestone 3) | React Flow interactive graph |
| Azure OpenAI Interpretation | 🔲 Planned (Milestone 3) | GPT-4.1 default + Astra escalation |
| Threat Model Engine | 🔲 Planned (Milestone 4) | Evidence-linked findings |
| PDF Report Export | 🔲 Planned (Milestone 5) | ReportLab PDF generator |
