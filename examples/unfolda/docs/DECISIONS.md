# Unfolda Architecture Decisions

Status: draft
Last updated: 2026-03-15

---

## Purpose

This document records accepted architecture decisions for the Unfolda MVP.

It complements:

- `docs/PRD.md`
- `docs/ARCH_DISCOVERY.md`
- `docs/ARCHITECTURE.md`
- `docs/ARCHITECTURE_GUARDRAILS.md`
- `docs/PIPELINE_CONTRACTS.md`

This file should contain only decisions that are already accepted.
Ideas, benchmarks, and undecided alternatives should remain in discovery or product documents until they are resolved.

When a decision changes:

- pipeline stage responsibilities
- pipeline stage inputs or outputs
- storage and retention semantics
- privacy boundaries
- runtime topology
- external integration boundaries

the related architecture documents must be updated together.

---

## Decision Record Format

Each decision record includes:

- `ID`: stable decision identifier
- `Status`: current decision status
- `Date`: acceptance date
- `Context`: why the decision matters
- `Decision`: the chosen direction
- `Consequences`: practical follow-on effects and constraints

Status values for this file:

- `accepted`
- `superseded`

---

## DEC-000 — Architecture Scope

**Status:** accepted  
**Date:** 2026-03-10

**Context**

The project includes multiple documents describing the architecture from different angles, but implementation planning requires a clear definition of the authoritative architecture scope.

**Decision**

The following documents together define the architecture of the system:

- `docs/ARCHITECTURE.md` — full architectural model
- `docs/ARCHITECTURE_GUARDRAILS.md` — architectural constraints
- `docs/PIPELINE_CONTRACTS.md` — stage input and output contracts
- `docs/DECISIONS.md` — accepted architectural decisions

**Consequences**

- Architecture changes must update these documents together when relevant.
- Implementation work must not contradict accepted decisions or architecture guardrails.
- Task plans and builder work inherit their constraints from this architecture scope.

---

## DEC-001 — Runtime Stack Split

**Status:** accepted  
**Date:** 2026-03-10

**Context**

Unfolda needs a strong mobile-first SaaS frontend, explicit API boundaries, and a backend pipeline that is well suited to EPUB processing, structured text handling, and LLM orchestration.

**Decision**

The MVP uses a two-runtime, single-product architecture:

- `Next.js` with TypeScript for the user-facing web application and admin UI
- `FastAPI` for API endpoints, validation endpoints, and job-control APIs
- Python workers for asynchronous pipeline orchestration and stage execution
- orchestration logic remains separated from pipeline stage implementations
- `PostgreSQL` as the canonical metadata and state store
- `Redis` as a lightweight, non-canonical queue broker
- S3-compatible object storage for uploads, outputs, and structured resumable artifacts

The backend API and worker should live in the same Python codebase for MVP.

**Consequences**

- The web app and API backend have an explicit authentication boundary.
- The system accepts two runtimes, but avoids microservice sprawl.
- Pipeline logic remains in Python, which is the language used for orchestration and domain-heavy processing.
- Runtime topology is fixed unless a later decision explicitly replaces it.

---

## DEC-002 — Shared SaaS With Strong Logical Isolation

**Status:** accepted  
**Date:** 2026-03-10

**Context**

Unfolda is a shared SaaS, not a single-user tool and not a per-tenant dedicated deployment. The MVP needs reliable ownership boundaries, credit controls, abuse resistance, and support-safe admin visibility.

**Decision**

The MVP uses a shared SaaS deployment with strong logical per-user isolation:

- the authenticated `user` is the ownership root
- every canonical entity carries `user_id` directly or is reachable through an owning `job`
- each user may have at most one active job at a time
- credit eligibility checks occur before queue admission and again before expensive translation work begins
- audit events are required for credit grants, balance adjustments, reservations, consumptions, refunds, admin actions, retries, cancellation requests, signed URL issuance, policy rejections, and expensive provider activity
- object-storage keys are namespaced by `user_id` and `job_id`

**Consequences**

