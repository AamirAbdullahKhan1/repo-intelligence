# ServiceBridge Business Requirements Document

Document ID: SB-BRD-001  
Version: 1.0  
Date: 6 November 2026  
Status: Draft for business and architecture review  
Business owner: Enterprise Service Operations  
Audience: Product, engineering, architecture, privacy and service operations teams

## 1 Purpose and business context

ServiceBridge will provide a shared service portal for organizations that manage employee support requests. Employees currently submit requests through disconnected email inboxes, and support teams repeatedly search policy documents and manually transfer requests between departments. We need a tenant-aware application that manages requests, retrieves relevant knowledge and offers optional AI assistance while retaining human control over consequential actions.

This document defines intended business behavior and selected design constraints. It is not an implementation report. No source repository, production deployment record or runtime evidence accompanies this document. Product names listed as candidates are not final selections. All organizations, people and examples in this document are fictional.

## 2 Business outcomes and scope

OBJ-01: Reduce median request assignment time by 30 percent relative to the pilot team's measured baseline within three months of rollout. The baseline must be collected before the pilot.

OBJ-02: Allow employees to find approved answers with citations and escalate unanswered questions into tracked requests.

OBJ-03: Give administrators a traceable record of request updates, AI suggestions, approvals and integration failures.

V1 includes employee self-service, agent queues, knowledge ingestion, retrieval assistance, notifications, audit reporting and optional AI response drafting. Native mobile applications, autonomous refunds, payroll changes and automatic employee access provisioning are outside V1. A responsive browser interface is required.

## 3 Users and authorization

ROLE-01 Employee: Creates and views permitted requests, searches approved knowledge and gives answer feedback.

ROLE-02 Support agent: Works assigned queues, updates requests, reviews AI drafts and sends responses.

ROLE-03 Knowledge editor: Publishes and withdraws documents within an assigned tenant and department.

ROLE-04 Tenant administrator: Manages tenant settings, department roles, integration configuration and usage limits.

ROLE-05 Auditor: Reads authorized audit records without modifying requests or tenant configuration.

ROLE-06 Platform operator: Operates the shared platform. Routine operational access must not grant unrestricted access to tenant document contents.

AUTH-01: Users shall authenticate through their organization's OpenID Connect identity provider. Group-to-role mappings shall be tenant-specific. Authentication and tenant authorization must also apply to background jobs and integrations where relevant; a valid login alone is insufficient to authorize access to another tenant's records.

Acceptance: An employee from Tenant A cannot retrieve Tenant B's request through a guessed identifier, search result, attachment URL or assistant citation. A support agent without a department assignment cannot access that department's restricted knowledge.

## 4 Request management requirements

FR-01 Request submission: An employee shall create a request with subject, description, category and optional attachments. A successful submission returns a reference number. Repeated submissions with the same tenant-scoped idempotency key shall not create duplicate requests.

Acceptance: Retrying a timed-out submission with the same key returns the original reference. An unauthorized or oversized attachment is rejected with an understandable reason.

FR-02 Request lifecycle: Requests shall support New, Assigned, In progress, Waiting for employee, Resolved and Closed states. Each state change records actor, timestamp and previous and new state. Reopening rules shall be configurable by the tenant.

FR-03 Assignment: Assignment shall consider tenant, category and department. AI may suggest a category and queue, but deterministic eligibility checks shall prevent assignment to an unauthorized team. Low-confidence suggestions shall require agent review. The confidence threshold has not been approved.

FR-04 Conversations: Employees and agents shall exchange messages on a request. Internal agent notes must not appear in employee responses, search results or assistant context accessible to employees.

FR-05 Notifications: Assignment, employee reply and resolution shall trigger email notifications. Failed delivery shall be retried without duplicating a business event. Microsoft Teams notifications are desirable after the email pilot, subject to tenant approval.

FR-06 Search: Agents shall search requests by reference, permitted text, status and department. Search filtering must enforce authorization before returning results or counts.

FR-07 Scheduled processing: A background process shall identify requests approaching their configured response deadline and create escalation notifications. A failed run must be recoverable without generating duplicate escalations.

FR-08 Reporting: Tenant administrators shall view request volumes, assignment times, resolution times and AI acceptance rates. Metrics must identify their time window and exclude records the viewer cannot access.

## 5 Knowledge and document requirements

KN-01: Knowledge editors shall upload PDF, DOCX and Markdown documents. Each document records tenant, department, owner, version, effective date and access classification. Image-only PDFs may be rejected in V1 with an explanation; OCR is not committed for V1.

KN-02: Uploaded documents shall enter a processing workflow that extracts text, divides it into retrievable passages, creates embeddings and indexes passages with access metadata. Processing status shall distinguish pending, completed, failed and withdrawn documents.

KN-03: Replacing a document shall preserve its audit history and prevent superseded passages from being used for new answers after the replacement is published. How existing conversations display withdrawn citations needs a product decision.

