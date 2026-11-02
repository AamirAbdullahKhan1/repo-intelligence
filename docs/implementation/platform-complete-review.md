# Repo Intelligence: complete current-state review

Reviewed 31 October 2026. This is the single reading guide for understanding the platform today. It supersedes broad capability impressions from proposals, not the underlying technical records. No application code, dependencies or API contracts were changed for this review.

## The essential distinction

**Goal:** reconstruct an understandable, accurate architecture from arbitrary client repositories through deterministic static analysis.

**Implemented product:** a bounded TS/JS static-analysis application with selected framework/configuration rules, source evidence, saved graph results and interactive overview/workflow exploration.

**Current shortfall:** architectural meaning and presentation are less mature than code-fact extraction. Broad language/framework support and enterprise scalability have not been established.

The earlier curated image used manual source-review context and image generation. It was not produced automatically by this engine. The strategic review documents recommend future work; their proposals are not implemented features.

## Feature inventory and mechanisms

| Feature | What happens behind the scenes | Practical boundary |
|---|---|---|
| Public GitHub intake | Validate root HTTPS GitHub URL; fixed API resolves HEAD to commit SHA; fixed codeload archive retrieval | No arbitrary Git servers, private authentication, branch selector, Git hooks, submodules or LFS retrieval |
| ZIP upload | Stream bounded upload; validate entries/paths/types/sizes before regular-file extraction | ZIP only; encrypted archives/symlinks/special files rejected; nested archives inert |
| Snapshot identity | Hash input bytes; read-only flags; compare fingerprints after analysis | Source integrity checks, not an OS sandbox; hashes do not prove semantic correctness |
| Jobs and cancellation | Two executor threads, capacity four active/queued jobs; coarse phase progress; polling and cancellation | Local single-process design; unfinished jobs marked interrupted on restart, no resume/distributed queue |
| Discovery | Sorted walk inventories files, reads selected manifests/configuration, identifies source extensions | Broad inventory is not broad semantic support; exclusions and caps apply |
| Package ownership | Nearest manifest/source-root ownership, package entities and source membership | A package is not automatically a deployed service |
| Language/framework summary | File extensions and package/configuration signatures | Detection does not imply complete adapter support; Python is inventory only |
| Source parsing | TypeScript Compiler API creates ASTs from supplied JS/TS texts | No general Python/Java/Go/C# semantic provider; no target compilation/build |
| Declaration extraction | Collect functions with bodies, classes/interfaces, files and supported nested ownership | Not a full inheritance, DI, class-state or component-composition model |
| Imports/re-exports | Compiler module/name resolution; separate type-only references | Partial tsconfig/workspace resolution; target dependency types not installed |
| Calls/constructors | Resolve call signature to a local declaration with implementation body | Signature-only/library/dynamic cases can remain unknown; no runtime reachability/order proof |
| SDK recognition | Bound imports, constructors, shallow assignments/receiver origins and selected factory returns | Fixed catalogue; library identity does not establish a deployed service or exact resource |
| HTTP detection | Supported unshadowed fetch calls with statically obtainable absolute URL host | Relative/dynamic destinations and reassigned values have gaps; not complete API mapping |
| Next.js adapter | Recognize selected named HTTP route exports and handler links | Root-route omission confirmed; not complete rewrites/middleware/server-client semantics |
| Express adapter | Recognize selected literal app/router registration with supported bound receiver and handler | No comprehensive router mounts, dynamic paths or middleware flow |
| Wrangler adapter | Read supported JSON/JSONC entry/binding/storage/container declarations and profiles | Declarations, not deployed/observed infrastructure; not general Wrangler TOML support |
| Compose extraction | Bounded safe YAML event/node parsing; service and depends_on declarations | STARTS_AFTER does not establish network communication or readiness |
| Canonical graph | One entities/edges/evidence/unknowns collection; shared snapshot identity | A common fact model, not complete recovered architecture |
| Grounding validation | Check unique IDs, endpoints, support IDs, source hashes, UTF-16 ranges and body requirements | Valid source location does not prove an interpretation correct |
| Uncertainty | Store unresolved references/reasons; presentation distinguishes statuses and supports diagnostic markers | Status coverage is rule-dependent; no complete branch-condition model or calibrated confidence |
| Metadata redaction | Mask selected common token/credential patterns | Not comprehensive secret scanning; paths/identifiers retained |
| Persistence/history | SQLite stores summary and whole canonical graph JSON; UI remembers selected analysis/job | No incremental file analysis, robust refactor tracking, tenant isolation or retention-management product |
| Summary | Languages/frameworks, packages/modules, routes, integrations/storage, coverage and limitations | Fixed bounded lists; supported relationship total includes ownership/import/type edges |
| Hierarchy | Repository → package → logical component → functions/classes; search/pagination | Ownership hierarchy does not imply deployment hierarchy; all details are not semantically complete |
| System overview | Group canonical nodes, aggregate typed edges, select bounded visible content | Heuristic roles/salience, not yet a mature semantic architecture engine |
| Internal workflow | Selected entry, bounded outgoing graph traversal with optional dependency/nested/unknown information | Static dependency neighbourhood, not guaranteed business-process execution sequence |
| Layers | Source, infrastructure or combined projection | Configuration and source facts must retain their different meanings |
| Evidence explorer | Selected node/edge shows type, labels, source location, rule, status, limitations and support records | Up to 100 citations/API response and 10 raw supporting relationships in aggregate details; no full retained source browser |
| Diagram interaction | React Flow renders selectable graph; ELK worker computes layered placement and orthogonal routes | Renderer/layout cannot supply missing semantics; no first-class architecture export workflow currently |
| Tool diagnostics | Report package presence separately from active integration using actual backend interpreter | An installed package is not automatically part of analysis |
| API/contracts | FastAPI routes, Pydantic graph models, shared TS/generated schemas | Schema consistency is not semantic correctness; richer multi-provider reconciliation is proposed |