- Ownership checks cannot remain ad hoc inside application code.
- Storage cleanup and support tooling can rely on explicit ownership paths.
- Future billing or plan-based controls can be added without changing the core tenancy model.
- Dedicated infrastructure per user is out of scope for MVP.

---

## DEC-003 — LLM Integration Boundary

**Status:** accepted  
**Date:** 2026-03-10

**Context**

The product depends on high-quality translation and explanation generation, but the architecture must prevent LLM behavior from leaking into unrelated stages or binding the codebase too tightly to a vendor-specific implementation.

**Decision**

The MVP uses a single-provider adapter boundary for LLM integration:

- only the `translation` stage may invoke an LLM
- prompts must live in `prompts/`
- prompt assets are organized under `prompts/translation/`, `prompts/guided_explanations/`, `prompts/system/`, and `prompts/templates/`
- each prompt definition includes `prompt_id`, `prompt_version`, `target_stage`, and `model_family_compatibility`
- provider and model selection must come from configuration, not hardcoded implementation logic
- provider retries must be explicit and bounded
- provider payloads must be scoped to the current translation batch and required context only

The exact provider and model remain deferred.

**Consequences**

- No other pipeline stage may invoke LLMs directly or indirectly.
- Prompt changes that affect pipeline behavior become architecture-relevant changes.
- Prompt changes affecting translation behavior require a `prompt_version` update recorded in `job_run` metadata.
- Multi-provider routing is not part of the MVP baseline.
- A later provider benchmark may finalize the initial vendor without changing this boundary.

---

## DEC-004 — Storage, Retention, And Privacy Boundary

**Status:** accepted  
**Date:** 2026-03-10

**Context**

Unfolda processes copyrighted third-party book content. The architecture must minimize retention, control provider exposure, and prevent raw-content leakage through logs, support tools, or artifact sprawl.

**Decision**

The MVP adopts the following storage and privacy boundary:

- uploaded EPUBs and generated EPUBs live only in object storage
- structured resumable artifacts may live in object storage when needed
- canonical metadata lives in `PostgreSQL`
- raw book text must never appear in logs, traces, analytics payloads, or error payloads
- signed URLs must be object-scoped, short-lived, and purpose-specific
- support and admin tooling default to metadata-only views
- any exceptional raw-content access must be time-bounded, purpose-limited, and audited
- provider payloads must include only the text and metadata needed for the current batch
- provider configurations or contracts should disable customer-data training where available

Retention rules:

- uploaded files are deleted after terminal state plus retention window
- generated files are deleted after first download or retention expiry, according to policy
- structured resumable artifacts follow the same retention owner as the job
- long-term retention keeps metadata only, not book content

**Consequences**

- Cleanup must be explicit and reliable.
- Observability design is constrained by the no-raw-text rule.
- Provider choice includes a data-handling review, not only quality and cost.
- Debugging relies on normalized metadata and structured artifacts instead of raw payload logging.

---

## DEC-005 — Long-Book Processing And Consistency Strategy

**Status:** accepted  
**Date:** 2026-03-10

**Context**

The PRD requires paragraph-visible output, translation consistency across books, and successful processing of typical books in the 50,000 to 100,000 word range. Whole-book prompts are too brittle, and fully independent paragraphs are too inconsistent.

**Decision**

The MVP uses:

- paragraph-visible output
- chapter-scoped translation context
- token-bounded internal translation batches
- explicit batch checkpoints
- translation batch planning that respects `max_tokens_per_request`, `target_tokens_per_request`, and paragraph boundary integrity
- translation batch targets that stay roughly within 30-60% of the effective model context window
- job-scoped consistency memory containing a terminology map, named-entity registry, rolling chapter context summary, and unresolved ambiguity notes
- automated non-LLM translation quality checks such as untranslated segment detection, language mismatch detection, extremely short translation detection, and hallucinated paragraph detection

Translation batches are the primary resumable unit.
Consistency memory is explicit, job-scoped, and not reused across books.

**Consequences**

