# Prioritized improvement proposal

Date: 2 November 2026. Recommendations only; no implementation or dependency changes were made. References are the [individual reports](README.md) and the existing [deterministic solution](../deterministic-reconstruction-solution.md). These priorities keep foundation fixes ahead of execution management and UI expansion.

Complexity is an engineering estimate: L = localized change, M = several modules/contracts, H = semantic or cross-project work. No schedule, accuracy or performance numbers are invented.

## P0 — correctness and evaluation foundations

| Improvement | Problem / research reference | Fit and complexity | Dependencies / risks | Acceptance test |
|---|---|---|---|---|
| Explicit source outcomes | Production files excluded; RepoDNA inventory/parse/extraction distinction | Worker discovery plus coverage; M | Exclusion-policy changes increase scope and cost | `public/runtime.js` included deliberately; generated/vendor/test cases remain classified; every skip and limit has a reason |
| Correct root-route extraction | Missing Next root endpoints; RepoDNA route/navigation model is useful but not a binding oracle | Existing Next adapter; L initially | Route groups, exports, conflicting framework conventions | Root/nested supported methods map to actual handlers; shadowed/invalid exports do not become routes |
| Stale-value prevention | Wrong host after reassignment; Joern staged reaching definitions | Conservative invalidation first; worker value module next; M→H | Program point, closures, branches and side effects | Old host absent after reassignment; unsupported mutation yields unknown; alternatives never silently discarded |
| Project-aware resolution | Incomplete aliases/workspaces; Understand context and Sourcegraph index prerequisites | Restricted TS config/project host; H | Missing external configs/generated exports; path escape and condition ambiguity | Config-relative aliases, inheritance, workspace exports/subpaths and cycles have labelled results; no target installs or outside-root reads |
| Typed truth corpus | No architectural precision/recall evaluation; StructSAR metric separation | Synthetic fixtures plus manually labelled held-out snapshots; M | Ambiguous human architecture; sampling bias | Expected and prohibited typed edges, source support and scope recorded; evaluate wrong/missed edges independently from grouping |
| Provenance-safe graph semantics | Resolved may hide heuristic binding; RepoDNA resolver labels and Understand references | Versioned internal/contract design; M | Migration and extra-field permissiveness | Source/config/derived origins, rule versions, support IDs and context survive save/reopen; invalid support chain rejected |

Existing synthetic probe output is a reproducible issue description, not a substitute for permanent regression tests. Existing tests `test_typescript_worker.py`, `test_framework_adapters.py`, `test_exploration.py` and `test_ingestion.py` should be preserved and extended deliberately. No tests were run for this research.

## P1 — complete the architecture chain

| Improvement | Problem / reference | Fit and complexity | Dependencies / risks | Acceptance test |
|---|---|---|---|---|
| Bounded values/helper summaries | Config-to-client chains missing; Joern data-flow stages | Worker-only language semantics, normalized symbolic outputs; H | P0 resolution; invalidation/alias/loop precision; budget growth | Literal/assignment/branch/import/config/helper cases establish exact/alternative/unknown values with full support |
| Framework callbacks and mounts | Handlers often indirect; RepoDNA Express reconciliation | Extend language-scoped adapters, retain compiler binding; M/H | Avoid name-based receiver assumptions; versions vary | Supported imported handlers and router prefixes resolve; arbitrary callbacks and dynamic mounts stay explicit |
| Runtime-context classification | Relative fetch can mean different things | Next/browser/server/shared adapter facts; M/H | Import graph alone does not determine execution | Browser same-origin case matches only under supported conventions; server-relative/unknown cases not guessed |
| HTTP linker | Frontend/backend disconnected | Python cross-source reconciliation over language facts; H | Destination, profile, method, base path/rewrite and endpoint semantics | Same path on two backends selects by supported destination or stays ambiguous; both ends/config chain inspectable |
| Resource linker | SDK package mistaken for resource use | Client operation + config + declaration linkage; H | Profiles, instance identity, unknown environment; no credentials retained | Unused clients yield no data operation; same-named databases/profiles remain distinct; missing binding yields integration with unknown instance |
| Responsibility/boundary rules | Directory role ≠ application responsibility | Interpretation functions before projections; H | Overlapping/shared roles and business-intent limits | Route/API/UI/worker/shared-contract facts drive generic labels; package/build/deployment boundaries remain distinct |
| Richer queryable support | Need callers, references and derivation inspection | Reverse indexes over canonical facts; M | Whole-graph load cost; avoid second graph | Reverse callers/references produce bounded results and retain relation/status; no claimed runtime impact |

