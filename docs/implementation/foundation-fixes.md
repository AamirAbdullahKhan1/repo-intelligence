# First foundation fixes

Implemented 2 November 2026. No tools/dependencies were added, and no API/canonical graph schema was changed. Existing saved analyses are historical results; new analysis uses the changed worker fingerprint.

## Changes

1. **Stale URL prevention.** The compiler worker now indexes symbol writes during its existing first traversal. Initializer following rejects reassignment, compound/logical writes, destructuring targets, updates, loop-target writes, captured writes, redeclarations and files using direct eval/with. Symbols remain scope-bound, so an unrelated shadowed name does not invalidate the real declaration. Unsupported values remain HTTP unknowns rather than false host edges. Resolved initializer chains retain source-definition evidence alongside their callsite.
2. **Source inclusion.** Public browser code and source under scripts/plugins are parsed as candidates. They are not executed, dynamically imported, installed or assumed production-reachable. Test/documentation/experimental exclusions and generated/vendor directories remain excluded with reasons. Explicit vendor directories prevent bundled libraries under public assets from dominating the recovered application graph.
3. **Next root routes.** Match `app/route.js|ts`, `src/app/route.js|ts` and nested equivalents relative to each owning manifest package. Existing route-group handling remains; lookalike app folders elsewhere are not automatically routes. Registration and handler relationships retain source evidence.

## Efficiency

Symbol mutation lookup is a set membership check after a single existing source pass; it does not rescan every file for each HTTP call. The compiler host now precomputes supplied-source directories instead of scanning all text paths on every directory-existence query. Existing byte/time/output limits remain unchanged. These are bounded implementation improvements, not an enterprise performance claim.

## Verification

`backend/tests/test_foundation_regressions.py` adds three integration-level static-analysis tests, covering positive, negative, scope/shadowing, evidence and deterministic-rerun cases. All three failed against the previous engine and pass after the changes. The full backend suite passes: **64 tests**. Existing warnings concern a TestClient alias deprecation and an intentionally duplicated ZIP member in an ingestion fixture.

The restricted Windows sandbox blocked Python's local socketpair initialization for FastAPI TestClient. A diagnostic stack established the cause; the suite passed outside that restriction. No target fixture application was executed. A malicious configuration sentinel remains absent after parsing.

The existing GitDiagram verification ZIP was analyzed by the same trusted pipeline, with snapshot integrity and evidence validation. Final machine-readable output: `output/foundation-fixes/gitdiagram-summary.json` and `gitdiagram-analysis.json`. The initial broader-inclusion observation is retained separately as `gitdiagram-initial-summary.json`; it is not a comparable speed benchmark because vendor scope changed afterward.

## Deliberate limits

Reassigned values currently become unresolved, including some that future program-point analysis could recover precisely. This removes demonstrated false positives without claiming complete data flow. Import-based value propagation, branch joins, helper summaries, relative HTTP matching, responsibility grouping and configured-resource linking remain follow-up work.

Docs/experiments and explicit test/vendor/generated patterns still affect coverage; restored files are candidates rather than a complete production-reachability classification. Framework exports through wrappers/re-exports, full Next execution context and routing precedence remain partial.

These changes improve the facts feeding the architecture graph. They do not claim that the current overview has acquired full semantic architecture interpretation.
