# Repo Intelligence

AI-assisted repository intelligence platform that analyses a software repository, reconstructs its architecture and workflows, identifies potential security threats from code evidence, and generates an evidence-backed security assessment report.

> **Milestone 1 — Foundation.** This release delivers the application shell, API infrastructure, and end-to-end connectivity. Repository analysis, architecture mapping, threat modelling, and PDF export are planned for subsequent milestones.

---

## Architecture

```
repo-intelligence/
├── frontend/                        # React · Vite · TypeScript · Tailwind CSS
│   ├── src/
│   │   ├── components/              # Reusable UI components
│   │   │   ├── Sidebar.tsx          # Navigation sidebar with backend status
│   │   │   ├── RepoInputPanel.tsx   # GitHub URL / ZIP input with validation
│   │   │   ├── BackendStatusCard.tsx
│   │   │   ├── EmptyState.tsx
│   │   │   ├── PageHeader.tsx
│   │   │   └── StatusBadge.tsx
│   │   ├── pages/                   # Route-level page components
│   │   │   ├── Dashboard.tsx        # Main overview with input panel
│   │   │   ├── Architecture.tsx     # Planned: interactive diagram (Milestone 3)
│   │   │   ├── Workflows.tsx        # Planned: workflow analysis (Milestone 3)
│   │   │   ├── ThreatModel.tsx      # Planned: threat findings (Milestone 4)
│   │   │   └── Reports.tsx          # Planned: PDF export (Milestone 5)
│   │   ├── layouts/
│   │   │   └── AppLayout.tsx        # Sidebar + main content layout
│   │   ├── services/
│   │   │   └── api.ts               # Typed API client (proxied through Vite)
│   │   ├── hooks/
│   │   │   └── useHealth.ts         # Backend health polling hook
│   │   └── types/
│   │       └── index.ts             # Shared TypeScript types
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
│   │   │           └── capabilities.py  # GET /api/v1/capabilities
│   │   ├── core/
│   │   │   ├── errors.py            # AppError hierarchy + exception handlers
│   │   │   └── logging_config.py    # Structured logging setup
│   │   ├── schemas/
│   │   │   ├── common.py            # ErrorResponse
│   │   │   ├── health.py            # HealthResponse
│   │   │   └── capabilities.py      # CapabilitiesResponse, Capability
│   │   ├── services/                # Service stubs (implemented in later milestones)
│   │   │   ├── repository/          # Planned: GitHub clone + ZIP ingestion
│   │   │   ├── analysis/            # Planned: language/framework detection
│   │   │   ├── architecture/        # Planned: component model builder
│   │   │   ├── llm/                 # Planned: Azure OpenAI routing
│   │   │   ├── threat_model/        # Planned: evidence-linked threat findings
│   │   │   └── reporting/           # Planned: ReportLab PDF generation
│   │   ├── main.py                  # FastAPI app, CORS, exception handlers
│   │   └── config.py                # Pydantic Settings (all env vars)
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_health.py
│   │   ├── test_capabilities.py
│   │   └── test_config.py
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
| pnpm | 9+ | `npm install -g pnpm` |

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

# Configure environment
cp .env.example .env
# Edit .env — see Environment Variables below

# Start the development server
uvicorn app.main:app --reload --port 8000
```

The API is then available at **http://localhost:8000**.  
Interactive documentation: **http://localhost:8000/docs**

---

## Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install

# Start the development server
pnpm dev
```

The frontend is then available at **http://localhost:5173**.  
Vite proxies all `/api` requests to `http://localhost:8000`.

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in the values. The backend starts without Azure OpenAI credentials — only LLM-dependent features require them.

