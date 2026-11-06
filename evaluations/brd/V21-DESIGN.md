# BRD lab 2.1 design and scope

This release strengthens BRD interpretation and architecture synthesis. It does not turn the local evaluation server into a production tenant-isolated enterprise service, and does not claim universal BRD accuracy.

## Responsibilities and ownership

The model identifies logical components before operations. Operations provide an owner component and exact ownership evidence. The validator accepts ownership only when its target is an accepted component and its quotations match the document. Missing ownership is an explicit gap; unsupported ownership is quarantined independently of the operation's existence.

Overview compilation maps owned operations onto those components and aggregates typed edges. Each derived arrow retains original relationship IDs, operation IDs and ownership evidence. Internal connections remain in the original graph. Unowned operations are retained rather than discarded. Unconnected entities and budget omissions remain explicit. No deployable service is inferred merely from ownership.

Vendor selection is separate from a required logical capability. An intended supplier/model/embedding service may have an unresolved vendor. Named vendor candidates stay candidates. This distinction depends on source interpretation; the engine cannot safely invent a missing provider node.

## Intended processes and controls

Workflows may have evidenced steps, transitions, explicit guards, approval/validation/authorization gates and failure outcomes. Step and transition identities are local to their workflow. Sequence basis is explicit, derived or unspecified. Typed dependencies never automatically become execution order.

Invalid step evidence or transition endpoints prevent process compilation; the interaction view can still be inspected. Required approval needs a path to a subsequent action. A represented root-to-consequential-action path bypassing required approval is flagged and suppresses that process view. Conditional approval remains distinct. Decision branches and missing failure paths are flagged for review. These graph checks are not proof that a proposed process exactly satisfies every business rule, and English action-word checks are deliberately limited.

## Documents and coverage

The source ledger preserves every nonblank source line, including Markdown headings, plain text, bullets, numbered lists and table rows. It recognizes additional ID forms, mixed-case identifiers and common plain headings. Requirement text placed in a heading is not discarded. Unknown identifiers, languages and layouts still need review. PDF, scanned images and Word layout extraction are outside this slice.

Lexical clause units distinguish fully quoted, partially quoted and unquoted text. All retain semantic status not assessed. This prevents a source-block reference from being presented as complete clause understanding. Lexical splitting is bounded to 6,000 units with omissions counted; the complete source ledger remains available. These units are not a formal decomposition of legal or business obligations.

Scope-difference warnings help reviewers distinguish pilot/production estimates from conflicts; the original model claim is preserved. No rule silently resolves stakeholder disagreements. Mandatory cues now include requires, but lexical cues remain hints rather than a semantic classifier.

## Reporting and efficiency

The default Markdown leads with business context, logical responsibilities and one bounded overview. It lists workflows and decisions and includes up to three process diagrams. The audit Markdown and JSON retain all records, quality exceptions, source evidence and view traces. All diagram sources remain downloadable. Empty/no-edge diagrams are suppressed; controls have a separate view.

Model requests omit redundant per-block hashes and navigation metadata while preserving every source block's wording, ID, section and lexical cues. There are still two planned model calls with no automatic repairs or retries. The inventory policy is limited to inventory instead of asking it to plan workflow graphs. The richer process contract can increase completion cost. Inventory and relationship completion budgets default to 22,000 tokens each, independently configurable from 2,000 to 24,000 using BRD_INVENTORY_TOKENS and BRD_RELATIONSHIP_TOKENS. Provider timeout defaults to 480 seconds per stage, configurable from 30 to 600. Existing environment settings take precedence. These are ceilings, not predicted usage or a cost improvement claim.

## Evaluation and remaining limits

Tests use independently specified procurement expectations and varied clinic, warehouse, vague-AI, non-AI, multilingual and adversarial fixtures. They verify evidence, isolation of untrusted document instructions, ID reuse, aggregation, guards, bypass detection and quotation coverage. Blank-model tests do not establish that the LLM understands a new domain.

Live evaluation should measure omissions and unsupported claims per fixture, latency, tokens, ownership gaps and process review findings. Do not convert passing tests, quotation coverage or zero quarantines into an architecture accuracy percentage. Independent Mermaid parsing, graphical preview, long-document partitioning/resume and broad semantic benchmarking remain future work. Existing v1/v2 analyses are preserved unchanged and require a new run to use 2.1 logic.
