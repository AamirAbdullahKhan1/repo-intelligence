# Repo Intelligence: progress explained in plain language

Status: 4 November 2026. Based on implemented code and saved GitDiagram result `b9306863eb1c…`. This is a progress report, not a claim of enterprise readiness.

## What we are building

The platform takes a GitHub repository or ZIP and tries to draw a trustworthy map of the application: its major responsibilities, how they connect, and which databases, storage systems and outside services they use.

It reads the source without starting the submitted application. The current analysis pipeline does not send source to AI models or install the submitted project's dependencies. Every reported connection should have a reason that the user can inspect.

Think of examining a building's plans to reconstruct its layout. We can identify doors, rooms and wiring from the plans. We cannot establish exactly which doors people used yesterday, or what equipment was installed outside the supplied plans.

## Where we began, and why progress felt slow

We began by discovering files, parsing TS/JS, identifying functions and imports, and recording relationships. This produced a large code map. Initial grouping relied heavily on source ownership and folders, and the diagram was too crowded.

We then added clearer views, source citations, improved project resolution, route discovery, selected API matching and direct resource rules. Later grouping used broad categories such as API handling and AI integration. These were technical roles rather than reconstructed application features.

The central mistake in our progress assessment was treating more extracted connections as equivalent to a better architecture. They are different achievements. Before the latest work, 4,620 of 4,754 eligible file/function/endpoint entities remained in Other analyzed source. That was a grouping limitation, not 97% parsing failure. The overview hid much of this material to remain readable, so extraction improvements often made little visible difference.

We now have a separate, early architecture-reconstruction pass. It follows public routes into their implementations, allows shared helpers, and retains paths to supported operations. Its current labels describe route-based responsibilities; it does not automatically recover every business concept.

## What happens behind the scenes now

1. **Receive and freeze the source.** Check the input and make a consistent snapshot, so the analysis and citations refer to the same version.
2. **Read the language structure.** Use TypeScript's compiler machinery to recognize declarations, imports and supported calls. Parsing means reading the grammar, not running the code.
3. **Follow supported connections.** Resolve local calls, framework routes and selected callbacks. A callback is work passed to another function to invoke immediately, later or when an event happens.
4. **Follow selected values through helpers.** The new bounded-flow subsystem tracks objects, returned clients, arguments and symbolic configuration. It repeatedly revisits affected relationships when it learns something new, stopping at explicit limits. Its first production consumer is S3-compatible storage analysis, not every TS/JS operation.
5. **Identify resource operations.** Establish that a bound storage client performs a supported operation and trace its bucket argument. Knowing an SDK is imported is insufficient.
6. **Build architecture slices.** Follow supported paths from routes, collect their implementation members, and summarize supported resource and integration relationships. A helper can belong to multiple slices.
7. **Present and explain.** Show a bounded overview, with deeper workflows and code in separate views. Selecting a relationship exposes source locations and, where available, paginated value-flow evidence.

“Deterministic” means identical source, settings and analysis versions should produce identical semantic output. It does not mean the output is automatically complete or correct.

## Tools actually in use

| Technology | Plain-language job |
|---|---|
| TypeScript Compiler API 5.9.3 | Reads TS/JS and supplies symbols, signatures and module resolution |
| Node.js trusted worker | Runs our analyzer separately from the Python backend; it does not run the submitted application |
| Custom JavaScript analysis modules | Framework/callback rules, value flow, selected client operations and provenance |
| Python and FastAPI | Handle ingestion, analysis jobs, API requests, interpretation and validation |
| Pydantic | Checks that exchanged graph records have the expected structure |
| PyYAML and inert JSON/configuration readers | Read supported configuration declarations without executing configuration files |
| SQLite | Saves jobs, analysis graphs and history |
| React and TypeScript | Build the user interface |
| React Flow | Provides the interactive diagram |
| ELK.js | Calculates diagram layout |
| Vite | Builds and serves our frontend during development |
| pytest and Playwright browser checks | Check backend behavior and important UI flows |

The graph is a stored collection of entities and typed connections. We do not currently need a separate graph database.

Jelly 0.13.0 was installed and tested in an isolated research folder. It is not integrated into production. It found useful additional candidate connections, but also needs accuracy and filesystem-resolution review. Its execution-based modes are outside our current approach.

CodeQL, Joern, dependency-cruiser, Knip and Semgrep have informed the research; they are not all active analysis stages. Syft remains a future software-inventory/SBOM option, not a function-relationship resolver. We are not running every researched package or using a local AI model in this pipeline.

## Measured progress on GitDiagram

