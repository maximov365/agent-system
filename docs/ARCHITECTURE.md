# Unfolda Architecture

Status: draft
Version: 0.1
Last updated: 2026-03-10

---

## Purpose

This document defines the target MVP architecture for Unfolda.

It translates the product requirements from `docs/PRD.md` and the recommendations from `docs/ARCH_DISCOVERY.md` into a concrete architectural direction that implementation work must follow.

This architecture is intentionally opinionated about:

- pipeline boundaries
- SaaS runtime boundaries
- storage and retention behavior
- privacy and provider data handling
- cost control
- operational safety for long-running jobs
- canonical state and artifact ownership

This document complements:

- `docs/ARCHITECTURE_GUARDRAILS.md`
- `docs/ARCHITECTURE_CHECKLIST.md`
- `docs/PIPELINE_CONTRACTS.md`

If implementation pressure suggests a different direction, the change must be escalated and documented rather than introduced silently.

---

## Architectural Summary

Unfolda is a SaaS web product for transforming uploaded EPUB books into translated or guided-reading EPUB outputs.

The MVP architecture is a two-runtime, single-product system:

- `Next.js` with TypeScript for the user-facing web application and admin UI
- `FastAPI` in Python for API endpoints, validation endpoints, signed URL issuance, and job-control APIs
- Python workers for asynchronous pipeline orchestration and stage execution
- `PostgreSQL` as the canonical metadata and state store
- `Redis` as a lightweight, non-canonical queue broker
- S3-compatible object storage for uploaded EPUB files, generated EPUB files, and resumable structured artifacts
- one external LLM provider behind a provider adapter boundary

The system must preserve the pipeline:

`ingestion -> segmentation -> translation -> formatting -> export`

The stack is not the full architecture. The MVP also depends on explicit control boundaries for:

- risk containment
- per-user SaaS isolation
- user-facing credits and internal cost separation
- privacy and security
- cost control
- operations policy
- telemetry and quality validation
- resumability and idempotency

---

## Guiding Principles

- Keep pipeline stages conceptually distinct and independently testable.
- Keep domain logic separate from infrastructure and I/O.
- Treat book content as sensitive input.
- Keep state explicit, durable, and auditable.
- Prefer risk-contained MVP controls over stack-only simplicity.
- Prefer bounded, reversible mechanisms over heavyweight platforms.
- Preserve reproducibility markers for every executable run.
- Avoid hidden state, hidden retries, and hidden cross-stage coupling.

---

## Architecture Invariants

The following rules must always hold:

- `PostgreSQL` is the canonical system of record for job, run, batch, credit, artifact metadata, audit, and cost state.
- `Redis` must never contain canonical job, batch, artifact, or credit state.
- Worker memory is ephemeral and must never be relied on for resumability, recovery, or auditability.
- Pre-submission analysis is advisory and must never create canonical pipeline artifacts.
- Raw book text must never appear in logs, metrics, traces, analytics payloads, or error payloads.
- Every provider call must be attributable to exactly one `job_run` and one `translation_batch`.
- Every cost-significant provider interaction must emit a `cost_ledger_entry`.
- Every credit grant, reservation, consumption, and refund must be attributable to the owning `job_run` or admin action.
- Credit reservations, consumptions, and refunds must be idempotent per `job_run`.
- The translation stage is the only stage allowed to invoke LLMs.
- Translation batches are the resumability boundary for long-running jobs.
- Every `job_run` must record pipeline, prompt, provider configuration, and model version markers before translation begins.
- Object-storage artifacts are not canonical without corresponding database metadata.
- One user may have at most one active job at a time in MVP.

These invariants are intended to be implementation-shaping rules, not descriptive guidance.

---

## System Context

Unfolda supports the following user journey in MVP:

1. The user signs in through the web app.
2. The user uploads an EPUB and receives lightweight pre-submission analysis.
3. The user configures processing options and sees estimated word count, ETA, and credit cost.
4. The API validates eligibility, reserves credits, and creates a job.
5. A background worker processes the book through the pipeline.
6. The user monitors durable progress and ETA.
7. The user downloads the generated EPUB.
8. Files and intermediate artifacts expire according to retention policy, while metadata remains.

The architecture must optimize for:

- mobile-first upload and progress UX
- long-running asynchronous jobs
- credit transparency before submission
- paragraph-level reading output
- context-aware translation quality
- temporary storage of copyrighted content
- controlled external LLM usage
- minimal long-term retention of user content

