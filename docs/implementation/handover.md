# Implementation handover

31 October 2026. Scope: the requested restructuring and integration of the existing TS/JS prototype. The [before-change audit](audit-before.md) was written before runtime changes. This report distinguishes verified behavior from remaining work.

## Structure and ownership

Before:

```text
backend/app/services/{analysis,architecture,repository,llm,threat_model,reporting}
backend/app/schemas/ + api/v1/endpoints/         legacy synchronous producer
frontend/src/{context,pages,components,...}    legacy result/sessionStorage screens
tools/static-poc/                             separate compiler experiment + tests
frontend/public/static-poc/gitdiagram.json    saved experiment bypassing API
output/                                      research + generated POC artifacts
```

After:

```text
backend/
  app/
    api/routes.py                   transport and bounded query endpoints
    ingestion/{github,archive,snapshot}.py
    analysis/{pipeline,configuration}.py
    evidence/{validation,redaction}.py
    graph/projections.py
    persistence/store.py
    {config,contracts,jobs,main}.py
  workers/typescript/
    {index,guard}.cjs
    adapters/{next,express,wrangler}.cjs
    package.json + package-lock.json
  tests/                            actual compiler + negative cases + API/intake
  requirements.txt + .env.example
frontend/
  src/
    components/{repository,diagrams,evidence}/
    hooks/useRepository.ts
    pages/Architecture.tsx
    services/analysis.ts
    App.tsx + main.tsx + index.css
  public/favicon.svg                local asset; no public client graph
  package.json + pnpm-lock.yaml + pnpm-workspace.yaml
shared/{contracts,schemas}/
samples/known-system/               inert source fixtures
scripts/                            schemas, inspection, CLI and acceptance checks
docs/implementation/                audit, handover and security limitations
data/                               ignored SQLite and temporary job inputs
output/                             ignored generated/research artifacts
tmp/restructure-backup/             ignored original user edits/non-provider tests
```

The compiler worker and evidence/projection logic were retained and moved. The legacy regex producer and its synchronous API were retired because the live application bypassed the working compiler prototype. The static-public-data screen and second coordinator were removed after migration. Existing synthetic source fixtures were retained. Five pre-existing edited backend files and the initial working-tree patch were preserved in the ignored backup; no actual `.env` file was copied.

## Removed provider implementation

Removed `backend/app/services/llm/{client,__init__}.py`, `AzureLLMService`, provider request/prompt logic and `enhance_architecture_explanation`; removed its legacy analyze-route orchestration, provider capability reporting and `LLMNotConfiguredError`. The old architecture fields/types for model usage and provider-backed explanations were retired with their producer/UI.

Removed the `openai==1.57.0` requirement and uninstalled it from the backend virtual environment. After checking that no installed package required them, removed orphaned provider transitive packages `jiter` and `distro`. Removed duplicate httpx and unused PDF/test-plugin requirements. Removed unused pytest-asyncio from the environment. Removed Azure endpoint/key/version/deployment fields, credential validators, `.env.example` entries and actual provider entries in local `.env` files without printing values. The README now describes only the static product path. No provider abstraction or future AI placeholder was added.

Removed obsolete threat/report placeholder screens, old provider-dependent tests, old result/context schemas, duplicate `react-flow-renderer`, and unused router/icon libraries. Analyzed repositories may themselves contain provider imports; the worker records those as ordinary dependency/SDK evidence without invoking them.

## Actual tool integration matrix

Versions were inspected in the application's own environments; absence on PATH does not inventory every installation elsewhere on the machine. Reproduce with `scripts/tool_status.py`; the machine-readable inspection is [tool-state.json](tool-state.json).

