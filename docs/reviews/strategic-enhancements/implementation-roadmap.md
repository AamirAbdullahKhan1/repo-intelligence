# Implementation roadmap

Date: 31 October 2026. Proposal only; no implementation or installations performed. Phases are ordered by evidence and product value rather than number of tools. No calendar or throughput estimates are asserted without measurements.

## Phase 0 — Establish the correctness baseline

**Objective:** know which architecture claims are correct and preserve current behavior intentionally.

**Selected additions:** hand-labelled fixtures, scope/uncertainty expectations and a small evaluation harness. No new production tool.

**Why first:** existing regression/UI checks do not measure architectural accuracy. More resolved edges could otherwise conceal more false positives.

**Dependencies:** current saved graph, existing test suite and documented support scope. Reuse `test_typescript_worker.py`, `test_framework_adapters.py`, `test_exploration.py` and the saved synthetic probe cases.

**Expected outcome:** versioned evaluation data that distinguishes direct facts, inferred/candidate links, omissions and unsupported scope. Include Next.js/Express and at least a contrasting repository topology; do not overfit GitDiagram.

**Acceptance criteria:**

* Document expected nodes/typed edges and supporting ranges, plus relationships that must remain absent/unknown.
* Include stale URL assignment, root route, production `public/` code, unused SDKs, type-only imports, aliases, conditional hosts and unrelated same-name resources.
* Record precision/missed edges separately per edge kind, not a single graph-size score.
* Capture baseline time, memory/output size and view load/index costs on a stated machine without invented targets.
* Preserve current ingestion, evidence, saved-analysis and functional regression tests. Record which checks were actually run.

**Risks:** annotation mistakes and treating the curated image as ground truth. Resolve ambiguous expectations explicitly; use independent human review when available, without requiring an agent or new tool.

## Phase 1 — Fix known correctness and coverage failures

**Objective:** eliminate confirmed wrong/missing facts before adding broader inference.

**Selected additions:** custom source-scope and Next route-rule corrections; conservative invalidation for mutable URL values; safe module/config resolution improvements as separate tested increments.

**Priority:** these are demonstrated gaps in the existing worker, not hypothetical benefits of external tools.

**Dependencies:** Phase 0 fixtures. Keep current TS compiler and worker boundary.

**Expected outcome:** improved precision/coverage in supported patterns, with explicit uncertainty elsewhere.

**Acceptance criteria:**

* Mutable URL fixture no longer emits the stale host. Emit the new host only if the supported analysis establishes it; unknown is an acceptable initial conservative result.
* Root and nested Next route fixtures resolve correctly; invalid/shadowed exports do not create endpoints.
* Production source under `public/` is handled deliberately; generated/vendor exclusions remain explicit and bounded.
* No target install, import, plugin execution, build or network access is introduced.
* Snapshot/engine identity changes correctly for changed semantics; existing saved analyses remain readable.
* Positive and negative regression tests pass; source evidence remains grounded.

**Risks:** broader file scope increases parsing cost; regex fixes overgeneralize framework rules; changed resolution can regress aliases. Limit and measure each change independently.

## Phase 2 — Bounded values, configuration and client origins

**Objective:** recover selected configuration-to-operation relationships safely.

**Selected additions:** reaching definitions for a limited statement subset, immutable cross-file bindings, symbolic environment keys, finite string values and selected client/helper summaries. Curated typings only in a separately gated metadata pilot.

**Why now:** this directly supports resource and HTTP relationships that inventory/import tools cannot provide.

**Dependencies:** Phase 1 correctness, abstract-domain design and privacy rules. Define budgets from measurements before broadening supported syntax.

**Expected outcome:** fewer wrong initializer assumptions and more explainable client/config/resource identities.

**Acceptance criteria:**

* Reassignment, aliases, branches and unsupported writes have labelled tests; unknown branches are not collapsed to one endpoint.
* Every derived value records its supporting assignments/imports/config keys and analysis rule.
* State/iteration/recursion limits are deterministic and reported as coverage/unknowns.
* Symbolic secrets are tracked by key without retaining their actual values in graphs/logs.
* Typing metadata, if enabled, is version-matched, pinned and read-only; signatures never masquerade as local implementations.
* Relative URL mapping remains a candidate until caller context and routing/base-path evidence suffice.
* Compare precision and coverage against Phase 0; new false links block promotion even if resolution counts increase.

**Risks:** state explosion, alias unsoundness, accidental secret propagation and overconfident runtime claims. Start narrow; widen to unknown when unsupported.

## Phase 3 — Architecture interpretation and one obvious overview

**Objective:** make source facts answer “what are the major parts and how do they connect?”

**Selected additions:** internal interpretation rules, evidence-backed roles/resource relationships, better entry-point selection, and revised projections. Keep React Flow/ELK. Direct architecture export can be included if it uses the same projection and evidence mapping.

**Why prioritized:** a new renderer or scanner cannot repair path-based semantic grouping. Bounded existing views still fail the user's comprehension goal.

**Dependencies:** tested source facts and initial Phase 2 summaries. If new persisted fields are needed, separately review schema version/migration and API compatibility before implementation. No silent contract changes.

**Expected outcome:** clearly distinct packages, logical components, integrations and declared deployment resources; one default system architecture and selective internal workflows.

**Acceptance criteria:**