| Result | Meaning |
|---|---|
| 412 source files parsed | The selected TS/JS source scope was read; not the entire inventory being understood perfectly |
| 4,417 compiler-bound implementation calls | Recorded call sites linked to local implementations; not 4,417 unique functions |
| 6,989 standard-library references | Known language/library calls kept separate from missing application implementations |
| 191 callback relationships | Supported possible callback connections; not guaranteed executions |
| 24 contextual resource claims | Ten distinct operation/destination pairs, kept separate where caller context differs |
| Two symbolic storage references | Public/private bucket configuration keys; actual deployed bucket/account values remain unknown |
| 19 route-based capability slices | Implementation grouped around known public interfaces rather than only folders or broad roles |
| 15 overview nodes and 17 edges | A bounded view; additional slices remain available and omissions are reported |
| Twelve checked generation-stage functions reachable | Selected GitDiagram stages connect through supported relationships; not proof of a complete runtime sequence |

The recovered path can now connect the generation request, stream callback, finalization, artifact helpers and storage operations. That is a meaningful end-to-end improvement beyond recognizing an isolated SDK import.

## How efficient and reliable is it?

**Speed:** one full GitDiagram run took about 42 seconds for the 412-file source scope. This is a useful local observation, not a general promise for other repository sizes.

**Work performed:** the new storage flow analysis required 849 tracked value locations and 848 dependency steps on this snapshot. It completed without exhausting its own budgets. Demand-driven analysis avoids trying to propagate every value everywhere.

**Repeatability:** a repeat of the full pinned input produced byte-identical canonical graph output.

**Engineering checks:** 98 backend tests passed. Frontend build and browser checks passed, including evidence inspection and reopening the saved scan. Tests show covered behaviors work and help prevent regressions; they do not measure whole-repository architecture accuracy.

**Accuracy:** no defensible overall percentage has been established. The proposed targets are at least 95% correct reported critical relationships and recovery of at least 90% of agreed expected critical relationships, measured on defined supported profiles. These remain goals.

**Enterprise scale:** not demonstrated. The worker currently has limits including a 4,000-entry inventory cap, 32 MiB parsed-text budget, 120-second deadline and 1,536 MiB Node heap cap. Upload limits are separate. A repository can reach a cap because of non-source files too. Limits protect the service; they do not prove scalability. Full analysis memory and concurrent-client capacity have not been benchmarked.

## Limitations and how we plan to address them

| Limitation | Plain-language explanation | Planned response |
|---|---|---|
| Incomplete resource coverage | The newer flow mechanism mainly handles supported S3-style storage paths; complex Redis/DB wrappers remain | Extend the shared flow and operation models to coordination and database paths |
| Selective framework support | Reading JavaScript does not automatically explain every framework's conventions | Add version-scoped models with independent positive and negative examples |
| Some values remain unknown | Helpers, branches, object mutation, dynamic keys and external code can hide the destination | Improve targeted propagation and mutation handling; retain alternatives or abstain |
| Limited architecture meaning | Route slices do not yet identify every business capability or worker boundary | Combine entry points, operations and resource relationships; use neutral labels where meaning is uncertain |
| Incomplete workflow ordering | A call graph does not establish branch order, retries or parallel completion | Add supported control-flow and stage models while keeping deferred/event work distinct |
| Missing deployment context | Code may refer to configuration supplied elsewhere | Preserve symbolic configuration and reconcile it with supplied declarations; do not invent deployment values |
| Unresolved records | Current result retains 3,311 call, 53 import, 60 HTTP and four resource unknown records | Classify causes and prioritize those blocking important architecture paths rather than chase a zero count |
| Insufficient independent validation | GitDiagram and synthetic examples are not enough to prove generality | Freeze independent repository profiles, review expected claims and test an unfamiliar holdout |
| Capacity and isolation not production-proven | Local safety guards and bounded jobs are not a complete enterprise execution boundary | Measure peak memory/concurrency and strengthen OS-level isolation before deployment claims |

The unresolved counts are not all missing imports or incorrect arrows. They include external implementations, generated/platform references, assets and patterns not yet understood. Likewise, a valid source citation proves where evidence came from; it does not by itself prove our interpretation is right.

## Where we stand and what comes next

We have a functioning static-analysis foundation and the first integrated example of following values into resources and presenting the result through a separate architecture layer. We are past a folder-only map, but we do not yet have a generally validated TS/JS architecture-recovery product.

The next useful work is Redis coordination and richer operation/workflow interpretation, using the same flow/provenance foundation. Validate on Next/SSE, Express mounted routing, separated frontend/backend, workspaces and Workers, plus an unfamiliar holdout. Measure wrong connections, missed expected connections, evidence completeness, speed and memory separately.

Each subsequent delivery should show a before/after architecture and a reviewed claim scorecard. Increasing rule counts or producing a fuller diagram is insufficient.

## A short explanation you can give someone else

“Our platform reads a repository without running the application and builds a source-backed map of how its parts connect. It combines compiler information, controlled framework rules and bounded value tracking, then summarizes the evidence into architecture views. We now recover selected TS/JS request and storage paths, but broader framework coverage, business-level grouping and independent accuracy/scale validation are still in development.”