| Tool | Installed | Invoked/imported and data path | Status and decision |
|---|---|---|---|
| TypeScript Compiler API | 5.9.3, worker-owned locked package | `workers/typescript/index.cjs` parses source, resolves aliases/imports/re-exports/declarations/local implementation calls; worker JSON passes validation into SQLite and both views | **Implemented and tested**, primary TS/JS engine; project/config coverage remains partial |
| Tree-sitter | No backend Python installation found | None | **Deferred intentionally**; a second syntax parser adds no current tested language coverage |
| ast-grep | No relevant CLI on PATH | None | **Deferred intentionally**; add only with a concrete structural-rule requirement |
| Syft | Not on PATH | None; current inventory comes from package manifests and source inventory | **Deferred intentionally**, not installed/integrated. It would improve transitive/lockfile SBOM coverage, not call resolution. This MVP has no complete SBOM or Syft output ingestion; add a bounded local inventory adapter as a separate follow-up |
| Semgrep CE | No CLI/Python package found in inspected environment | None | **Deferred intentionally**; no security-rule scanning or Semgrep relationship claims |
| NetworkX | Not installed in backend venv | None; standard-library maps/sets/deque perform bounded traversal and projection | **Deferred intentionally**; no algorithm currently justifies adding it |
| SQLite | Python runtime 3.45.3 | `persistence/store.py`, transactions store job state, summary and canonical graph JSON including entities/edges/evidence/unknowns | **Implemented and tested**, including reopen with a new app instance |
| React Flow | reactflow 11.11.4 | `ArchitectureCanvas.tsx` renders API nodes/edges and emits selections | **Implemented and browser tested**; obsolete renderer package removed |
| ELK.js | 0.12.1 | `ArchitectureCanvas.tsx` creates a browser Web Worker; layered layout and orthogonal section paths reach React Flow | **Implemented and browser tested**; routing uses ELK coordinates, with fixed node positions and zoom/pan |
| PyYAML | 6.0.3 | `analysis/configuration.py`, bounded SafeLoader syntax tree -> Compose service/startup-order declarations -> same validator and graph | **Implemented and tested, narrow scope**; not a generic infrastructure interpreter |
| Gitleaks | Not on PATH | None | **Deferred intentionally**; limited metadata regex redaction is implemented, a comprehensive secret scan is not |

The frontend also uses React 18 and Vite 5.4.21. Prettier 3.9.10 is a development formatter, not an analyzer. Installing these trusted application packages used disabled lifecycle scripts. No submitted repository's package manager was invoked.

## Integrated execution path

```text
React repository input -> FastAPI accepted job -> bounded local executor
  -> GitHub commit archive OR uploaded ZIP
  -> same archive validator -> temporary read-only source snapshot
  -> Python analysis.pipeline -> trusted Node/TypeScript worker
  -> narrow Python configuration stage
  -> IPC schema + citation/reference validation + snapshot-integrity recheck
  -> metadata redaction -> SQLite graph + summary + job completion
  -> backend graph projections -> ELK browser worker -> React Flow
```

`shared/contracts/analysis.ts` owns frontend transport definitions. Backend Pydantic models in `app/contracts.py` own response/worker validation; `scripts/export_contracts.py` generates JSON schemas and OpenAPI in `shared/schemas`. The schema check detects stale generated JSON. TypeScript definitions still require coordinated review when backend models change; this is not a generated TypeScript client.

No graph inference happens in the frontend. Graph/projection IDs, support edge IDs and evidence IDs remain available for inspection. SQLite stores the canonical graph as one validated JSON payload, not independently indexed entity tables; this is sufficient for the local MVP but has scaling costs on repeated detail requests.

## Intake status

**GitHub: implemented and tested.** Root public GitHub URL allowlist; HEAD resolved to immutable commit SHA; fixed-host streamed archive retrieval with TLS verification, quotas and no redirects. Credentials/proxies are not inherited. Git is never invoked, so hooks, checkout filters, submodule operations and LFS retrieval cannot run. The archive then enters the exact ZIP pipeline. Private authentication, branch selectors and retry/rate-limit handling are deferred. Live acceptance used `octocat/Hello-World`, pinned to `7fd1a60b01f91b314f59955a4e4d4e80d8edf11d`; its README-only input correctly produced zero parsed source files.

**ZIP: implemented and tested.** Multipart submission gets a queued job. Validate paths, regular file types, case/duplicate/conflict safety, entry/byte/ratio/path quotas and streamed sizes. Normalize one outer directory. Do not extract nested archives. Extracted source lives in an allocated OS temporary directory outside the project and persistence tree. Freeze source files, fingerprint all bytes, analyze and recheck, then clean up temporary source. Both archive input methods are tested with identical bytes and identical resulting snapshot IDs. Detailed limits and incomplete OS controls are in [security-and-limits.md](security-and-limits.md).

