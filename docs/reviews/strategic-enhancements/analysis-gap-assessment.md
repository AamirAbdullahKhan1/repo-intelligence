# Analysis gap assessment

Date: 31 October 2026. Current code is the baseline. This document proposes changes; none were implemented. Candidate tools were researched, not installed or executed. See [impact review](architecture-impact-review.md) for sources, safety profiles and qualitative costs.

## Priority and evidence

P0 means incorrect facts/safety or the ability to evaluate correctness. P1 means the next highest architecture value. P2 means expansion after the supported scope is reliable. These are prioritization judgments, not measured ROI.

| Priority / gap | Current limitation and evidence | Architectural impact | Proposed assistance: does it solve it? | Preferred implementation and expected benefit | Remaining limits |
|---|---|---|---|---|---|
| P0: stale initializer values | `index.cjs:literal` follows variable initializer; saved `mutable_url` probe records old host after unconditional reassignment | Wrong external integration arrow with valid citation | Bounded reaching definitions directly helps; Syft/clustering do not | Compiler-worker program-point values; invalidate unknown mutations. High correctness value for supported values | Aliasing, callbacks, mutable closures and side effects can force unknown |
| P0: skipped production code | `walk` excludes `public`, `scripts`, `plugins` by path; saved probe skips `public/runtime.js` | Important browser functionality disappears; GitDiagram has production public video assets | No additional scanner needed; another scanner could merely mask the omission | Purpose-aware source inclusion with recorded scope and strict byte budgets. Recover valid production files without executing them | Generated/minified/vendor code still needs explicit coverage treatment |
| P0: route omissions | `adapters/next.cjs` nested-route regex misses `src/app/route.ts`; saved probe has no endpoint | Missing entry points and workflow anchors | Custom framework-rule fix; pattern tools are unnecessary for this case | Explicit route-path cases, export identity, positive/negative fixtures | Middleware, rewrites and dynamic routing remain partial |
| P0: no architectural truth corpus | Regression tests exist; 61-pass historical report; no labelled diverse corpus | Cannot quantify false architecture or judge proposed additions | dependency-cruiser/Grimp can compare imports, not act as truth | Hand-labelled entity/edge/unknown fixtures and representative repositories. Enables precision/coverage evaluation | Human annotation scope and disagreements must be documented |
| P0 deployment gate: containment | `guard.cjs` blocks selected Node APIs; flags/fingerprints protect source integrity; no OS-enforced sandbox | Every extra parser/plugin adds attack surface for uploads | No analysis tool solves containment | Preserve restrictions; add OS filesystem/egress/process/resource controls before public operation | Host/container escape and parser vulnerability management remain ongoing |
| P1: responsibility abstraction | `component()` uses paths; `Index.decorate` labels directory roles; `aggregate` summarizes edges | Source groups can be mistaken for UI/backend/services | Interpretation rules help; Louvain only supplies structural hints | Evidence-backed roles, membership and boundary types; allow mixed/unknown roles. High comprehension value | Business intent and arbitrary frameworks cannot always be recovered statically |
| P1: execution context | React/package detection exists; no complete JSX or Next browser/server context model | Relative fetch and frontend/backend boundaries can be misleading | Custom framework semantics, assisted by compiler data; no package scanner solves it | Distinguish browser/server/shared/unknown context; model supported framework conventions | Framework versions, bundler transforms and runtime configuration |
| P1: config-to-resource links | `resolveOrigin` shallow SDK tracking; `literal` partial strings; Wrangler/Compose declarations separate | Storage/database/queue links missing or overgeneralized | Value propagation plus framework/SDK summaries helps; typings help signatures only | Symbolic env/config keys, client origin, supported operation and deployment binding derivations | Missing env values, arbitrary helpers and external deployment configuration |
| P1: HTTP endpoint matching | Literal host extraction and selected routes do not establish complete client-server mapping | Cannot reliably join browser action to own backend route | Bounded values/context plus method/path matching partially solves | Preserve candidate matches and rewrite/base-path evidence; require sufficient predicates before a resolved link | Proxies, service discovery, runtime hosts and dynamic methods |
| P1: compiler configuration fidelity | Worker reads root tsconfig fields, restricted host; no complete nested config/reference resolution or installed dependency declarations | Missed module/symbol identities in monorepos | dependency-cruiser comparison can reveal differences; curated typings improve selected APIs | Safe in-snapshot config inheritance/reference handling and package resolution; no executable config | Unsupported build plugins/custom loaders stay unresolved |
| P1: one main architecture | Overview is bounded, but graph salience and helper-based entry selection remain heuristic | User cannot quickly locate or explain the system | LikeC4 may export a model; does not choose correct content | Rework projection selection around roles/entry points/resources; one obvious overview and drill-down. High product value | Layout cannot compensate for missing facts; human validation required |
| P1 before extra providers: evidence semantics | Graph validates IDs/ranges but allows extra fields and arbitrary kinds; statuses interpreted by presentation | Conflicting tools could duplicate/upgrade ambiguous findings | Normalization/reconciliation boundary, not an off-the-shelf scanner | Provider provenance, typed claims, support chains, consistent status semantics and conflict records | Rules remain fallible; migration needed if persisted fields change later |
| P2: external API signatures | Target dependencies not installed; local-body-only calls intentional | Library calls often lack rich API identity | Curated declarations help identity/types, not actual implementation | Version-pinned trusted metadata and SDK summaries | Mismatch, declaration inaccuracies and dynamic library behavior |
| P2: Python semantics | Python inventory does not equal semantic support | Python apps cannot receive equivalent architecture recovery | Grimp/import-linter cover imports/contracts only | Filesystem `ast` provider first; selected framework rules and conservative binding | Dynamic imports, decorators/metaclasses, DI remain difficult |
| P2: inventory breadth | Manifests inventoried, no full lockfile SBOM | Third-party version/transitive visibility incomplete | Syft useful for exactly this inventory gap | Optional package findings with locations and declared/installed distinctions | Package inventory does not establish resource usage |
| P2: infrastructure breadth | Compose and Wrangler narrow; Terraform absent | Declared infrastructure may be missing | HCL parser/Inframap can help resource references | Optional declaration provider with resource addresses and original source spans | Remote modules/state/runtime deployment not established |
| P2: graph scale | SQLite whole graph JSON; `Index` rebuilt by API calls | Extra tools enlarge response-time/memory cost | NetworkX may add memory rather than fix storage | Measure load/index cost; cache immutable indexes first; index storage only if measurements justify | File-level incremental analysis and stable identities across refactors remain separate work |

