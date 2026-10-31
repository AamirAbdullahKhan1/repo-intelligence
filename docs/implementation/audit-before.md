# Before-change implementation audit

Date: 31 October 2026. Recorded before restructuring. This is the initial audit, not an assertion that the requested integration already exists.

## Existing structure and execution paths

```text
backend/app/services/{analysis,architecture,repository,llm,threat_model,reporting}
backend/app/schemas/{analysis,architecture,health,...}
backend/app/api/v1/endpoints/{analyze,health,capabilities}
frontend/src/{pages,components,context,services,types}
tools/static-poc/{analyze.cjs,run.py,tests,assess.py,verify-ui.cjs}
frontend/public/static-poc/gitdiagram.json
output/{research,review,static-poc}
```

- Production `/analyze/github` and `/analyze/upload` synchronously ingest/analyze inside async request handlers and call `AzureLLMService`. The legacy builder uses regex heuristics, fabricated fallback edges and fixed workflow templates. These outputs cannot be promoted as evidence-validated static results.
- The separate proof of concept uses TypeScript 5.9.3 from **frontend/node_modules**, a confined compiler host, Node source parsing, source locations, a Python range/reference validator, SQLite and three projections. It is invoked manually; its static public JSON is not a job API or saved-analysis browser.
- Frontend context persists legacy results in sessionStorage; the static page bypasses API/context. Legacy graph state can remain stale after filters change. The experiment updates controlled graph state but has manual columns and dense component graphs. No ELK integration exists.
- ZIP extraction has size/count limits but uses a string-prefix containment check, skips rather than rejects symlinks, and lacks normalized duplicate/case-conflict checks. ZIP wrapper normalization is absent in the legacy API.
- Git intake uses shallow clone with only hook/prompt suppression; global Git configuration/filter/LFS implications and hard retrieval quotas are incomplete. Workspaces are temporary and results/source identity are not durably tied to API snapshots.
- Legacy tests primarily check fixture output presence; some assert the old fabricated graph/LLM capability and need replacement with current contract tests. The ten proof-of-concept regressions genuinely test static resolver behavior and will be migrated intact.
- `.env` and `.env.example`, Settings, dependencies, endpoint orchestration, errors, capabilities, README and old UI types contain obsolete provider configuration. Actual credential values were not printed during this audit.

## Installed state observed

| Tool | Observed state before changes | Actual use |
|---|---|---|
| TypeScript | 5.9.3 in frontend | POC worker imports it via frontend path |
| React Flow | reactflow 11.11.4 plus duplicate react-flow-renderer 10.3.17 | UI imports reactflow; old package redundant |
| SQLite | Python runtime 3.45.3 | POC artifacts only, not API jobs/history |
| PyYAML | 6.0.3 in backend venv | Installed; no active shared config stage |
| ELK | Not installed | No automatic hierarchical layout |
| Syft | Not on PATH | No integration |
| NetworkX | Not installed in backend venv | Not used; basic projections do not require it |
| Tree-sitter / ast-grep / Semgrep / Gitleaks | No corresponding CLI on PATH | Not integrated; absence from PATH alone does not inventory every machine environment |
| OpenAI | 1.57.0 in backend venv | Active legacy Azure client; must be removed |
| ReportLab | 4.2.5 in backend venv | Declared for planned PDF, not needed by current product path |

## Retain / replace decisions

Retain the compiler-backed worker and its ten regressions; retain source/range validation and improve its schema handling; retain working React Flow and FastAPI shells. Move implementation ownership into backend/worker packages and shared contracts. Replace the legacy graph producer/API/context, not the whole product indiscriminately. Replace unsafe ingestion internals while keeping URL/ZIP behavior. Remove inactive threat/PDF placeholders from current navigation. Generated outputs remain outputs; historical research is labelled historical and not an active dependency list.

Before mutation, preserve the working-tree patch and the five pre-existing edited backend files under ignored `tmp/restructure-backup`. No actual `.env` values go into backups/reports. A versioned archive of old application source is not retained as runnable product code. Audit report and git history explain the retired implementation.

## Planned controlled phases

1. Establish the shared contract and independent worker package; migrate static regression tests.
2. Remove provider implementation/configuration/dependencies and unused legacy producer.
3. Implement safe shared ingestion, job/result persistence and the common pipeline.
4. Integrate API/context/history/evidence and two bounded projections; ELK handles layout.
5. Test ZIP/GitHub, saved reopening, static call evidence, layout/view switching and documented security limits. Re-run tool inspection and publish actual statuses.