## How the engine reads code

An AST is the code's grammar tree. A symbol identifies a declaration. The compiler can associate an imported alias with that declaration. The analyzer first collects declarations/imports/ownership, then resolves supported calls and integration patterns.

For example, importing `save as store` and then calling `store()` can establish a call to the local `save` implementation. The word `save` or a folder named `db` does not prove database access. To establish a particular database relationship, the engine needs a client identity, an operation and sufficient resource/configuration evidence. Those chains are currently incomplete.

SDK origin tracking is shallow reasoning about where a receiver came from. URL tracking follows a narrow set of literals/concatenations/initializers. Neither is full control-flow, reaching-definitions, points-to or interprocedural data-flow analysis. A static graph can therefore contain both missing links and false links.

The canonical graph is like a case file: entities are things identified in the repository, edges state specific relationships, evidence records their source, and unknowns document gaps. Projections are simplified views of that case file. The UI does not send source code to a model for interpretation.

## Components and technology ownership

| Module | Main implementation | Purpose |
|---|---|---|
| `backend/app/ingestion` | Python, HTTPX, ZIP handling | Controlled retrieval and snapshot preparation |
| `backend/app/jobs.py` | Python thread executor | Job capacity, lifecycle and cleanup |
| `backend/app/analysis/pipeline.py` | Python subprocess coordination/Pydantic | Fixed worker invocation, limits, validation and fingerprints |
| `backend/workers/typescript` | Node.js, TypeScript Compiler API 5.9.3 | Source semantics and framework adapters |
| `backend/app/analysis/configuration.py` | Python, PyYAML 6.0.3 | Narrow Compose declarations |
| `backend/app/evidence` | Python | Citation/reference validation and limited redaction |
| `backend/app/contracts.py`, `shared` | Pydantic, JSON Schema, TypeScript | Data contracts; these models are not AI models |
| `backend/app/persistence` | SQLite | Saved analyses/jobs |
| `backend/app/graph` | Python dicts/maps/queues | Aggregation, hierarchy, summary and bounded traversal |
| `backend/app/api` | FastAPI | Upload, job, history, exploration, evidence and tool endpoints |
| `frontend/src` | React, TypeScript, Vite, Tailwind | UI and API state |
| Diagram components | React Flow 11.11.4, ELK.js 0.12.1 | Interaction and layout |
| Tests/scripts | pytest, synthetic fixtures, browser acceptance scripts | Functional/regression verification |

FastAPI is pinned to 0.115.5 and Pydantic to 2.10.3 in backend requirements. The platform is a modular monolith with a separate trusted analyzer process, not a microservice deployment.

Syft, Semgrep, ast-grep, Tree-sitter, NetworkX, Joern, dependency-cruiser, Grimp, import-linter, LikeC4 and Inframap are not active stages of the implementation reviewed here. Several have only been researched/proposed. Backend tool inspection explicitly reports several as absent/deferred; it does not inventory every candidate. NetworkX 3.3 in a historical system-Python report does not mean the backend uses it. Active backend PyYAML 6.0.3 and historical system PyYAML 6.0.2 belong to different environments.

## Enterprise efficiency: what can and cannot be claimed

No representative enterprise benchmark, p95 latency, throughput, peak-memory study or architecture precision/recall study has been performed. Enterprise suitability depends on repository structure/languages as well as size. A small enterprise TS project might fit; a large or multilingual monorepo may exceed limits or lack semantic support.

| Current bound | Consequence |
|---|---|
| 50 MiB compressed upload | Larger archives rejected |
| 100 MiB expanded; 12 MiB per archive file | Input-size rejection, independent of what source is useful |
| 5,000 archive entries | Includes directory entries, not just parsed code |
| 4,000 inventoried worker files | Broader than source count; excluded directory behavior affects count |
| 1,200,000 bytes per selected relevant file | Oversized selected files skipped with coverage reason |
| 32 MiB selected text budget | Analysis fails when total budget is exceeded |
| 120-second worker timeout | Worker limit, not a guarantee for full upload/retrieval/job completion |
| 1,536 MiB Node heap setting | Heap cap, not total process or job RAM; Python/compiler/native buffers also cost memory |
| 64 MiB worker stdout | Large graph output rejected |
| 150,000 worker edges; contract entity/evidence limits also apply | Not unlimited graph capacity |
| Two running jobs; four active/queued total | Limited concurrency, no horizontal/distributed job orchestration |
| Workflow depth 1–6; visible node limit 5–80, default 24 | Bounded browser content, not bounded full analysis work |

