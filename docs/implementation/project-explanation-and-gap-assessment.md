# Repo Intelligence: explanation and honest gap assessment

Reviewed 31 October 2026. This describes the current implementation, rather than the eventual product promise. No engine changes were made for this review.

## A description you can reuse

Repo Intelligence reads a repository without running the submitted application or requiring an AI model. It uses compiler technology and framework rules to identify code elements and supported relationships, records their source evidence, and presents simplified architecture views with drill-down exploration. Its strongest current capability is traceable TypeScript/JavaScript code analysis. Turning those facts into a clear, responsibility-based architecture is still its main development gap.

Do not describe it as understanding every language or framework, recovering every runtime interaction, or guaranteeing architectural accuracy.

## How code understanding works

1. **Discovery:** inventory files, manifests and configuration. Detecting a language is different from supporting its semantics. Python files can be inventoried, but the implemented semantic source analyzer handles TypeScript and JavaScript.
2. **Parsing:** the TypeScript Compiler API constructs an abstract syntax tree: a structured representation of declarations, imports, expressions and other grammar elements.
3. **Symbol resolution:** the compiler associates names with declarations, including supported import aliases and re-exports. This is stronger than matching strings or function names.
4. **Relationship extraction:** two passes collect declarations and imports, then resolve calls and constructors to local implementation bodies where possible. Type-only references remain distinct from runtime dependencies.
5. **Specialized interpretation:** adapters recognize limited Next.js routes, Express registrations and Wrangler declarations. A Python configuration stage reads a narrow subset of Docker Compose. A fixed SDK catalogue and shallow receiver-origin tracking identify some external integrations.
6. **Evidence validation:** references, IDs, source hashes and ranges are checked. These establish that citations and graph references are consistent; they do not prove that an extraction rule correctly interpreted behavior.
7. **Canonical graph:** entities, typed relationships, evidence, coverage and unknowns are stored together. Both diagram views derive from this graph.
8. **Projection and layout:** source facts are grouped into fewer visible nodes. ELK places boxes and routes connectors; React Flow displays and lets users explore them. Layout does not infer architecture.

For example, `import {save as store} from './db'` followed by `store()` can be resolved to the local `save` implementation. This supports a code-call relationship. The filename `db` and function name `save` do not establish a database interaction by themselves.

Static calls describe links present in code, not a guaranteed execution sequence. The current worker does not implement comprehensive control-flow, points-to or cross-function value analysis. Dynamic dispatch, wrappers, callbacks, configuration values and dependency internals therefore leave gaps.

## Project structure and technologies

| Area | Implementation | Purpose |
|---|---|---|
| API and orchestration | Python, FastAPI, Pydantic | Uploads, jobs, validated data contracts and analysis coordination |
| Ingestion | HTTPX, ZIP validation, snapshot fingerprints | Public GitHub retrieval and bounded archive extraction |
| Source analyzer | Node.js, pinned TypeScript Compiler API 5.9.3 | Parse and resolve supported TS/JS code without running it |
| Configuration analysis | Python, PyYAML | Narrow configuration/deployment declaration interpretation |
| Evidence | Python validators and limited redaction | Keep citations and graph references consistent |
| Storage | SQLite | Saved jobs, summaries and canonical graph JSON |
| Presentation backend | Graph projections and bounded exploration | Aggregate facts and serve selected neighbourhoods |
| Browser UI | React, TypeScript, Vite, Tailwind | Analysis, summary, hierarchy, diagram and evidence controls |
| Diagram interaction/layout | React Flow 11.11.4, ELK.js 0.12.1 | Interaction and automatic positioning |
| Verification | pytest, compiler fixtures, browser acceptance scripts | Regression and functional checks |

Relevant directories are `backend/app/ingestion`, `backend/app/analysis`, `backend/workers/typescript`, `backend/app/evidence`, `backend/app/graph`, `backend/app/persistence`, `frontend/src`, and `shared`.

This is a modular monolith with a separate trusted analyzer process, not a collection of independently deployed microservices. The Node worker communicates through JSON; it does not import or execute the submitted app.

The backend environment uses PyYAML 6.0.3 and has no NetworkX installation. System Python has PyYAML 6.0.2 and NetworkX 3.3; those are separate from the backend environment. NetworkX is not driving the diagrams. Syft, Semgrep, ast-grep and Tree-sitter are deferred, not active stages. Syft would inventory software components, rather than resolve source calls. pyan3, pycallgraph2, VizTracer and OpenTelemetry tracing are not part of this platform's active analysis.

## What the existing GitDiagram result establishes

Recorded results include 840 inventoried files, 386 parsed source files, 4,240 entities and 10,892 relationships. Relationships include ownership, definitions, imports and type references as well as calls: the total is not a count of runtime communications. Of 12,074 call/constructor expressions, 3,833 resolve to local implementation bodies. Unknowns also include library, builtin and generated-code cases; they are not automatically broken application links.