## API contracts

All paths are under `/api/v1`. Full schemas and examples are available at local `/docs` and `shared/schemas/openapi.json`.

| Method and path | Input | Response |
|---|---|---|
| GET `/health` | — | status, version, engine, schema version |
| POST `/analyze/github` | JSON `{ "url": "https://github.com/owner/repo" }` | 202 `Job` |
| POST `/analyze/upload` | multipart `file`, ZIP | 202 `Job` |
| GET `/jobs/{id}` | job ID | `Job`: queued/running/complete/failed/cancelled, phase, coarse progress, snapshot ID or sanitized error |
| POST `/jobs/{id}/cancel` | job ID | current `Job`; cancellation is asynchronous |
| GET `/analyses` | — | latest 50 saved analysis summaries |
| GET `/analyses/{snapshot}` | content/engine snapshot ID | `Analysis`: provenance, coverage, inventory, counts, diagnostics, scope and tool details |
| GET `/analyses/{snapshot}/entries` | — | up to 500 route candidates, or implemented functions in route-less projects |
| GET `/analyses/{snapshot}/view` | `kind=system|workflow`, `entry_id`, depth 1–6, limit 5–80, dependencies, nested; system `layer=source|infrastructure|all` | `View`: same snapshot ID, projected nodes/edges and truncation/static-semantics metadata |
| GET `/analyses/{snapshot}/evidence` | `record_id`, kind and system layer | selected raw/projected record, first 100 source citations and truncation flag |
| GET `/analyses/{snapshot}/unknowns` | offset; limit 1–200 | total and paginated unresolved records |

Default workflow depth is 2 and node budget 24; edges cap at 100. Progress is phase-based, not an estimated percentage of compiler work. Jobs survive as records; incomplete work is marked interrupted on server restart. Saved results can reopen after restart. Active-job browser polling and analysis selection use local IDs; the browser does not store the full client graph in localStorage.

## Generated GitDiagram views

The supplied local public snapshot was packaged and submitted through the **real ZIP API**. No dependencies were installed in it and none of its scripts/builds ran. Inventory: **840 files, 386 parsed source files, zero syntax-failure records, 3,833 resolved local implementation call sites and 21 SDK API call sites**. Signature-only/dynamic/unavailable targets remain unresolved. These counts measure extractor behavior, not architecture accuracy.

Verified graph snapshot: `8b14186f6aec18085a25f11c5e1198612708b226793c6aae190c7fa977198b2a`.

The source overview aggregates SDK identities into one explicit library group, retains HTTP hosts grounded in literal fetch call sites and shows package ownership boundaries. Cross-package call arrows represent source-level implementation calls. Package labels do not imply deployable network services. Infrastructure is a separate filter within system architecture: Wrangler declarations include profiles, resources and service/log/container bindings. Alternate/test configurations are not combined into an asserted running deployment.

![GitDiagram source overview](../../output/integration/gitdiagram-system-diagram.png)

The selected workflow example is **POST `/api/generate/stream`**, two static hops: the route export, POST implementation, admission function and cancellation/abort setup. It is intentionally a readable entry neighborhood. It does **not** establish GitDiagram's entire generation sequence: substantial work lives in callbacks/nested functions, whose dispatch is not fully modeled. Increase depth, enable qualified nested definitions, select a function and explore its calls to inspect further evidence.

![GitDiagram selected static entry workflow](../../output/integration/gitdiagram-workflow-diagram.png)

Both images come from one saved graph. Exact snapshot ID and final browser assertions are in `output/integration/ui-verification.json`. Matching API payloads: `zip-system.json`, `gitdiagram-workflow.json`; full UI screenshots: `gitdiagram-system.png`, `gitdiagram-workflow.png`, `gitdiagram-infrastructure.png`. Artifacts are generated locally and ignored by Git, not shipped as public application data.

## Verification and remaining failures

