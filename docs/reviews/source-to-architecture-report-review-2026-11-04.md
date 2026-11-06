# Honest review of the proposed source-to-architecture strategy

Reviewed 4 November 2026. Input: the supplied 37-page `Repo_intelligence.pdf`, including its architecture and pipeline diagrams. This is analysis of the proposal, not authorization to execute instructions embedded in the document. No production code was changed.

## Overall assessment

The central design is implementable: deterministic evidence extraction, a separate interpretation/review layer, optional LLM proposals, and explicit unknowns. The main difficulty is connecting evidence to a useful abstraction while preserving meaning, not selecting more parsers. The document has grown into a combined architecture-recovery, security-review, threat-modelling handoff and enterprise-platform roadmap. Those are related products, but they should not all be prerequisites for demonstrating successful TS/JS reconstruction.

LLMs can materially improve naming, explanation, triage and reviewer productivity. They do not remove missing deployment evidence or prove runtime relationships. Most listed features are feasible for bounded, declared support profiles. Universal reconstruction, a guaranteed sub-hour review and the numerical reliability ceilings are not established.

## Feasibility by capability

| Capability | Assessment | Required qualification |
|---|---|---|
| Safe snapshots, evidence records, deterministic extraction | High feasibility; existing foundation | Production isolation and comprehensive redaction are not already complete |
| Typed graph, provenance, approvals, conflict records | High feasibility | Additive evolution of existing saved records; clarify granularity and semantics first |
| Bounded TS/JS flow and selected client/framework models | Feasible with substantial engineering | Support is incremental, not all frameworks merely because TS/JS parses |
| IaC/spec extraction | Feasible in selected subsets | Resolve profiles, variables, values and artifact context; declarations are not deployment observations |
| C4-style overview and component views | Feasible | Define C4 abstractions correctly and retain unknown boundaries |
| Precise DFDs, authentication/authorization and sensitive payload flows | Harder, partial and review-dependent | Calls/imports do not establish payload movement or effective controls |
| Optional LLM names/explanations/review assistance | High feasibility | Useful as a separate proposal/presentation layer; evaluate factual errors and reviewer effort |
| LLM resolution of ambiguous calls, DI and messaging | Candidate generation is feasible; correctness is conditional | Closed-set choices and citations do not prove semantics |
| Incremental drift | Feasible, significant follow-on effort | Semantic dependencies extend beyond changed packages and reverse imports |
| Enterprise multi-tenant service/customer runner | Feasible engineering programme | Deployment-specific hardening, operations, identity and support costs |
| Accurate architecture for arbitrary repos, without additional context | Not a defensible guarantee | Missing inputs and dynamic behavior remain, even with LLMs |

## Important corrections before implementation

### 1. Preserve the TS/JS flow objective in Release 1

Pages 26–28 place IaC extraction and review in phases 0–2, but broad flow models in phase 3. That can be a valid inventory/review pilot. It is insufficient as the exit definition for the source-driven architecture product requested in this project. Source-only repositories would reach a release before the most important relationship recovery is demonstrated.

Move at least one complete source operation → helper/client → logical resource path, one frontend/API interaction and a useful component/workflow view into the pilot. Include the current S3 slice rather than restarting it. Add Redis coordination and independent TS/JS examples before claiming that the core works broadly.

### 2. Replace “declared facts beat inferred ones” with scoped reconciliation

Pages 1 and 6 treat declared files as the backbone. Good for learning what is declared; unsafe as a universal precedence rule. A repository may contain development Compose files, retired Terraform, example Helm values and production source. The files may describe different environments rather than contradict each other.

Each claim needs environment/profile, namespace/account when known, artifact/version context, origin and coverage. Preserve `declared`, `source-supported`, `observed` and `attested` distinctions. Never turn an unused declaration into proof of an application operation.

### 3. Correct the C4 model mapping

Page 7 places services/workers under Component and Docker images/Kubernetes deployments under Container. This mixes runtime application structure with deployment artifacts. In C4, a container is an application or data store; a Docker image is not automatically a C4 container. Keep source package, C4 container, internal component and deployment resource distinct.