- Translation orchestration must manage batch planning and checkpoint persistence explicitly.
- Quality and resumability are improved without introducing a persistent cross-book glossary system.
- `docs/PIPELINE_CONTRACTS.md` defines the segmentation outputs needed for chapter references, token estimates, structural references, and batch-boundary planning.
- Translation quality safeguards must remain provider-independent and must not rely on extra LLM calls in MVP.
- Exact consistency-memory schema details remain open for later refinement, but the job-scoped memory model is fixed.

---

## DEC-006 — Credits And Internal Cost Control

**Status:** accepted  
**Date:** 2026-03-10

**Context**

The MVP now includes a user-facing credits system, but credits and actual LLM cost are not the same thing. The product needs a user-visible access model and a separate internal model that protects unit economics.

**Decision**

The MVP uses two related but separate control layers.

User-facing credits:

- credits are an abstract unit, not raw words
- credit cost is derived from source word count, mode, and settings using admin-configurable multipliers
- users receive an initial credit grant at registration
- estimated credit cost is shown before job confirmation
- credits are reserved on job submission
- reserved credits are consumed on successful completion
- reserved credits are refunded on failure or cancellation
- credit reservations, consumptions, and refunds must be idempotent per `job_run`
- For MVP, the user-confirmed credit reservation is based on the pre-submission estimate shown before confirmation. Authoritative ingestion metadata may inform analytics and future policy tuning, but must not silently increase the reserved credit amount after confirmation.

Internal cost control:

- pre-run cost estimation
- hard cost caps
- batch-level token accounting
- prompt budget discipline
- bounded retry budgets

Internal cost caps apply at:

- per-job level
- per-user internal cost budget period level
- per-retry-budget level

When an internal cost threshold is exceeded, the system must fail safely with a clear policy reason instead of continuing implicitly.

**Consequences**

- User-facing credits remain distinct from actual inference-cost accounting.
- The credits abstraction supports future payment integration without changing the core pipeline or credit logic.
- Every cost-significant provider interaction must produce a `cost_ledger_entry`.
- Prompt growth and credit multiplier changes become reviewable and architecture-relevant rather than hidden implementation drift.
- Later pricing or billing work can build on the same accounting model.

---

## DEC-007 — Operations Model For Long-Running Jobs

**Status:** accepted  
**Date:** 2026-03-10

**Context**

Long-running asynchronous book jobs require more than a queue. Without an explicit operations model, retries, throttling, stuck jobs, poison inputs, and deployment changes can corrupt execution state or make support impossible.

**Decision**

The MVP uses a lightweight queue with an explicit job-operations model:

- concurrency is bounded by provider throughput, worker memory, and acceptable in-flight cost exposure
- backpressure prevents new translation work from starting when budgets are saturated
- provider throttling is handled with capped concurrency, rate-limit-aware backoff with jitter, and retry classification as `provider-transient`
- each provider request uses an explicit request timeout, retry timeout budget, and maximum retry attempts
- timeouts are classified as `provider-transient`
- failures are classified as `provider-transient`, `content-deterministic`, `system`, or `policy`
- retries are allowed only for `provider-transient` and temporary infrastructure failures
- retries must not occur for content-deterministic failures or policy violations
- retries preserve `batch_index`, `input_hash`, `prompt_version`, `pipeline_version`, and `provider_configuration_version`
- workers use leases, heartbeats, lease-expiry detection, and explicit recovery rules
- poison jobs move to quarantine or an equivalent non-retrying failure state
- cancellation is best-effort and takes effect at safe checkpoints
- deployment changes must preserve in-flight compatibility or drain workers first

**Consequences**

- Operations behavior is part of architecture, not an implementation afterthought.
- Worker code must respect lease ownership and recovery rules.
- Duplicate retry execution is treated as an architecture bug, not an acceptable edge case.
- Heavy workflow engines remain out of scope for MVP.

---

## DEC-008 — Observability And Quality Validation Model

**Status:** accepted  
**Date:** 2026-03-10

**Context**

LLM pipelines fail in ways that are expensive, slow, and difficult to debug if the system only exposes coarse job statuses. The MVP needs enough telemetry to operate the runtime and enough benchmark visibility to detect quality regressions.