---

## High-Level Components

### Web Application

The web application is responsible for:

- Google login UX
- file upload flow
- pre-submission metadata display
- job configuration flow
- credit balance and estimated credit cost display
- progress and ETA display
- jobs list and download flow
- credit transaction history display
- admin and support UI surfaces

The web app must not implement pipeline logic.
It consumes narrow API contracts and renders product state.

### Authentication Boundary

The web app and the API backend run as separate processes with separate runtimes.

Authentication flows through:

1. The user authenticates via Google login in the web app.
2. The web app obtains a token or session credential.
3. Every API call from the web app to the backend includes this credential.
4. The API backend validates the credential and resolves the authenticated `user_id` before processing any request.

The exact mechanism (JWT, opaque session token, or BFF proxy) is an implementation decision recorded in `docs/DECISIONS.md` before build.
The architectural rule is: the API backend must never trust unauthenticated requests, and user identity must be resolved at the API boundary, not inside worker or pipeline logic.

### API Backend

The API backend is responsible for:

- authenticated user APIs
- validation and submission endpoints
- pre-submission analysis endpoints
- enforcing one active job per user
- credit eligibility, reservation, and policy checks before queue admission
- signed URL issuance for upload and download
- credit balance and credit history APIs
- job status, progress, retry, and cancellation endpoints
- admin APIs for credit balances, grants, settings, and job inspection

The API backend is the policy boundary between the UI and execution layer.
It must not contain core translation or formatting logic.

### Worker Runtime

The worker runtime is responsible for:

- queue consumption
- pipeline orchestration
- stage execution ordering
- checkpoint persistence
- bounded retries
- terminal credit-settlement finalization
- progress and ETA updates
- stuck-job recovery participation through heartbeat and lease rules
- cleanup triggers and terminal-state handling

The worker is where orchestration lives.
Pipeline stage logic remains inside stage modules rather than in queue handlers.

### Database

`PostgreSQL` is the canonical system of record for:

- users
- credit accounts
- credit transactions
- jobs
- job runs
- documents
- translation batches
- artifact metadata
- job events
- cost ledger entries
- progress snapshots
- retention state

The database stores metadata and durable execution state, not long-term raw book content.

### Queue Broker

`Redis` is execution plumbing only.

It is used for:

- enqueueing runnable work
- coordinating worker pickup
- supporting lightweight job dispatch

It must not be treated as canonical state.

### Object Storage

S3-compatible object storage is the binary and large-artifact boundary for:

- uploaded EPUB files
- generated EPUB files
- structured resumable translation artifacts

Object storage is temporary by policy.
Retention is driven by canonical metadata in `PostgreSQL`.

### LLM Provider Boundary

The translation stage may invoke one external LLM provider through a provider adapter.

This boundary must:

- externalize prompts in `prompts/`
- externalize provider and model selection through configuration
- keep retries explicit and bounded
- support token and latency accounting
- minimize payload content to the current batch and required context only

No other pipeline stage may invoke LLMs directly or indirectly.

---

## Prompt Architecture

Prompt assets are stored under:

```text
prompts/
  translation/
  guided_explanations/
  system/
  templates/
```

Each prompt definition must include:

- `prompt_id`
- `prompt_version`
- `target_stage`
- `model_family_compatibility`

Prompt changes affecting translation behavior require a `prompt_version` update recorded in `job_run` metadata.

---

## Pipeline Versioning

Pipeline version must change when:

- pipeline stage order changes
- stage input or output contracts change
- segmentation logic changes
- translation prompt strategy changes
- formatting structure changes
- export structure changes

Minor internal implementation changes that do not affect stage contracts must not change the pipeline version.

---

## Runtime Topology

The MVP is a shared SaaS deployment with strong logical isolation.

It is not:

- a soft multi-user app with ad hoc ownership checks
- dedicated infrastructure per user
- a microservice mesh
- a workflow-engine-first platform

The runtime topology for MVP is:

```text
User Browser
    |
    v
Next.js Web App
    |
    v
FastAPI API Backend
    | \
    |  \
    |   \----> Object Storage (uploads, outputs, structured resumable artifacts)
    | 
    +-------> PostgreSQL (canonical state, credits, jobs, runs, batches, events, costs)
    |
    +-------> Redis (queue signaling only)
                 |
                 v
           Python Worker Runtime
            |      |        \
            |      |         \----> Object Storage
            |      \--------------> PostgreSQL
            \---------------------> LLM Provider
```