* Shared protocol code is not automatically labelled UI because of directory names.
* No directory or graph cluster is promoted to a deployable service without evidence.
* Every derived or aggregated relationship exposes original entity/edge/evidence IDs and rule assumptions.
* Calls, imports, API candidates and configuration declarations remain visually and semantically distinct.
* An unfamiliar user can identify major responsibilities, select a meaningful module entry, inspect support and locate uncertainty; record task success and confusion rather than inferring usability from automated clicks.
* Both views and export, if implemented, use the same saved canonical result; reopening does not rescan.
* Run existing functional/browser tests plus focused checks for changed projections. New user studies require actual participants; do not label an internal walkthrough as one.

**Risks:** overfitting labels to GitDiagram, hiding useful information, or maintaining interpretation twice. Keep semantics in backend rules and test varied topologies.

## Phase 4 — Run only justified research pilots

**Objective:** determine whether external tools improve a measured gap before adding default dependencies.

**Selected additions:** choose pilots separately; none is mandatory.

| Pilot | Question | Acceptance / stop criterion |
|---|---|---|
| dependency-cruiser | Does an independent module scan reveal real resolver gaps? | Fixed config and equivalent scopes; classify disagreements against labelled truth. Keep development-only if no new reliable production value. |
| NetworkX | Do filtered communities improve component suggestions beyond explicit rules? | Stable pinned output and better human/task evaluation; never infer services. Stop if utilities/unknowns dominate clusters or semantic quality does not improve. |
| Curated typings | Do version-matched declarations improve needed API identity? | No installs/network during analysis; provenance and mismatch tests; improvement without converting signatures into implementations. |
| ast-grep | Is a demanded unsupported syntax pattern significantly easier to maintain? | Trusted parsers/rules, exact locations and negative fixtures; stop if it duplicates compiler rules or cannot resolve identity needed by the feature. |
| Joern, chosen language | Does a demanded language benefit enough to justify another runtime? | Audited safe frontend/process tree; labelled call/data-flow evaluation, source evidence and measured costs. No target build/download. Stop if cost or provenance fails. |

**Dependencies:** Phases 0–3 metrics and provider safety checklist. Pin a release; inspect its actual discovery/config paths. Pilot runtime and security claims must be backed by execution monitoring in an isolated environment, not documentation alone.

**Expected outcome:** adopt, keep as development-only, or discard each pilot with evidence. A negative result is useful.

**Risks:** turning experiments into permanent default stages without validation, treating tool agreement as proof, or silently expanding the trusted process/network surface.

## Phase 5 — Demand-led ecosystem and export support

**Objective:** broaden useful coverage without weakening source evidence.

**Selected additions:** a filesystem Python AST provider first if Python demand exists; Grimp as optional comparator; Syft for a separate package view; local HCL provider/Inframap evaluation for infrastructure; LikeC4 one-way export only if requested. Semgrep/Checkov remain separately scoped optional findings providers until a concrete feature justifies them.

**Dependencies:** stable normalization/reconciliation rules, proven safe profiles and a reviewed schema-evolution path. Choose one vertical at a time.

**Expected outcome:** explicit new support scope and separate inventory/infrastructure/policy views, with architecture links only when evidence supports them.

**Acceptance criteria:**

* Python package discovery does not import submitted modules, load target `.pth` files or custom contracts.
* Package declaration, locked version, imported API and deployed service remain different facts.
* Terraform analysis performs no init/plan/apply/provider/backend/remote-module execution; unresolved references stay unresolved.
* Provider-local IDs reconcile predictably and conflicts retain original claims.
* Optional exporter consumes canonical projections and preserves IDs/evidence mapping; no second authoritative model.
* Optional provider failure records incomplete coverage without fabricating successful empty analysis.

**Risks:** thin multi-language support marketed as general understanding, extra maintenance, and third-party tool output losing source spans.

## Deployment gate — Required before public multi-tenant uploads

This gate can progress alongside local semantic work; it is not a reason to postpone correctness or a claim that the present local tool is already production-isolated.

**Objective:** enforce untrusted-input boundaries outside the application process.

**Selected work:** least-privilege analysis workers, restricted filesystem mounts, denied analysis egress, process-tree/resource budgets, tenant-aware access/retention and bounded diagnostic logs. Retain controlled GitHub ingestion in a separate permitted network boundary.

**Dependencies:** deployment platform selection and a concrete threat model. Candidate tools cannot be approved merely because their advertised function is static.

**Acceptance criteria:** adversarial fixtures cannot execute package/config/plugin code, access host secrets, escape allowed paths, spawn unauthorized descendants or reach network endpoints; limits terminate the whole job process tree; partial artifacts are not published as complete; access tests enforce ownership of saved results. Run controlled containment tests and document residual risks.

**Risks:** incorrectly treating language-level monkey patches, Docker defaults or read-only flags as complete isolation; parser vulnerabilities; sensitive state/snippet retention. No blanket “fully secure” claim.

## Deliberately excluded

Do not rewrite the existing analyzer, install every researched tool, build a complete JavaScript interpreter, make clustering a service detector, create runtime trace claims from static paths, auto-fetch/install dependencies for a job, load target configuration code, or replace SQLite/rendering before evidence shows a need. Avoid numerical accuracy/speed claims until labelled evaluation and measurements support them.
