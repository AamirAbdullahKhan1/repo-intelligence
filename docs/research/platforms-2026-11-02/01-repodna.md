# RepoDNA: implementation-level technical report

Research date: 2 November 2026. Source snapshot: `AnasBabari/RepoDNA@f05b17c12c9d8d4542fb58b6915507ff176217db`. No project code, build, tests or application was executed. See [methodology](README.md) for evidence labels and local source inventory.

## 1. Product and scope

**Verified:** RepoDNA is a source-to-artifact analyzer with a React graph/exploration application, a TypeScript web analysis path, and a separate Python engine. Browser ZIP/folder analysis and server public-repository analysis are distinct paths. The parser registry includes Python, JS, TS, TSX and experimental Go. Registration is not equivalent to full language semantics.

Its intended users need onboarding, code exploration, structural maps and potential change-impact inspection. Outputs include portable versioned JSON artifacts, architecture components, imports/calls/routes, ranked entries/files, flow views, inventory and diagnostics. v2 exports include machine-readable formats; their existence does not establish that every possible graph relationship is extracted.

The README's concise product claim is not our evidence for the mechanisms below. Source links use the inspected commit.

## 2. Actual end-to-end processing paths

### Public web repository

1. [`app/api/v2/analyses/route.ts`](https://github.com/AnasBabari/RepoDNA/blob/f05b17c12c9d8d4542fb58b6915507ff176217db/app/api/v2/analyses/route.ts): API coordinates revision resolution, auth/rate limits and durable workflow start/status. It exposes status/events/artifact endpoints, rather than doing all work in one UI request.
2. [`app/workflows/analyze-public-repository.ts`](https://github.com/AnasBabari/RepoDNA/blob/f05b17c12c9d8d4542fb58b6915507ff176217db/app/workflows/analyze-public-repository.ts): `analyzeAndCachePublicRepository` checks configured artifact storage and commit-addressed cache, fetches repository contents, analyzes, validates/caches the artifact and emits progress. Cache hit avoids analysis. The seven-day public cache uses private Vercel Blob storage; it is not a local-only SaaS path.
3. [`ingestion.ts`](https://github.com/AnasBabari/RepoDNA/blob/f05b17c12c9d8d4542fb58b6915507ff176217db/app/lib/analyzer/ingestion.ts): `fetchGitHubRepo` supports bounded archive and Git-tree acquisition. Tree traversal and selected file reads preserve inventory/skips/truncation. It does not install or launch the target application.
4. [`v2/pipeline.ts`](https://github.com/AnasBabari/RepoDNA/blob/f05b17c12c9d8d4542fb58b6915507ff176217db/app/lib/analyzer/v2/pipeline.ts): `analyzeRepositoryV2` invokes the earlier analysis, adapts it, enriches inventory, compacts the graph and computes analytics. v2 is not a second independent compiler engine.
5. The validated portable artifact feeds the viewer and exports. Deployment-specific cache/retention guarantees were not tested.

### Browser folder/ZIP path

[`deep-scan-client.ts`](https://github.com/AnasBabari/RepoDNA/blob/f05b17c12c9d8d4542fb58b6915507ff176217db/app/lib/deep-scan-client.ts) creates [`deep-analysis.worker.ts`](https://github.com/AnasBabari/RepoDNA/blob/f05b17c12c9d8d4542fb58b6915507ff176217db/app/workers/deep-analysis.worker.ts), with progress, abort/error handling and an inline fallback. This is a browser Worker running trusted analyzer code, not a target-code execution worker. ZIP extraction uses the project's ingestion policy. Private acquisition endpoints and retention options exist, but a full private-auth/retention audit is outside this source review.

### Python engine

[`core/repodna/engine.py`](https://github.com/AnasBabari/RepoDNA/blob/f05b17c12c9d8d4542fb58b6915507ff176217db/core/repodna/engine.py), `analyze_repository`, uses `repository_source`, per-file SHA identities, `AnalysisCache`, and concurrent uncached-file analysis. It then rebuilds relationships/architecture. Python AST analysis and regex-oriented JS analysis in this engine must not be confused with the web Tree-sitter path.

## 3. Discovery, parsing and extraction

[`app/lib/analyzer/index.ts`](https://github.com/AnasBabari/RepoDNA/blob/f05b17c12c9d8d4542fb58b6915507ff176217db/app/lib/analyzer/index.ts), `analyzeRepositoryFiles`, fingerprints technologies, collects manifest inventory, derives path aliases, parses files, resolves imports/calls, resolves Express mounts, builds architecture/flows and ranks results. `resolveParserMode` defaults to Tree-sitter unless options/environment select legacy.

[`parser/registry.ts`](https://github.com/AnasBabari/RepoDNA/blob/f05b17c12c9d8d4542fb58b6915507ff176217db/app/lib/analyzer/parser/registry.ts) maps extensions to parser factories and caches initialized instances. [`parser/javascript.ts`](https://github.com/AnasBabari/RepoDNA/blob/f05b17c12c9d8d4542fb58b6915507ff176217db/app/lib/analyzer/parser/javascript.ts), `JavaScriptSyntaxParser.parse`, walks named syntax nodes, records symbols/imports/calls/JSX-related evidence, budgets extraction and disposes syntax trees. Parse errors and extraction limits make results partial.

[`analyzers/tree-sitter.ts`](https://github.com/AnasBabari/RepoDNA/blob/f05b17c12c9d8d4542fb58b6915507ff176217db/app/lib/analyzer/analyzers/tree-sitter.ts), `analyzeTreeSitter`, converts syntax facts into `PartialAnalysis` and recognizes selected framework/database/SDK identities. Initialization failures can invoke the legacy JS/TS extractor with notices. This changes extraction depth; it is not transparent semantic equivalence.

Python web parsing has its own syntax adapter; Python CLI [`analyzers/python.py`](https://github.com/AnasBabari/RepoDNA/blob/f05b17c12c9d8d4542fb58b6915507ff176217db/core/repodna/analyzers/python.py) uses `ast.parse`. CLI [`javascript.py`](https://github.com/AnasBabari/RepoDNA/blob/f05b17c12c9d8d4542fb58b6915507ff176217db/core/repodna/analyzers/javascript.py) uses regex-based constructs. None of these observations proves complete scope/type/value resolution.

Framework imports and selected syntactic operations contribute database/external-system detection. They must not be interpreted as verified database-instance binding or network invocation. Full cross-file configuration data flow was not established in the inspected path.

## 4. Relationship resolution: the critical distinction

[`graph.ts`](https://github.com/AnasBabari/RepoDNA/blob/f05b17c12c9d8d4542fb58b6915507ff176217db/app/lib/analyzer/graph.ts) implements the core web resolution:

* `resolveJavaScriptImport`: candidate extensions/index files and configured prefix aliases. This is custom path resolution, not the TypeScript type checker or full package-exports resolution.
* `resolvePythonImport`: relative/absolute module candidates and inferred package roots.
* `resolveGoImport`: suffix-match package directories and choose the lexicographically first matching non-test Go file. This is an approximate file representative, not Go package/type resolution.
* `resolveCalls`: indexes symbols by terminal name and file. It tries a matching symbol in imported target files for dotted calls, a unique same-file name, then a repository-unique name. Scores are assigned by these branches (for example 0.92/0.88), not calibrated probabilities.

**Inferred limitation:** a repository-unique name can still refer to a different receiver or shadowed declaration. Finding one matching method in an imported file does not establish that this receiver points to it. This is a source-based risk assessment; no synthetic execution test was performed here.

This is an important place where our existing compiler-bound local implementation calls are a stronger mechanism for the supported subset. That is not a measured overall accuracy victory.

[`express.ts`](https://github.com/AnasBabari/RepoDNA/blob/f05b17c12c9d8d4542fb58b6915507ff176217db/app/lib/analyzer/express.ts) separately reconciles router mounts/imports and prefixes, with diagnostics for unresolved cases. This is worth studying for our currently narrow mount coverage; not every middleware/runtime registration is resolved.

## 5. Architecture reconstruction and graph model

`classifyFile` in `graph.ts` prioritizes tests, routes/API directories, service/DAO/database/worker paths, UI symbol/extensions, domain/infra/configuration paths and an unclassified fallback. `buildArchitecture` places files into fixed role categories such as frontend/API/services/database. Connections are aggregated resolved **imports between categories**.

This is useful abstraction, but not a reconstruction of deployment topology. A folder named `models` can fall into the database category without proving persistent database usage. Categories span projects unless additional scope is retained. Generic `src/app` is explicitly left unclassified when stronger evidence is absent.

[`artifact-loader.ts`](https://github.com/AnasBabari/RepoDNA/blob/f05b17c12c9d8d4542fb58b6915507ff176217db/app/lib/schema/artifact-loader.ts), `adaptV1ToV2Viewer`, materializes file/symbol/route/dependency nodes and edges from earlier records. Source presence in an adapter output is not an additional resolution pass. Resolved name-based call targets can receive `resolved` status; the UI therefore needs to expose resolver provenance, not treat that word as compiler certainty.

[`v2/types.ts`](https://github.com/AnasBabari/RepoDNA/blob/f05b17c12c9d8d4542fb58b6915507ff176217db/app/lib/analyzer/v2/types.ts) defines `GraphNode`, `GraphEdge`, `SourceRange`, inventory/coverage/diagnostics, centrality and unresolved records. Edges carry nullable target, type, status, confidence, file/range, explanation, resolver/version and optional alternatives. Node kinds include semantic possibilities beyond the extractors inspected; a schema enum is not proof of emitted accurate facts. IDs are artifact/source identities, not guaranteed refactor-stable identities.

`compactGraph` in `v2/pipeline.ts` mutates the artifact to a bounded subgraph (defaults 8,000 nodes/12,000 edges), preserves inventory separately, prioritizes file/structural entities and balances edge families. It also filters unresolved records to retained edges. This is **artifact compaction**, not merely UI hiding; discarded detail is not available from that artifact just by expanding the canvas.

[`analytics.ts`](https://github.com/AnasBabari/RepoDNA/blob/f05b17c12c9d8d4542fb58b6915507ff176217db/app/lib/analyzer/v2/analytics.ts), `detectCommunities`, performs sorted undirected connected-component BFS. It is not Louvain or learned architectural clustering. Containment links can join broad parts of the graph. Centrality uses degree; reported cycles are bounded DFS-derived cycles, not proof of architectural roles.

## 6. “Execution tracing” and impact

`buildFlows` in `graph.ts` starts at route/handler records and breadth-first follows resolved call links, limiting nodes (default 12) and depth (5). The output is a possible static call neighborhood. Its timeline does not establish runtime order, branch choice, concrete receiver or even that the route is invoked. `FlowRecord.confidence` is a fixed heuristic based on whether a trace has more than its initial node.

[`RepoWorkspace.tsx`](https://github.com/AnasBabari/RepoDNA/blob/f05b17c12c9d8d4542fb58b6915507ff176217db/app/components/RepoWorkspace.tsx), `DependenciesView`, matches symbol names from a user query and lists imports into matching files and calls into matching symbols. This inspected impact UI is primarily direct dependency lookup; do not advertise it as complete transitive behavioral change impact.

## 7. Interaction, storage and scale

The viewer has architecture/code-graph exploration, routes/traces, dependencies, inventory, unresolved lists, evidence/detail drawers, search, graph scope and saved/export options. [`ArchitectureGraph.tsx`](https://github.com/AnasBabari/RepoDNA/blob/f05b17c12c9d8d4542fb58b6915507ff176217db/app/components/ArchitectureGraph.tsx) maps architecture roles/connections to React Flow nodes/positions. We did not launch the UI or evaluate comprehension. Browser worker parsing, explicit graph budgets, source inventory and acquisition fallback are concrete engineering choices, not enterprise throughput measurements.

Python per-file parse reuse is verified in engine/cache calls. Public commit-artifact caching is different from dependency-aware incremental analysis. No complete web changed-file invalidation/relinking engine was established. Per-file caching alone does not solve cross-file semantic invalidation.

Stack: React 19, Next/Vinext entry scripts, TypeScript, Tree-sitter/WASM, React Flow, AJV, fflate and optional hosted workflow/blob/auth services; Python AST/cache engine separately. Dependency versions and deployment behavior are snapshot-specific.

## 8. Comparison to our platform and lessons

**Already shared:** static intake, typed records, unknowns/evidence, architecture/detail views and bounded exploration.

**Useful stronger breadth:** Python syntax analysis, experimental Go, portable artifacts, explicit acquisition/parse coverage, mount handling, export/trace navigation and public commit cache. Accuracy superiority is not established.

**Different:** name-based cross-file call resolution and fixed architecture role buckets, compared with our compiler-based local call resolution and directory ownership groups. Neither alone solves reliable responsibility recovery or configured resource identity.

**Adopt ideas:** capability/coverage accounting, unresolved reasons, artifact/view separation, source-linked route navigation, mount fixtures and versioned analyzer provenance.

**Do not copy:** global unique-name calls as authoritative, arbitrary confidence percentages, static timelines labelled guaranteed execution, compaction that loses canonical findings without a retained-detail strategy, or docs' absolute safety wording. Static parsers still process hostile input.

The main value of RepoDNA is putting understandable exploration around static findings. It does not demonstrate that we must replace our compiler or that the static-analysis ceiling has been reached.

Workflow: [RepoDNA diagram](workflows/repodna.mmd). Tests inspected include `v2-semantic-graph.test.ts`, `resolution-gaps.test.ts`, `express-mounts.test.ts` and `parser-extraction-limits.test.ts`; none were run.
