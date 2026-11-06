# TS/JS core approach: research, diagnosis and implementation decision

4 November 2026. This is a reassessment of the current implementation, not a claim that general TS/JS reconstruction is solved. The research experiment is isolated from production dependencies.

## Decision

Keep the TypeScript parser/resolver, ingestion, canonical evidence graph and saved-analysis pipeline. Replace the strategy of extending individual expression walkers indefinitely with a bounded data-flow layer and a dedicated architecture-reconstruction pass. Evaluate Jelly as an auxiliary semantic provider before deciding whether to reuse its solver or implement a smaller targeted solver. Do not replace the whole platform with a tool that emits another function graph.

The product milestone must be an evidence-backed architecture and an intelligible request workflow. Compiler counters, fewer warnings and more edges are supporting measurements, not the milestone.

## Why the diagram is not improving enough

Fresh inspection of snapshot `d35bbceee8a9…` found:

| Measurement | Actual result | Interpretation |
|---|---:|---|
| File/symbol/endpoint entities eligible for role grouping | 4,754 | Not a count of files or runtime components |
| Entities in Other analyzed source | 4,620 / 97.18% | The direct-operation role classifier leaves most entities unclassified; this is not 97% parsing failure |
| Technical role groups | 10 | Technical categories, not cohesive application capabilities |
| Callback relationships | 191 | Useful workflow facts |
| Callback kind accepted by role aggregation | No | The latest callback improvements are not consumed by this architecture aggregation pass |
| Concrete resource-operation edges | 0 | Real resource chains remain missing |
| Unresolved records | 3,311 calls; 53 imports; 60 HTTP | Distinct and potentially overlapping questions, not diagram-error totals |

These facts are recorded in `output/research/tsjs-core-reset/baseline.json`. The relevant implementation is `backend/app/analysis/responsibilities.py`: it classifies endpoints and direct callers of recognized operations, puts other entities into a catch-all group, and aggregates a fixed list of edge kinds. It does not reconstruct capability boundaries or summarize an entry-point slice.

The frontend's focused overview then excludes catch-all groups when specific roles are available. Consequently, useful extracted code can remain invisible to the overview. Broad roles also combine unrelated routes. This is a model deficiency before it is a layout problem. Simply including the new edge kind would improve connectivity but would not solve capability reconstruction.

## Research findings that affect our design

### 1. Call graphs require object and function flow

Jelly's documented core uses points-to/control-flow analysis and library access paths. That is closer to our higher-order functions and returned-client problem than collecting compiler signatures alone. It is intentionally incomplete and primarily targets Node.js programs; it supplies neither our Next/React architecture nor deployment interpretation. Its README distinguishes static analysis from optional dynamic and approximate modes. We will evaluate static mode only. [Jelly](https://github.com/cs-au-dk/jelly).

The current `values.cjs` follows bounded AST expressions, rejects async helpers and branching return shapes, and does not solve a graph of assignments to a fixed point. Its safety checks are useful, but they cannot become a general interprocedural flow analysis merely by adding more syntax cases.

### 2. Bounded propagation is a practical design, with an explicit completeness cost

Indirection-bounded analysis limits how far object/function flow propagates. The published evaluation reports a performance/recall trade-off on its benchmarks, not a universal accuracy guarantee. Our adoption is the engineering principle: retain budgets and state which paths remain unexplored; never silently label partial results complete. Our existing recursive AST depth limit is not equivalent to the paper's solver. [Indirection-Bounded Call Graph Analysis](https://cs.au.dk/~amoeller/papers/bounded/paper.pdf).

### 3. Scope data-flow queries to architecture questions

