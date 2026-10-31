# Architecture exploration and tool-environment reconciliation

31 October 2026. This change improves presentation over the existing validated graph. It does not rewrite the analyzer, change ingestion, install tools, or regenerate the GitDiagram analysis.

## What changed

The first screen now presents a repository summary and a bounded architecture diagram. On the saved GitDiagram snapshot, it shows **13 high-level nodes**, including the existing generation, storage, MCP, explainer, admin, routes/pages and UI module boundaries, rather than individual functions. Three package boundaries and expandable integration/infrastructure collections retain their canonical members.

Packages and directory groups are explicitly source boundaries. A Next.js routes/pages module can contain both frontend and server code; it is not split into invented frontend/backend services. An infrastructure collection can remain unconnected when runtime communication is not established. Source-root candidates remain qualified as candidates.

The main summary shows languages, frameworks identified from manifests, packages/source roots, logical modules and route entries. Expanded summary details explain integrations, storage declarations, coverage and limitations. Compiler counters and raw inventory are available in **Detailed diagnostics & tools**, rather than leading the result page.

## Progressive exploration

- **Repository → applications/packages → logical modules → functions/classes.** The explorer uses original entity IDs, search and pagination. Breadcrumbs return to parent levels. Click a module to open a scoped workflow; click a function to use it as the entry.
- **System architecture** stays at source/module/integration level, including when a module is selected. It shows that module's supported neighborhood, not a grid of function declarations.
- **Core workflow** follows canonical static calls from a chosen route/function/method or module entry. Entry search and pagination, depth, node limit, imports, nested definitions and unresolved-marker controls are available. Repeated call sites to the same target are aggregated with original support-edge/evidence IDs retained.
- The compact overview prioritizes up to two relationships per source. Increasing the node budget above 24 explicitly expands the set of visible packages/modules, while the explorer always retains the complete paginated hierarchy. **More module connections** exposes additional recorded groups. Its diagram is capped at 24 edges by default; detailed module overviews permit up to 60. Omitted modules remain available through the explorer.
- Opening evidence automatically refits the canvas, so the inspector does not obscure nodes. ELK still supplies layered positions and orthogonal routes; React Flow supplies interaction. No new layout package was introduced.
- Completing analysis or reopening an analysis from history returns to the overall view, including when the saved snapshot ID is unchanged.

## Evidence and uncertainty

Selecting a connection shows its relationship type, source/caller, target, resolution status, source file/range, and limitations. Initially only three source citations are displayed. More citations, hashes/ranges, record IDs, and individual supporting canonical relationships are available on demand.

Status semantics:

| Display | Meaning |
|---|---|
| Source-supported | A declaration or static relationship has source support; it does not guarantee runtime execution |
| Conditional | The canonical record is conditional, such as a qualified nested-definition relation |
| Ambiguous | The canonical record explicitly reports ambiguity; the UI does not manufacture this status |
| Unresolved | No target has been established; a diagnostic or optional placeholder is shown |

Calls, imports, configuration declarations and ownership use distinct labels and line styles. Runtime conditions may remain unknown even when a static implementation target is supported.

**Needs context** is a separate, paginated section following the selected module/package. Optional workflow markers are limited to five and never infer a real service/target. Their source association uses existing declaration/citation ranges; their target stays unknown. The original unknown record index and evidence IDs are retained. Unavailable dependency implementations and generated files account for many unresolved records; these are not all broken application connections.

## Bounds and provenance

| Query/output | Bound |
|---|---|
| Hierarchy and entry search | 30 records by default, maximum 60 per page |
| Graph nodes | Default 24, configurable 5–80 |
| Workflow depth | 1–6, default 2 |
| Workflow edges | Maximum 100 |
| Optional unresolved markers | Maximum 5, within the node/edge budget |
| Repository package summary | First 20, with total and truncation flag |
| Integration/storage summary | First 30 identities; complete canonical lists remain in the explorer |
| Evidence response | First 100 citations; first 3 shown initially |
| Individual supports of an aggregate | First 10 shown on demand; complete support IDs remain on the record |

Large package counts cannot bypass the node limit. Default package selection, component grouping, edge aggregation and unknown markers are presentation rules over the stored graph. Group nodes carry canonical member IDs; aggregate edges carry original support-edge and evidence IDs. They are not new analysis claims. A grouped SDK arrow means recorded use of one or more represented libraries, not use of every library in the collection.

## API additions

Existing intake, job, persistence and graph contracts remain. New presentation responses have separate Pydantic models in `backend/app/api/presentation_models.py`, TypeScript contracts in `shared/contracts/analysis.ts`, and generated JSON/OpenAPI schemas.

- `GET /api/v1/analyses/{snapshot}/overview`: concise, bounded repository summary.
- `GET /api/v1/analyses/{snapshot}/hierarchy`: `parent_id`, `query`, `offset`, `limit`.
- `GET /api/v1/analyses/{snapshot}/explore/entries`: `scope_id`, search and pagination.
- `GET /api/v1/analyses/{snapshot}/view`: adds `scope_id`, `show_unknown`, `connections`; existing depth/node/dependency options remain.
- `GET /api/v1/analyses/{snapshot}/unknowns`: adds scoped, bounded diagnostics.
- `GET /api/v1/analyses/{snapshot}/evidence`: supports canonical and aggregate records, with scope/view context and caller/target labels.
- `GET /api/v1/tools`: the actual backend interpreter and its tool inventory.