**Decision**

The MVP uses structured telemetry with two linked scopes:

Runtime telemetry:

- structured logs
- durable per-job timeline
- stage timings
- provider latency and throttling metrics
- token usage metrics
- credit reservation events
- credit settlement events
- credit refund events
- credit balance adjustment events
- throughput metrics
- retry and error-class metrics
- stuck-job and quarantine metrics

Quality telemetry:

- an evaluation dataset covering representative language pairs, modes, and book shapes
- comparable benchmark runs
- regression detection before high-impact prompt, provider, or pipeline changes ship

Timeline events include at minimum:

- `job_created`
- `job_validated`
- `job_queued`
- `credit_reserved`
- `job_run_created`
- `job_run_leased`
- `job_processing_started`
- `batch_started`
- `batch_completed`
- `batch_failed`
- `retry_scheduled`
- `cancel_requested`
- `job_cancelled`
- `credit_consumed`
- `credit_refunded`
- `job_completed`
- `job_failed`
- `cleanup_started`
- `cleanup_completed`
- `job_expired`

**Consequences**

- Support and debugging use durable job timelines instead of raw log spelunking alone.
- Quality regression detection becomes part of release safety for prompts, providers, and pipeline behavior.
- Telemetry schema design is a first-class implementation task.
- Telemetry must remain metadata-only and respect the no-raw-text rule.

---

## DEC-009 — Canonical Metadata And Artifact Model

**Status:** accepted  
**Date:** 2026-03-10

**Context**

Postgres as system of record and Redis as queue plumbing is correct but incomplete without a canonical entity model, resumability boundary, idempotency key, and artifact ownership rules.

**Decision**

The MVP uses a hybrid canonical model:

- `PostgreSQL` stores canonical metadata and state
- object storage stores binaries and structured resumable artifacts
- `Redis` stores execution signaling only

Minimum canonical entities:

- `user`
- `user_credit_account`
- `credit_transaction`
- `job`
- `job_run`
- `document`
- `artifact`
- `translation_batch`
- `job_event`
- `cost_ledger_entry`

Canonical resumability and identity rules:

- translation batches are the primary resumable unit for translation work
- the idempotency boundary is `job_run_id + batch_index + pipeline_version + input_hash`
- artifacts are not canonical without corresponding database metadata
- every `job_run` records pipeline, prompt, provider configuration, and model version markers
- credit reservations, consumptions, and refunds are attributed and settled per `job_run`
- `pipeline_version` changes when pipeline stage order, stage input or output contracts, segmentation logic, translation prompt strategy, formatting structure, or export structure changes
- minor internal implementation changes that do not affect stage contracts do not change `pipeline_version`
- in-flight runs and retries use the recorded `pipeline_version`, `prompt_version`, and `provider_configuration_version` from run start
- workers must never silently upgrade version markers for an in-flight run
- segment identifiers must be deterministic and stable for the same document so runtime artifacts, retries, and quality checks can reference the same logical segment

**Consequences**

- Worker memory cannot be trusted for resumability.
- Artifact cleanup, credit history, and auditability depend on database-backed ownership and lifecycle records.
- Structured runtime artifacts are persistence wrappers around pipeline-stage outputs, not replacements for stage contracts.
- Changes to canonical entities or idempotency semantics are architectural changes.

---

## DEC-010 — Progress And ETA Model

**Status:** accepted  
**Date:** 2026-03-10

**Context**

The PRD requires reconnectable progress and ETA for long-running jobs. Progress must survive browser refresh, disconnects, retries, and support inspection.

**Decision**

Progress and ETA are backend-owned, durable job metadata derived from:

- stage-weighted progress
- throughput-informed ETA
- ETA smoothing based on rolling throughput averages
- periodic persistence into canonical job state

Progress computation must not depend on a live browser session or direct worker-to-UI streaming.

**Consequences**

