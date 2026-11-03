# Compiler libraries and saved-scan deletion

Implemented 3 November 2026.

## Compiler-host repair

TypeScript supplied the compiler library directory with forward slashes on Windows, while requests were compared after Windows path normalization. The trusted-library predicate therefore rejected files that existed.

The directory is now normalized once with path.resolve, matching the existing normalization of requested paths. The host still allows only explicitly supplied snapshot files and lib.*.d.ts files directly inside the trusted compiler library directory. No dependency installation, target build, compiler plugin loading, source execution or general filesystem fallback was added.

The graph now reports standard_library_files and known_library_calls. Calls whose signature declarations come from trusted standard-library files are preserved in library_references with caller, file/line, API name, trusted library filename and validated callsite evidence. They are no longer reported as unresolved calls. They are not promoted to local implementation-body CALLS edges or runtime observations. Other source/ambient signatures without concrete bodies remain separately unresolved.

## Same-snapshot result

The existing GitDiagram verification ZIP still yields 412 parsed source files, 14,717 call/new expressions and zero syntax failures.

| Measurement | Before | After |
|---|---:|---:|
| Trusted standard-library files loaded | 0 | 63 |
| Local implementation calls | 4,416 | 4,417 |
| Known standard-library call references | 0 | 6,989 |
| Compiler target unavailable | 10,069 | 3,061 |
| Signature available, body not established, excluding trusted library references | 232 | 250 |
| Total unresolved call records | 10,301 | 3,311 |
| Unresolved imports | 53 | 53 |
| Unresolved HTTP references | 60 | 60 |

This is a 67.86% reduction in unresolved **call records** on the same scope. It is principally corrected semantic context and classification, not 6,989 new application connections or an architecture-accuracy percentage. Full signature_only_calls remains 7,239, including the 6,989 trusted library references; it must not be added to unresolved_calls to calculate unknowns without excluding those known references.

Artifacts: output/compiler-library-fix/gitdiagram-analysis.json and gitdiagram-summary.json. A freshly verified result is added to main saved history and the isolated preview as a new snapshot; existing historical scans are preserved. The latest summary records its exact snapshot ID and single-run time. No enterprise speed claim is made.

## Saved-scan deletion

- Each saved scan has a Delete scan button and inline Confirm delete / Keep scan choices.
- DELETE /api/v1/analyses/{snapshot} transactionally removes that one graph/summary and its terminal-job pointers. Other scans and active jobs are retained. Missing results return 404.
- Deleting the selected scan clears its canvas and remembered selection; deleting a different scan preserves the current selection. Reload does not resurrect the deleted result. Stale remembered IDs are cleared when their analysis is no longer found.
- Older scans without the compiler-library coverage marker show a notice requiring a new scan to apply current fixes.
- This is logical deletion from application history, not a secure physical wipe of database pages or removal of separate research/export files. Source repositories are not deleted by the endpoint, and request IDs are never used as filesystem paths.

## Verification

83 backend tests pass. New regressions cover real trusted-library loading, standard-library signatures versus local bodies, shadowed globals, preserved reference evidence, deterministic reruns, single-scan deletion, unrelated scan retention, completed-job cleanup, CORS DELETE and persistence after reopening.

Frontend TypeScript checks and production build pass. scripts/verify_scan_deletion.cjs verifies Keep scan cancellation, deletion of an unselected/selected scan, localStorage/canvas cleanup, reload persistence and old/new scan notices. Browser results: two intentional DELETE requests against disposable preview data, zero analysis submissions and zero browser errors. Screenshots and results are in output/compiler-delete-review/.

## Still outstanding

The 53 import records need asset/generated/platform classification. Wrapper-based R2/Redis resource reconstruction and business/domain responsibility naming remain incomplete. Trusted-library recovery improves available semantics but does not resolve missing third-party types or general object/helper value flow. The next architecture-focused work should follow bounded configuration and returned-client summaries into resource operations.
