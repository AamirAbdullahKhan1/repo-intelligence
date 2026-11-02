# Joern: rich code graphs and analysis passes

Date: 2 November 2026. Source: `joernio/joern@0738a6199bc860a788b7f28b2779997f210c405d`. Selected implementation files were read; Joern was not installed, built or run. **Verified** means inspected source/specification; performance and exact runtime behavior remain untested. [Workflow](workflows/joern.mmd).

## Product and input

Joern is a queryable code-analysis platform, particularly for program/security investigation, not an automatic application-architecture diagrammer. Input depends on a selected language frontend; some frontends consume source while others use different representations. Output is a Code Property Graph (CPG), enriched analysis layers, query results and optional exports.

**Documented:** frontends share X2CPG infrastructure, but support and options differ. The default frontend-selection heuristic can choose the language with the most supported files; it is not a full polyglot orchestration strategy. A common graph schema is not automatic cross-language call resolution. [Frontends](https://docs.joern.io/frontends/).

## JS source processing: verified execution path

[`JsSrc2Cpg.scala`](https://github.com/joernio/joern/blob/0738a6199bc860a788b7f28b2779997f210c405d/joern-cli/frontends/jssrc2cpg/src/main/scala/io/joern/jssrc2cpg/JsSrc2Cpg.scala), `createCpg`, creates an empty graph and temporary output, invokes `AstGenRunner.execute`, computes an input hash, applies `AstCreationPass`, then type-node, metadata, dependency, configuration, private-key-file and import passes. It does not execute the target JS as the extraction mechanism.

[`AstCreationPass.scala`](https://github.com/joernio/joern/blob/0738a6199bc860a788b7f28b2779997f210c405d/joern-cli/frontends/jssrc2cpg/src/main/scala/io/joern/jssrc2cpg/passes/AstCreationPass.scala) converts parsed frontend results into graph additions. [`AstGenRunner.scala`](https://github.com/joernio/joern/blob/0738a6199bc860a788b7f28b2779997f210c405d/joern-cli/frontends/jssrc2cpg/src/main/scala/io/joern/jssrc2cpg/utils/AstGenRunner.scala) is an additional trusted tool boundary; its subprocess/configuration behavior requires audit before our adoption. “No target execution” must not be confused with “no analyzer subprocess.”

[`X2Cpg.scala`](https://github.com/joernio/joern/blob/0738a6199bc860a788b7f28b2779997f210c405d/joern-cli/frontends/x2cpg/src/main/scala/io/joern/x2cpg/X2Cpg.scala), `defaultOverlayCreators`, orders Base, ControlFlow, TypeRelations and CallGraph layers. Importing a source AST alone is therefore distinct from creating a more complete analysis graph. Language-specific postprocessing and type recovery vary; this review does not claim all call targets resolve.

## CPG model and provenance

**Verified specification:** node/property families cover files/namespaces, methods/parameters/returns, types/members, calls/identifiers/literals/locals and control structures. Edge families include AST, REF, CALL/ARGUMENT/RECEIVER, CFG, dominance, control dependence and REACHING_DEF. Source filename/line/column fields provide navigation. Metadata records language and applied overlays. Internal node IDs should not be mistaken for stable identities across independent reparses. [CPG specification](https://cpg.joern.io/).

AST captures syntax ownership; CFG captures potential control transfers; data-dependence edges capture modeled value relationships. None is a runtime trace. A method-call node's text/name/type is not equivalent to an independently confirmed concrete implementation link. Unknown constructs are representable, but the exact unresolved diagnostics and type approximations vary by frontend.

The schema's generality makes it useful for queries. It does not inherently supply our desired application/service/resource ontology. Browser-server boundaries, API-to-route matching and declared database identities still require specialized semantics.

## Data flow and queries

[`OssDataFlow.scala`](https://github.com/joernio/joern/blob/0738a6199bc860a788b7f28b2779997f210c405d/dataflowengineoss/src/main/scala/io/joern/dataflowengineoss/layers/dataflows/OssDataFlow.scala) defines a named data-flow overlay using configured semantics and a reaching-definition limit. [`ReachingDefPass.scala`](https://github.com/joernio/joern/blob/0738a6199bc860a788b7f28b2779997f210c405d/dataflowengineoss/src/main/scala/io/joern/dataflowengineoss/passes/reachingdef/ReachingDefPass.scala) partitions work by method, creates a data-flow problem, solves forward propagation, and adds reaching-definition edges. Methods over the configured definition threshold are skipped. This is a practical example of analysis budgets reducing completeness.

**Documented:** CPGQL exposes typed Scala traversals, calls/callers and source/sink data-flow queries such as `reachableBy` and `reachableByFlows`. External-library behavior needs suitable semantics; a returned path is a modeled flow, not proof of actual execution. [Data-flow queries](https://docs.joern.io/cpgql/data-flow-steps/).

Taint flow is useful for propagation patterns but not identical to exact URL/value recovery. We need a value domain for configuration and resource identity, not merely whether input can influence a sink.

## Storage, scale and extensibility

Important documentation drift: the general CPG documentation still discusses OverflowDB, but the inspected repository's [4.0 migration note](https://github.com/joernio/joern/blob/0738a6199bc860a788b7f28b2779997f210c405d/changelog/4.0.0-flatgraph.md) states migration to Flatgraph. The current [technology-stack document](https://github.com/joernio/joern/blob/0738a6199bc860a788b7f28b2779997f210c405d/contributing-docs/07_tech_stack.md) describes a columnar in-memory graph implementation and external AST generators. This is not a mandatory Neo4j architecture. The pinned build selects CPG dependency version 1.7.79.

Parallel passes, explicit budgets and specialized graph storage are concrete scalability mechanisms; we did not measure memory, latency or incremental analysis. Frontend availability, compilation requirements and missing dependency context must be qualified per language. There is no basis here to claim arbitrary language mixing resolves inter-service calls.

Custom trusted passes/semantics can extend the CPG. That is a useful extension pattern, but arbitrary query scripts/plugins from uploaded repositories must never run in our platform. Joern does not require an LLM for the inspected extraction/data-flow path.

## Architecture and UX

Joern's central UX is code querying, shell/server workflows, path inspection and graph exports rather than a main high-level architecture dashboard. A query or custom pass can derive higher-level facts; there is no inspected universal grouping stage that turns a CPG into an accurate cloud/application diagram. Impact analysis would be a chosen reverse traversal, not automatically a complete behavioral effect calculation.

## Comparison and recommendation

We already have typed source facts and evidence, but lack Joern's richer control/data-flow representation and general query vocabulary. Adopt the **staged enrichment idea**: source facts first, bounded value/flow facts next, explicit architectural derivations afterward. Preserve overlay version, prerequisites and omitted analysis.

Building a full CPG is substantial engineering and storage overhead. We need selected program-point values and support chains first. Pilot a specific Joern frontend only if it solves a measured demanded-language gap better than a smaller provider. Do not integrate it merely to redraw our graph or assume its data-flow layer recovers application architecture automatically.
