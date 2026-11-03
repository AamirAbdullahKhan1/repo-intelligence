# Project-aware TS/JS resolution and imported values

Implemented 2 November 2026. No dependencies installed, target code executed, or UI/schema changes made.

## What changed

- The nearest tsconfig.json/jsconfig.json is parsed with the installed TypeScript API. Supported inherited options retain compiler-relative path semantics. Missing/invalid inherited configuration produces diagnostics and no guessed aliases.
- Import extraction and compiler binding share a cached, project-aware module resolver. The host sees supplied snapshot texts and trusted compiler libraries only.
- Explicit package.json workspaces (array and packages-object forms) provide virtual package lookup without node_modules installation. TypeScript interprets exports/main/types. Missing build outputs and inaccessible export subpaths stay unresolved. Duplicate workspace names are not arbitrarily selected.
- Resolved local packages are internal relationships, including packages named like known SDKs. A local package named openai does not become an external AI integration.
- Bounded string analysis now supports template expressions and imported variable initializers, including aliases/re-exports resolved by the compiler. Resolved HTTP relationships retain the use/import declaration and original value-definition evidence. Reassigned, type-only, unavailable and environment-dependent values remain unresolved.

## Verification

Five regression tests exercise nested project aliases, inherited config-relative paths, JS configuration, workspace exports, prohibited private exports, missing build output, internal SDK-name collisions, unavailable inheritance, imported/template values, mutation rejection, evidence and deterministic reruns. Full backend suite: **69 passed**, with two existing fixture/deprecation warnings.

Fresh GitDiagram analysis uses the existing verification ZIP through validated ingestion and the static pipeline. Artifacts are in output/project-resolution/. Saved UI analyses are not overwritten. Counts are coverage observations, not semantic accuracy measurements. See gitdiagram-summary.json for the final run.

Final observation: 412 parsed source files, zero syntax failures, zero configuration diagnostics, 4,416 bound implementation calls. Four additional HTTP destination edges were recovered from template expressions in scripts (IndexNow submission and Cloudflare tooling). These are tooling-source references, not newly proven production communication paths. Final graph: 4,864 entities and 12,579 edges. One run took 30.968 seconds; this is not an enterprise benchmark or demonstrated speedup.

## Boundaries

This is project-aware **module resolution**, not independent compiler programs per project. Compiler-wide checking options still use the existing shared program; differing JSX/type/global environments and project-reference build semantics are not fully modeled. Configuration selection currently uses nearest conventional config, not complete include/exclude or overlapping-project membership. Files remain source candidates under existing scope policy.

Workspace discovery currently supports package.json workspace patterns with ordinary star/double-star matching. pnpm-workspace.yaml-only declarations, negations and brace/extglob patterns are not implemented. No source location is guessed from a missing dist export. Package-supplied compiler configuration outside the snapshot is unavailable.

Imported string analysis retains the existing depth limit of five and conservative mutation checks. It is not reaching definitions, control-flow feasibility, general object/alias analysis, full helper summaries or runtime reachability. Environment references do not acquire invented literal values. Intermediate barrel declarations are not all included in value provenance; source import and terminal definition are retained.

Remaining work includes relative HTTP-to-route matching, richer client/config/resource correlation, responsibility interpretation and the overview projection. These changes strengthen underlying links; they do not claim the diagram is now architecturally complete.

## Primary references

- [TypeScript Compiler API](https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API): compiler host, checker and custom module resolution.
- [TypeScript module reference](https://www.typescriptlang.org/docs/handbook/modules/reference): aliases, resolution modes and package exports.

The worker remains on its installed TypeScript version. The API documentation warns that future major versions change the programmatic API; no version migration was performed here.