KN-04: Search and retrieval must filter by tenant, department access and document publication status. A similarity match is not authorization to disclose a passage.

KN-05: Attachments shall be stored separately from transactional request records. Download access shall expire and shall be authorized for the requesting user. The storage vendor and scanning service are not selected.

## 6 AI assistance requirements

AI-01 Answer assistance: An employee may ask a question against published knowledge. The assistant shall retrieve permitted passages, construct grounded context and produce an answer with document and passage references. When the available material is insufficient, it shall state that it cannot establish the answer and offer escalation.

Acceptance: A question without supporting material must not produce a fabricated policy citation. A response citing a passage must link to a document version the employee is authorized to view.

AI-02 Drafting: An agent may request a response draft using the current request and permitted knowledge. The agent shall review and explicitly send the response. Generating a draft must not send a message or close the request.

AI-03 Summarization: An agent may generate a conversation summary. The summary shall be identified as generated content and shall distinguish employee-visible messages from internal notes. It must not change the underlying request record automatically.

AI-04 Model configuration: Tenant administrators may select an approved model profile within centrally allowed policies. Configuration shall identify model purpose, provider endpoint reference, model identifier, request limits and credential reference. Secret values must not be embedded in reports or client-visible configuration.

AI-05 Provider options: Azure OpenAI and an approved OpenAI-compatible enterprise gateway are candidates for generation. An embedding provider is not selected. Neither an SDK choice nor an actual deployed model is established by this document. Fallback routing must never bypass a tenant's region or provider restrictions.

AI-06 Streaming: Answers should appear incrementally in the browser. Cancellation shall stop further user-visible output and attempt to cancel upstream work. If upstream cancellation is unsupported, usage accounting must record the limitation.

AI-07 Structured suggestions: Category and assignment suggestions shall use a defined output schema and be validated against tenant-permitted categories and queues. Malformed output shall not update the request.

AI-08 Tool boundaries: The assistant may retrieve permitted knowledge and fetch the status of the current authorized request. It shall not send email, alter identity roles, execute shell commands or close requests autonomously in V1. Tool access requires server-side authorization independent of model output.

AI-09 Optional MCP integration: A future knowledge connector may use a tenant-approved MCP server to expose document search. V1 shall record connector configuration if provided, but connection, tool discovery and invocation are outside the V1 commitment. The transport, server product and authentication design are unspecified.

AI-10 Feedback and accounting: Users may mark an answer useful or not useful. Record profile reference, model identifier as requested, latency, token usage when available, retrieval references and outcome. Requested model identity must not be represented as independently verified provider deployment identity.

AI-11 Trust boundaries: Uploaded documents, employee messages and external search results shall be treated as untrusted content. Embedded instructions must not override application policy, request tools or authorize disclosure. Detection or filtering alone is not considered sufficient protection.

AI-12 Evaluation: Before pilot release, a reviewed test set must cover grounded answers, unsupported questions, cross-tenant retrieval, malicious document instructions, stale citations and malformed structured output. The acceptance threshold for answer usefulness remains to be agreed with support operations.

## 7 Intended application workflows

WF-01 Submit and assign: Employee authenticates; application authorizes tenant access; validates submission; stores request and attachment metadata; records an assignment job; worker applies routing rules and optional AI suggestion; stores assignment; notification delivery is scheduled. A successful request must remain recoverable if notification delivery fails.

WF-02 Retrieve and answer: Application authorizes the user; retrieves only permitted published passages; builds context; calls the selected model profile; validates citation references; streams the answer; records permitted accounting and feedback metadata. Insufficient evidence leads to an explicit unknown and an escalation offer.

WF-03 Publish knowledge: Editor uploads a version; application authorizes publication scope; storage accepts the document; a worker extracts text and builds passages and embeddings; indexing completes; the version becomes available for retrieval. Failed processing must not publish a partially indexed version.

WF-04 Review and send: Agent requests a draft; application gathers authorized request context; model returns a suggestion; agent edits and approves; application stores and sends the approved message. Draft creation and message sending are separate operations.

WF-05 Retry integration: Delivery job invokes the configured integration; failure records an attempt and retry state; exhausted retries enter an operator-visible failure queue. Replay must preserve tenant ownership and business-event identity.

These describe intended behavior. They do not establish deployed services, source call sequences or actual execution traces.

## 8 Logical responsibilities and integration needs

The solution needs employee and agent interfaces; request and authorization handling; knowledge processing; retrieval and generation coordination; notification delivery; scheduled escalation; audit and reporting. These responsibilities may share a deployment. This BRD does not mandate one service per responsibility or a microservice architecture.

INT-01 Identity: OpenID Connect integration with tenant identity providers, including group mappings and key rotation handling.

INT-02 Email: A transactional email provider shall support delivery status and retry handling. SendGrid is a candidate, not a selected implementation.

INT-03 Model access: Calls shall use approved profile configuration and credential references. Client browsers must not receive provider secrets.