This keeps the system simple while still making the most important product-killing boundaries explicit.

Key topology rules:

- The web app talks to the API, not to workers directly.
- The API is the boundary for authentication, policy, and signed URL issuance.
- Workers consume execution signals from `Redis`, but reconcile and persist authoritative state in `PostgreSQL`.
- Object storage is used for binary and large structured artifacts, not as the canonical state store.
- The LLM provider is reachable only from translation-stage execution inside the worker runtime.

---

## Core Data Flow

### Submission Flow

1. The client requests an upload session from the API.
2. The API authenticates the user, applies upload policy checks, and issues a short-lived upload URL.
3. The client uploads the EPUB to object storage.
4. The API runs lightweight pre-submission analysis to extract source-language preview, word-count estimate, and submission metadata without invoking the full pipeline.
5. The user configures the job and sees estimated word count, approximate processing time, and estimated credit cost.
6. On confirmation, the API checks active-job and credit eligibility, reserves credits, creates or finalizes canonical records for the input artifact and job, then enqueues execution.

Pre-submission estimates are advisory.
Authoritative document metadata is produced by ingestion during execution.
If authoritative ingestion results differ materially from pre-submission estimates, policy handling must follow an explicit reconciliation rule rather than silent mutation.

### Processing Flow

1. A worker leases the queued job run.
2. The worker loads the uploaded artifact and executes the pipeline in order.
3. After each meaningful boundary, the worker persists progress, events, and batch state.
4. Orchestration persists translation-batch outputs, resumable structured artifacts, and cost records at explicit checkpoints.
5. Export produces the final EPUB artifact.
6. At terminal settlement, orchestration finalizes the credit reservation idempotently: consume on success, refund on failure or cancellation.
7. The worker transitions the job to a terminal state and emits final events.

For MVP, the user-confirmed credit reservation is based on the pre-submission estimate shown before confirmation. Authoritative ingestion metadata may inform analytics and future policy tuning, but must not silently increase the reserved credit amount after confirmation.

### Download Flow

1. The user requests the completed output.
2. The API verifies ownership and job state.
3. The API issues a short-lived download URL for the output artifact.
4. The output is downloaded directly from object storage.

### Cleanup Flow

Cleanup is owned by a dedicated scheduled process, not by inline API or worker logic.

1. A periodic cleanup task scans for terminal jobs past their retention deadline.
2. Cleanup removes uploaded files, generated files, and structured intermediate artifacts from object storage.
3. Cleanup updates artifact metadata in the database and marks content as deleted.
4. Metadata remains in the database after content deletion.
5. Jobs move to `expired` when their retained files are no longer available.

Rules:

- cleanup must be idempotent and safe to re-run
- cleanup must not delete artifacts for jobs that are still eligible for retry
- cleanup must not run concurrently with an active `job_run` for the same job
- cleanup emits `cleanup_started` and `cleanup_completed` timeline events

---

## Pre-Submission Analysis Boundary

Pre-submission analysis is not a pipeline stage.

It is a lightweight, read-only capability executed between upload and job confirmation.

Its responsibility is to extract submission-relevant metadata such as:

- source-language preview
- estimated word count
- lightweight structural signals
- early eligibility indicators

It must not:

- produce canonical pipeline artifacts
- invoke LLMs
- replace ingestion
- mutate document-processing state

The authoritative document representation is still produced by ingestion during job execution.

For MVP, pre-submission metadata is advisory.
For MVP, the user-confirmed credit reservation is based on the pre-submission estimate shown before confirmation. Authoritative ingestion metadata may inform analytics and future policy tuning, but must not silently increase the reserved credit amount after confirmation.

---

## Job Lifecycle State Machine

This section defines the operational state contract for `job` and `job_run`.

### User-Visible `job`

The user-visible lifecycle is:

```text
validating -> queued -> processing -> completed -> expired
      |          |           |
      |          |           +--------> failed
      |          |           +--------> cancelled
      |          +--------------------> failed
      |          +--------------------> cancelled
      +-------------------------------> failed
```

Rules:

- `validating`, `queued`, and `processing` are the only active job states in MVP.
- `completed`, `failed`, `cancelled`, and `expired` are terminal user-visible states in MVP.
- `expired` occurs only after content-bearing artifacts have been removed by retention cleanup and may follow `completed`, `failed`, or `cancelled`.
- A retry does not mutate a historical run into success; it creates a new `job_run` under the same `job`.
- Credit settlement follows the terminal outcome of the effective `job_run`: consume reserved credits on success, refund them on failure or cancellation.
- A successfully honored cancellation request must resolve to `cancelled`, not `failed`, once execution has been safely stopped.

