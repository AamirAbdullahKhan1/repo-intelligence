# GitDiagram: bounded source context, model interpretation and graph compilation

Date: 2 November 2026. Public source pinned to `7876ab0ca8b5ee46e836235e23c4886d5cdb79ae`. Selected ingestion, source-context and graph code were inspected; no model call, application execution or test run occurred. **Verified** below refers to those files; wider runtime/deployment statements are **Documented**. [Workflow](workflows/gitdiagram.mmd).

## Product and workflow

GitDiagram targets readable repository overviews with clickable source paths. GitHub repository input leads to bounded tree/README/source context, AI interpretation, a structured graph, validation/repair, deterministic Mermaid compilation and browser rendering. It does not need to recover a compiler-level call graph to generate a useful diagram; the model provides semantic interpretation from the supplied subset.

The current project is Next.js/React/TypeScript, with documented R2 artifact persistence and Redis coordination. Old descriptions of a separate FastAPI backend do not describe this snapshot. Videos/admin/MCP are product extensions, not the architecture extraction mechanism. [Architecture documentation](https://github.com/ahmedkhaleel2004/gitdiagram/blob/7876ab0ca8b5ee46e836235e23c4886d5cdb79ae/docs/architecture.md).

## Ingestion and source selection

[`github.ts`](https://github.com/ahmedkhaleel2004/gitdiagram/blob/7876ab0ca8b5ee46e836235e23c4886d5cdb79ae/src/server/generate/github.ts), `getGithubData`, reads repository metadata/default branch, recursive tree and README, with path/type/blob metadata and special handling for partial trees. The file includes explicit README/request/cache limits. It is not downloading and semantically parsing every source file.

[`source-context.ts`](https://github.com/ahmedkhaleel2004/gitdiagram/blob/7876ab0ca8b5ee46e836235e23c4886d5cdb79ae/src/server/generate/source-context.ts) selects and fetches bounded source context; [`source-excerpt.ts`](https://github.com/ahmedkhaleel2004/gitdiagram/blob/7876ab0ca8b5ee46e836235e23c4886d5cdb79ae/src/server/generate/source-excerpt.ts) constructs excerpts, and [`source-references.ts`](https://github.com/ahmedkhaleel2004/gitdiagram/blob/7876ab0ca8b5ee46e836235e23c4886d5cdb79ae/src/server/generate/source-references.ts) supports identifying relevant source references/import context. This improves grounding but remains sampling. Files absent from context cannot be assumed fully understood.

No target dependency installation/build is inherent in this ingestion path. External AI requests transmit selected repository context, so this mode does not satisfy our core local-first/no-model requirement.

## Graph generation and validation

The architecture document describes managed single-request overview-plus-graph and alternative two-stage model paths. This review did not trace every model/provider dispatch branch and deliberately avoids tying the design to mutable model names.

[`graph.ts`](https://github.com/ahmedkhaleel2004/gitdiagram/blob/7876ab0ca8b5ee46e836235e23c4886d5cdb79ae/src/server/generate/graph.ts) implements `parseDiagramGraph`, `validateDiagramGraph`, `buildFileTreeLookup`, path normalization/stripping and repair feedback. Nodes/groups/edges have generated identifiers, labels, shapes and repository paths. Validation checks allowed graph structure, referenced identities/paths and connectivity/limits. An existing path proves path validity, not that its claimed responsibility or communication edge is true.

`compileDiagramGraph` in the same file escapes text, maps node/group identities, renders typed shapes/connectors and constructs GitHub links. This deterministic presentation step follows model interpretation; it is not deterministic architecture recovery. `mermaid.ts` re-exports separate syntax validation, while the architecture document describes browser sanitization/link controls. We did not independently run browser security tests.

## Architecture and uncertainty

Model interpretation supplies responsibility grouping, frontend/backend concepts, external-system labels and high-level links from context. No inspected compiler binding, complete reaching definitions, validated route-call-destination chain or per-edge semantic proof supports a claim of full static architecture resolution.

Invalid graph/path repair is explicit. Semantic uncertainty for each architectural edge is less rigorously represented than a canonical graph retaining unresolved source targets. A polished connected graph may still be incomplete or wrong; our design should allow disconnected/unknown destinations instead of repairing them cosmetically.

## Storage, interaction and scale

Documented successful artifacts reopen without another generation; quota/cancellation/coordination and failed-run state are distinct from saved diagrams. This is repository-result caching, not file-level dependency-aware incremental analysis. Mermaid/source links, streaming explanations and export provide a coherent answer-first experience. Tree/source budgets reduce model context and rendering work, but also bound coverage. No measured speed/cost/accuracy comparison with our platform was performed.

## What we should learn

Already shared: repository intake, structured graph validation, saved views and source navigation. GitDiagram's different strength is producing concise semantic overviews early, with explicit graph-to-renderer separation. We can adopt a narrow architecture-view contract, readable role labels and safe deterministic export without adopting model inference.

Our compiler supports stronger local binding for its resolved subset, while our current diagrams often communicate less well. Neither claim proves overall superiority. We should recover semantic labels from supported framework/operation evidence and expose incomplete relationships rather than ask a renderer to compensate for missing architecture.
