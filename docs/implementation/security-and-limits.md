# Security controls and limits

This is a local, single-user development MVP. It is **not ready to accept hostile multi-tenant uploads as a publicly hosted service**. Bind the API to loopback. No authentication, tenant separation or OS sandbox is supplied.

## Implemented and tested

| Control | Implementation and evidence |
|---|---|
| No target execution | TypeScript parses supplied text using a confined compiler host. No target imports, plugins, builds, package installation, emission or lifecycle scripts. A fixture containing a filesystem write and throw is parsed without executing it. |
| Public GitHub allowlist | Only root HTTPS `github.com/owner/repo` URLs. API resolves HEAD to a 40-character commit SHA; codeload retrieves that SHA. No Git executable, hooks, filters, submodules or LFS fetching. No arbitrary destinations, redirects, credentials, environment proxies or TLS-verification bypass. Live retrieval tested with `octocat/Hello-World`. |
| Shared ingestion | Both methods use the same ZIP validator, extracted snapshot, `analysis.pipeline.analyze`, validator and SQLite store. API regression supplies identical bytes through both inputs and checks identical snapshot IDs. |
| Archive paths | Reject traversal, absolute/drive/UNC/ADS paths, Windows device names, control characters, ambiguous dot/space endings, repeated paths, case conflicts including parent directories, and file/directory conflicts. Paths are containment-checked after resolution. |
| Archive entry types | Reject symlinks and special file modes; reject encrypted archives. Nested archives remain inert files. |
| Archive quotas | 50 MiB compressed, 100 MiB actual expanded total, 12 MiB per file, 5,000 entries, 32 path components, 1,024-character relative path. Reject >200:1 compression for entries over 1 MiB. Declared sizes are checked before extraction; streamed sizes and CRC are checked during extraction. |
| Source integrity | Extract to a server-created private temporary directory; mark regular files read-only, hash every input file, recheck hashes after parsing. Remove temporary source after jobs. Read-only file flag is tested. |
| Worker resources | Two simultaneous jobs and four total running/queued slots. Fresh Node process per job; V8 heap limit 1,536 MiB, 120-second worker deadline, streamed stdout cap 64 MiB, bounded IPC queue. Worker inventory limit 4,000 files, parsed-text limit 32 MiB, relevant-file limit 1.2 MB, edge limit 150,000. Deadlines and cancellation tested. |
| Worker environment | Fixed trusted worker path and working directory; no stdin. Only PATH/system/temp environment variables are retained. `NODE_OPTIONS` and provider credentials are not inherited. |
| Network/process guard | Trusted worker blocks imports of common networking, child-process and thread APIs, and overrides global fetch. A direct `node:https` attempt is rejected by a test. Compiler resolution reads supplied text and trusted standard libraries. |
| Evidence integrity | Versioned Pydantic IPC validation; duplicate IDs, dangling endpoints/citations, implementation-body requirements, content hashes, UTF-16 ranges and start/end line/column checks. Invalid-column and dangling-target negative tests. |
| Output handling | Source snippets and environment values are not included in the graph/API. Common GitHub, secret-key, AWS access-key and credential-in-URL formats are masked in metadata. No subprocess stderr or unexpected exception details are returned to clients. SQL values are parameterized. |
| Browser | Local assets and system fonts. Browser acceptance test rejects nonlocal HTTP requests; final run observed none. ELK runs in a Web Worker; graph views and evidence/unknown pages have response caps. |

## Partially implemented or unverified

- **OS isolation is not implemented.** The Node module guard is defense in depth for trusted analyzer code. It can be bypassed by arbitrary native/process access and is not a security boundary. The worker has its host account's filesystem privileges. No Windows restricted token, Job Object, container, network namespace or firewall-enforced egress policy was established or tested.
- Read-only files are an accidental-write guard. The host account can restore write permission; directory ACL immutability and a read-only filesystem mount are not enforced. Filesystem fingerprints detect changes after analysis, rather than preventing all possible changes.
- V8 heap limits do not cap total RSS, native allocations, CPU share or disk space. Acquisition has request timeouts and an elapsed deadline checked while streaming; these are not an OS watchdog for every ingestion/parser operation. YAML has byte/event/depth limits. No adversarial-parser fuzzing campaign has been run.
- FastAPI receives/spools multipart bodies before endpoint streaming checks. An independently enforced HTTP body limit, slow-client deadline and rate limit at the server/proxy are still required for public deployment.
- Metadata pattern redaction is deliberately limited. It is not a comprehensive secret audit. Source filenames and citation paths are preserved; sensitive names or unfamiliar secret formats can remain. No Gitleaks scan is claimed.
- SQLite is local plaintext storage. Filesystem ACL review, encryption, authentication, retention/deletion controls, aggregate disk quotas, tenant ownership checks and a secure download/export policy remain work.
- Job execution assumes **one API process**. Do not use multiple uvicorn workers with this in-process queue. Startup marks previously queued/running jobs interrupted; it does not coordinate a distributed worker fleet.
- Do not start a project-root development auto-reloader that watches `data/`, `tmp/` or extracted repository files. Intake can create arbitrary source extensions and trigger a development restart. Use the documented command without reload, or restrict reload to trusted application directories.
- Cancellation during a network read can wait until the read timeout. Cancellation signals are checked between acquisition chunks and in worker orchestration; extraction itself has bounded size/count but no per-entry cancellation hook.
- GitHub retrieval supports public root repository URLs only. Private credentials, branch/subdirectory selectors, retry/backoff and GitHub rate-limit recovery are intentionally deferred.

## Analysis limits

Support is TS/JS only. Current project awareness uses the root tsconfig's path aliases and a supplied-source compiler host. Full `extends`, project references, nested compiler configurations, installed external declarations, generated OpenNext code and build-time transformations are not reconstructed.

Next app-route exports, a narrow bound-receiver Express adapter, Wrangler JSON/JSONC declarations and narrow Docker Compose YAML declarations are implemented. Express mount prefixes/middleware execution and broader frameworks are incomplete. Wrangler TOML, Kubernetes, Terraform and a generic YAML architecture interpreter are not implemented. Compose `depends_on` establishes a declaration about startup ordering, not traffic or database use.

Dynamic dispatch, callbacks invoked by frameworks, reflection, runtime environment values, custom database wrappers, dependency injection and conditional configuration propagation can remain unresolved. Relative frontend fetch URLs remain unknown unless their destination is independently established. Unused literals are not promoted into services. SDK construction/use establishes library usage, not an actual database/cache/server hostname. Imported signatures do not establish implementation calls.

Workflow arrows are static source relationships, not a timeline or a guaranteed execution path. Nested definitions are hidden by default and optionally displayed as dashed lexical links. Selecting a function enables exploration from that symbol. Depth/node/edge caps can omit supported neighbors; the response and UI expose truncation. Tests cover selected positive and negative cases; no labeled multi-repository accuracy corpus or accuracy percentage is claimed.
