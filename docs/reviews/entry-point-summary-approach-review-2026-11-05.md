# Review: entry-point-driven reconstruction and the accompanying critique

5 November 2026. Reviewed the supplied proposal and the ten-point review against the current source. No production implementation was changed. The referenced organizational v1.1 document was not supplied here; detailed compatibility with that separate document is not verified.

## Verdict

Adopt as a refinement of the existing pipeline, with modifications. The important next step is reusable, parametric effect summaries and framework registration models above existing facts, not replacing extraction or simply traversing more functions. Entry points and boundary operations together provide useful architectural anchors; neither a call graph nor route reachability alone establishes application architecture.

## What already exists versus what would be new

| Capability | Current implementation | Proposed change |
|---|---|---|
| Shared symbol identities and call facts | Existing worker, canonical entity IDs and callsites | Improve revision/cross-run identity without duplicating symbols per journey |
| Entry-driven slices | `capabilities.py` already performs bounded traversal from endpoint groups | Reuse summaries and broaden entry types; do not describe root traversal as entirely new |
| Function/object flow | Demand-built worklist with bounded call contexts | Parametric summaries for supported effects; keep contextual fallback for unsupported interactions |
| S3 operation/configuration tracking | Existing operation provider, logical bucket references and caller-context claims | Normalize into effect summaries without losing context or provenance |
| Express routes | Literal verb registrations and selected bound handlers | Router identities, mount composition and registration relationships; current mount prefixes are explicitly unmodeled |
| Callback contracts | Selected runtime/framework and local-parameter models | Extend function-value propagation and registration semantics selectively |
| Capability grouping | Primarily route-prefix slices | Operation-aware grouping, shared-infrastructure annotations and entry coverage diagnostics |
| Summary persistence and SCC scheduling | Not a general bottom-up summary system | New bounded subsystem, additive records and versioned cache keys |
| Journey display | Bounded call/callback graph | Shared expandable effect graph with explicit scheduling/branch uncertainty |

Keep TypeScript, Node, FastAPI/Pydantic, SQLite, the original evidence graph, existing flow providers, React Flow and ELK. New derived records must not silently reinterpret old saved analyses.

## Assessment of the ten recommendations

### 1. Bottom-up summaries and recursive components: adopt with limits

A strongly connected component (SCC) is a group of functions that can call around a cycle. Schedule these groups in dependency order, but preserve individual function identities and internal evidence. Iterate summaries inside a recursive group until stable or a deterministic budget is reached. Merely condensing the graph does not solve recursive effects.

The graph itself can grow as callback/receiver targets are discovered. Call-target discovery and summaries may therefore require a bounded joint fixed point, not a permanently fixed call graph built once before all value analysis.

Do not precompute every expensive analysis for every function just to call the design bottom-up. Build local effect facts, then summarize the relevant reachable/operation-bearing portion and its dependencies. An inexpensive repository-wide operation inventory supports orphan diagnostics.

### 2. Parametric summaries: adopt as the default supported mechanism

Example: `save(bucket,payload)` can summarize “possible storage write; Bucket = parameter 0; payload = parameter 1.” At each caller, substitute argument/configuration expressions and record the instantiation evidence. The function remains one canonical entity; its effects have separate caller-specific bindings.

Summaries also need receiver/client identity, object-field paths, return bindings, configuration references, unknown side effects and unsupported operations. Parametric expressions cannot remove every need for context. Dynamic dispatch, closures, alias mutation and factories can require bounded specialization or an explicit unknown. Retain the existing contextual implementation as a fallback until equivalent supported behavior is demonstrated.

### 3. Exits and effect relevance: adopt, but do not erase controls

Boundary operations are strong architectural anchors: inbound requests, outbound HTTP, storage/database operations and messaging. Preserve the operation callsite, client, arguments and resolution separately from its external resource identity.

Collapse implementation detail in views rather than deleting pure functions from the canonical graph. Validation, authorization, transformations and response construction can be architecturally significant even without external side effects. A dependency used to decide what data leaves the application should not disappear merely because it computes a value.

### 4. Reachability honesty: adopt early

Report recognized effectful functions not connected to known entries, and distinguish these reasons: no supported entry, unresolved hop, traversal truncated, excluded/unsupported scope, exported library API, or apparently disconnected source.

