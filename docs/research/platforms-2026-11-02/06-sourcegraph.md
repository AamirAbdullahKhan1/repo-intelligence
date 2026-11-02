# Sourcegraph Code Intelligence: symbols, occurrences and navigation

Date: 2 November 2026. This is a code-intelligence reference, not a direct architecture-recovery competitor. SCIP schema source pinned to `scip-code/scip@bbec5345bfae602b31286a9ec74e2c2042713f50`. Sourcegraph server internals and running indexes were not inspected. **Verified** denotes schema source; **Documented** denotes official service/indexer behavior. [Workflow](workflows/sourcegraph.mmd).

## Product and processing

Sourcegraph precise navigation uses language-specific indexes uploaded to an instance; search-based navigation is a separate fallback. Definitions/references/implementations are useful developer navigation outputs, not high-level service/resource diagrams. Documentation recommends CI indexing for complex/authenticated builds to reuse existing project context. This makes a blind adoption incompatible with our no-install/no-build analysis requirements. [Precise navigation](https://sourcegraph.com/docs/code-navigation/precise-code-navigation).

Auto-indexing periodically schedules repository/commit jobs, clones into executor environments, runs selected commands and uploads results. Job inference uses repository structure, with explicit configuration for complex cases. This is execution orchestration around indexers; it does not mean a raw source archive always yields complete semantics. No executor or target build was run here. [Auto-indexing](https://sourcegraph.com/docs/code-navigation/auto-indexing).

## Verified index model

[`scip.proto`](https://github.com/scip-code/scip/blob/bbec5345bfae602b31286a9ec74e2c2042713f50/scip.proto) defines an `Index` with metadata, documents and optional external symbols. Documents have canonical relative paths, language, occurrences and symbol information. Occurrences connect ranges to symbol identities/roles; relationship records express semantic navigation relations such as references/implementations. Metadata identifies producer/version and encodings. This decouples production of semantic facts from their consumption.

This is not a universal explicit function-call/data-flow graph. A reference occurrence must be interpreted in its syntax/context before calling it a function invocation. Symbol identity can include package/version/descriptors, with local symbols scoped differently. It does not establish deployment/resource identity or a source hash for every asserted architecture relationship.

SCIP succeeds LSIF as the preferred Sourcegraph navigation interchange. Legacy LSIF compatibility/migration is documented, but this review did not reconstruct an old LSIF server pipeline. [Migration](https://7.1.sourcegraph.com/admin/how-to/lsif-scip-migration).

## Indexer depth and execution requirements

The official TypeScript indexer quick start expects project dependencies to be installed; SvelteKit guidance also includes generated configuration preparation. Large-index troubleshooting discusses memory limits. This does not prove every invocation executes target code, but the documented default workflow does not satisfy our constraints without qualification. [scip-typescript](https://github.com/sourcegraph/scip-typescript).

Different language indexers have different compiler/dependency requirements. A language listed as supported does not imply successful indexing from an incomplete ZIP with no installed metadata. AI features are separate from this core navigation protocol; no LLM is required to interpret the inspected SCIP records.

## Architecture, storage and exploration

SCIP offers source-level symbol navigation, cross-file relationships and external-symbol metadata. It does not by itself infer frontend/backend boundaries, routes, database usage or component responsibilities. Those would require additional analysis and interpretation.

Server upload processing, query indexes and dependency/commit matching provide reusable navigation, but this report does not claim current table layout, storage engine internals or measured scaling. Do not confuse Sourcegraph text-search indexing with precise semantic indexing. Policies/retention and repository/commit selection matter for cost; they are not proof of complete incremental semantic invalidation.

Definition/reference navigation from code and diffs is a useful UX model. An index containing an edge is not an explanation of why a high-level architectural connection follows. Our evidence chains still need their own representation.

## Comparison and adoption

We already use compiler symbols internally but lack a general persistent symbol-occurrence navigation layer. Borrow producer metadata, document-relative locations, explicit symbol scope and consumer/producer separation. Later, a qualified external SCIP import could supplement metadata only after snapshot/version/path checks; never accept its occurrences as prevalidated application architecture.

Substantial work would be needed for multi-language canonical symbols, cross-package version matching, index ingestion and reverse navigation. Deferred: running arbitrary indexer commands, dependency installation, build-capture orchestration and adopting a distributed navigation backend. For our immediate problems, extend the current safe compiler host before introducing another indexer.