Reproduce schema checks with `backend/.venv/Scripts/python.exe scripts/export_contracts.py --check`.

## Reconciled tool environment

The discrepancy came from inspecting different Python installations, rather than an active NetworkX integration or an unnoticed backend PyYAML downgrade.

| Package | Backend virtual environment | System Python | Product usage |
|---|---|---|---|
| NetworkX | Not installed | **3.3**, installed | Unused by this backend; intentionally deferred. Standard Python maps/sets/deque handle bounded projections. |
| PyYAML | **6.0.3**, metadata and loaded module match | **6.0.2**, installed | Backend 6.0.3 actively parses the existing narrow Compose configuration stage. System 6.0.2 is not the backend parser. |

Backend interpreter: `C:/Users/Asus/OneDrive/Desktop/repo-intelligence/backend/.venv/Scripts/python.exe`.

System interpreter: `C:/Users/Asus/AppData/Local/Programs/Python/Python312/python.exe`.

The inspection records version, interpreter, prefix and loaded PyYAML path. Snapshots retain the tool details recorded at analysis time; reopening does not replace those with current runtime versions. Historical research recommendations are not evidence of installation/integration.

| Tool | Actual backend/workspace state | Integration category |
|---|---|---|
| TypeScript | 5.9.3, worker-owned | Integrated and active |
| React Flow | 11.11.4 | Integrated and active |
| ELK.js | 0.12.1 | Integrated and active, browser Web Worker |
| SQLite | Python runtime 3.45.3 | Integrated and active |
| PyYAML | 6.0.3 in backend | Integrated and active |
| NetworkX | Absent in backend; 3.3 in separate system environment | Deferred in backend; system copy installed but unused by backend |
| Tree-sitter | Not found in backend environment | Deferred intentionally |
| ast-grep / Semgrep / Gitleaks | Not found on inspected backend PATH / package environment | Deferred intentionally |
| Syft | Not on backend PATH | Future SBOM inventory; not source-code relationship resolution |
| Required missing tools | None in the inspected working environment | None |

`integration_status` distinguishes `active`, `installed_unused`, `deferred`, `missing_required` and `removed`. Installed optional packages do not become active merely by being present. Other environments elsewhere on the machine were not exhaustively inventoried.

Reproducible reports: [backend tool state](tool-state.json), [system Python comparison](system-python-tools.json). Run the inspector with an explicit interpreter:

```powershell
.\backend\.venv\Scripts\python.exe scripts/tool_status.py
python scripts/tool_status.py
```

The latter reports whichever interpreter `python` resolves to; it is not automatically the backend runtime.

## Acceptance on saved GitDiagram

Snapshot: `8b14186f6aec18085a25f11c5e1198612708b226793c6aae190c7fa977198b2a`.

- Understandable initial architecture: **13 nodes**, no function/file/route nodes in the default system diagram.
- Major modules identifiable in the diagram and complete paginated explorer.
- Package → generation module → individual function navigation verified in Chrome.
- An individual routed edge was clicked; caller/target, status and source citations were inspected.
- A scoped unresolved record was selected and its evidence inspected.
- Both architecture views were switched; returning to system from a module retains component-level abstraction.
- The same saved analysis reopened through history and browser reload.
- The exploration-only browser run made **zero analysis submissions** and zero external page requests. No page errors occurred.
- The existing browser ZIP regression is retained via `scripts/verify_ui.cjs`; it uses the new explorer flow and optionally uploads only the small known-system fixture.
- The analyzer fingerprint matches the one stored in the GitDiagram snapshot. Stored canonical graph hashes before/after are recorded in `output/usability/preservation.json`.

**61 backend tests passed**, including the original 53 regressions and eight new presentation tests. The production frontend build, TypeScript check, formatting check and schema consistency check passed. Both browser flows passed with no page errors; the ZIP flow also verified that completing an identical saved snapshot returns to the overall view.

Test results and exact browser assertions are saved in `output/usability/`. All previous compiler/ingestion regressions remain; new tests cover hierarchy/search/pagination, scoped workflows, status-preserving aggregation, provenance, unresolved markers, saved graph immutability, tool categories, many-package limits, and component-level system views.

## Remaining limits

This change improves organization and presentation; it adds no new parser, framework resolver, callback interpretation, deployment inference or accuracy claim. The existing TS/JS analysis coverage and security limitations still apply. Classes/interfaces are available as source declarations; call exploration uses the existing function/method records and does not add inheritance, dependency-injection or runtime-dispatch inference.

The overview is deliberately selective. A missing visible arrow does not establish independence; use more connections, scoped workflows, imports and diagnostics for details. Backend queries currently load/index the saved JSON graph for each request; response sizes are bounded, but very large saved graphs would benefit from indexed persistence/cached projections. Saved source locations remain evidence references, not a source-code browser.