The recorded suite passed 61 tests and browser acceptance checks. These establish tested functionality and regression preservation, not measured architectural precision or human comprehension. There is no diverse labelled ground-truth benchmark or controlled comparison proving superiority to competitors.

The curated architecture image used manual source-review context and image generation. It is not the automatic analyzer's output or an accuracy benchmark. In particular, some storage/context relationships in that interpretation are not yet recovered automatically.

## Confirmed gaps and drawbacks

### Architecture abstraction

Grouping currently relies heavily on packages, paths and role heuristics. A directory is useful ownership evidence but does not necessarily represent a responsibility, deployment boundary or service. Shared protocol/schema code under a features directory can be mislabelled as UI code. Choosing prominent connections by counts and SDK preference does not reliably choose the most important architectural relationships.

This explains why a graph with relatively few visible nodes can still be hard to understand. The missing work is partly interpretation, not simply hiding more nodes or changing layout.

### Three reproducible analyzer limitations

Tiny synthetic fixtures were parsed by the trusted worker, without executing target code or rescanning GitDiagram. Results are saved in `output/review/explanation-analysis-probes.json`.

* A URL variable initialized to one host and unconditionally reassigned to another still produced a link to the initial host. Initializer following is insufficient value analysis: this is a false positive despite valid source citations.
* `public/runtime.js` was excluded by the blanket assets/test/tooling rule. Production browser JavaScript can live under `public/`, including GitDiagram's video engine.
* A `GET` export in `src/app/route.ts` produced no registered endpoint. The current Next.js adapter misses this root-route form.

These were documented, not fixed, during this review.

Other limitations include partial tsconfig/workspace handling, absent target dependency types, incomplete React composition and Next.js server/client context, dynamic routes, middleware mounts, dependency injection and resource mapping. Recognizing a database package or configuration declaration is different from proving a particular function uses a database.

### Usability, scale and deployment

The UI exposes many useful controls, but entry-point recommendations can favour helpers rather than business operations. The default view remains closer to a grouped source explorer than a complete architecture report. A first-class exportable architecture artifact and a clearer overview-to-workflow journey remain useful improvements.

SQLite stores a whole graph JSON document; requests load and index that document. Exploration has bounds, but this storage design is not an indexed large-graph database. There is no file-level incremental analysis, and position-derived identifiers are not stable across arbitrary refactors.

Safe extraction, fixed retrieval and not executing target code reduce risk. Read-only file flags are not an OS security sandbox. Public multi-tenant use still needs stronger process/resource/network isolation, authentication, tenant separation and operational controls. This is not yet a complete threat-modelling or vulnerability-assessment product.

## Fair comparison

[GitDiagram](https://github.com/ahmedkhaleel2004/gitdiagram) is oriented toward AI-assisted architecture explanation and presentation. Its [architecture documentation](https://github.com/ahmedkhaleel2004/gitdiagram/blob/main/docs/architecture.md) describes bounded source excerpts, validated structured graph generation and deterministic Mermaid compilation. It should not be dismissed as unvalidated diagram generation. It also offers product features such as export, private-repository support, videos and MCP integration.

[REA](https://github.com/morluto/rea) is a broader reverse-engineering workbench, including static source analysis and optional runtime, browser, binary and provider workflows. Its static JavaScript analysis does not require running the target; terminal workflows need not require an LLM. Local operation and evidence are already strengths of REA, so those are not unique advantages of our platform.

Our defensible distinction is a focused source-to-diagram workflow with mandatory source provenance and no mandatory AI interpretation or source submission to a model. Our narrower scope may make a simpler product possible, but the current UX has not achieved that simplicity. No head-to-head accuracy, speed or cost benchmark has established overall superiority.

## Recommended development order

1. Fix known incorrect/missing extraction rules with small regression fixtures. Existing tools suffice.
2. Strengthen architecture interpretation between the canonical facts and rendered diagram: responsibilities, logical boundaries, resource usage and communication types, each with evidence and limitations.
3. Add bounded value/configuration propagation where it resolves real missing relationships; avoid guessing database or network links from names.
4. Make the first screen an understandable architecture report. Keep workflow exploration, evidence and diagnostics accessible through selection rather than competing for initial attention.
5. Validate a small number of framework stacks deeply across diverse labelled repositories. Measure wrong edges, missed edges, unresolved cases and whether a newcomer can explain the diagram quickly.
6. Harden isolation and tenancy before public uploads; broaden language support after the supported analysis is trustworthy.

Repeatedly scanning an unchanged GitDiagram snapshot cannot add missing semantic rules. Reuse saved facts to improve presentation, and rerun analysis only when extraction behavior or input changes.