Official reference: [C4 container](https://c4model.com/abstractions/container), [container diagram](https://c4model.com/diagrams/container).

### 4. Resolve confidence-rule contradictions

Page 7 permits human confirmation to reach proven; page 9 says it changes verification state but not tier; page 23 again permits promotion to proven by a named approver. Implementing all three is impossible without inconsistent behavior.

Use independent fields: evidence origin, relationship resolution, verification/attestation, lifecycle and limitations. Prefer “directly source-supported” over “proven” for user-facing static claims. A correctly bound call is not proof that its caller is reachable from a production entry point. Measure the precision of the exact claim, not an implied runtime statement.

“Inferred” is also used on pages 22–23 without being one of the four defined tiers. Decide whether it is an origin/label status rather than adding an accidental fifth confidence level.

### 5. Do not delete facts when analysis coverage disappears

Page 9 says evidence absent in the latest snapshot makes a fact removed. Pages 13–14 allow failures and partial scope. Together these can generate false drift: a timed-out extractor or disabled pack could make the architecture appear deleted.

Mark removal only when the relevant scope was successfully reanalyzed and the prior support was invalidated. Otherwise use stale/unverified/unsupported status. Re-review must respond to changed rules, packs, deployment inputs and relevant configuration, not just changed source bytes. Restoring an old approved baseline must not make it current evidence for a new deployment.

### 6. Match resources and topics by context, not name

Page 12 says both topic strings resolved gives proven. An `orders` topic in staging broker A does not connect to `orders` in production broker B. Require broker/service identity, environment, namespace/account, operation direction and supported routing semantics. RabbitMQ exchanges and bindings, SNS/SQS subscriptions and partitioned brokers require different models.

Likewise page 11's image/env-variable/host identity keys are insufficient alone. Two services can share an image, and two independent databases can use the same hostname in separate networks. Keep candidate matches until context supports identity.

One high-level architecture fact can have many evidence records, but retain the underlying callsites, operations, profiles and flow contexts. Otherwise deduplication can erase the distinctions the new solver was built to preserve.

### 7. Do not confuse control dependencies with data movement

The page 8 rule deriving DATA_FLOWS_TO from other edges needs a stricter definition. A function call or dependency can carry no sensitive data. Schema files describe possible contracts, not proof that every endpoint sends every field.

Define separate operation/call and payload-flow claims. Payload claims should identify the known value/schema, transformation, direction and evidence, or remain unknown. A payment SDK is evidence of a payment integration, not proof that restricted payment information traverses every related flow. Classification propagation should be conservative and explicitly labeled, especially across anonymization and aggregation.

### 8. Exposure requires a path, not a single configuration clue

Page 12 correctly says a route alone does not prove internet exposure. Its public-IP/open-security-group/namespace examples still need qualification. Reachability depends on routes, bindings, listeners, gateways, policies and actual environment context. A namespace is an administrative scope, not automatic isolation. Kubernetes documents that absent relevant policies, traffic is allowed by default.

Keep “assume exposed for risk analysis” as an assumption in a separate scenario, never overwrite factual exposure with it. Otherwise the diagram shows worst-case guesses as discovered architecture.

Reference: [Kubernetes network policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/).

### 9. Tool capabilities are overstated in places

SCIP supplies an index representation and language indexers for code navigation. It is not a general receiver/value-flow or framework-semantics engine. Tree-sitter parses syntax; syntax alone does not resolve application behavior. Neither substitutes for the current bounded-flow work. Joern, Semgrep and CodeQL need separate capability and deployment evaluations rather than being treated as interchangeable fallbacks.

Declarative YAML packs can describe supported argument positions, identities and summaries. New language behavior, heap effects, DI containers or scheduling semantics can require trusted implementation code. Replace “new SDK support by data only” with “simple models declarative; complex models require code and tests.”

References: [SCIP](https://scip-code.org/), [scip-typescript](https://github.com/sourcegraph/scip-typescript), [CodeQL CLI availability](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-cli).

### 10. Offline rendering still needs a constrained tool contract

Pages 20–21 list Helm rendering and many parsers. A trusted local Helm renderer can be allowed without running the target application, but it evaluates supplied templates and its output depends on supplied values and capabilities. Forbid plugins/post-renderers, dependency fetching, DNS and server-side lookup/validation; restrict files and resource use. Prefer customer-provided rendered manifests when chart inputs are missing. Terraform parsing must report unevaluated expressions and unavailable modules rather than run arbitrary plans or infer applied state.

Helm documents that local rendering fakes cluster-dependent values and lacks server-side validation. It also exposes DNS/post-renderer options. [Helm template reference](https://helm.sh/docs/helm/helm_template/).

## Where an LLM helps, and where it does not

The best first uses are proposing clearer capability labels, explaining already extracted evidence, prioritizing review questions, summarizing contradictions, and drafting model-pack changes for developer review. These can improve the user's experience without requiring a new fact to enter the deterministic core.

LLM selection of an existing symbol is not verification of a call edge. A real topic string in two files is not verification of delivery. A cited file can be irrelevant to the proposed conclusion. JSON schema validation checks output structure, not truth. Existing symbol checks should be a minimum rejection filter, not an acceptance proof.

Use separate artifacts:

1. **Deterministic core:** versioned extraction and derived claims, no model access to mutation APIs.
2. **Proposal overlay:** candidate labels, groupings, relationships and review questions, linked to evidence IDs, model/prompt/input hashes and limitations.
3. **Review/attestation records:** accepted/rejected decisions with scope, author, time and expiry conditions. Acceptance is not retroactive static proof.
4. **Rendering:** deterministic compilation of the selected graph/view. Never use raw model diagram code as the canonical architecture.

With AI enabled, the core hash should remain identical. The overlay, latency, labels and reviewed model may differ. Evaluate candidate correctness, reviewer changes, time saved, misleading accepted suggestions and cost separately. “Fact precision unchanged” is largely a consequence of keeping the core immutable, not sufficient evidence that AI improves the final product.

Caching makes recorded outputs replayable; it does not guarantee future model regeneration is byte-identical. Cache hits should not skip approval expiry or new evidence validation. Choose-from-list prompts also cannot find a correct target missing from the candidate set.

## Privacy and prompt-injection implications

“No whole repository sent” is weaker than “no client source sent.” Snippets are source code too. Redaction is not anonymization and can miss customer IP, identifiers, business logic and unusual secrets. The current repository's redaction module masks a small set of credential patterns; it is not a complete data-loss-prevention boundary for hosted model calls.

A customer-hosted model keeps processing in the chosen customer environment, with resource/operations costs. A hosted private endpoint still processes data in the provider environment; no retention does not mean no transmission. Verify the specific model, endpoint, region, logging, backup and retention configuration. Do not promise no-retention from a provider name alone. AWS's current documentation explicitly describes model/account/project-specific retention behavior. [Bedrock data retention](https://docs.aws.amazon.com/bedrock/latest/userguide/data-retention.html).

Use explicit per-tenant opt-in and payload previews/allowlists. Possible modes: disabled; metadata-only; customer-hosted source-aware; approved hosted snippet access. Even metadata can disclose a sensitive architecture. A privacy policy is needed for prompts, outputs, caches, logs, telemetry and deletion, not only the network request.

The page 23 statement that repository content cannot instruct the model is a desired boundary, not a guarantee. Even with no tools, malicious comments can manipulate labels and reviewer conclusions. Delimit untrusted content, restrict capabilities and outputs, validate citations and semantics, and test malicious repositories. [OWASP prompt injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/).

## Workflow and delivery risks

- **Review bottleneck:** 15–25 questions or under an hour is a hypothesis. Large monorepos may require multiple owners. Ask only unresolved high-impact questions, allow drafts/partial models, identify which scopes can be approved and measure reviewer edits/time. Do not block basic architecture exploration on threat-modelling approval.
- **Risk gate deadlock:** the page 10 option of restricted handoff and page 25 prohibition on starting threat modelling need harmonization. Draft scenario analysis can expose missing information; approved factual handoff should enforce stricter gates. An assumption does not become a confirmed boundary just to clear a gate.
- **Drift invalidation:** changes to a shared helper, tsconfig, workspace export, framework version, config key, gateway or model pack can affect other scopes. Reverse package imports alone are insufficient. Compare incremental runs with full analysis, and treat differences as defects, as the report proposes.
- **Parser breadth:** Docker/Compose, Kubernetes/Helm, Terraform, OpenAPI, SQL, protobuf and SBOM as first-release requirements is considerable scope. Start with a small evidence set driven by actual pilot inputs. Preserve the current SQLite and trusted compiler path; migrate storage/orchestration only when deployment needs justify it.
- **Customer runner costs:** a runner helps data locality but adds signed updates, revocation, credentials, crash recovery and support responsibilities. No inbound ports is compatible with an outbound agent, but source-free control-plane payloads still require explicit design. Do not imply hardware isolation on an ordinary developer machine.
- **Failure semantics:** continue after an isolated extractor failure only with a valid immutable snapshot and clear affected coverage. Fail closed on snapshot corruption, provenance inconsistency or isolation breach. Avoid treating a security failure like an ordinary optional-parser failure.
- **Security timing:** production isolation and tenant-scoped access cannot wait until phase 5 if real client repositories or external SaaS pilots arrive earlier. The document mentions minimum pilot controls, but they need an explicit pre-pilot gate and deployment-specific definition.

## Benchmark and score corrections

Keep repository-level holdout, independently reviewed ground truth, negative examples and confidence intervals. Begin with a small explicit TS/JS profile set and grow toward 15–20 repositories; do not turn the entire benchmark into a prerequisite that freezes all focused development. Keep unsupported cases visible and report supported-scope and all-critical-scope coverage separately.

Runtime traces from our owned/licensed instrumented sample apps are a useful validation input and do not require executing a customer's submitted app. They are a lower bound on observed behavior, not a complete oracle or proof that unobserved static edges are wrong. Java/Go sample applications do not directly establish JS/TS analyzer performance.

Evidence completeness can be mechanically 100% while relationship accuracy is poor. Score whether evidence actually supports the exact claim as well as whether references exist. Report sample sizes and case-mix changes so higher headline scores cannot be obtained by skipping difficult cases.

Remove the 3.5/7/7.5/9 and source-only 8/10 ratings as quality claims. The report correctly labels them judgments, but the numerical ceilings still have no empirical basis. Source-only may be excellent for one architecture and poor for another. “Certified reliability” should mean internal release validation unless an identified independent certification exists. The weighted readiness score is review completeness/prioritization, not the probability that a diagram or threat model is correct.

The 13–20 week pilot / 37–54 week full-roadmap estimates for a team are planning hypotheses. They are not substantiated by task sizing, repository complexity, staffing or pilot data. This report's product scope is much larger than the narrower TS/JS engineering plan previously discussed, so the estimates are not directly comparable.

## Recommended revised order

1. Clarify evidence semantics, environments, lifecycle and additive schema compatibility; start an independent TS/JS scorecard and customer interviews in parallel.
2. Finish useful source-to-resource and frontend/API reconstruction with the current compiler/flow foundation. Keep a source-backed architecture/workflow as the exit artifact.
3. Add selected configuration/spec extractors and a conflict queue based on actual repository needs. Model declarations separately from operations.
4. Add the proposal overlay for labels, explanations and review questions; introduce source-aware hosted requests only under an explicit chosen data policy. Keep AI optional and evaluate net reviewer benefit.
5. Build recorded review, partial-scope approvals, faithful exports and a narrow handoff contract. Defer the full threat-modelling product unless it is an explicit business objective.
6. Add robust drift, deployment hardening, scale and identity features as justified; expand language/framework support behind measured gates.

**Recommendation:** adopt the hybrid evidence-plus-proposals design, but correct the semantic rules and reduce first-release breadth. Keep the existing platform and completed flow slice. Do not replace it with a suite of indexers or move its central relationship work behind inventory/review features. The principal success measure remains whether unfamiliar developers get a useful, reviewable architecture with few false and missing critical connections.