- **53 backend tests passed**, including the 10 migrated compiler regressions, retained synthetic monorepo fixture, framework adapters, grounded spans, safe archive cases, both inputs sharing an engine, persistence/reopen, API queue saturation/cancellation, worker deadline checks, malformed-input error redaction and limited network-guard rejection.
- The old monorepo fixture remains; its assertions now match compiler-backed evidence. Unconfigured aliases and SDK imports cannot justify the old synthetic `VERIFIED` Redis deployment/read/write claims. Tests for retired regex/provider/placeholder contracts were retired with that implementation, rather than reporting them as unchanged passing tests.
- **Frontend TypeScript check and production Vite build passed.** ELK code is a separate Web Worker bundle; the application JS bundle is approximately 308 kB before gzip. Formatting check is supplied as a reproducible development command.
- **Actual local Chrome acceptance passed**: source overview, infrastructure view, selected core workflow, node evidence, function drill-down, saved selection/reopen and real browser multipart ZIP submission. Final run had zero page errors and zero nonlocal page requests. A minimap obstruction found during testing was fixed; remote web-font requests inherited from the old shell were removed.
- **Live GitHub + ZIP API checks passed**. GitDiagram uses the supplied local snapshot for the full analysis; GitHub transport was separately exercised on a small public repository. The mocked identical-input API regression checks downstream parity.
- Generated schema consistency was checked. Provider SDK absence was checked in the backend environment. No unresolved test failure is being carried as a passing result.
- Windows sandbox restrictions prevented asyncio's local socket-pair creation, so API/browser acceptance ran outside that restricted tool sandbox. This does not establish that the application itself provides an OS sandbox.
- The pre-existing auto-reloading server reset large uploads during verification; the exact cause in that old process was not isolated. A fresh server using the documented command **without reload** passed. The old project-only reload process was replaced, and the default port 8000 then passed both live intake checks. Extracted snapshots now use OS temporary directories outside the project/persistence tree; a regression verifies their location and cleanup. GitDiagram includes a Python experiment, which is inventoried but never executed or analyzed as Python. The final browser preview is at port 5175, proxying to a dedicated API on 8001 with `data/acceptance`; both servers use the completed code.

Remaining warnings: the installed Starlette/anyio TestClient alias emits a deprecation warning, and constructing a deliberately duplicated ZIP test emits Python's duplicate-entry warning. Neither is an application failure. Broad dependency upgrades are deferred to a separate compatibility change.

## Acceptance status and next work

| Area | Status |
|---|---|
| Organized modular monolith; one worker/engine | Implemented and tested |
| Platform provider/AI removal | Implemented and tested |
| Public GitHub and safe ZIP intake | Implemented and tested within stated quotas |
| Queue/status/cancel, saved analyses and SQLite reopen | Implemented and tested; single-process architecture |
| System and core workflow views from unified graph | Implemented and tested; bounded, conservative projections |
| Evidence and unresolved diagnostics | Implemented and tested; semantic completeness not proven by citation validation |
| Language/compiler configuration coverage | Partially implemented; TS/JS root aliases, no installed client dependencies or full project references |
| Framework and callback reconstruction | Partially implemented; Next/Express/selected configuration rules, incomplete framework dispatch |
| Frontend relative API mapping/config propagation/custom DB wrappers | Partially implemented or unresolved; no invented connections |
| Syft SBOM, Semgrep rules, Gitleaks scan | Deferred intentionally; no installation/integration claimed |
| Comprehensive secret handling | Partially implemented; metadata patterns only |
| OS read-only filesystem, egress denial, process/RSS/CPU isolation | Not implemented or verified |
| Private repos, multi-tenant auth, distributed queue, encrypted/retained data lifecycle | Not implemented |
| Accuracy percentage or universal framework support | Not claimed; labeled evaluation corpus not implemented |

Prioritize an OS-isolated execution service before public untrusted use. For better architecture reconstruction, next add labeled fixtures for framework callback dispatch, nested tsconfig/project references, proven relative-client API mapping and config-to-client data flow. Then add narrowly tested framework adapters. Add Syft when transitive SBOM inventory becomes a product requirement; it will not solve source-call resolution. Improve graph persistence with indexed records/cached projections and retention before scaling to many large snapshots. Keep uncertain relationships visible and measure precision against labeled edges before asserting accuracy.
