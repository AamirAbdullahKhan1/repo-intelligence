# BRD skill evaluation lab

**Current release: 2.1.** See [2.1 architecture and process changes](V21-DESIGN.md). New runs add evidenced operation ownership, component-level aggregation, structured workflow steps/guards, approval-bypass checks, lexical-fragment coverage and a concise report with a separate audit download. Historical analyses stay unchanged. The fixture directory contains additional domains and formats; support for every BRD is not assumed.

An isolated local interface for running either of two reusable BRD skills against an organization Azure OpenAI deployment. Version 2 adds a source ledger, canonical intelligence model, quotation/graph validation, coverage and deterministic report/diagram compilation. It does not modify the production repository-analysis pipeline. It uses Python's standard library and has no package installation step. See [v2 design and limitations](V2-DESIGN.md).

Each selected skill uses two planned model calls: inventory, then relationships/workflows using the inventory's validated identities. Neither skill invokes the other. Completion budgets and timeouts apply per stage; latency and token usage can be higher than v1. See [observed validation results](V2-VALIDATION.md).

## Start

From the repository root in PowerShell:

```powershell
if (-not (Test-Path evaluations/brd/.env)) { Copy-Item evaluations/brd/.env.example evaluations/brd/.env }
# Edit evaluations/brd/.env locally and set AZURE_OPENAI_API_KEY.
python evaluations/brd/server.py
```

Alternatively run `powershell -ExecutionPolicy Bypass -File evaluations/brd/start.ps1`. The launcher creates a blank local `.env` from the template if absent and locates Python on PATH or at the known user Python 3.12 installation. Add the key locally, stop the process and restart it. It does not install anything or change system policy.

Use your existing Python executable if `python` is not on PATH. Python 3.10 or newer is required. Open http://127.0.0.1:8766. The key is read only on the server and is never returned to the browser. After adding a previously empty key, refresh the page; replacing an existing key requires restarting. Environment variables take precedence over `.env`. The deployment identifier need not match the model actually reported by the provider; both are retained in run metadata.

Select a skill, load the sample or paste/upload a UTF-8 `.md` or `.txt` BRD, confirm Azure data sharing and run. For PDF or Word, extract and review text first; page/layout extraction is not included. Input limit is 100,000 characters. The inventory budget is 14,000 completion tokens; the richer relationship/process budget defaults to 22,000 (BRD_RELATIONSHIP_TOKENS, 2,000 to 24,000). The default provider timeout is 480 seconds per stage (BRD_TIMEOUT_SECONDS, 30 to 600). There is one active run and no automatic retry. Budgets include reasoning where applicable. Unsupported/over-budget output is withheld rather than silently truncated. The runner uses max_completion_tokens and does not assume temperature controls are supported. This is a bounded local pilot, not a large-document partitioning engine.

## Outputs and review

Each result is saved under ignored `results/<run-id>/` as concise `report.md`, complete `audit-report.md`, `result.json`, `source-ledger.json`, stage proposals/usage, `intelligence-model.json` and `.mmd` files. **The source ledger and audit preserve BRD text**, so treat these files as confidential. Audit content is fetched on demand rather than duplicated in every result response. JSON includes original and aggregated graph traces, process records, quality issues and lexical clause-quotation coverage; semantic correctness remains unverified. History reopens v1/v2 results unchanged; run a new analysis to use 2.1. Reports, audit and diagram sources can be downloaded separately.

The report preview renders a safe subset of Markdown, with no raw model HTML. Mermaid diagrams are exported as editable sources; this version deliberately does not execute model-generated diagram code or load external renderer scripts. There is no graphical Mermaid preview yet. Use an approved local Mermaid renderer if needed; do not paste confidential reports into public diagram sites.

V2 validates source IDs, exact quotations, required fields, unique graph IDs, endpoint/workflow references and claimed coverage. Unsupported records are quarantined. Report citations and Mermaid are compiled from accepted records. Non-stop provider responses are failed, not published. Exact quotations do not prove semantic entailment and no external Mermaid parser is run. Use `docs/fixtures/brd/ServiceBridge-evaluator-guide.md` separately for human evaluation. That guide is never included in the model request.

## Scope and controls

This is a single-user local evaluation tool, not a tenant-ready service. It binds to loopback, checks Host and a per-process request token, serves no cross-origin permissions, disables redirects for credential-bearing Azure calls and loads no third-party browser resources. Do not expose it through a public tunnel or reverse proxy. The selected BRD and selected skill instructions are transmitted to the configured Azure resource. Existing source code, other skills, expected answers and previous reports are not included.

Keep `.env` and `results/` private. Results can contain confidential material and are stored as plaintext local files; delete their run directories locally when no longer needed. There is no secure erase, authentication, tenant isolation, comprehensive redaction or production audit service in this pilot. Closing a browser does not cancel a running Azure request; do not start another submission until it has finished. Interrupted runs are not automatically resumed. The model has no tools or access to local files beyond the supplied prompt.

Skill files contain normal SKILL.md metadata and Markdown instructions, but this runner explicitly loads them as a system message; it is not a universal host-agent runtime. Both skills currently support BRD-only input. Source analysis and combined BRD-to-code comparison remain outside this lab.

## Verify without credentials

To rebuild validation and reports from a completed 2.1 interpretation without calling Azure:

```powershell
python evaluations/brd/reprocess.py <saved-analysis-id>
```

This creates a new saved result with its parent ID, zero new model usage and separately recorded original analysis cost/time. It does not overwrite history, reinterpret the BRD or migrate older contracts by guessing ownership or process steps.

```powershell
python -m unittest discover -s evaluations/brd -p "test_*.py" -v
```

Tests stub Azure responses and make no live model requests. The Azure REST request uses the deployment-scoped Chat Completions endpoint and `api-key` header. References: [Azure Chat Completions](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/chatgpt), [API version lifecycle](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/api-version-lifecycle).
