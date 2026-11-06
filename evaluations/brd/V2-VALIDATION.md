# BRD lab v2 validation results

Date: 6 November 2026. Input: unchanged fictional ServiceBridge BRD. No project source code or evaluator answer key was sent to the model.

## Observed results

| Check | Observed result |
|---|---|
| Deterministic regression suite | 16 tests passed |
| Mocked browser checks | Desktop/mobile, sample input, HTML safety, downloads, saved history, model and source-ledger tabs passed |
| Real saved-result browser check | Completed Azure AI report, canonical model and original ledger reopened successfully |
| AI canonical-model pilot | Run 726b4801950f449897df998784303c36; 146.5 seconds; 23 entities, 18 relationships, 6 workflows; no structurally quarantined records |
| Staged repository pilot | Run d300aa8ac4ce4b039ec8f0601f32d766; 300.45 seconds; 46 entities, 52 relationships, 17 workflows; no structurally quarantined records |
| Repository traceability | 78 of 82 source blocks referenced; no explicit requirement IDs left without an accepted reference; this is not semantic coverage |
| Repository review exceptions | 8 lexical interpretation warnings; semantic correctness remains unverified |
| Repository token usage | 49,802 total provider-reported tokens across two stages |

The AI pilot exercised the shared canonical model and compiler before the final two-stage orchestration was introduced. The repository pilot exercised the final staged architecture. Do not describe both as identical pipeline measurements, or assume a live staged AI result has been evaluated.

## Targeted spot checks

The AI pilot separated answering, drafting, summarization, assignment, knowledge preparation and authorized status fetching. Drafting required approval; assignment was conditional; answering and summarization left approval unspecified. Candidate providers remained candidates, and MCP remained future scope.

The repository inventory retained all six roles and logical transactional, document, retrieval and job-state resources. The relationship stage represented all five named WF requirements. It kept draft generation separate from approved sending. Future MCP search and Teams notification workflows remained in the canonical model but were excluded from current intended diagrams; recording supplied MCP configuration remained a separate current requirement.

These are sampled checks against the BRD, not a complete hand-labelled evaluation of every claim. Record-to-source quotation matching does not prove the full interpretation. A represented requirement can still have clauses omitted or misunderstood.

## Failures found and handled

The deployment rejected the older max_tokens request parameter; the runner now uses max_completion_tokens. The deployment identifier did not establish the provider-reported model family. Early single-pass requests timed out or exhausted their completion budget without readable JSON. The runner withheld architecture reports for those failures and preserved diagnostic artifacts. Low reasoning effort and two bounded interpretation stages were introduced; neither is a guarantee that every future document fits the budget.

The staged pilot took about five minutes and more tokens than a short prose report. This upgrade adds validation and auditability; it does not establish a speed or cost improvement. Large-document partitioning, resumability, external Mermaid parser validation, graphical preview and a broad semantic benchmark remain future work.