### Executable `job_run`

The execution lifecycle is:

```text
created -> leased -> processing -> completed
    |         |          |
    |         |          +--------> failed
    |         |          +--------> cancelled
    |         +-------------------> failed
    |         +-------------------> cancelled
    +-----------------------------> failed
    +-----------------------------> cancelled
```

Operational rules:

- only one `job_run` may be active for a `job` at a time in MVP
- a retry creates a new `job_run`
- lease ownership must be explicit and time-bounded
- a lost lease triggers recovery logic, not blind duplicate processing
- cancellation is a control signal that takes effect at a safe checkpoint, usually a batch boundary
- a successfully honored cancellation transitions the active `job_run` to `cancelled`
- credit reservations, consumptions, and refunds must remain idempotent per `job_run`

### Translation Batch Progress State

The primary resumable unit is the translation batch.

Its lifecycle is:

```text
pending -> in_progress -> completed
   |           |
   |           +--------> failed
   +--------------------> skipped
```

Rules:

- `completed` batches are the canonical progress boundary for translation work.
- `failed` batches retain structured error metadata without relying on worker memory.
- `skipped` is allowed only for explicit policy or recovery reasons, never as a silent drop.

---

## Pipeline Architecture

The processing pipeline remains:

`ingestion -> segmentation -> translation -> formatting -> export`

The roles below refine the architecture without changing the stage order.

### Ingestion

Responsibility:

- validate the uploaded EPUB for MVP
- detect unsupported or DRM-protected input
- extract recoverable structure and text
- detect source language at the book level
- preserve document metadata and structural references

MVP notes:

- MVP supports EPUB input only, even if the generic pipeline contracts remain format-agnostic conceptually
- low-confidence language detection may trigger anomaly checks and a user override path

Must not:

- call LLMs
- segment content
- perform translation
- format output

### Segmentation

Responsibility:

- transform the normalized document into paragraph-visible segment structures
- preserve chapter and structural references needed for later reconstruction
- attach deterministic batch-planning metadata such as token estimates and chapter boundaries

Key rule:

- the user-visible boundary remains the paragraph
- internal batching may be smaller or grouped differently, but output is reconstructed at paragraph level

Contract note:

- `docs/PIPELINE_CONTRACTS.md` defines segmentation outputs for chapter references, token estimates, structural references, and batch-planning metadata
- implementation must treat those fields as part of the stable segmentation contract
- segment identifiers must be deterministic and stable for the same document so resumability, translation artifacts, and quality checks can reference the same logical segment across retries

Must not:

- rewrite meaning
- call LLMs
- perform formatting

### Translation

Responsibility:

- translate paragraph-visible segments into the target language
- generate explanations for `Guided` mode
- maintain cross-batch translation consistency inside a single job

This is the only LLM-enabled stage.

Architectural decision:

- `Guided` mode may use separate internal passes for translation and explanations, but both passes remain part of the translation stage, not separate pipeline stages

Operational model:

- work is executed as chapter-scoped, token-bounded translation batches
- batches are the primary resumable unit
- batch outputs are persisted by orchestration as structured artifacts

Must not:

- change segmentation boundaries
- embed presentation formatting
- hide retries or hidden mutable state

### Formatting

Responsibility:

- turn translated segments into mode-specific structured reading output
- assemble deterministic block structure for `Translate` and `Guided` modes

Formatting must remain deterministic and must not call LLMs.

### Export

Responsibility:

- reconstruct a valid EPUB
- preserve spine, chapter order, links, images, footnotes, and CSS when possible
- inject output metadata and disclaimer content

Export is the final structure-assembly stage.
It must not perform translation or change formatting semantics.

### Orchestration Boundary

Pipeline orchestration is external to the stages.

Orchestration is responsible for:

- stage execution order
- retries
- checkpoint persistence
- progress persistence
- lease and heartbeat participation
- state transitions

Orchestration must not become a hidden parallel pipeline implementation.

---

## Translation Batch Size Policy

Translation batches must respect:

- `max_tokens_per_request`
- `target_tokens_per_request`
- paragraph boundary integrity

The batch planner should aim for:

- `target_tokens_per_request` approximately 30-60% of the effective model context window