An orphan does not prove dead code or identify a missed entry rule conclusively. A library can intentionally expose exported functions without a server entry. “Reachable share” needs a declared denominator and must not become an accuracy percentage. Count known possible reachability, not actual runtime reachability.

An entry-only demand strategy cannot discover every orphan. Keep discovery and a bounded effect inventory over the supported source scope before computing entry views.

### 5. Registrations and router flow: adopt as a concrete first milestone

Model application/router allocation identities, imported/returned router values, literal mount prefixes, route verbs and ordered registration evidence. A router mounted twice creates two route instances with shared handler implementation; it is not a duplicate function.

Keep route definition, mounted endpoint and handler invocation as different facts. Preserve method, router ancestry, application/project, prefixes and registration source locations. Respect supported Express versions/settings; strict routing, patterns and conditional registrations need qualification or unknown status.

Middleware order is not guaranteed execution order. Middleware can terminate the response, throw or call `next('route')`; request-time behavior cannot be replaced with registration order.

Official references: [Express middleware](https://expressjs.com/en/guide/using-middleware/), [Express routing](https://expressjs.com/en/guide/routing/).

### 6. Hubs and shared helpers: adopt as a presentation/grouping rule

High fan-in is a useful hint for shared implementation, not a definitive role. A central business orchestrator can also be a hub. Keep shared membership and use route affinity, effects, operations, ownership and explicit boundaries as multiple signals.

Exclusive resource identity is not enough: many unrelated features use the same PostgreSQL instance or S3 bucket. Prefer operation kind, entity/table/topic where established, public interfaces and cohesive interactions. Explain grouping support rather than claiming graph clustering discovers a unique business architecture.

### 7. Operation versus configured resource: strongly adopt

“Calls a bound database client's query operation” and “uses PostgreSQL instance X” are different claims. Preserve partial progress when the destination is unknown. Resource linking requires bound client identity and configuration/profile context; do not classify arbitrary `db.query` by its method name.

The existing S3 provider already demonstrates part of this separation. Refactor it into an effect provider, not discard its client/bucket evidence.

### 8. Identity and caching: modify the recommendation

Qualified path plus body hash is useful for a revision key, but not sufficient long-lived logical identity. A body edit would otherwise create a new function identity and make drift look like deletion/addition. Identical anonymous bodies and captured variables also complicate it.

Use three layers: logical symbol identity within repository/package/module and declaration ownership; declaration/semantic revision fingerprints; snapshot-bound source citations. Keep ambiguous cross-run matching explicit and preserve historical IDs. Body/source positions can support matching; neither is a complete universal stable key.

Summary cache keys must include relevant language/project/module options, extractor/model versions, external/trusted declarations, accessed module/configuration inputs, and callee-summary revisions. Captured variables and imported constants can change effects without changing the function body.

Within recursive groups, hash a canonical converged group result and its external dependencies; do not recursively hash mutually dependent summaries forever. Start with in-run reuse before introducing persistent incremental caches.

### 9. Deterministic budgets: adopt the distinction

Use deterministic counts of processed constraints, candidates, contexts, nodes and edges to decide semantic truncation. Keep process deadlines and heap limits as safety controls. If a safety timeout occurs, mark the run/scope incomplete rather than claiming its timing-dependent partial result is the reproducible completed model.

The current flow module includes both count limits and an elapsed-time budget; it should be refined accordingly. A successful repeat on one snapshot does not prove all limit-triggered runs deterministic.

### 10. Journey labeling: modify

“Effects in source order” is better than claiming execution order, but still misleading across calls, callbacks, loops, exceptions and async work. Until relevant control flow exists, present a possible-effects dependency graph, with source location used only for stable display ordering. Separate immediate, registered, event-triggered and deferred relationships.

The proposal's application initialization → registration → request → database chain mixes startup and per-request behavior. Show startup registering a handler in one view and the request entering that handler in another; a request does not re-run route registration.

## Additional corrections

**Imports are not function calls, but they are not semantically inert.** Loading a module can initialize top-level code, register routes or replace a global. Type-only imports differ from value/side-effect imports. Keep module-initialization facts separate from ordinary function participation. GitDiagram's global fetch replacement is a relevant existing example.

**External is not a resolution state.** Track location/scope separately from resolved/ambiguous/unresolved. A target can be an unambiguously resolved external SDK operation whose runtime implementation or remote endpoint is unavailable. Also preserve direct versus possible invocation and partial-analysis status independently.

**Control-flow detail can be staged, but uncertainty cannot.** Basic error/branch/callback distinctions must remain visible now. Authentication function presence does not prove it guards every route, and a call later in a file is not necessarily performed after another operation.

**Summary expansion must retain provenance.** Store summary effect templates plus derivation references and callsite bindings. Reuse a shared DAG rather than enumerating every path, but let users expand an effect to its supporting chain. Cycles and budget boundaries must be inspectable.

**Package ownership must not stop supported local traversal.** The current capability pass restricts traversal to the same application/package identity. That can omit a workspace shared library called by a route. The revised layer should follow resolved local workspace bodies across source-package boundaries, retain their ownership/shared status, and stop at justified analysis/runtime boundaries rather than at every package boundary.

## Research claims and performance

The general summary-based direction is established. IFDS, however, is a specific framework for finite, distributive dataflow problems with valid call/return paths. A custom JS points-to/effect analysis is not automatically IFDS/IDE, and their precision or complexity guarantees do not transfer without showing the required assumptions. [Reps, Horwitz and Sagiv](https://pages.cs.wisc.edu/~fischer/cs701.f14/popl95.pdf).

Jelly and indirection-bounded analysis remain relevant references for dynamic function/object flow and bounded work. They are not architecture generators or reasons to replace working compiler/provider code. [Indirection-bounded analysis](https://cs.au.dk/~amoeller/papers/bounded/), [Jelly](https://github.com/cs-au-dk/jelly).

The reviewer is reasonable to expect compiler/checker work to be important, but we have not measured that it dominates our 42-second run. Summary fixed points, heap alternatives, configuration linking, evidence serialization/validation and repeated queries can also dominate. Record per-stage time and peak memory before promising that journeys are cheap or that bottom-up summaries deliver a specific speed-up. Count bounds and safe partial results remain necessary.

## Smallest useful proof of concept

Use an independent five-route Express fixture/repository with:

- One imported router mounted under `/users`, and the same router mounted at a second prefix.
- A shared validation helper and same-named functions in different files.
- One PostgreSQL query, one S3 helper called with different bucket arguments, one literal outbound HTTP operation.
- One three-function recursive group, one unresolved indirect callback and one effectful function with no recognized entry.

Deliver mounted endpoints, shared symbol graph, parametric effect summaries, bounded recursive processing, expandable possible-effect journeys and an orphan/coverage report. Keep the current GitDiagram case as a regression, not the fixture template.

Acceptance must include:

1. Correct full route paths and methods, with separate registration evidence.
2. A shared helper has one entity and multiple caller edges.
3. Recursion terminates without losing effects or inventing paths across callers.
4. Different bucket arguments remain different effects; unknown arguments remain parametric/unknown.
5. Unknown callbacks and orphan effects are reported with reasons.
6. Repeated completed output is identical, including deterministic semantic-budget truncation.
7. Hand-reviewed expected effects and negative relationships are checked.
8. Every displayed effect expands to source-backed summary and callsite evidence.
9. Editing an unrelated line does not arbitrarily replace all logical identities; editing a callee invalidates affected summaries.
10. Existing S3/callback fixtures and old saved analyses remain valid.

## Recommended implementation sequence

1. Define the summary/effect/registration contract, identity-vs-revision rules and known coverage. Build the labeled independent fixture first.
2. Extend Express mounts/registrations and operation inventory; publish orphan diagnostics immediately.
3. Add local parametric summaries and bounded SCC fixed points, initially in-run only. Migrate one supported S3 effect and retain contextual fallback.
4. Derive shared journey DAGs and operation-aware capability views, preserving controls/shared helpers and source evidence.
5. Measure correctness and cost on the fixture, existing GitDiagram snapshot and an unfamiliar holdout. Add persistent incremental caching only after invalidation tests pass.

This is an implementable improvement to the current architecture, not a reason for another broad rewrite. Its success depends on recovered boundary effects, correct caller bindings and understandable abstraction—not how much of the call graph is traversed.
