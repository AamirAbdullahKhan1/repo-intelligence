# Callback and helper-value reconstruction — 4 November 2026

The TS/JS analyzer now connects supported callbacks without treating every nested function as invoked. Customer source remains parse-only; no new tools, model calls or customer dependency installation were introduced.

## Implemented

- `MAY_INVOKE_CALLBACK` is a separate, conditional canonical relationship. Workflow queries follow it within existing depth, node and edge budgets. The UI labels it “Possible callback invocation”; evidence retains the API, registration site, implementation and limitations.
- Bound compiler standard-library identities support `ReadableStream.start`, Promise executors, timers, microtasks and typed EventTarget listeners. Bound `next/server` imports support aliased `after`. Local shadowing and indexed reassignment invalidate these models.
- Local implementation summaries recognize direct invocations of function parameters and properties of identifier parameters. The actual callback argument is connected at each caller, with evidence of the invocation inside the helper. Different callers' callbacks are not pooled. Unused properties and nested definitions are not promoted into calls.
- A bounded expression resolver follows immutable local/imported initializers, object properties, renamed object destructuring, straight-line helper returns and simple positional arguments. It rejects branching value-return helpers, async value summaries, spreads, computed object properties, recursion beyond the bound and indexed writes.
- SDK identity tracking consumes these summaries. Same-identity SDK returns can retain package-level usage across alternatives; this establishes neither a concrete remote endpoint nor successful delivery. The old factory-wide origin cache was removed to avoid reusing argument-dependent results across calls.
- PostgreSQL/Redis resource recognition can follow supported returned/destructured clients and helper-supplied connection options. URL evidence can originate in a different file and is cited against that file.

## Verification

Backend regression suite: **88 passed**, with the two existing warnings. Frontend TypeScript check and production build passed. Five focused tests cover callback contracts, shadowing, unused nested functions, caller separation, SDK object destructuring, cross-file configuration, parameterized database options, mutation rejection and deterministic repeated analysis.

`scripts/verify_callback_snapshot.py` runs the trusted static analyzer on the existing GitDiagram ZIP and writes the canonical graph, summary, workflow and measured results under `output/callback-values-review`. It does not execute GitDiagram.

The previously disconnected generation route now reaches all twelve checked stage functions: admission, GitHub fetching, repository context, source context, cost estimate, quota admission, model streaming, graph validation, Mermaid compilation, finalization, SSE writer and session audit. The final machine-readable measurements are in `verification.json`. Reachability uses supported calls and conditional callback relationships, with no lexical-containment edges.

The final GitDiagram run took **38.9 seconds** (one local run, not a capacity benchmark), extracted **191 conditional callback relationships**, and preserved **4,417 compiler-resolved implementation calls**. SDK-use classifications changed from 23 to 17 under the stricter origin handling. The normal 80-node, depth-six generation workflow returns 70 nodes, including eight callback edges, and correctly marks the result truncated. A fresh saved result (`d35bbceee8a9…`) was added to the application's history without deleting historical scans. The running API returns the new callback relationships.

## Remaining limits

- This is bounded static reachability, not a guaranteed execution sequence or proof that every branch runs. Local callback summaries do not yet model arbitrary callback forwarding, captured registration, array-held tasks or multi-hop parameter aliases.
- Callback registration does not prove cancellation, delivery, frequency or completion. Only `ReadableStream.start` is modeled here; pull/cancel and arbitrary stream implementations need their own contracts.
- Value summaries are not whole-program points-to or reaching-definitions analysis. Object mutation through arbitrary aliases, external side effects, dynamic property access, async factories, environment-specific values and complex wrapper lifecycles remain incomplete.
- The GitDiagram snapshot still yields **zero concrete resource-use links**. Synthetic supported PostgreSQL/Redis patterns pass; this must not be described as completing GitDiagram's S3/R2/Upstash wrapper analysis.
- Conservative checks change SDK classifications. Counts are not accuracy scores; removed classifications should not be mistaken for lost compiler calls. The compiler implementation-call count is preserved.
- The default bounded workflow can still truncate. All twelve stages being reachable in the audit does not mean all fit in its initial 80-node view. Capability-level workflow abstraction remains separate work.
- Enterprise capacity and architecture precision/recall across independent repositories remain unproven. New language expansion should wait for the remaining TS/JS resource and grouping validation.
