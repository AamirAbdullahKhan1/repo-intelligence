# Repo Intelligence: current-result assessment

**Date:** 2 November 2026  
**Conclusion:** The result is substantially better organized and covers more source files. Improvements to semantic resolution on GitDiagram's previously analyzed files are much smaller. The large unresolved count needs diagnosis and better classification, not cosmetic removal. This audit found a concrete Windows compiler-host defect that should be fixed before adding more analysis tools.

## 1. What was compared

This report compares saved artifacts, not remembered screenshots:

- Historical GitDiagram graph: snapshot `8b14186f6aec18085a25f11c5e1198612708b226793c6aae190c7fa977198b2a`, read through SQLite in read-only mode from `data/analysis.sqlite`.
- Current verification graph: snapshot `f1df189a4178b3793a4228714fa23908f651b126e19ed4cf00451d781067db66`, in `output/resource-responsibilities/gitdiagram-analysis.json`.
- Intermediate foundation, project-resolution and HTTP-linking graph artifacts.
- Latest frontend browser results in `output/frontend-review/browser-results.json`.
- A syntax-only audit of saved call records against the existing GitDiagram ZIP, and a synthetic compiler-host reproduction. No submitted application was executed. No application code was modified for this report.

Machine-readable evidence: [comparison](../../output/reviews/current-result/comparison.json), [call shapes](../../output/reviews/current-result/call-shapes.json), [compiler-host probe](../../output/reviews/current-result/lib-host-probe.json). Paths are relative to this document.

## 2. Measured before and after

| Measurement | Historical result | Current result | Interpretation |
|---|---:|---:|---|
| Parsed source files | 386 | 412 | 26 additional files, a 6.74% increase |
| Syntax failures | 0 | 0 | Parsing remained successful within the selected scope |
| Call/new expressions | 12,074 | 14,717 | Broader analysis scope |
| Calls bound to local implementation bodies | 3,833 | 4,416 | 583 more, all in newly included files |
| Call records with a signature but no concrete body established | 232 | 232 | Not equivalent to missing import files |
| Call records with compiler target unavailable | 8,009 | 10,069 | Increase comes from newly included files |
| Total unresolved call records | 8,241 | 10,301 | Includes both preceding categories |
| Unresolved import records | 53 | 53 | No measured reduction on this repository |
| Unresolved HTTP records | 52 | 60 | Existing-file improvement plus additional new-file unknowns |
| Route records | 50 | 50 | Root-route fix is verified by fixtures; no additional GitDiagram routes recovered |
| Entities | 4,240 | 4,875 | Current total includes derived role groups |
| Relationships | 10,892 | 12,624 | More source plus derived aggregations; not an accuracy score |

The raw local-call count rose 15.21%. **This is not a 15.21% improvement in accuracy.** All 583 additional bound calls are from restored source candidates such as scripts and the browser video engine.

On the exact historical 386-file scope (all 386 source hashes match):

- Bound implementation calls remain **3,833**.
- Unresolved call records remain **8,241**.
- HTTP unknowns decrease from **52 to 44**; eight requests now have conditional route links.

The 26 additional files add 583 bound calls, 2,060 unresolved call records and 16 HTTP unknowns. Consequently, the rising total unknown count is explained by broader scope, but the lack of improvement on existing call resolution is also real.

The local-body-binding fraction is 31.75% historically and 30.01% currently, with different denominators. Neither percentage measures architectural correctness: built-in/library calls do not require a local implementation body, and newly included files have a different call mix.

## 3. What changed and how effective it has been

| Change | Demonstrated benefit | Remaining limit |
|---|---|---|
| Restored public/scripts/plugins source candidates | 26 additional files and their source relationships recovered | Production reachability is not established by inclusion |
| Conservative variable mutation handling | Regression tests reject stale URL destinations | Reassigned but recoverable values still become unknown |
| Nested configuration and workspace resolution | Positive/negative fixtures establish correct aliases, exports and cross-file binding | No local-call-count improvement measured on GitDiagram's original scope |
| Imported constants and template strings | Four additional HTTP host references in tooling scripts | Not evidence of new production communication paths |
| Next client request-to-route matching | Eight conditional links, including admin session and sponsor API | No general proxy/origin or request-wrapper resolution |
| Resource rules | Fixtures prove direct R2/pg/redis operations with evidence | **Zero concrete source-to-resource links recovered on GitDiagram** |
| Responsibility interpretation | 11 explicit, evidence-backed technical groups | Broad roles, not business/domain component recovery |
| Diagram-first frontend | A focused 10-node overview, separate deeper tabs and evidence-linked host list | Filtering improves presentation, not semantic completeness |