- The UI transport may evolve independently of the progress model.
- ETA remains approximate early in a run and improves as more throughput data becomes available.
- Support tooling can inspect the same progress state seen by users.
- Progress logic belongs to orchestration and canonical job state, not to the frontend.

---

## DEC-011 — Pre-Submission Analysis Boundary

**Status:** accepted  
**Date:** 2026-03-10

**Context**

The MVP now depends on lightweight analysis between upload and job confirmation to show source-language preview, word-count estimate, processing estimate, and credit cost before the user confirms the job. This affects UX, credit reservation, and separation from the authoritative pipeline.

**Decision**

The MVP includes a pre-submission analysis boundary with the following rules:

- it runs after upload and before job confirmation
- it is lightweight and read-only
- it may extract source-language preview, estimated word count, lightweight structural signals, and early eligibility indicators
- it must not invoke LLMs
- it must not produce canonical pipeline artifacts
- it must not replace ingestion
- authoritative document metadata is still produced by ingestion during execution

For MVP, pre-submission metadata is advisory.
For MVP, the user-confirmed credit reservation is based on the pre-submission estimate shown before confirmation. Authoritative ingestion metadata may inform analytics and future policy tuning, but must not silently increase the reserved credit amount after confirmation.

**Consequences**

- Pre-submission analysis is an explicit architectural capability, not an upload helper and not a pipeline stage.
- Support and policy handling can explain estimate vs authoritative differences without mutating confirmed user expectations.
- Credits, ingestion, and submission flow remain loosely coupled but explicitly reconciled.

---

## DEC-012 — Job Cancellation Model

**Status:** accepted  
**Date:** 2026-03-10

**Context**

Treating cancellation requests as `failed` obscures the difference between execution errors and an intentional stop. This weakens user experience, support clarity, telemetry, and credit-settlement semantics.

**Decision**

The MVP uses an explicit cancellation model:

- `cancelled` is a distinct terminal user-visible job state
- cancellation is best-effort and takes effect at safe checkpoints, typically batch boundaries
- queued work may be cancelled before execution begins, and running work may be cancelled once the active checkpoint is reached
- a successfully honored cancellation transitions the effective `job_run` to `cancelled`
- reserved credits are refunded idempotently on cancellation
- cancellation produces explicit timeline and audit events rather than being folded into generic failure handling

**Consequences**

- UI, API, worker orchestration, telemetry, and support tooling must distinguish `cancelled` from `failed`.
- Credit settlement and job history become clearer for users and admins.
- Cancellation remains operationally bounded and does not require interrupting an in-flight provider call mid-request.

---

## DEC-013 — Authentication Mechanism Between Next.js and FastAPI

**Status:** accepted  
**Date:** 2026-03-14

**Context**

FEAT-AUTH requires an authenticated user identity to be resolved at the FastAPI boundary on every request. `docs/ARCHITECTURE.md` §Authentication Boundary states that the exact mechanism (JWT, opaque session token, or BFF proxy) is an implementation decision to be recorded before build. This was listed as a deferred decision in this document until Architect planning for FEAT-AUTH resolved it.

**Decision**

The MVP uses JWT forwarded from NextAuth.js to FastAPI:

- NextAuth.js handles Google OAuth in the Next.js web app and issues a signed JWT (HS256, shared secret)
- Every API call from the Next.js frontend to the FastAPI backend includes `Authorization: Bearer <token>` in the request header
- The FastAPI `get_current_user` dependency validates the JWT signature using the shared `NEXTAUTH_SECRET`, decodes the `user_id`, and injects it into the request context
- Requests with missing, invalid, or expired tokens are rejected with HTTP 401 before reaching any business logic
- The JWT validation library on the Python side is `PyJWT` (actively maintained, zero transitive dependencies)
- Sessions persist in the browser via a signed HTTP-only cookie managed by NextAuth.js

This approach:
- is stateless and requires no shared session store between the two runtimes
- fits the DEC-001 two-runtime architecture (Next.js + FastAPI) without adding new infrastructure
- is reversible: the JWT boundary can be replaced with an opaque token or BFF pattern in a later decision without changing the underlying OAuth flow

**Consequences**