This policy exists to reduce prompt explosion, avoid unstable latency, and keep retry behavior bounded.

---

## Long-Book Processing Strategy

The MVP must support books in the typical 50,000 to 100,000 word range without relying on whole-book or whole-chapter prompts.

The architecture therefore adopts:

- paragraph-visible output
- chapter-scoped translation context
- token-bounded internal batches
- explicit batch checkpoints

This strategy is chosen because it supports:

- bounded provider calls
- resumability after partial failure
- durable progress reporting
- better consistency than fully independent paragraph translation
- cleaner recovery than chapter-sized retry units

The translation batch is the primary unit for:

- resumability
- cost accounting
- provider retry behavior
- partial progress

---

## Consistency Strategy

Translation consistency is a job-scoped concern, not a global knowledge system.

The MVP uses job-scoped consistency memory composed of:

- terminology map
- named-entity registry
- rolling chapter context summary
- unresolved ambiguity notes

Rules:

- consistency memory is explicit and inspectable
- it is scoped to a single job run
- it is not reused across books
- it is not exposed as a user-editable glossary in MVP
- formatting and export remain unaware of how consistency was produced

Consistency memory may be persisted by orchestration as structured translation artifacts when needed for resumability, but it is governed by the same retention window as the job.

---

## Translation Quality Safeguards

The translation stage must support automated quality checks.

Possible checks include:

- untranslated segment detection
- language mismatch detection
- extremely short translation detection
- hallucinated paragraph detection

These checks must not rely on external LLM calls in MVP.

They are intended to catch obvious translation failures before export while preserving the translation-stage boundary.

---

## SaaS Isolation Model

Unfolda is a shared SaaS with strong logical user isolation.

### Ownership Model

The ownership root is the authenticated `user`.

Every major canonical entity must either:

- carry `user_id` directly, or
- be reachable through an owning `job`

This applies to:

- jobs
- job runs
- documents
- artifacts
- translation batches
- events
- credit records

### Storage Key Namespace

Object storage keys must be namespaced by ownership boundaries:

- keys must include `user_id` and `job_id` as path components
- keys must not rely on random identifiers alone without ownership context
- key structure must make it possible to enumerate and delete all artifacts for a given job during cleanup

Example key pattern: `users/{user_id}/jobs/{job_id}/{artifact_type}/{artifact_id}`

This prevents orphaned files, simplifies retention cleanup, and reduces the risk of cross-user access mistakes.

### Credits And Eligibility

Credits are a first-class architecture concern.

The user-facing credits model follows these rules:

- credits are an abstract unit, not raw words
- estimated credit cost is derived from source word count, mode, and settings using admin-configurable multipliers
- the user sees current credit balance and estimated credit cost before confirming a job
- credits are reserved at job submission
- reserved credits are consumed on successful completion
- reserved credits are refunded on failure or cancellation
- credit reservations, consumptions, and refunds must be idempotent per `job_run`
- users have access to a basic credit transaction history
- the initial credit grant on registration is admin-configurable

Eligibility checks must occur:

- before job confirmation and queue admission
- again before expensive translation work begins
- before retrying cost-significant execution

User-facing credits and internal cost accounting are related but distinct.

### Abuse Prevention

MVP abuse controls must include:

- file-size cap
- MIME and structural validation
- DRM rejection
- one active job per user
- rate limits on upload, submission, and retry endpoints
- policy rejection for jobs exceeding cost or processing limits

### Auditability

The system must produce audit events for:

- credit grants and balance adjustments
- credit reservations, consumptions, and refunds
- admin actions
- retries
- cancellation requests
- signed URL issuance
- policy rejections
- expensive provider activity

Admin tooling must not bypass audit or ownership rules casually.

---

## Security, Privacy, And Compliance Boundary

Book content is sensitive input and must be handled accordingly.

### Data Classification

The architecture distinguishes:

- authentication and user metadata
- job metadata and settings
- uploaded EPUB binaries
- generated EPUB binaries
- structured intermediate artifacts for resumability
- provider request and response payloads
- logs, metrics, and audit events

### Storage Rules

- raw uploaded EPUBs live only in object storage
- generated EPUBs live only in object storage
- structured resumable artifacts live in object storage when needed
- canonical metadata lives in `PostgreSQL`
- raw book text must not be retained long-term in logs, traces, or analytics systems

### Logging Rules

Raw book text must not be logged in:

- application logs
- worker logs
- traces
- analytics events
- error payloads

Errors should be structured and informative without leaking source content.

