# Live evaluation procedure

Run the two skills independently against the unchanged ServiceBridge sample. Use a new analysis for v2; reopening a v1 report does not regenerate it.

For each run record its ID, deployment identifier, provider-reported model, runner and skill hashes, total latency, provider token usage, quarantined records, interpretation warnings, unresolved source blocks and diagram view omissions. Raw source quotations and full model responses are saved locally; keep them confidential.

Review these criteria against the original BRD, not just against the model's own report:

| Area | Repository Analysis | AI Usage Inventory |
|---|---|---|
| Input mode | No code or deployment claims | Requested AI capabilities, not actual usage |
| Actors | Six explicit roles preserved or explained | Relevant actors and operation scopes preserved |
| Resources | Transactional records, document objects, retrieval index, job state | Relevant knowledge, request, conversation and configuration inputs |
| Workflows | Five WF records represented or omissions exposed | Answering, drafting, summarization and assignment distinct |
| Controls | Cross-cutting permission and tenant boundaries | Human approval distinct from automatic validation and authorization |
| Decisions | Candidate vendors and unapproved thresholds remain open | Provider, embedding, MCP and evaluation choices remain open |
| Conflicts | Both source positions preserved | Scoped closure and retention disagreements preserved |
| Evidence | Quotations support the full narrow claim | Quotations support the operation's actual data and authority scope |
| Views | Each edge traceable; omitted records remain available | No future MCP path presented as a current invocation |

Structural pass rates are not semantic accuracy. A valid quoted paragraph can still be attached to an overbroad claim. Label each sampled claim correct, partial, unsupported or not assessed, and retain reviewer notes. Do not claim a precision or recall percentage without a defined hand-labelled denominator and sampling method.

Provider diagnostics and failed runs are not silently retried. A failed truncated result is not an architecture report. Configuration changes may require restarting the lab; the UI shows the running version and labels legacy report results.