- The `NEXTAUTH_SECRET` env var must be set in both the Next.js and FastAPI environments and must be a strong random value
- The JWT secret must never be committed to the repository
- JWT expiry and session configuration must be explicit; silent session expiry is a known risk and must be handled by NextAuth.js session callbacks
- The initial credit grant amount remains a deferred Product decision; Builder must use a configurable `INITIAL_CREDIT_GRANT` env var with a safe default
- `python-jose` must not be used; `PyJWT` is the pinned library for this boundary

---

## Deferred Decisions

The following items are intentionally not yet accepted decisions:

- exact LLM provider and model selection
- exact retention window duration *(resolved via configuration: `RETENTION_WINDOW_DAYS` env var, default 30 days — FEAT-RETENTION, 2026-03-15; promote to accepted decision when a product-level duration is confirmed)*
- exact initial credit grant amount *(resolved via configuration: `INITIAL_CREDIT_GRANT` env var, default 100 credits — FEAT-AUTH, 2026-03-15; promote to accepted decision when a product-level amount is confirmed)*
- exact credit conversion multipliers per mode and settings *(resolved via configuration: configurable env vars with defaults — FEAT-CONFIG, 2026-03-15; promote to accepted decision when multipliers are validated by Product)*
- exact consistency-memory schema details
- exact anomaly heuristics for source-language detection
- exact benchmark thresholds for launch quality gates

These should be promoted into accepted decision records only after the necessary benchmark, product, or implementation work is complete.

## DEC-014 — QUEUE and RETENTION Build-Order Dependency Clarification

**Status:** accepted  
**Date:** 2026-03-15

**Context**

`docs/FEATURE_MAP.md §Capability Dependency Map` lists:

- `QUEUE` depends on `STORAGE, COST, TELEMETRY, RETENTION`
- `RETENTION` depends on `STORAGE, QUEUE, TELEMETRY`

This creates an apparent circular dependency: QUEUE requires RETENTION, and RETENTION requires QUEUE. During routing for post-FEAT-COST features, Iteration Manager identified this as an ambiguity that would block sequential implementation planning unless resolved explicitly.

**Decision**

The two dependency entries have different semantics and must not be treated symmetrically:

**RETENTION → QUEUE** is a **concrete implementation dependency**.
RETENTION's cleanup worker reads job state (`terminal_state`, `retention_deadline`) from the `jobs` table, which is owned and populated by QUEUE. RETENTION cannot be implemented without the `jobs` table existing. Build order must be QUEUE first.

**QUEUE → RETENTION** is an **operational lifecycle dependency**.
QUEUE's full lifecycle includes the `job_expired` terminal state and the emission of `cleanup_started` / `cleanup_completed` timeline events. These lifecycle boundaries are part of QUEUE's design. However, QUEUE's code does not import or call RETENTION. QUEUE emits cleanup timeline events; RETENTION's scheduled worker acts on them independently. QUEUE is complete as a feature without RETENTION's worker being deployed.

Build order: **QUEUE → RETENTION**.

FEAT-QUEUE Architect must plan the job model, state machine, orchestration, and cleanup timeline event emission without depending on RETENTION's cleanup logic being present. FEAT-QUEUE acceptance criteria must explicitly note that `cleanup_started` and `cleanup_completed` events are emitted by the job lifecycle but cleanup execution is deferred to FEAT-RETENTION.

**Consequences**

- FEAT-INGEST may proceed immediately (depends only on STORAGE, which is complete).
- FEAT-QUEUE may proceed after FEAT-INGEST (depends on STORAGE ✅, COST ✅, TELEMETRY ✅, RETENTION — operational only, not blocking).
- FEAT-RETENTION may proceed immediately after FEAT-QUEUE is approved.
- The `QUEUE → RETENTION` entry in `docs/FEATURE_MAP.md` reflects operational lifecycle completeness, not a build-time code dependency. This distinction applies when routing future features that depend on QUEUE.
- No change to `docs/FEATURE_MAP.md` is required; this decision record provides the authoritative interpretation.

---