### Provider Boundary

Provider payloads must contain only what is needed for the current translation batch:

- current source text for the batch
- bounded job-scoped consistency context
- required mode and language settings

The provider must not receive the full book unless explicitly justified and approved.

Where available, provider configuration or contract terms should disable provider training on customer content.

### Access Rules

- support and admin tooling default to metadata-only views
- any exceptional raw-content access must be time-bounded, purpose-limited, and audited
- secrets are managed outside the codebase and rotated without code changes
- signed URLs are object-scoped, short-lived, and purpose-specific

### Retention Rules

- uploaded EPUBs are deleted after terminal state plus retention window
- generated EPUBs are deleted after first download or retention expiry, whichever policy occurs first
- structured intermediate artifacts follow the same retention owner as the job
- long-term retention keeps metadata only, not book content

---

## Cost Architecture

Internal cost control is a dedicated architecture concern because user-facing credits alone are not enough to protect unit economics.

The MVP intentionally separates:

- user-facing credits, which control product access and are visible to the user
- internal cost accounting, which tracks actual LLM economics and protects unit economics

Credits are an abstract product unit. They are not a direct mirror of provider token cost.

The MVP uses a layered cost-control model:

- pre-run cost estimation
- hard caps
- batch-level token accounting
- prompt budget discipline
- bounded retry budgets

### Estimation

Before queue admission, the system estimates likely inference cost using:

- source word count
- mode
- language pair
- expected number of passes
- internal batching assumptions

The estimate is approximate but must be good enough to reject obviously uneconomic jobs.

### Hard Caps

Cost caps should exist at three levels:

- per job
- per-user internal cost budget period
- per retry budget

When a cap is exceeded, the system fails safely with a clear policy reason rather than continuing implicitly.

### Accounting

The system records token usage and estimated provider cost at:

- translation batch level
- job run level

This enables:

- cost debugging
- credit-policy evolution
- future pricing design
- regression detection after prompt or provider changes

### Prompt Budgets

Prompt size is part of architecture, not only implementation detail.

The system should maintain explicit prompt budget targets per mode so prompt growth remains visible and reviewable.

---

## Operational Model For Long-Running Jobs

The queue remains lightweight, but operations behavior is explicit architecture.

### Concurrency And Backpressure

Concurrency must be bounded by:

- provider throughput budget
- worker memory footprint
- acceptable in-flight cost exposure

Backpressure must prevent new translation work from starting when provider or worker budgets are saturated.

### Provider Rate Limit Strategy

Workers must respect provider limits through:

- a global in-flight provider request cap
- a per-worker in-flight request cap
- rate-limit-aware exponential backoff with jitter
- retry classification that treats throttling as `provider-transient`
- admission backpressure before launching new translation batches
- explicit throttling metrics and timeline events

The system must reduce new work before amplifying retries under throttling conditions.

### Provider Timeout Policy

Each provider request must have:

- request timeout
- retry timeout budget
- maximum retry attempts

Timeouts must be treated as `provider-transient` failures.

### Failure Taxonomy

Failures should be classified into:

- provider-transient
- content-deterministic
- system
- policy

This classification controls retries, support triage, and terminal reasons.

### Retry Policy

Retries are allowed only for:

- provider-transient failures
- temporary infrastructure failures

Retries must not occur for:

- content-deterministic failures
- policy violations

Retries must preserve:

- `batch_index`
- `input_hash`
- `prompt_version`
- `pipeline_version`
- `provider_configuration_version`

### Stuck Jobs

Workers must participate in:

- lease ownership
- heartbeat updates
- lease expiry detection
- explicit recovery rules

Stuck jobs must not remain ambiguous indefinitely.

### Poison Jobs

Jobs that repeatedly fail for deterministic content or policy reasons must move to quarantine or an equivalent non-retrying failure state.

### Cancellation

Cancellation is best-effort and should take effect at safe checkpoints, typically batch boundaries rather than in the middle of a provider call.

When a cancellation request is honored, the user-visible job state must resolve to `cancelled`, not `failed`.
The effective `job_run` should transition to `cancelled`, and reserved credits should be refunded idempotently.

### Deploy Safety

In-flight work must remain compatible with deployment and migration changes.

The system should prefer:

- backward-compatible schema changes during active runs
- worker draining before incompatible changes
- explicit run version markers for reproducibility

---

## Telemetry And Quality Validation

The MVP does not need a full observability platform, but it does need structured telemetry aligned with operational and product decisions.

