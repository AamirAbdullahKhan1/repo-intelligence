# TS/JS architecture reconstruction: readiness and workflow comparison

Assessed 3 November 2026 against saved GitDiagram snapshot `8f4203a9ed5d5c620afe9bf1cbdaa0ba234db221ef1183cf30808acd072ff38b` and source text from its existing verification ZIP. This assessment changed no application code and executed no submitted application.

## Assessment

The platform has a useful extraction/evidence foundation and a clearer presentation. It does not yet reliably reconstruct the application-level workflow in the supplied diagram. Expanding semantic support to additional languages now would carry unresolved analysis problems into more providers.

The attached diagram describes one workflow, POST /api/generate/stream. A fair comparison therefore includes the platform's workflow for that exact route, rather than comparing only its broad system overview.

The supplied diagram is a manually curated source interpretation. It should be checked as a set of architectural claims, not treated as a guaranteed runtime trace. Cancellation, failures, deadlines and deferred operations affect its apparent ordering. The earlier manual assessment also explicitly qualified persistence/terminal-output ordering and post-response completion.

## What is currently established

| Capability | Current evidence | Confidence boundary |
|---|---|---|
| Source parsing | 412 source files, zero syntax failures | Selected scope only; parser success is not semantic completeness |
| Local call binding | 4,417 implementation-body bindings | Supported direct static bindings, not runtime reachability |
| Standard APIs | 63 trusted library files; 6,989 preserved library references | Declaration/signature identity, not local runtime bodies |
| Route records | 50 routes; reference POST route found and linked to its handler | No independent all-routes recall measurement |
| Client-to-route matching | Eight conditional relationships | Narrow same-package Next client patterns |
| Resource linking | Direct R2/pg/redis fixtures pass | Zero concrete resource-use links on this GitDiagram snapshot |
| Interpretation | 11 technical role groups; focused 10-node overview | Broad API/AI/payment/email roles, not recovered domain components |
| Engineering verification | Latest recorded suite: 83 backend tests; frontend/browser acceptance passes | Regression and usability-function checks, not an architectural accuracy benchmark |

Remaining unknowns are 3,311 call records, 53 imports and 60 HTTP records. They are different questions and can overlap at a source callsite. Their sum is not a count of incorrect architecture arrows.

## Exact comparison with the supplied workflow

I checked whether named implementations are extracted and whether they can be reached from the route through recorded HANDLED_BY/CALLS/CONSTRUCTS and supported integration edges. An expanded depth-12 audit was used to avoid confusing the ordinary UI depth limit with a missing connection.

| Reference workflow stage | Representative extracted implementation | Present as a symbol? | Connected from route without lexical-containment expansion? |
|---|---|---|---|
| Request entry | POST | Yes | Yes |
| Credentials/admission/rate limits | admitGenerationRequest | Yes | Yes |
| GitHub metadata/tree/README | getGithubData | Yes | No |
| Prepare/select repository context | prepareRepositoryContext, fetchSourceContext | Yes | No |
| Estimate cost and reserve quota | estimateGenerationCost, admitComplimentaryQuota | Yes | No |
| Model streaming | streamCompletion | Yes | No |
| Structured graph generation/validation orchestration | generateValidatedGraph | Yes | No |
| Graph compilation | compileDiagramGraph | Yes | No |
| Session/finalization orchestration | finalizeGenerationStream | Yes | No |
| SSE writer construction | createGenerationSseWriter | Yes | No |

This verifies presence of particular functions, not recovery of the meaning of every reference block. For example, finding finalizeGenerationStream does not prove the complete persistence/terminal-order interpretation.

The actual UI projection at depth 6 and node limit 80 contains 57 nodes and 67 edges and is truncated. Raising limits does not supply the missing semantic links. It mainly expands admission/cancellation/helper relationships.

The source places the main work in this structure:

```text
POST handler
  → constructs ReadableStream
      → supplies a start(controller) callback
          → declares and calls run()
              → repository/context/model/graph/finalization work
```

The graph records lexical containment of nested functions and many calls inside them. It does not model the ReadableStream callback contract as an invocation/registration relationship. Adding CONTAINS_SYMBOL to the audit makes all the listed functions reachable, but lexical containment alone cannot establish invocation. Enabling that toggle everywhere would include unused nested functions and is not a valid semantic fix.