CodeQL distinguishes local flow from more expensive global flow and supports library summaries. Adopt this separation: start at routes and recognized operations, then ask where a receiver, callback or destination came from. Taint tracking is not a substitute for preserving exact value identity. CodeQL remains an optional comparison provider, not an unconditional dependency: its documented private-repository availability has licensing conditions that need review for a client-code service. [Data-flow analysis](https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-javascript-and-typescript/), [library models](https://codeql.github.com/docs/codeql-language-guides/customizing-library-models-for-javascript/), [CLI availability](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-cli).

### 4. Combining tools requires claim reconciliation, not a union of arrows

The static architecture-recovery comparison found useful complementary tools but also reproducibility failures. Its results are microservice-specific and cannot be transferred to TS/JS frontend capability accuracy. Deployment and source facts are complementary: a resource declaration is not proof of an operation. Our merger must preserve each provider, rule, source range and status; provider agreement does not independently prove correctness. [Architecture-recovery comparison](https://arxiv.org/html/2412.08352v1).

The JavaScript call-graph comparison also warns against headline accuracy: its small-program recall uses the union of verified tool results as a proxy, and the larger Node.js results show different behavior. We must evaluate our actual profiles, not select a tool by a quoted percentage. [Call-graph comparison](https://arxiv.org/pdf/2405.07206).

### 5. Modular extractors should enrich a stable architecture model

ModARO offers a relevant pattern: extractors with declared input requirements enrich model entities, and separate linking combines facts. Its evaluation concerns microservices, not arbitrary React/Next behavior. Adopt typed extractor prerequisites and explicit model/linker stages. Do not adopt unrestricted third-party extractor execution. [ModARO](https://arxiv.org/html/2602.08181v1).

## Executed provider experiment

I installed **Jelly 0.13.0** only under `output/research/tsjs-core-reset/jelly-pilot`, with npm install scripts disabled. I ran its static analyzer on the 412 file paths from our existing public GitDiagram result. No submitted package installation/build, approximate interpretation, dynamic tracing or application execution was used. Flags and outputs are preserved in `jelly-run.json`, `jelly-diagnostics.json` and the stdout/stderr logs. Production dependencies were not changed.

| Pilot result | Measurement / qualification |
|---|---|
| Wall time | 11.344 seconds for this one run |
| Tool-reported maximum memory | 441 MB; not an independently sampled process-tree peak |
| Analyzed modules | 411; the extra input in our graph is `workers/presence/src/env.d.ts` |
| Analysis warnings | 801; environment/module resolution requires audit |
| Completion state | **Partial: indirection limit reached**, although exit status is zero |
| Matched function declaration start positions | 3,174 |
| Compared unique caller/target pairs with both endpoints matched | Ours 1,466; Jelly 2,011 |
| Shared pairs | 1,388 |
| Additional Jelly candidates in that matched subset | 623 |
| Pairs present only in ours in that matched subset | 78 |

These are not precision, recall, newly confirmed relationships or directly comparable total callsite counts. Function position normalization excludes unmatched locations and module/synthetic differences. Our canonical IDs, callback vocabulary and source evidence must not be discarded in a merge. Jelly also attempted to resolve packages above the snapshot directory, then reported them skipped outside its base directory: production adoption requires a snapshot-only resolver, not its default host resolution.

Source inspection of three pilot differences illustrates both benefit and risk:

- `withEdgeAnswers` invokes the supplied `app` function; the candidate linking its nested `fetchAndKeep` function to the `handler.fetch` wrapper in `cloudflare/worker.ts` is supported by the source argument and invocation. This is a multi-boundary function-flow case beyond our narrow local summary.
- The candidate from the relay `alarm` method to the callback passed to `jobs.map` is supported by the standard array callback contract. Our current callback adapter does not model array methods.
- A self-call candidate in `cloudflare/outgoing-fetch.ts` is suspect: that file captures `globalThis.fetch` before overwriting it. A flow-insensitive solver can conflate the earlier capture and later assignment. This candidate needs flow-sensitive handling and must not become a confirmed recursive call.

**Decision from the experiment:** Jelly is worth a constrained adapter/benchmark, and it already exposes useful missing patterns. It is not a drop-in replacement or proof of a better final architecture. Preserve ours as a complementary provider; validate additional candidates and reconcile module contexts. The next provider evaluation must include negative fixtures for global overwrites, callbacks, receiver aliasing and factory contexts.

The reproducible pilot and comparison scripts are `scripts/research_jelly_pilot.py` and `scripts/compare_jelly_pilot.py`. Raw comparison data is `output/research/tsjs-core-reset/provider-comparison.json`. The scripts run only the public pinned research input and do not modify production graphs.

## Concrete processing design

```text
Immutable ZIP snapshot and declared project contexts
  → compiler facts: symbols, imports, assignments, calls, properties, returns
  → bounded value/function-flow graph and reusable summaries
  → framework/client semantic models
  → operation facts: exposes route, invokes callback, calls API, reads/writes resource
  → resource and destination reconciliation
  → entry-point capability slices and shared implementation membership
  → evidence-backed architecture model
  → overview / request-workflow / implementation views
```

The evidence graph remains the canonical record. Architecture entities are derived claims with original member IDs and complete supporting paths. A second database technology is unnecessary for this design.

### Flow layer we need

Represent a bounded set of possible values: function identities, object allocation identities, module-export identities, literals, symbolic configuration references, and unknowns with reasons. Emit constraints for assignments, parameter/argument flow, returns, object property reads/writes, imports/exports and awaited supported Promise values. Process a worklist until stable or an explicit budget is exhausted.

Use allocation-site object identities so unrelated `client.send` properties are not merged solely by name. Separate call contexts where needed so two factories with different configuration arguments do not become one proven resource. Model cached `??=` initialization as alternatives, not an automatic blanket rejection and not an unconditional constant. Start with targeted summaries around architecture-relevant operations; full heap/path sensitivity is not the first milestone.

The compiler remains responsible for binding and project resolution. A flow provider adds possible implementation/receiver candidates; it does not overwrite compiler facts or assert runtime execution. Preserve candidate sets and distinguish unknown from an empty set. Do not represent a type declaration as a concrete local implementation.

### Architecture models we need

Separate source package, runtime/deployment boundary, capability, client instance, declared resource and external system. A source folder is ownership evidence; it does not create a service.

Start capability slices from entry points, public operations and recognized resource/API boundaries. Follow supported direct/callback relationships. Use shared membership when helpers serve multiple capabilities. Derive conservative labels from route groups, exported interfaces and supported operations; allow explicit user labels as annotations. Do not claim deterministic recovery of a unique business interpretation.

Keep cross-boundary resource/API operations when collapsing helpers. A derived capability edge must carry the original supporting path, not just the two groups' names. Rank overview entities by architectural role and boundary significance, then apply a visible node budget. Deeper views retain omitted details. Use existing ELK/ReactFlow; layout changes cannot compensate for absent resource or capability facts. LikeC4's model/view separation is a useful design reference, not a required dependency. [LikeC4 views](https://likec4.dev/dsl/views/).

## Tool decisions

| Tool/technology | Decision | Concrete role |
|---|---|---|
| TypeScript Compiler API | Keep | TS/JS syntax, bindings, project/module resolution; no claim it alone supplies complete value flow |
| Jelly | Isolated static pilot | Compare receiver/function/callback flow on the same source scope; no production adoption before measured benefit |
| Custom flow summaries | Build/refactor | Framework callbacks, symbolic config and targeted resource/client operation chains |
| dependency-cruiser | Comparison reference | Import/module-resolution checks, not workflow inference |
| Knip | Reuse documented conventions selectively | Entry discovery patterns; do not execute its config-loading plugins against client code |
| Joern | Alternate provider if pilot evidence warrants | CPG/flow comparison; no immediate rewrite or assumption its TS support resolves our architecture |
| CodeQL | Optional benchmark subject to terms | Demand-driven flow/library-summary reference |
| Semgrep | Targeted recognizers where useful | No assumption its general dataflow supplies object/whole-repository architecture recovery |
| Syft | Remains deferred | Inventory/SBOM, not source relationship resolution |
| SQLite / current evidence graph / ELK | Keep | Persistence, provenance and bounded visual projections |

Knip explicitly documents dynamic configuration loading; borrow inert conventions rather than assuming its full pipeline is execution-free. dependency-cruiser's documentation distinguishes module relationships from a complete behavioral model. Joern documents configurable TypeScript/type propagation. Semgrep documents path/alias limitations in its general dataflow engine. [Knip](https://knip.dev/explanations/plugins), [dependency-cruiser](https://github.com/sverweij/dependency-cruiser/blob/main/doc/faq.md), [Joern](https://docs.joern.io/frontends/javascript/), [Semgrep](https://docs.semgrep.dev/writing-rules/data-flow/data-flow-overview).

## First integrated acceptance slice

Use GitDiagram's generation route, but freeze source-backed expected claims before changing extraction. Validate these separately:

1. Route → admission → repository-context capability.
2. Context → model operation → graph validation/compilation capability.
3. Finalization → artifact operation → logical R2 bucket reference.
4. Admission/quota operation → Redis coordination/configuration reference.
5. Root overview represents these capabilities and resources with inspectable supporting paths; workflow expands their functions and conditional callbacks.

For R2, the source includes `s3ModulePromise ??= import(...)`, an awaited module, a cached constructor, an async returned `{client,s3}` object, renamed destructuring, `send(new ...Command(...))`, helper-supplied bucket arguments and symbolic environment reads. The current direct-client adapter does not cover this chain. A succession of special cases is not the chosen long-term fix: these are concrete transfer/summarization requirements for the flow layer plus an S3 command model.

Recover a logical resource keyed by symbolic bucket/configuration evidence when its deployment value is unavailable. Do not invent the account, bucket value or cloud deployment. Similarly, a fetch URL derived from an environment helper remains symbolic until supported config resolves it; a Redis label requires bound operation/config evidence.

## Delivery gates and order

**First: architecture contract and provider comparison.** Compare the existing provider and Jelly on fixed source scope and negative fixtures. Publish missed and spurious relationships by category, parse/module coverage, timeout/partial state, latency and memory. Matching location formats is part of the adapter. Never import every candidate edge into production.

**Second: one real resource chain plus capability projection together.** Make the generation/artifact path visibly appear in the architecture with evidence. The next delivery must include a generated before/after diagram and a claim scorecard, not just a test count. A missing precise bucket value does not block identifying a supported logical storage interaction.

**Third: coordination and separated frontend/backend paths.** Add symbolic configuration and destination-aware HTTP resolution. Keep branch/callback/deferred conditions visible. Resource linkage and capability grouping must both consume the improved facts.

**Fourth: independent TS/JS fixtures and repositories.** Evaluate Next/SSE, Express mounted routers, React with separate API, workspace exports and JS workers. Use hand-reviewed positive and negative claims; include an unfamiliar holdout. Declare supported profiles before scoring. Do not silently exclude a failing construct after evaluation.

Proposed release targets remain ≥95% precision and ≥90% recall on agreed critical supported claims, reported per category with sample sizes and abstentions. They are goals, not measured current quality. Also measure whether a newcomer can identify the major parts and one request path from the first view. Benchmark capacity separately; the existing single-repository timings do not establish enterprise readiness.

## What this research does not establish

No paper establishes a universal, exact static architecture for every TS/JS program. No candidate has yet been proved superior on our benchmark merely by being installed. A successful call-graph extraction is not successful architecture reconstruction. Nevertheless, the implementation gaps above are concrete, and the proposed bounded-flow plus architecture-model design gives us a testable path beyond incremental syntax patches.