### Runtime Telemetry

The minimum telemetry surface should include:

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

Logs and events should include stable fields such as:

- `job_id`
- `job_run_id`
- `user_id`
- `stage`
- `batch_index`
- `provider`
- `error_class`
- version markers

Telemetry must avoid leaking raw book text.

### Job Timeline Events

The durable job timeline should use explicit event classes such as:

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

Events are metadata-only records and must not embed raw book text.

### Benchmark Telemetry

The architecture also requires quality telemetry outside runtime execution:

- an evaluation dataset across representative language pairs and book shapes
- comparable benchmark runs
- regression detection before high-impact prompt, provider, or pipeline changes ship

This is the main architectural guard against quality collapse despite technically correct execution.

---

## Canonical Data And Artifact Model

The MVP adopts a hybrid canonical model:

- `PostgreSQL` for metadata and state
- object storage for binaries and structured resumable artifacts
- `Redis` for execution signaling only

### Canonical Entities

The minimum entity model is:

- `user`: authenticated account and ownership root
- `user_credit_account`: current credit balance, reservation totals, and admin-configurable grant state
- `credit_transaction`: grant, reservation, consumption, refund, and admin adjustment history
- `job`: user-submitted transformation request and user-visible lifecycle
- `job_run`: concrete execution attempt for a job, including pipeline version and runtime configuration
- `document`: normalized book metadata and language-detection state
- `artifact`: metadata record for stored objects
- `translation_batch`: resumability and progress record for a batch within a run
- `job_event`: audit and support timeline entry
- `cost_ledger_entry`: token and estimated-cost accounting entry

### Artifact Classes

Artifacts may represent:

- source upload
- output EPUB
- translation batch result
- consistency-memory snapshot if needed for resumability
- other structured intermediate artifacts explicitly approved for the pipeline

### Concrete Runtime Artifact Contracts

These runtime artifact contracts complement `docs/PIPELINE_CONTRACTS.md`.
They define what orchestration persists for resumability and operational clarity.

Runtime artifacts are persistence wrappers around pipeline-stage representations.
For example, a `translation_batch_artifact` wraps the `TranslatedSegmentCollection` output defined in `docs/PIPELINE_CONTRACTS.md`, adding orchestration metadata such as `batch_index`, `input_hash`, `token_usage`, and `consistency_memory_snapshot`.
Pipeline contracts define what a stage produces; runtime artifact contracts define how orchestration persists it.

Exact physical serialization may vary, but the logical fields below are required.

#### Document Entity

```text
document
  - document_id
  - job_id
  - user_id
  - source_type               = epub
  - title
  - author
  - detected_language
  - detection_confidence
  - user_language_override
  - source_word_count
  - estimated_token_count
  - chapter_count
  - estimated_batch_count
  - created_at
```

This entity is the normalized metadata record produced by ingestion.
Cost estimation, batch planning, and progress weight calculations depend on it.

#### Credit Transaction

```text
credit_transaction
  - transaction_id
  - user_id
  - job_id                  (optional)
  - job_run_id              (optional)
  - type                    (grant / reservation / consumption / refund / admin_adjustment)
  - amount
  - balance_after
  - created_at
```

These records provide the minimum audit trail for support, idempotent settlement, and future payment integration.

#### Input Artifact Metadata

```text
input_artifact
  - artifact_id
  - artifact_type            = source_epub
  - user_id
  - job_id
  - storage_key
  - content_sha256
  - size_bytes
  - mime_type
  - created_at
  - retention_deadline
```

#### Translation Batch Artifact

```text
translation_batch_artifact
  - artifact_id
  - artifact_version
  - job_id
  - job_run_id
  - batch_index
  - chapter_ref
  - paragraph_ids[]
  - input_hash
  - source_segments[]
  - translated_segments[]
  - explanation_blocks[]
  - consistency_memory_snapshot
  - token_usage
  - provider_metadata
  - created_at
```

#### Output Artifact Metadata

```text
output_artifact
  - artifact_id
  - artifact_type            = output_epub
  - user_id
  - job_id
  - job_run_id
  - storage_key
  - content_sha256
  - size_bytes
  - created_at
  - first_downloaded_at
  - retention_deadline
```

#### Failed Batch Error Artifact

```text
failed_batch_error_artifact
  - artifact_id
  - artifact_version
  - job_id
  - job_run_id
  - batch_index
  - error_class
  - provider_request_id
  - retry_eligible
  - normalized_error_payload
  - created_at
```

