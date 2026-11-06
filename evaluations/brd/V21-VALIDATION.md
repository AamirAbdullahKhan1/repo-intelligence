# Version 2.1 evaluation record

Date: 6 November 2026. All live inputs were fictional. No client repository code, evaluator answer key or credentials were included in model prompts.

## Verified mechanisms

The regression suite contains 35 tests for source preservation, normative headings, bullets/tables/plain text, Unicode evidence, ownership and aggregated provenance, unknown vendor selection, workflow guards, approval bypasses, invalid process evidence, source-fragment coverage, scope-difference warnings, safe output, model failure handling, AI absence and local revalidation. Mocked Chrome checks cover desktop/mobile, report and audit downloads, history, source/model tabs and HTML injection prevention.

The additional domain fixtures are procurement, clinical appointments, warehouse dispatch tables, vague future AI, multilingual procurement and adversarial vendor text. Automated fixture tests verify deterministic mechanics with hand-authored interpretations; they do not prove model accuracy for every domain or language.

## Live observations

| Input and skill | Observed result |
|---|---|
| Procurement with Repository Analysis | 60.36 seconds; 10 entities, 8 relationships, 3 workflows. Unspecified ownership and incomplete rejection-process structure were exposed as review findings. |
| ServiceBridge with Repository Analysis | 304.08 seconds; 50 entities, 48 relationships, 12 workflows. Overview had 14 connected nodes and 17 aggregated relationships. Request management and AI coordination became explicit components. |
| Procurement with AI Usage Inventory | 11.7 seconds; zero AI entities, workflows or diagrams. One inventory call; the relationship call was skipped. |

ServiceBridge retained intended generic generation, embedding, email and storage capabilities while keeping vendor choice unresolved and named vendors as candidates. It represented knowledge publication as nine steps/eight transitions and draft/review/send as five steps/four transitions. It still had missing approval linkage in assignment, absent process detail in some workflows, and incomplete failure branches. Those gaps were reported; unsafe process views were suppressed rather than certified.

The main ServiceBridge report was about 199 lines versus about 1,580 in the previous reviewed export. Full details remain in the separate audit and JSON. About 46,191 total provider-reported tokens were used in that live run. This single observation is not proof of lower cost or faster performance on other BRDs.

A first full 2.1 inventory attempt exhausted its reasoning budget without readable output. It was withheld. The inventory policy was narrowed and its completion budget made configurable before the successful run. There is no automatic retry or repair loop.

## Remaining limits

Exact quotations, ownership references, branch topology and approval-path checks do not prove semantic completeness. Lexical fragments are not formal obligations. English lexical heuristics have limited cross-language coverage; structured per-action approval fields avoid relying solely on English action names. Complex layout extraction, scanned documents, independent Mermaid parser validation, graphical preview, long-document partitioning/resume and a broader hand-labelled semantic benchmark remain future work.

The runner is still a single-user local evaluation application. These are enterprise-oriented analysis improvements, not production authentication, tenant isolation, encryption-at-rest, tamper-proof auditing or a certification of enterprise readiness.