## What “better” should mean

Do not optimize for entity count or fewer unknowns alone. A conservative unknown is preferable to an unsupported resolved edge. Report:

* Correct/incorrect extracted edges by relationship kind, not one mixed score.
* Missed expected edges within an explicitly supported language/framework scope.
* Candidate and unresolved cases separately, including why analysis stopped.
* Evidence completeness and whether a derived edge's entire support chain can be inspected.
* Input scope coverage, exclusions, truncation and provider failure.
* Determinism for identical snapshots, pinned engines, rule/config versions and budgets.
* Analysis and view-query time, peak memory and output size on fixed hardware; collect measurements before numerical targets.
* Whether an unfamiliar user can identify major responsibilities, inspect a relationship and understand uncertainty without reading source-level thousands of nodes.

The saved GitDiagram overview has 13 nodes and 24 edges. That proves it is bounded, not that its abstraction is correct. The earlier curated image uses manual interpretation and is not a ground-truth graph.

## Recommended first scope

Deepen TS/JS Next.js and Express analysis on small, varied applications before new language rollouts. Start with the three known failures, source scope, module resolution, context and resource-use chains. Use the saved GitDiagram facts for projection work, rescanning only when extraction behavior changes. Include other applications so the rules do not overfit GitDiagram.

Useful negative examples include unused clients, unused dependencies, reassigned URLs, conditional hosts, unrelated same-named resources, type-only imports, server-side relative fetch, invalid route exports and unsupported object mutation. The engine must show an unknown or candidate instead of inventing a resolved architecture edge.

## Non-solutions

* Syft cannot connect a function to a database simply by discovering a database package.
* Import graphs and SCCs cannot establish network communication or deployment boundaries.
* A community partition cannot decide that a group is a microservice.
* Declaration metadata cannot prove a library's implementation or runtime dispatch.
* A second renderer cannot recover missing architectural semantics.
* Valid source ranges and agreement between scanners cannot prove a rule correct.
* Static call reachability is not guaranteed execution order.

The most valuable improvement is a smaller number of correct, explainable architecture relationships, supported by inspectable facts, rather than more scanners or a denser graph.
