# Final technical understanding

Date: 2 November 2026. Conclusions synthesize the individual reports; recommendations are not implemented features or measured superiority claims.

## 1. How do these systems reconstruct architecture?

They solve different portions of the task. RepoDNA parses syntax, heuristically resolves links and groups files into roles. Understand documents a persistent entity/reference model with configurable groupings. Joern enriches code into semantic graph layers. CodeSee documents interactive dependency/review maps. GitDiagram asks a model to interpret bounded context. Sourcegraph indexes symbols/occurrences for navigation. StructSAR groups files after learning from dependency structure.

There is no common hidden algorithm that already solves source-to-application architecture completely. Their strongest reusable pattern is separating analysis facts, aggregation/interpretation, and presentation.

## 2. Which techniques are effective for code understanding?

Compiler binding is stronger than matching terminal names for supported constructs. Syntax trees enable broad extraction but do not independently establish receiver identity. Control/data-flow stages support value reasoning; framework/library models supply conventions a language parser cannot know. Configuration and API declarations contribute context but not runtime observations.

Finding `import`, locating a file, identifying a call, binding its implementation, and assigning it to an application workflow are distinct achievements. Our tests and coverage should distinguish them.

## 3. Which techniques fit our constraints?

Retain compiler analysis through a snapshot-contained host, inert configuration parsing, language-specific static rules and bounded value propagation. Normalize facts and derive cross-source claims explicitly. Trusted, preinstalled analyzers may run; submitted application code, plugins, package scripts and builds may not. Runtime trace labels and deployment claims must reflect what source can actually establish.

## 4. What does RepoDNA do particularly well?

It connects analysis artifacts to understandable exploration: technology/inventory outcomes, routes, bounded static flow views, unresolved information, role-oriented architecture and exports. Its separate browser/public/Python paths show practical product engineering.

Its inspected heuristic call resolution and category-based architecture are not evidence that it has solved our semantic gaps better. We should adopt useful coverage/navigation patterns while retaining stronger compiler identity and improving resource/context linking.

## 5. What should we learn from Understand and Joern?

Understand: one parsed reference model can serve many abstraction levels while retaining exact supporting references. Architecture groupings can be distinct from folders and from facts.

Joern: enrich incrementally through explicit passes, typed relationships, prerequisites and analysis budgets. Model unknowns/omitted flow rather than treating parser success as completeness. We need selected value facts and derivations before a full CPG or new graph database.

## 6. What should we learn from CodeSee and GitDiagram?

CodeSee: focused visibility, collapsed groups and code navigation make dense information usable. GitDiagram: a deliberate high-level graph contract and deterministic diagram compiler help produce a coherent answer-first artifact.

Those are presentation lessons, not source-correctness guarantees. Keep them secondary to our foundation work. A clickable path or attractive connected graph is insufficient verification.

## 7. What should we do differently?

Keep facts, derived claims and user groupings distinct. Preserve full source/configuration support, project/profile/runtime context and resolution status. Avoid uncalibrated percentages, global name guesses, service-by-folder inference, unbounded tool additions and silent graph compaction. Offer a supported application view when infrastructure is missing rather than invent cloud boundaries.

Evaluate communication/resource edges separately from grouping. Treat source/contract disagreements and unknown destinations as meaningful findings. Additional languages need dedicated semantics and tests, not just another parser registration.

## 8. What should we build next?

First fix the demonstrated stale-value, source-exclusion and root-route cases. Then strengthen project-aware symbol resolution and bounded value/configuration tracking. Use those facts to link one complete route-to-client-to-resource chain. Add semantic responsibility interpretation once those connections are trustworthy.

The next proof is a correct, inspectable end-to-end chain on small positive/negative fixtures, an unfamiliar repository and GitDiagram—not another infrastructure layer. See the [prioritized proposal](improvement-proposal.md) for acceptance criteria and [comparison](comparison.md) for limits on the evidence.
