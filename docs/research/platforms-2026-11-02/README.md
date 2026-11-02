# Repository intelligence and architecture reconstruction: deep technical research

Research date: **2 November 2026**. This package answers the attached research assignment. It is research and design discussion only: no application features, dependencies, API contracts, containers or production configurations were changed.

## Read this first

The most useful result is a division of responsibilities, not a recommendation to copy one product:

* RepoDNA: approachable artifacts, coverage and source-linked exploration; inspected call binding and role grouping remain heuristic.
* Understand: documented reusable entities/references supporting multiple evidence-preserving views.
* Joern: explicit semantic enrichment passes and bounded data-flow analysis.
* CodeSee/GitDiagram: focused presentation and coherent diagram contracts; appearance does not establish semantic accuracy.
* Sourcegraph: semantic index producer/consumer separation and reference navigation, with language-specific execution prerequisites.
* StructSAR: evaluate module grouping separately from source extraction; learned partitions do not establish services or resource usage.

For our platform, fix the three demonstrated failures, strengthen project/value resolution, then connect a complete entry-to-resource chain. Keep execution management and UI expansion secondary. These are recommendations, not implemented capabilities.

## Deliverables in assignment order

### 1. Individual technical investigations

1. [RepoDNA — deepest source review](01-repodna.md)
2. [SciTools Understand — documented parsed model](02-understand.md)
3. [Joern — CPG and semantic passes](03-joern.md)
4. [CodeSee — map interaction and unknown internals](04-codesee.md)
5. [GitDiagram — bounded context and model-generated graph](05-gitdiagram.md)
6. [Sourcegraph — SCIP and navigation](06-sourcegraph.md)
7. [StructSAR and architecture-recovery research](07-structsar.md)

### 2. Workflow diagrams

[Seven rendered Mermaid blocks and standalone diagram sources](workflow-diagrams.md). Each diagram describes the inspected or best-supported workflow. Static paths are not runtime traces; unknown internals remain labelled.

### 3. Comparative technical matrix

[All seven projects across the 22 requested dimensions](comparison.md), split into analysis, representation and execution tables for readability.

### 4. Our platform versus existing solutions

[Current position, reusable mechanisms and gaps](our-platform-vs-solutions.md).

### 5. Prioritized improvement proposal

[P0/P1/P2/deferred work, integration costs, risks and acceptance tests](improvement-proposal.md).

### 6. Final technical understanding

[Answers to the eight concluding questions](final-understanding.md).

## Evidence labels

* **Verified:** source code or formal schema inspected and supporting the stated mechanism. This is static verification, not successful execution or measured accuracy.
* **Documented:** official documentation describes behavior, but we did not independently reproduce it. For closed-source products this is the primary evidence class.
* **Inferred:** a reasoned consequence or design assessment, explicitly distinguished from implementation facts.
* **Unknown:** inspected evidence cannot establish the claim. Unknown is not proof of absence.

This convention deliberately avoids treating official marketing descriptions as independently measured capabilities. Synthesis and recommendation documents inherit the supporting report's qualifications; recommendation wording is our engineering judgment.

## Source inspection and reproducibility

Pinned public source snapshots:

| Project | Commit | Inspection scope |
|---|---|---|
| RepoDNA | `f05b17c12c9d8d4542fb58b6915507ff176217db` | Source archive; main web/Python pipelines, parser/resolver/adapter, graph/schema, flow/impact, cache and UI files; selected tests read |
| Joern | `0738a6199bc860a788b7f28b2779997f210c405d` | File inventory and selected frontend/pass/data-flow/storage-reference sources |
| GitDiagram | `7876ab0ca8b5ee46e836235e23c4886d5cdb79ae` | Current file inventory, ingestion/source-context, graph/compiler and architecture documentation |
| SCIP protocol | `bbec5345bfae602b31286a9ec74e2c2042713f50` | Formal protobuf schema and protocol README; Sourcegraph/indexer documentation separately |
| StructSAR | `6157b5cc8cff0dac4262f430fdeb9ba20e9faf7a` | Source archive; preprocessing, runner, graph builders, model/cluster/evaluation files and paper |

Downloads, repository tree inventories, commit metadata and a per-file SHA-256 manifest are under `output/research/platforms-2026-11-02/`. Archives were bounded/path-checked before extraction. Some archives include more files than were read; the manifest proves captured bytes, not that every file was audited. Reports identify the actual mechanisms inspected.

Source URLs in reports are pinned where possible. Commercial documentation is mutable; access date is the research date above. No proprietary parser/database implementation was reverse-engineered. Public source selection is not a complete security or license audit.

Public retrieval used the Windows HTTPS client after restricted Python networking/certificate validation failed. TLS verification was not disabled. No repository hooks, package managers, builds, analyzer applications, tests, trained models or uploaded-client sources were executed or sent to external model services. Research scripts only retrieved/hashed/read public material and generated these documents/diagrams.

## Limits of this exercise

* No live product walkthroughs, comparative execution, latency/memory measurements or accuracy experiments were performed.
* Existing local application source and earlier recorded artifacts were inspected as baseline. Historical test counts remain historical; tests were not rerun.
* RepoDNA public/private/browser/Python paths differ; findings do not automatically apply to every path.
* Joern documentation and current source differ on storage generation; the report records the pinned source's Flatgraph transition.
* CodeSee dependency maps and enterprise Service Map claims are distinguished. Service availability was not checked through an authenticated session.
* Sourcegraph navigation is not treated as architecture reconstruction. StructSAR clustering is not treated as route/resource extraction.
* No blanket “better than competitors,” universal accuracy, complete no-execution safety or enterprise scalability claim follows from this research.

The result is a source-grounded engineering basis for the next foundation changes, not another installed tool stack.