The frontend deliberately filters helper/unclassified and generic library groups from the focused overview when specific roles exist. Those records remain in deeper exploration. Individual HTTP hosts moved into an expandable evidence-linked list. This explains why the screen is much smaller without implying that analysis resolved thousands of additional relationships.

The latest recorded backend suite passes 80 tests. Frontend type checking/build and browser acceptance pass. Browser checks cover all six tabs, workflow component selection, evidence, uncertainty, canonical diagram IDs and reopening the same saved analysis, with no browser/API errors and no new analysis submission. This is functional verification; no independent newcomer study or architectural precision benchmark has been completed.

## 4. What the “8.3k unresolved” number actually means

The older saved result has **8,346 unknown records**:

- 8,241 calls;
- 53 imports;
- 52 HTTP references.

The current verification result has **10,414 unknown records**:

- 10,301 calls;
- 53 imports;
- 60 HTTP references.

These are records, not necessarily distinct defects. A fetch expression can have both an unknown implementation-call record and a separate HTTP-destination record. Treating their sum as a count of broken architectural connections is misleading.

The historical 8.3k figure is still present in saved analyses in the main database. If a screen shows that figure, inspect its snapshot ID: viewing an older analysis does not rerun the improved engine. The separate frontend preview uses the newer `f1df189a4178…` analysis.

### The 53 import records are mostly not missing application source

| Category | Records | Appropriate treatment |
|---|---:|---|
| CSS/stylesheets | 41 | Asset dependency; all 41 targets are present in the supplied ZIP |
| Generated `.open-next` outputs | 9 | Generated output unavailable/excluded; retain an explicit boundary without running a build |
| `cloudflare:workers` virtual module | 2 | Platform-provided module; model as platform dependency |
| `@opennextjs/aws/types/overrides.js` | 1 | External package subpath; inspect inventory/resolution context |

The current code-only import resolver categorizes the stylesheets as unknown because their texts are not supplied as TS/JS analysis inputs. We should represent their presence and asset relationship separately. We must not parse CSS as JavaScript or turn it into a service.

Correct categorization can remove misleading warnings from the primary problem list while preserving all records. It does not create additional application call connections.

## 5. Newly discovered defect: trusted compiler libraries rejected on Windows

The worker obtains its trusted library directory from TypeScript, which returns a forward-slash path in this installation. Its containment predicate compares that string with a Windows-normalized backslash path. The strings differ, so the predicate rejects existing trusted `lib.*.d.ts` files. The corresponding trusted-library directory check has the same mismatch.

An isolated probe reproduces the production predicate using synthetic source containing five ordinary calls: Math.max, JSON.stringify, String, Array.map and Promise.resolve. It parses the text but never runs it.

| Synthetic probe | Current predicate | Normalized comparison |
|---|---:|---:|
| Trusted default library permitted | No | Yes |
| Compiler library files loaded | 0 | 63 |
| Calls with a signature declaration | 0 of 5 | 5 of 5 |

**This is the first engine fix I recommend.** Normalize the trusted-library directory at construction, retain the strict file allowlist and snapshot boundary, and add Windows/POSIX-style path regressions plus normal-global and shadowed-global cases.

The isolated result establishes the defect, not the number of GitDiagram calls it will recover. Many corrected calls may become known standard-library signatures rather than local implementation calls. The current counter still puts signature-only cases into unknown records, so the visible unknown total might remain high until the taxonomy is corrected. We must not mark library signatures as locally implemented bodies.

This also exposes a test gap: the earlier regression fixtures exercised local symbols and conservative unknown behavior, but did not assert that trusted standard-library declarations were actually loaded.

## 6. What the unresolved call audit shows

The audit matched all 10,301 call records to AST call/new expressions using their saved UTF-16 citation positions. The categories below are **syntactic shapes**, not verified root causes or predicted recovery counts:

| Shape | Records |
|---|---:|
| Other property/receiver calls | 3,117 |
| Identifier calls | 2,117 |
| Common collection/string method names | 2,602 |
| Standard-global-shaped property calls | 1,643 |
| Constructor expressions | 779 |
| Dynamic import expressions | 23 |
| Other callable expressions | 15 |
| Computed receiver calls | 5 |

Examples include map (370), push (279), trim (234), useState (121), useRef (90) and fetch (81). A name such as get or set does not prove Redis/database access; a method named map does not prove an Array receiver. Even a global-shaped name may be shadowed. Compiler binding and receiver evidence remain necessary.