INT-04 Storage: The platform requires transactional records, document objects, a retrieval index and asynchronous job state. PostgreSQL with a vector extension is one candidate; a separate vector service remains an option. A queue product and cache product have not been selected.

INT-05 Inbound delivery events: If the chosen email provider supports callbacks, the application shall validate authenticity and associate the event with the correct tenant and delivery record. The final endpoint path and signature scheme depend on provider selection.

No cloud provider, region, network topology, container platform, API path, package manager, programming language or framework is mandated here.

## 9 Data governance and nonfunctional requirements

NFR-01 Tenant isolation: Tenant identifiers and permission checks shall apply to transactional queries, retrieval indexes, object access, job payloads, caches and audit queries. The physical isolation model is an architecture decision.

NFR-02 Performance: For the pilot load of 200 concurrent authenticated users and 20 new requests per minute, non-AI request reads shall have a 95th percentile server response time below 800 milliseconds, excluding client network time. Search, uploads and exports need separate performance budgets.

NFR-03 AI responsiveness: For answers using already indexed knowledge, target first visible answer content within 4 seconds at the 95th percentile under the agreed pilot workload. Provider time counts toward this target. Full-answer latency, answer lengths and provider capacity assumptions require separate agreement.

NFR-04 Availability: Target 99.9 percent monthly availability for request submission and viewing, measured by agreed synthetic checks. AI unavailability shall not prevent manual request processing. Measurement location, exclusions and support obligations need agreement before contractual use.

NFR-05 Recovery: Target recovery point of 15 minutes and recovery time of 4 hours for transactional request data. Recovery objectives for object storage and retrieval indexes remain unspecified and must be agreed before production approval.

NFR-06 Confidentiality: Encrypt data in transit and at rest. AI data egress requires an approved tenant policy covering provider, region, permitted data categories and retention. Redaction must not be assumed to remove all confidential material.

NFR-07 Retention: Retain request records for 365 days after closure unless the tenant has an approved alternative. Operational logs shall be retained for 30 days. Legal-hold rules and deletion obligations must be resolved before production.

NFR-08 Audit: Record privileged configuration changes, role changes, request state changes, publication events and AI draft approvals. Audit access shall be restricted; routine logs shall not contain full prompts, secret values or complete document passages.

NFR-09 Accessibility: Core employee and agent workflows shall target WCAG 2.2 AA, subject to accessibility testing. Keyboard operation and understandable error messages are required.

NFR-10 Observability: Operators shall see processing failures, queue backlog, retry counts, AI provider failures and tenant-level usage limits without routine access to customer content.

NFR-11 Deployment: Production and nonproduction shall use separate credentials and data boundaries. The deployment model and scaling strategy require architecture review. No specific autoscaling, subnet, gateway or cloud-managed service is established by this requirement.

## 10 Stakeholder review notes

NOTE-01 Product workshop: Product requests automatic closure of requests when an AI answer is judged satisfactory, to reduce agent workload. This conflicts with the human-control direction in AI-02 and AI-08 and is pending resolution; it is not an approved exception.

NOTE-02 Privacy review: Privacy requests deletion of identifiable request content within 90 days after closure, while operations requests the 365-day retention in NFR-07. Neither preference has been reconciled into an approved retention policy.

NOTE-03 Pilot planning: An early planning estimate mentions 2,000 concurrent users. NFR-02 defines the current pilot test workload as 200. Production capacity requirements have not been approved; do not silently treat the estimate as a tested capacity.

NOTE-04 Commercial request: A stakeholder asks for a fast and inexpensive assistant. No numeric per-answer cost limit has been agreed. A proposed model price or token budget requires approval and must not be invented from this phrase.

## 11 Release gates and open decisions

GATE-01: Demonstrate authorized request submission, assignment, response and audit workflows with integration failures and retries.

GATE-02: Demonstrate knowledge permission filtering, publication replacement and cited answers, including negative tests that must return an unknown or refuse unauthorized retrieval.

GATE-03: Resolve retention and autonomous-action conflicts. Approve provider data handling, recovery scope and pilot evaluation thresholds.

GATE-04: Review performance and recovery test results. Targets are requirements, not evidence that the targets have been achieved.

Open decisions include implementation stack; deployment boundaries; selected data, queue and email products; model and embedding profiles; legal hold; withdrawn citation behavior; AI usefulness threshold; production workload; search and export budgets; and the future MCP connector design.

## 12 Glossary

Tenant: A customer organization with its own users, permissions and data scope.

Embedding: A numeric representation used to retrieve passages related to a question.

Grounded answer: An answer supported by identifiable permitted source material.

Model profile: Approved configuration describing a model's purpose and access settings.

Idempotency: Repeating the same operation with the same identity does not create an additional business result.

Retrieval index: Searchable representations of published knowledge, including access metadata.

MCP: Model Context Protocol, mentioned here only as a possible future connector interface.