The [ReadableStream documentation](https://developer.mozilla.org/en-US/docs/Web/API/ReadableStream/ReadableStream) defines the start callback behavior. [Next.js after](https://nextjs.org/docs/app/api-reference/functions/after) supplies a separate deferred callback contract. These contracts can support narrow, versioned static models while retaining conditions and distinguishing them from ordinary direct calls.

Machine evidence: [stage audit](../../output/reviews/tsjs-readiness-2026-11-03/generation-workflow-audit.json) and [actual UI projection](../../output/reviews/tsjs-readiness-2026-11-03/actual-ui-workflow.json).

## Persistent gaps, in priority order

### 1. Callback registration and parameter flow

The engine understands direct implementation calls better than callbacks supplied to runtime/framework APIs. ReadableStream.start is an immediate blocker for the reference workflow. Promise executors, event handlers, after callbacks and helper functions receiving callable arguments require similarly explicit contracts or bounded callsite analysis.

**Fix:** add typed registration/possible-invocation relationships using compiler/import identity and allowlisted API models. Distinguish immediate, event-triggered and deferred callbacks. Reject shadowed/lookalike APIs and unsupported argument shapes. Do not turn every nested definition into a call.

**Proof required:** the route reaches its stream callback and main processing functions through these supported relationships, with constructor/registration and callback evidence. Unused nested functions remain disconnected.

### 2. Values and returned objects across helper boundaries

Useful facts are lost across configuration helpers, returned object properties, destructured clients, wrapper callbacks and selected dynamic imports. Reassignment is conservatively rejected rather than resolved at the point of use. Some source interface signatures also lack an established concrete implementation.

**Fix:** bounded function summaries, symbolic configuration references and selected object/alias propagation. Model branch alternatives, invalidation and analysis limits. Avoid whole-program interpretation or guessed values.

**Proof required:** follow a helper-produced client/configuration through a real operation and retain its evidence chain, including negative mutation/branch cases.

### 3. Resource and external-integration destinations

Recognizing S3 or Redis-related source areas is not the same as linking an operation to a configured resource. GitDiagram's R2 wrapper uses dynamically imported SDK objects and returned/destructured clients; its Redis wrapper builds HTTP destinations through environment helpers. Current direct resource rules do not recover those chains.

**Fix:** use the bounded summaries above to connect operation → receiver/client → configuration reference → resource declaration or explicitly unresolved destination. Keep declared infrastructure separate from used resources and actual deployment state.

**Proof required:** recover at least the diagram-artifact persistence and quota/coordination chains, or report exactly which destination step is unknown. Naming every get/set receiver as Redis would be incorrect.

### 4. Capability/component boundaries and meaningful names

The role pass recognizes technical categories. It does not establish cohesive components such as Repository context collection, Diagram generation or Graph validation/compilation. It also collapses unrelated endpoints into broad API handling. Most eligible code entities remain in Other analyzed source.

**Fix:** derive entry-point-centered capability slices from supported operations and interactions, retain shared helpers as shared membership, then assign conservative labels from routes, interfaces and recognized operations. Domain naming follows justified grouping; renaming a directory-shaped box is insufficient.

**Proof required:** each component maps to its actual entry points and implementation members. Moving a helper to another folder should not arbitrarily change its responsibility. Conflicting/multiple roles remain inspectable.

### 5. Workflow abstraction, branches and order

A call graph has no complete control-flow or data-flow semantics. The reference includes admission failures, retries, alternative graph generation, terminal outcomes and deferred work. The current workflow view is bounded traversal, not synthesis of those stages or paths.

**Fix:** introduce stage projections backed by call/registration facts and narrowly supported control-flow conditions. Distinguish conditional branches, loops and deferred work. Keep failure paths alongside a clearly labelled main-path summary.

**Proof required:** grouped stages retain exact supporting functions/edges and do not imply unconditional order, especially across callbacks, cancellation and post-response work.

### 6. TS/JS project and framework support remains selective

Nearest-config selection is not full project membership/reference semantics. Workspace pattern support is limited; pnpm-only declarations and several patterns are not yet supported. Missing external typings limit receivers. Next route wrappers/catch-all/proxy/context rules and Express router mounts/middleware remain partial. Parsing TS/JS does not establish semantic support for every framework using those languages.

The 53 import warnings additionally need classification: 41 present stylesheets, nine generated OpenNext outputs, two platform virtual imports and one external subpath. These should not all be described as missing application code.

**Fix:** maintain an explicit support matrix with fixtures and version/context limits. Model assets/platform/generated boundaries without running builds or installing client dependencies.

### 7. Precision, recall and capacity are not yet demonstrated

Source citations and passing tests are necessary but insufficient. We have no independently reviewed multi-repository benchmark establishing component/connection recall, false-positive rate or enterprise capacity. The scan has explicit file/byte/time/heap limits.

**Fix:** evaluate component and relationship claims independently on fixed commits and supported profiles. Separate abstentions, unsupported constructs and missed supported cases. Measure resource use and latency under a published envelope.

## What must be proved before adding another language

I recommend holding additional language-provider implementation until this gate is met:

1. **Reference workflow:** the POST route connects through the supported stream callback to repository collection, model work, graph validation/compilation and finalization. Each grouped stage has evidence and explicit conditions; lexical containment is not used as invocation proof.
2. **Resource chains:** establish an inspectable application-operation → client/configuration → resource chain for supported storage and coordination patterns, including wrapper and negative fixtures.
3. **Independent repositories:** review at least five pinned TS/JS repositories/profiles, including unfamiliar projects: Next/SSE, Express mounted routing, separated frontend/backend, a workspace monorepo and a JS worker/library case. Publish what is actually supported.
4. **Measured quality:** proposed initial targets are at least 95% precision and 90% recall on the agreed supported critical relationship set, reported per relationship category with actual sample sizes and abstentions. These are proposed gates, not current scores or universal guarantees. Unsupported declarations cannot be used to quietly shrink the benchmark after evaluation.
5. **Stable output and user understanding:** repeated identical inputs/settings produce identical semantic artifacts; saved evidence reopens; a newcomer can identify major responsibilities, resources and one request path without navigating hundreds of nodes.
6. **Honest limitations:** unresolvable external values, reflection, generated code and runtime-selected behavior remain explicit unknowns. Runtime completeness is outside the static product claim.

Passing this gate for a defined TS/JS support envelope is a sound basis for adding another language. Waiting for every dynamic program to be fully resolvable is not a realistic gate.

## Immediate recommendation

The highest-value next step for this particular comparison is **callback-aware workflow reconstruction**, beginning with ReadableStream.start and a supported deferred callback model. Then follow the configuration/client wrappers needed for storage and coordination. Use those recovered chains to derive capability groups and labels.

The compiler-library repair was real and useful: it reduced unresolved call records from 10,301 to 3,311 on the same 412-file scope. It did not fix callback invocation, resource linkage or domain architecture synthesis. The current system is a tested foundation with selective semantic recovery, not yet a validated general TS/JS architecture reconstruction engine.
