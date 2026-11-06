# BRD lab v2 design and evaluation limits

## What changed

V1 sent numbered document text to a model and accepted a finished Markdown report and Mermaid blocks. V2 builds a source ledger first, requests bounded JSON interpretations, validates individual records, and deterministically compiles the accepted model into a report and diagram sources. Two planned model stages identify inventory first, then relationships and workflows using validated identities. This is not a team of agents or a second unstructured review of the first report. Both stages receive the BRD ledger, so prompt cost can exceed v1; a lower per-stage reasoning burden is the reason for this split, not a claim of lower total token cost.

The reusable skills describe investigation methods. `intelligence.py` supplies the shared engineering layer. Both skills are independently invocable and use the same evidence and canonical-ID conventions. Source-code analysis is not part of this BRD lab and the existing static engine is unchanged.

## Data contracts

`source-ledger.json` preserves document hash, exact source blocks, section names, explicit requirement IDs, line ranges, block hashes and lexical modality cues. It includes objectives, acceptance paragraphs, roles and release gates. A block can have several cues; the lexer does not claim to resolve sentence semantics. Source IDs are snapshot-relative.

`schemas/proposal.schema.json` describes model proposals. The model returns actors, components, operations, resources, data, external systems and controls; typed relationships; independently scoped workflows; findings; and source dispositions. Records preserve modality, release, interpretation status, derivation, scope and exact quotations. Workflows distinguish human approval, automated validation, authorization, input data, output destinations and failure handling.

`intelligence-model.json` contains accepted records, coverage and validation exceptions. The original bounded response is retained as `proposal.txt`; invalid records are quarantined by canonical ID and reason. Their evidence cannot satisfy coverage through a rejected edge or workflow. Invalid JSON or a non-stop completion fails the run instead of publishing a truncated architecture. Failure metadata is retained separately.

## What is checked

- Required shapes, field types, enums and count/text budgets.
- Unique IDs, valid endpoints and workflow membership.
- Every accepted record cites existing nonblank ledger content with an exact normalized quotation.
- Report citations are generated from ledger locations rather than model-written line numbers.
- Mandatory and approval cue checks flag or quarantine some unsupported interpretations.
- A model's claimed representation does not count unless an accepted record actually references the source.
- Missing explicit requirement mappings and missing WF-ID workflows are visible.
- Diagram labels and IDs use a closed generated grammar; raw model Mermaid is never accepted.
- Future and prohibited records are excluded from intended current views; they remain in the model and report.
- Each diagram retains its canonical entity and edge IDs and enumerates view-budget omissions.

## What is not proven

Exact quotations can still be attached to an incorrect paraphrase. A paragraph containing a human-review phrase can still be mis-scoped. Record-level modality fields cannot capture every clause in a long mixed statement. A source marked context or not relevant may still have been misunderstood. A workflow may omit a conditional branch even if all its references exist. Source-block coverage is not sentence coverage, recall, semantic accuracy or feature implementation coverage.

The compiler emits a restricted flowchart grammar, but no external Mermaid parser is included. Therefore metadata says closed compiler grammar, not Mermaid parser verified. The UI exports diagram sources and does not yet provide graphical rendering. No general proof of semantic correctness, universal architecture recovery, source implementation, runtime behavior or actual data disclosure is claimed.

The current views are bounded to 24 overview entities and 40 per workflow. Canonical records remain available outside the view. Selection reserves a representative per semantic kind, then ranks external systems, resources and components ahead of detail, using graph participation and canonical IDs as tie breakers. This heuristic does not prove the best business abstraction. Model generation is not deterministic; compilation from the same validated model is deterministic.

## Evaluation

Run `python -m unittest discover -s evaluations/brd -p "test_*.py" -v`. Tests cover real ServiceBridge source indexing, malformed evidence, missing endpoints, separate workflows, unsupported approval, future connectors, false coverage claims, safe compilation and non-AI/adversarial document handling. These verify deterministic mechanisms with hand-authored model responses; they are not measurements of live model accuracy.

Run each skill again on ServiceBridge and use the separate evaluator guide to assess six roles, logical resources, five application workflows or four AI operations as appropriate, control scope, unresolved decisions and cited support. Compare semantic errors and omissions against the v1 reports. Do not convert passing unit tests or reference counts into an overall correctness percentage.

The model response budget is 14,000 completion tokens per stage, including reasoning where applicable. The provider timeout defaults to 300 seconds per stage and can be configured with BRD_TIMEOUT_SECONDS from 30 to 600 seconds. There are two planned stages and no automatic retries or repair calls. Large or complex BRDs may exceed those budgets; document partitioning and resumable investigation are not implemented yet. Either failed stage withholds the final report. Per-stage responses and usage are retained.

For reasoning-enabled deployments, BRD_REASONING_EFFORT can explicitly select low, medium or high. Leave it empty for deployments without that API capability. A deployment identifier is not proof of its underlying model family. Response metadata is preserved even when completion tokens are exhausted before readable JSON is produced.