Rules:

- runtime artifacts are owned by the enclosing `job` and `job_run`
- translation batch artifacts are written only at explicit orchestration checkpoints
- error artifacts must contain normalized metadata, not raw source text
- artifact versions must be compatible with the `job_run` version markers

### Relational Shape

- one `user` owns one `user_credit_account`
- one `user_credit_account` owns many `credit_transaction` records
- one `user` owns many `jobs`
- one `job` points to one input `artifact`
- one `job` may have many `job_runs`, but only one active run in MVP
- one `job_run` owns many `translation_batch` records
- one `translation_batch` may reference one or more intermediate `artifact` records
- one successful `job_run` produces one output `artifact`
- terminal credit settlement emits `credit_transaction` records
- major state transitions emit `job_event` records
- expensive provider activity emits `cost_ledger_entry` records

### Resumability And Idempotency

The primary resumable unit is one translation batch.

The idempotency boundary is:

`job_run_id + batch_index + pipeline_version + input_hash`

Canonical progress is derived from:

- completed translation batches
- completed pipeline stages
- terminal job state

Artifacts are not canonical by themselves without corresponding database metadata.

---

## Progress And ETA Model

Progress and ETA must be durable job metadata, not a live worker-streaming illusion.

The recommended model is:

- stage-weighted progress
- throughput-informed ETA
- ETA smoothing using rolling throughput averages
- periodic persistence into canonical job state

ETA smoothing should reduce large oscillations during early job stages without hiding major throughput shifts.

This supports:

- browser refresh
- reconnect after disconnect
- support inspection
- improving ETA calibration over time

The UI transport for progress may evolve, but progress computation itself remains backend-owned and durable.

---

## Reproducibility And Versioning

Every executable run should preserve enough version markers to explain behavioral changes across time.

At minimum, `job_run` should carry:

- `pipeline_version`
- `prompt_version`
- `provider_configuration_version`
- `model_alias`
- worker code version where practical

These markers support:

- debugging
- regression analysis
- safer retries
- quality and cost comparisons across releases

The system should not silently resume a run under materially incompatible runtime assumptions.

## Version Compatibility Rules

A `job_run` must execute under the same:

- `pipeline_version`
- `prompt_version`
- `provider_configuration_version`

that were recorded when the run started.

If runtime versions change during execution:

- the existing run must continue using the recorded versions
- retries must reuse the original versions

New runs may use newer versions.

Workers must never silently upgrade versions for an in-flight run.

---

## Retention And File Lifecycle

The job owns the retention lifecycle for all content-bearing artifacts.

### Source Upload

- created during submission
- retained through processing and retry eligibility
- deleted after terminal state plus retention window

### Generated Output

- created at successful export
- retained until first download or retention expiry according to policy
- deleted by cleanup workflow

### Intermediate Structured Artifacts

- created only where needed for resumability or debugging within policy
- retained no longer than the owning job retention window
- deleted together with the job's content artifacts

### Long-Term Metadata

After content deletion, the system retains only metadata needed for:

- job history
- credit transaction history
- support and audit trails
- cost analysis
- architectural review

---

## Explicit Non-Goals For MVP Architecture

The MVP architecture explicitly does not include:

- multi-provider routing
- persistent cross-book glossary infrastructure
- dedicated infrastructure per user
- built-in reading client
- full billing platform
- full distributed tracing stack
- heavy workflow orchestration platform
- non-EPUB inputs or outputs

These may be revisited later, but they are not part of the baseline architecture.

---

## Architecture Implications For Future Work

Implementation planning should treat the following as architecture-defined boundaries rather than open design questions:

- `Next.js` plus `FastAPI` plus Python worker stack split
- shared SaaS with strong logical user isolation
- lightweight pre-submission analysis before job confirmation
- object storage for uploads, outputs, and structured resumable artifacts
- batch-based long-book translation strategy
- translation-only LLM boundary
- user-facing credits separated from internal cost controls
- job-scoped consistency memory
- layered cost controls
- explicit long-job operations policy
- hybrid canonical artifact model
- durable progress and ETA model

Items still expected to be finalized through decisions or benchmarks:

- exact LLM provider choice
- exact prompt and provider benchmark thresholds
- exact consistency-memory schema details
- exact anomaly heuristics for source-language detection
- exact retention window duration

---

## Architecture Checklist Confirmation

Architecture Checklist reviewed — no violations detected.