These observations suggest a mixture of missing standard/platform typings, absent third-party declarations, callbacks/receiver typing and genuine dynamic/application gaps. The audit cannot assign a reliable count to each cause without a semantic rerun.

As an architectural prioritization aid, 1,415 unknown call records occur in nodes within four existing HANDLED_BY/CALLS/CONSTRUCTS steps of discovered routes. This is an incomplete static neighborhood, not runtime reachability. Missing graph edges can hide other important operations outside it. It is a useful review queue, not a completeness metric.

## 7. What is still missing from the architectural result

1. **Concrete resource chains on GitDiagram.** R2 uses dynamic SDK imports, returned/destructured client objects and wrappers. Redis uses a custom HTTP wrapper and environment helper. Our direct models do not follow those chains yet. Zero resource links—and zero resource unknowns from those models—does not mean the resources are absent.
2. **Responsibilities beyond broad technical roles.** Of 4,754 eligible file/symbol/endpoint records, 4,615 remain under Other analyzed source. This is a mixed-granularity grouping denominator, not a claim that 97% of application behavior is unknowable. Most helper entities need not become separate architecture boxes.
3. **Complete major-path explanations.** Some relationships are established, but generation, persistence and rendering are not yet recovered end to end. A disconnected AI group in the focused view is a missing supported path in that view, not proof of an isolated subsystem.
4. **Calibrated accuracy and enterprise capacity.** Valid citation ranges and preserved IDs establish traceability. They do not prove correct architecture. Current repository/file/time/heap limits also prevent a blanket enterprise-scale claim.

## 8. Recommended next fixes, in order

### First: repair semantic context and reporting

- Fix trusted-library path normalization and its regression coverage.
- Reanalyze the same snapshot and report changes on the same file scope.
- Separate local-body binding, known library/platform symbol, signature-only declaration, unresolved application target and unsupported dynamic target.
- Record missing dependency/type context explicitly. Use trusted, pinned analyzer-side type/model packs where justified; do not install or run client dependencies.

**Success:** standard APIs are correctly identified; genuine application gaps remain visible; no global-name shortcuts or filesystem access outside the allowlist are introduced.

### Second: classify non-code imports

- Record the 41 existing stylesheet targets as asset dependencies.
- Mark generated outputs and virtual platform modules according to their evidence.
- Investigate the one external subpath through manifest/lockfile and resolution evidence.

**Success:** assets/platform/generated boundaries no longer masquerade as missing application implementations; original evidence remains inspectable.

### Third: bounded configuration and object/client summaries

- Follow named environment references without inventing secret values.
- Summarize supported helper returns and object properties.
- Follow destructuring of returned clients and literal dynamic imports.
- Connect receiver identity, operation, client/configuration and resource declaration when evidence permits; otherwise retain a symbolic destination/unknown.
- Verify positive, negative, shadowing, mutation, branch, budget and unfamiliar-repository fixtures before claiming improved coverage.

**Success:** recover one inspectable route → handler → wrapper → client → configuration/resource chain. Do not optimize for clearing every low-level unknown first.

### Fourth: evaluate architectural correctness

Define a reviewed set of required major components and connections, then score precision and recall separately for routes, HTTP links, resource links and component claims. Keep counts of assets, standard APIs and missing external implementations separate from critical architecture gaps. Compare supported views with the manual GitDiagram assessment without treating its runtime/deployment claims as automatic ground truth.

## 9. Overall judgment

**Presentation:** materially clearer, functionally tested, and still faithful to saved IDs.  
**Source coverage:** broader, with 26 restored files.  
**Same-scope local-call resolution:** no measured improvement yet.  
**HTTP linking:** a useful narrow improvement, eight conditional links.  
**Resource reconstruction on GitDiagram:** not solved.  
**Architecture grouping:** useful first technical abstraction, still coarse.  
**Confidence:** stronger regression and provenance controls, but no defensible accuracy percentage.

We should keep the improved frontend and now fix compiler semantic context before expanding the tool stack. The next meaningful proof is a correctly reconstructed critical resource workflow, not a smaller headline unknown count.

## Primary technical references

- [TypeScript module resolution](https://www.typescriptlang.org/docs/handbook/modules/reference): project resolution and package/type context.
- [CodeQL JS/TS data flow](https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-javascript-and-typescript/): local/global flow, property reads/writes and the distinction between syntax and data-flow representations.

These sources support the proposed methods. All repository-specific counts and the Windows defect above come from the local artifacts/probes, not those documents.