Efficiency strengths: no target install/build/runtime startup, sorted bounded scans, one primary compiler, saved graph reuse, bounded browser queries and worker-based layout. These avoid real classes of overhead but do not prove faster operation than competitors.

Bottlenecks: whole-program compiler state, full snapshot fingerprint passes, graph JSON serialization/deserialization, whole-graph reads and `Index` rebuilding per API request, repeated scans for evidence lookup and concurrent-job memory. A bounded diagram can still require loading the entire underlying graph. Raising limits without measuring these costs is not an enterprise scaling strategy.

Current recorded GitDiagram input: 840 inventoried files, 386 parsed source files and 2,002,832 selected source bytes; 4,240 entities and 10,892 edges. Of 12,074 call/constructor expressions, 3,833 resolved to local implementation bodies, 232 had signature-only results and 8,009 lacked a compiler target. These figures are not an application call-graph recall score: library/builtin/framework/generated calls have different expectations. Zero recorded syntax failures does not mean complete code understanding. Earlier prototype timing belongs to another engine state and should not be presented as current enterprise performance.

## Quality and security limitations

Three saved synthetic probes demonstrate a stale-initializer host false positive, omitted production `public/` JS and missed Next root route. See `output/review/explanation-analysis-probes.json`. They were not rerun or fixed during this review.

Other gaps: partial tsconfig/workspace resolution, absent target dependency declarations, dynamic dispatch and callback behavior, object/closure mutation, frontend/server context, cross-service protocols, API endpoint mapping, arbitrary framework wrappers and resource binding. These are not solved by graph layout or package inventories.

Safety measures include path/type/archive validation, fixed GitHub retrieval, reduced worker environment, selected Node network/process API blocking, no target imports/builds/installs, time/output limits, fingerprints, cleanup and limited redaction. These reduce risk; the process is not OS-sandboxed. Strong filesystem/egress/process-tree/resource isolation, authentication, tenant separation, retention/audit policy and hostile-input containment testing remain prerequisites for a public enterprise service. CORS is not authentication. Secret-pattern redaction is not a guarantee against disclosure.

Recorded tests include ingestion attacks, a repository executable-config sentinel, compiler bindings, frameworks, saved results, bounded views, evidence and browser interaction; the prior report says 61 tests passed. This review read tests/artifacts rather than rerunning them. Functional test success does not establish security completeness, architectural accuracy or human usability.

## What is lacking in the end result

The overview does not consistently select the application's meaningful responsibilities. Package/path groups, SDK library groups and infrastructure declarations are visible, but the bridge to a coherent application architecture is incomplete. High-degree helper functions can become recommended entries. Shared schemas/protocols can be labelled as UI because of path heuristics. Missing configuration/client/resource chains leave critical storage/integration arrows absent.

The internal view is a static neighbourhood. It cannot always tell a complete business story such as “user requests a diagram; repository context is collected; generation runs; result is stored; UI receives updates.” That story requires correct entry/context/protocol/resource facts and abstraction rules. Static analysis also cannot guarantee that this execution happens in production.

The UI has many exploration controls without a sufficiently clear starting answer. There is no first-class single shareable architecture-report/export journey; source citations do not include a full source browser. The initial 13-node/24-edge GitDiagram diagram is bounded but not therefore semantically sufficient.

Most importantly, there is no labelled diverse architecture benchmark or independent user-comprehension evaluation. We cannot support a numerical accuracy claim or overall superiority to GitDiagram/REA.

## Strengths to preserve and next decision

Preserve the safe intake direction, compiler rather than string-only extraction, explicit evidence/unknowns, one canonical saved result, bounded exploration and AI-independent core. Deterministic rules remain fallible; model independence does not mean error-free.

The most useful next objective is: **For a defined set of TS/JS Next.js and Express applications, generate a main architecture view whose important relationships can be traced to source/configuration evidence, whose uncertainties remain visible, and which an unfamiliar user can explain.**

Work in this order: labelled positive/negative fixtures and known bug fixes; bounded assignment/config/client reasoning; semantic responsibilities/context/resource connections; a simpler default architecture journey; diverse evaluation and actual performance measurement; then demand-led languages/tools and deployment hardening. Harden containment before public uploads regardless of feature sequencing.

Do not keep adding tools or rescanning an unchanged snapshot to compensate for absent inference rules. For detailed decisions see `docs/reviews/strategic-enhancements/architecture-impact-review.md`, `analysis-gap-assessment.md`, `revised-architecture-proposal.md` and `implementation-roadmap.md`. Those remain proposals, not delivered capabilities.

## Plain-language explanation to reuse

“Repo Intelligence is a source-code investigator. It reads supported code without running the submitted application, identifies building blocks and supported connections, and keeps the source evidence behind its findings. Users can view a simplified map and inspect the details. Today it primarily understands JavaScript and TypeScript, and we are improving how those code facts become an understandable architecture. It does not yet promise complete support for every framework or enterprise-sized repository.”