| Variable | Required for | Description |
|----------|-------------|-------------|
| `AZURE_OPENAI_ENDPOINT` | LLM features | Your Azure OpenAI resource endpoint |
| `AZURE_OPENAI_API_KEY` | LLM features | API key from Azure portal |
| `AZURE_OPENAI_API_VERSION` | LLM features | e.g. `2024-02-01` |
| `AZURE_OPENAI_GPT41_DEPLOYMENT` | LLM features | GPT-4.1 deployment name |
| `AZURE_OPENAI_ASTRA_DEPLOYMENT` | Escalation | GPT-6 Astra deployment name |
| `APP_ENV` | Optional | `development` / `production` |
| `LOG_LEVEL` | Optional | `DEBUG` / `INFO` / `WARNING` |
| `ALLOWED_ORIGINS` | Optional | Comma-separated CORS origins |
| `MAX_UPLOAD_SIZE_BYTES` | Optional | Default: 52428800 (50 MiB) |

> **Security note:** Never commit `.env`. It is listed in `.gitignore`.

### Model Routing Strategy

- **GPT-4.1** is the default model for architecture explanation and threat modelling.
- **GPT-6 Astra** is reserved for complex escalation tasks.
- API compatibility between deployments must be verified against the organisation's Azure configuration before use. They may not support identical parameters.

---

## Running Tests

```bash
cd backend
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS / Linux

pytest tests/ -v
```

### Type-checking the frontend

```bash
cd frontend
pnpm run type-check
```

---

## API Reference

### `GET /api/v1/health`

Liveness check. Returns HTTP 200 when the API is running. Does **not** require Azure OpenAI credentials.

```json
{
  "service": "repo-intelligence-backend",
  "status": "ok",
  "version": "0.1.0",
  "environment": "development"
}
```

### `GET /api/v1/capabilities`

Returns a structured list of all platform capabilities with their implementation status.

```json
{
  "service": "repo-intelligence-backend",
  "capabilities": [
    {
      "id": "health_check",
      "name": "Health Check",
      "description": "...",
      "status": "implemented"
    },
    {
      "id": "github_ingest",
      "name": "GitHub Repository Ingestion",
      "description": "...",
      "status": "planned"
    }
  ]
}
```

---

## Current Implementation Status

| Feature | Status |
|---------|--------|
| FastAPI application shell | ✅ Implemented |
| `GET /api/v1/health` | ✅ Implemented |
| `GET /api/v1/capabilities` | ✅ Implemented |
| CORS for local Vite dev server | ✅ Implemented |
| Centralised Pydantic settings | ✅ Implemented |
| Consistent JSON error responses | ✅ Implemented |
| Automated backend tests | ✅ Implemented |
| React frontend shell | ✅ Implemented |
| Sidebar navigation | ✅ Implemented |
| Repository input panel (URL + ZIP) | ✅ Implemented |
| Input validation (URL format, file type/size) | ✅ Implemented |
| Backend health indicator in UI | ✅ Implemented |
| Vite → FastAPI API proxy | ✅ Implemented |
| GitHub repository ingestion | 🔲 Planned (Milestone 2) |
| ZIP archive ingestion | 🔲 Planned (Milestone 2) |
| Repository inventory & analysis | 🔲 Planned (Milestone 2) |
| Architecture model construction | 🔲 Planned (Milestone 3) |
| Interactive architecture diagram | 🔲 Planned (Milestone 3) |
| Azure OpenAI integration | 🔲 Planned (Milestone 3) |
| Threat model generation | 🔲 Planned (Milestone 4) |
| PDF report export | 🔲 Planned (Milestone 5) |

---

## Known Limitations

- Repository analysis is not yet implemented. The Analyse button validates input and shows an honest status message.
- The architecture, workflows, threat model, and reports pages display empty states.
- Azure OpenAI credentials are not validated at startup; LLM features will fail gracefully with a 503 error when credentials are absent.
- No authentication or rate limiting is implemented (not required for local MVP development).

---

## Next Milestone (Milestone 2): Repository Ingestion

1. **GitHub ingest:** Clone a public repository to a secure temporary directory. Handle rate limits and reject private repositories gracefully.
2. **ZIP ingest:** Accept uploaded archives with path-traversal protection, file-type validation, and size enforcement.
3. **Repository inventory:** Walk the workspace and identify languages, frameworks, manifests, entry points, dependency files, and infrastructure configuration.
4. **Structured inventory API:** Return the inventory as a typed JSON response.
5. **Frontend integration:** Display the inventory in the Repository Summary section of the dashboard.