Callback/dynamic-dispatch handling should target concrete patterns, not implement an unbounded whole-language points-to engine. Library models declare preconditions and side effects. Unknown is a useful result when the supported analysis cannot establish identity.

## P2 — value after foundations work

| Improvement | Value / reference | Fit and complexity | Risks and validation |
|---|---|---|---|
| Python language provider | RepoDNA demonstrates useful AST breadth; Understand emphasizes context | Filesystem `ast` provider and explicit import scopes; H | Do not import client modules; evaluate Python-specific positives/negatives rather than count files |
| Incremental analysis | RepoDNA file cache and Sourcegraph commit indexes illustrate distinct cache units | File/fact/config/rule dependency invalidation; H | A parse cache is not complete incrementality; compare incremental graph with clean full analysis after edits/deletions/config changes |
| Semantic grouping experiment | StructSAR offers metrics, not a proven no-ML answer | Simple deterministic baseline before optional clustering; M/H | Measure partition agreement/cohesion separately; never infer services from clusters |
| Focused UX and exports | RepoDNA/CodeSee/GitDiagram show clearer journeys | Existing graph/view contract and renderer; M | Keep user view state separate from facts; newcomers inspect correct source support; no UI work ahead of P0/P1 |
| Immutable index reuse/storage profiling | All large graph products separate analysis from exploration | Cache indexes by analysis ID, then consider normalized SQLite; M | Measure stage/query cost and peak memory; do not migrate database without a measured bottleneck |

## Deferred or not adopted

* Full Joern/CPG replacement: broad runtime/schema cost before our narrow flow/linking requirements are established. A demanded-language pilot may become worthwhile.
* Neural StructSAR methods in core: no LLM, but still learned computation with resource/reproducibility costs; not our selected deterministic rule foundation.
* Automatic SCIP indexing with target installs/builds: conflicts with constraints. A validated precomputed-index import is a separate future proposal.
* CodeSee-like collaboration/review automation, GitDiagram video/admin features and hosted artifact-service migration: not foundation fixes.
* Neo4j, distributed queues, tool-per-container architecture and plugin marketplace: no demonstrated analytical need. Isolation work is a separate public-deployment gate.
* Global unique-name call resolution and arbitrary percentage confidence: reject as authoritative evidence. A candidate may be recorded without upgrading it to a bound implementation.

## First complete vertical

Build a static fixture with a browser/API entry, handler, application function, client operation and configuration-declared destination. Include unused SDKs, a shared schema and competing same-named destinations. The default view should have meaningful responsibilities; detail should expose actual source facts and conditions.

Success means the required links are correct and traceable, false alternatives absent, unresolved input explicit, and saved analyses stable—not a larger graph. Then validate on an unfamiliar repository and GitDiagram. Add stage timing/output-size observations from the first increment; resource targets follow measurements.

Keep application code unexecuted. Preserve existing pipeline, schema compatibility and regressions. If a contract extension is necessary, version and migrate it before publishing new artifacts. Candidate dependencies require an audited safe profile and a measured capability benefit.

## Evaluation design

Separate four questions:

1. **Extraction:** correct/missed imports, calls, routes and resource operations by kind and supported scope.
2. **Linking:** correct/incorrect destination identities and complete supporting chains; conditional/candidate outcomes separate.
3. **Abstraction:** component memberships and boundaries against labelled references; cohesion alone is insufficient.
4. **Presentation:** can an unfamiliar reader identify major parts, inspect a link and understand uncertainty? Automated UI clicks do not establish comprehension.

Use positive, negative and ambiguity fixtures, fixed public commit snapshots and a held-out project. Report all scope exclusions and provider failures. Do not turn a lower unresolved count into an accuracy claim. Use source/body identity and context checks; a source range's existence alone is not semantic validation.
