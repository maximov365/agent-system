# Unfolda — Feature Map

Status: draft
Version: 0.4
Last updated: 2026-03-10

---

## Purpose

This document answers one question: **what capability blocks does the system consist of?**

It maps every functional capability required for the MVP, grouped by domain. Each block is a cohesive unit of product functionality that can be planned, built, and tested as a distinct concern.

This is not a task list. It is a structural view of what the system must be able to do.

Sources:

- `docs/PRD.md` — product requirements
- `docs/ARCHITECTURE.md` — architectural model
- `docs/DECISIONS.md` — accepted decisions
- `docs/PIPELINE_CONTRACTS.md` — stage contracts

---

## System Map

```text
┌─────────────────────────────────────────────────────────────────┐
│                        USER-FACING                              │
│                                                                 │
│  ┌────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ ┌─────────┐  │
│  │  Auth  │ │  Upload  │ │ Precheck │ │ Config │ │ Jobs &  │  │
│  │        │ │& Validate│ │          │ │        │ │   DL    │  │
│  └────────┘ └──────────┘ └──────────┘ └────────┘ └─────────┘  │
│                                                                 │
│  ┌──────────────────┐  ┌────────────────────────────────────┐   │
│  │  Progress & ETA  │  │          Error & Retry             │   │
│  └──────────────────┘  └────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                    PROCESSING PIPELINE                          │
│                                                                 │
│  INGEST ──→ SEGMENT ──→ TRANSLATE ──→ FORMAT ──→ EXPORT        │
│                              │                                  │
│                       CONSISTENCY                               │
│                         MEMORY                                  │
│                     (supports TRANSLATE)                         │
├─────────────────────────────────────────────────────────────────┤
│                        PLATFORM                                 │
│                                                                 │
│  ┌────────────┐ ┌─────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Job Queue  │ │ Object  │ │ Credits  │ │    Retention     │ │
│  │ & Orchestr.│ │ Storage │ │ & Limits │ │    & Cleanup     │ │
│  └────────────┘ └─────────┘ └──────────┘ └──────────────────┘ │
│                                                                 │
│  ┌────────────┐ ┌─────────────┐ ┌──────────────────────────┐  │
│  │    Cost    │ │  Telemetry  │ │   Security & Privacy     │  │
│  │   Control  │ │             │ │                          │  │
│  └────────────┘ └─────────────┘ └──────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Admin Panel                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Capability Ownership Model

Capabilities belong to one of three domains:

**User-facing** — UI and API interaction with the system.

**Pipeline** — Deterministic document processing stages.

**Platform** — Infrastructure services supporting execution.

Rules:

- User-facing capabilities must not implement pipeline logic.
- Pipeline capabilities must not depend on UI behavior.
- Platform capabilities must remain reusable and must not embed product-specific business rules.

---

## Capability Boundaries

Capabilities are independent domains of responsibility.

A capability:

- owns a coherent part of system behavior
- exposes clear inputs and outputs
- must not duplicate responsibilities of another capability

Pipeline capabilities follow stage contracts defined in `docs/PIPELINE_CONTRACTS.md`.

Platform capabilities provide cross-cutting infrastructure but must not embed pipeline logic.

User-facing capabilities interact with the backend only through the API boundary.

---

## Capability Lifecycle

Capabilities interact through explicit lifecycle transitions.

- User-facing capabilities **initiate** jobs and **present** results.
- Pipeline capabilities **transform** documents through stages.
- Platform capabilities **enforce** operational policies including credits, usage limits, retention, cost limits, and security rules.

No capability may bypass the defined pipeline lifecycle.

---

## Standard Implementation Slice Types

Capabilities may decompose into the following implementation slices:

| Slice | Responsibility |
|---|---|
| UI | Frontend behavior |
| API | Request/response boundary |
| Domain | Core business logic |
| Worker | Asynchronous execution logic |
| Storage | Persistence and artifact management |
| Policy | Validation, credits, security rules |
| Telemetry | Logs, metrics, events |
| Admin | support and operational interfaces |
| Tests | Unit, integration, workflow tests |

Not every capability requires every slice type.

---

## User-Facing Capabilities

### AUTH — Authentication

Authenticate users via Google login and enforce identity at the API boundary.

| Field | Detail |
|---|---|
| Goal | Identify users and protect all API endpoints from unauthenticated access |
| Inputs | Google OAuth token from the web app |
| Outputs | Authenticated `user_id` resolved at the API boundary; session or token for subsequent calls |
| Dependencies | — (foundational; no capability dependencies) |
| Non-goals | Additional auth providers; user profile management; password-based login |
| Slices | UI, API, Policy, Tests |
| Ref | PRD §Delivery Model, ARCH §Authentication Boundary, DEC-001, DEC-002 |

---

### UPLOAD — EPUB Upload & Validation

Accept an EPUB file from the user, validate it, and store it as an input artifact.

| Field | Detail |
|---|---|
| Goal | Safely accept and validate user-provided EPUB files before any processing begins |
| Inputs | EPUB file via file picker or drag-and-drop |
| Outputs | Validated input artifact in object storage + artifact metadata in DB |
| Validation | File format, size limit (50 MB), EPUB structure, DRM rejection |
| Malformed EPUB | Attempt recovery; reject severely broken files at validation |
| Upload path | Client → signed URL from API → object storage |
| Dependencies | AUTH, STORAGE, SECURITY |
| Non-goals | Parsing EPUB content for translation; invoking LLMs; segmentation; content transformation |
| Slices | UI, API, Storage, Policy, Tests |
| Ref | PRD §Upload Experience, ARCH §Submission Flow, DEC-004 |

---

### PRECHECK — Pre-Submission Analysis

Fast EPUB inspection that runs after upload but before job configuration, providing the metadata needed for CONFIG and credit estimation without invoking the full pipeline.

| Field | Detail |
|---|---|
| Goal | Extract lightweight metadata from the uploaded EPUB so the user can configure the job and see credit cost before submission |
| Inputs | Validated EPUB artifact from UPLOAD |
| Outputs | Source language detection preview, estimated word count, EPUB structure summary, submission-relevant metadata |
| Timing | Runs immediately after successful UPLOAD validation; completes before the CONFIG screen is shown |
| Scope | Read-only inspection — does not modify the EPUB or produce pipeline artifacts |
| Dependencies | UPLOAD, STORAGE |
| Non-goals | Full content parsing for translation; segmentation; LLM invocation; replacing INGEST as a pipeline stage |
| Slices | API, Domain, Telemetry, Tests |
| Ref | PRD §Upload Experience, ARCH §Submission Flow |

---

### CONFIG — Translation Configuration

Collect and validate user-selected processing options and produce a normalized job configuration.

| Field | Detail |
|---|---|
| Goal | Present translation options to the user and produce a validated, normalized job settings object |
| Inputs | User selections: mode, target language, source language override, style, level, explanation depth; pre-submission metadata from PRECHECK |
| Outputs | Normalized job configuration validated at the API boundary |
| Options | Mode (Translate / Guided), target language (14 MVP), source language (auto / override), style (literal / natural), level (A1–C1), explanation depth (minimal / standard / detailed) |
| Pre-submission | Estimated word count, approximate processing time, and **estimated credit cost** displayed before confirmation |
| Balance check | If user's credit balance is insufficient for the estimated cost, submission is blocked with a clear message |
| Validation | Config is validated at the API boundary; invalid combinations are rejected before job creation |
| Dependencies | AUTH, PRECHECK (for language detection and word count estimate), QUOTA (credit eligibility check) |
| Non-goals | User-editable glossaries; prompt customization; per-chapter configuration |
| Slices | UI, API, Policy, Tests |
| Ref | PRD §Translation Options, PRD §Supported Languages |

---

### JOBS — Job List & Download

Show the user their submitted jobs with statuses and provide download access to completed results.

| Field | Detail |
|---|---|
| Goal | Give users visibility into all their jobs and access to completed outputs |
| Inputs | Authenticated user request |
| Outputs | Job list with statuses, progress/ETA, download links for completed jobs |
| Shown per job | Title, mode, target language, status, progress/ETA, download link |
| Statuses | validating, queued, processing, completed, failed, expired |
| Download | Via short-lived signed URL from object storage |
| Lifecycle ownership | Job state is owned by the orchestration layer (QUEUE) and exposed to the UI via API |
| Dependencies | AUTH, QUEUE, STORAGE, SECURITY |
| Non-goals | Built-in EPUB reader; reading progress tracking; job sharing |
| Slices | UI, API, Tests |
| Ref | PRD §Jobs List, PRD §Job Lifecycle, ARCH §Download Flow |

---

### PROGRESS — Progress & ETA

Provide durable, backend-owned progress tracking visible in the UI.

| Field | Detail |
|---|---|
| Goal | Show the user where their job is and how long it will take, surviving browser refresh and reconnect |
| Inputs | Progress snapshots persisted by the worker during processing |
| Outputs | Percentage progress and estimated time remaining, available via API |
| Model | Stage-weighted progress, throughput-informed ETA |
| Durability | Persisted in DB; survives browser refresh, reconnect, and retries |
| Dependencies | QUEUE, TELEMETRY |
| Ownership | Progress model is backend/domain-owned; worker only emits persisted snapshots |
| Non-goals | Live streaming from worker to browser; sub-second updates; per-paragraph progress |
| Slices | UI, API, Domain, Worker, Tests |
| Ref | PRD §Job Lifecycle, ARCH §Progress And ETA Model, DEC-010 |

---

### ERROR-UX — Error Handling & Retry

Present clear error feedback to users and support job retry.

| Field | Detail |
|---|---|
| Goal | Ensure users understand what went wrong and can take action |
| Inputs | Error states from validation, processing, and policy enforcement |
| Outputs | Structured error messages in the UI; retry action when eligible |
| Validation errors | Shown immediately before processing (file format, DRM, size, structure) |
| Processing failures | Job transitions to `failed` with a structured, user-readable error message |
| Policy failures | Credit balance insufficient, cost cap exceeded — shown with clear reason |
| Retry eligibility | Supported within retention window using original uploaded file; if file expired, user must re-upload |
| Credit rule | Failed jobs do not consume credits — reserved credits are refunded |
| Terminal guarantee | Every job reaches completed, failed, or expired — no silent drops |
| Dependencies | AUTH, QUEUE, STORAGE |
| Non-goals | Automatic retry without user action; partial result delivery; error recovery inside pipeline stages |
| Slices | UI, API, Policy, Tests |
| Ref | PRD §Error Handling, ARCH §Failure Taxonomy, DEC-007 |

---

## Processing Pipeline Capabilities

### INGEST — EPUB Ingestion & Language Detection

Parse the uploaded EPUB, extract text and structure, detect source language.

| Field | Detail |
|---|---|
| Goal | Produce a normalized document representation from a raw EPUB, including detected language |
| Inputs | Validated EPUB binary from object storage |
| Outputs | Normalized document: text, structure (spine, chapters, images, footnotes, links, CSS refs), metadata, detected source language, word count |
| Language detection | Book-level auto-detection; low confidence may trigger anomaly check; user can override via CONFIG |
| DRM handling | Detected and rejected at this stage |
| Malformed input | Attempt recoverable text extraction with best-effort structure preservation |
| Dependencies | STORAGE |
| Non-goals | Calling LLMs; segmenting content; translating; formatting output |
| Slices | Domain, Worker, Storage, Tests |
| Contract | `docs/PIPELINE_CONTRACTS.md` §Ingestion |
| Ref | ARCH §Ingestion, DEC-004 |

---

### SEGMENT — Text Segmentation

Split the normalized document into paragraph-level processing units with batch-planning metadata.

| Field | Detail |
|---|---|
| Goal | Produce a segment collection ready for translation batching |
| Inputs | Normalized document from INGEST |
| Outputs | Segment collection: paragraph-level segments with chapter refs, token estimates, batch-planning metadata |
| User-visible unit | Paragraph (internal splitting may occur for LLM context limits, but output reconstructs to paragraph level) |
| Dependencies | INGEST |
| Non-goals | Rewriting meaning; calling LLMs; formatting output; modifying document structure |
| Slices | Domain, Worker, Tests |
| Contract | `docs/PIPELINE_CONTRACTS.md` §Segmentation |
| Ref | PRD §Segmentation Model, ARCH §Segmentation, DEC-005 |

---

### TRANSLATE — AI Translation

Translate paragraph-level segments into the target language. The only LLM-enabled stage.

| Field | Detail |
|---|---|
| Goal | Produce translated (and optionally explained) segments for every paragraph in the book |
| Inputs | Segment collection from SEGMENT; job configuration from CONFIG; consistency memory |
| Outputs | Translated segment collection: translation per paragraph, explanations per paragraph (Guided mode) |
| Translate Mode | Context-aware full translation per paragraph |
| Guided Mode | Translation + explanation generation (may use separate internal passes) |
| Execution model | Chapter-scoped, token-bounded translation batches |
| Resumability | Translation batch is the primary resumable unit; persisted at explicit checkpoints |
| Prompts | Externalized in `prompts/` |
| Provider | Single provider adapter; model from configuration; no hardcoded vendor |
| Dependencies | SEGMENT, CONSISTENCY, COST, STORAGE, TELEMETRY |
| Non-goals | Changing segmentation boundaries; embedding presentation formatting; hiding retries; multi-provider routing |
| Slices | Domain, Worker, Storage, Telemetry, Tests |
| Contract | `docs/PIPELINE_CONTRACTS.md` §Translation |
| Ref | ARCH §Translation, DEC-003, DEC-005 |

---

### CONSISTENCY — Translation Consistency Memory

Maintain coherent translation across the entire book within a single job.

This capability supports the TRANSLATE stage but is not an independent pipeline stage. It has no separate stage contract in `docs/PIPELINE_CONTRACTS.md`.

| Field | Detail |
|---|---|
| Goal | Ensure names, terms, gender, and terminology remain consistent across all translation batches |
| Inputs | Translated batch outputs; extracted entities; previous consistency state |
| Outputs | Updated consistency memory: terminology map, named-entity registry, rolling chapter context summary, unresolved ambiguity notes |
| Scope | Job-scoped; not reused across books |
| Persistence | May be persisted as structured artifact for resumability; follows job retention window |
| Dependencies | Translation-batch outputs and prior consistency state (data dependency, not a capability-level dependency on TRANSLATE) |
| Non-goals | User-editable glossary; cross-book memory; persistent knowledge base |
| Slices | Domain, Storage, Tests |
| Ref | PRD §Translation Consistency, ARCH §Consistency Strategy, DEC-005 |

---

### FORMAT — Output Formatting

Assemble translated segments into mode-specific reading structures.

| Field | Detail |
|---|---|
| Goal | Produce structured reading output ready for EPUB reconstruction |
| Inputs | Translated segment collection from TRANSLATE |
| Outputs | Formatted document: mode-specific block structure per paragraph |
| Translate Mode | Translated paragraph replaces original |
| Guided Mode | 4-block structure: original → translation → explanations → original (shown again) |
| Behavior | Deterministic; no LLM calls |
| Dependencies | TRANSLATE |
| Non-goals | Translating text; modifying segment content; calling LLMs; changing segmentation boundaries; EPUB assembly |
| Slices | Domain, Worker, Tests |
| Contract | `docs/PIPELINE_CONTRACTS.md` §Formatting |
| Ref | PRD §Product Modes, ARCH §Formatting |

---

### EXPORT — EPUB Export

Reconstruct a valid EPUB from formatted output.

| Field | Detail |
|---|---|
| Goal | Produce a valid, downloadable EPUB that preserves book structure and includes output metadata |
| Inputs | Formatted document from FORMAT; original EPUB structure from INGEST |
| Outputs | Generated EPUB binary stored in object storage + output artifact metadata in DB |
| Preserves | Spine order, chapter structure, images, footnotes, links, CSS |
| Injects | Title suffix, preserved author, updated language, description note, disclaimer page |
| Dependencies | FORMAT, INGEST (for original structure), STORAGE |
| Non-goals | Translating text; reformatting content; calling LLMs; changing formatting semantics; producing non-EPUB formats |
| Slices | Domain, Worker, Storage, Tests |
| Contract | `docs/PIPELINE_CONTRACTS.md` §Export |
| Ref | PRD §EPUB Structure Preservation, PRD §Output Metadata, ARCH §Export |

---

## Platform Capabilities

### QUEUE — Job Queue & Orchestration

Async processing of book transformation jobs with explicit lifecycle management.

| Field | Detail |
|---|---|
| Goal | Orchestrate pipeline execution as background jobs with reliable state management |
| Inputs | Validated job from API with normalized configuration |
| Outputs | Terminal job state (completed/failed); progress updates; timeline events |
| Broker | Redis (signaling only, non-canonical) |
| Orchestration | Python worker runtime; stage execution ordering, checkpoint persistence |
| State | Canonical state in PostgreSQL; worker memory is ephemeral |
| Lifecycle | validating → queued → processing → completed/failed → expired |
| Lease model | Explicit lease ownership, heartbeats, expiry detection |
| One active job | Per user, at most one job in an active state |
| Dependencies | STORAGE, COST, TELEMETRY, RETENTION |
| Non-goals | Containing pipeline stage logic; calling LLMs; business ownership of content transformation rules; heavy workflow engine |
| Slices | API, Worker, Domain, Storage, Telemetry, Tests |
| Ref | ARCH §Worker Runtime, ARCH §Job Lifecycle State Machine, DEC-001, DEC-007 |

---

### STORAGE — Object Storage

Temporary storage for binary and structured artifacts.

| Field | Detail |
|---|---|
| Goal | Store and serve uploaded files, generated outputs, and structured resumable artifacts |
| Inputs | Binary files and structured artifacts from upload, pipeline, and orchestration |
| Outputs | Stored objects accessible via signed URLs; artifact metadata in DB |
| Artifact classes | `source_epub`, `output_epub`, `translation_batch_artifact`, optional `consistency_memory_snapshot` |
| Access | Via short-lived, purpose-specific signed URLs |
| Key namespace | `users/{user_id}/jobs/{job_id}/{artifact_type}/{artifact_id}` |
| Canonical metadata | In PostgreSQL; artifacts without DB records are not canonical |
| Dependencies | SECURITY |
| Non-goals | Long-term content retention; serving as canonical state store; replacing database for metadata |
| Slices | API, Storage, Policy, Tests |
| Ref | ARCH §Object Storage, ARCH §Storage Key Namespace, DEC-004 |

---

### QUOTA — Credits & Usage Limits

Manage user credit balances and enforce spending limits before and during processing.

| Field | Detail |
|---|---|
| Goal | Provide a transparent, user-visible credit economy that controls access to processing and supports future payment integration |
| Inputs | Source word count from INGEST; processing mode and settings from CONFIG; job completion/failure events |
| Outputs | Credit balance (visible to user); per-job credit cost estimate; reservation/consumption/refund events |
| Unit | Abstract credits — converted from source word count, mode, and settings via admin-configurable multipliers |
| Mode multipliers | Guided Mode costs more than Translate Mode (extra explanation passes); exact multipliers are admin-configurable constants |
| Credit visibility | User sees current balance in the UI at all times; estimated credit cost is shown before job confirmation; basic credit transaction history (grant, reservation, consumption, refund) |
| Initial grant | On registration, each user receives a configurable credit balance (amount set by admin) |
| Reservation | Credits are reserved when a job is submitted; consumed on successful completion; refunded on failure |
| Failed jobs | Do not consume credits — reserved amount is refunded to balance |
| Enforcement | Before queue admission + before expensive translation work begins |
| Idempotency | Credit reservations and refunds must be idempotent per `job_run` |
| Management | Admin manages credit balances — grant credits, adjust balances, view credit history |
| Dependencies | AUTH, ADMIN, COST |
| Non-goals | Self-service credit purchase (payment provider); automated billing; monthly resets; monetary price display |
| Future-ready | The credits abstraction is designed so that a payment layer (Stripe) can be added without changing the core pipeline or credit logic |
| Slices | UI, API, Domain, Policy, Admin, Tests |
| Ref | PRD §Credits & Usage Limits, ARCH §Quota Enforcement, DEC-002, DEC-006 |

---

### RETENTION — Retention & Cleanup

File lifecycle management ensuring no long-term content retention.

| Field | Detail |
|---|---|
| Goal | Delete content-bearing artifacts after the retention window; keep metadata only |
| Inputs | Terminal job state + retention deadline from DB |
| Outputs | Deleted artifacts in object storage; updated metadata in DB; `cleanup_started` / `cleanup_completed` events |
| Uploaded EPUB | Deleted after terminal state + retention window |
| Generated EPUB | Deleted after first download or retention expiry (whichever first) |
| Intermediate artifacts | Follow job retention window |
| Long-term | Metadata only (no book content) |
| Cleanup process | Dedicated scheduled task; idempotent; must not delete artifacts for retry-eligible jobs |
| Dependencies | STORAGE, QUEUE, TELEMETRY |
| Non-goals | Real-time deletion; content archival; backup management |
| Slices | Worker, Storage, Domain, Telemetry, Tests |
| Ref | PRD §Storage Policy, ARCH §Retention And File Lifecycle, DEC-004 |

---

### COST — Internal Cost Control

Layered cost protection for LLM-backed processing. This is the **internal** cost accounting layer — it tracks actual LLM token costs and enforces hard caps. The **user-facing** credit economy is managed by QUOTA.

| Field | Detail |
|---|---|
| Goal | Prevent economically unsafe jobs from running and account for actual inference costs |
| Inputs | Source word count, mode, language pair, batch-level token usage from provider |
| Outputs | Pre-run cost estimate; hard cap check results; `cost_ledger_entry` per provider call |
| Pre-run | Estimation based on word count, mode, language pair, expected passes |
| Hard caps | Per-job, per-user credit period, per-retry budget |
| Accounting | Token usage and estimated cost per batch and per run |
| Rejection | Jobs exceeding limits rejected before processing with clear policy reason |
| Boundary | COST tracks internal LLM economics; QUOTA manages user-visible credits — these are separate layers |
| Dependencies | TELEMETRY |
| Non-goals | Pricing logic, credit conversion, or user billing (that is QUOTA's responsibility); user-facing cost display; real-time cost dashboard |
| Slices | Domain, Worker, Policy, Telemetry, Tests |
| Ref | ARCH §Cost Architecture, DEC-006 |

---

### TELEMETRY — Observability & Quality Validation

Structured telemetry for operations, debugging, and quality regression detection.

| Field | Detail |
|---|---|
| Goal | Enable operations, debugging, and quality monitoring without leaking book content |
| Inputs | Events from all stages, orchestration, and platform capabilities |
| Outputs | Structured logs, durable job timeline, metrics, benchmark results |
| Runtime | Structured logs, job timeline events, stage timings, provider latency/throttling metrics, token usage |
| Timeline events | 16+ event types from `job_created` through `job_expired` |
| Quality | Evaluation dataset, comparable benchmark runs, regression detection |
| Correlation | All events must correlate with `job_id` and `job_run_id` |
| Dependencies | — (foundational; consumed by other capabilities) |
| Non-goals | Raw-text debugging; full distributed tracing stack in MVP; real-time alerting platform |
| Slices | Domain, Worker, Telemetry, Tests |
| Ref | ARCH §Telemetry And Quality Validation, DEC-008 |

---

### SECURITY — Security & Privacy

Book content protection and access control across all system boundaries.

| Field | Detail |
|---|---|
| Goal | Protect user content from leakage, unauthorized access, and misuse |
| Inputs | Policies applied across all capabilities |
| Outputs | Enforced content rules, DRM rejection, scoped provider payloads, audited access |
| Content rule | Raw book text never in logs, traces, analytics, or error payloads |
| DRM | Rejected at validation; never circumvented |
| Provider boundary | Payload scoped to current batch + bounded context only |
| Training opt-out | Provider config should disable training on customer content |
| Admin access | Metadata-only by default; raw-content access time-bounded and audited |
| Signed URLs | Object-scoped, short-lived, purpose-specific |
| Dependencies | — (cross-cutting; enforced across all capabilities) |
| Non-goals | Full penetration testing framework; SOC 2 compliance in MVP; encryption at rest beyond provider defaults |
| Slices | Policy, API, Storage, Tests |
| Ref | ARCH §Security Privacy And Compliance Boundary, DEC-004 |

---

### ADMIN — Admin Panel

Minimal admin interface for user and job operations.

| Field | Detail |
|---|---|
| Goal | Allow admin to manage user credit balances, configure credit settings, and monitor job execution |
| Inputs | Admin-authenticated requests |
| Outputs | User list, credit management actions, job inspection views |
| Credit management | Grant credits, adjust balances, view credit history per user, configure initial credit grant amount |
| Mode multipliers | Configure credit-to-word-count multipliers per processing mode (Translate / Guided) |
| Job monitoring | View job list, statuses, timelines, error details |
| Must not | Bypass ownership, retention, audit, or privacy controls |
| Dependencies | AUTH, QUOTA, QUEUE, TELEMETRY, SECURITY |
| Non-goals | Payment provider management; self-service billing dashboard; public-facing dashboard; raw book content access |
| Slices | UI, API, Policy, Admin, Tests |
| Ref | PRD §Credits & Usage Limits, PRD §MVP Scope, ARCH §Infrastructure Components, DEC-002 |

---

## Capability Dependency Map

| Capability | Depends on |
|---|---|
| AUTH | — |
| UPLOAD | AUTH, STORAGE, SECURITY |
| PRECHECK | UPLOAD, STORAGE |
| CONFIG | AUTH, PRECHECK, QUOTA |
| JOBS | AUTH, QUEUE, STORAGE, SECURITY |
| PROGRESS | QUEUE, TELEMETRY |
| ERROR-UX | AUTH, QUEUE, STORAGE |
| INGEST | STORAGE |
| SEGMENT | INGEST |
| TRANSLATE | SEGMENT, CONSISTENCY, COST, STORAGE, TELEMETRY |
| CONSISTENCY | — (data coupling with TRANSLATE; no capability-level dependency) |
| FORMAT | TRANSLATE |
| EXPORT | FORMAT, INGEST, STORAGE |
| QUEUE | STORAGE, COST, TELEMETRY, RETENTION |
| STORAGE | SECURITY |
| QUOTA | AUTH, ADMIN, COST |
| RETENTION | STORAGE, QUEUE, TELEMETRY |
| COST | TELEMETRY |
| TELEMETRY | — |
| SECURITY | — |
| ADMIN | AUTH, QUOTA, QUEUE, TELEMETRY, SECURITY |

Foundational capabilities with no dependencies: **AUTH**, **TELEMETRY**, **SECURITY**.

---

## Capability Index

| ID | Capability | Domain | Pipeline Stage |
|---|---|---|---|
| AUTH | Authentication | User-facing | — |
| UPLOAD | EPUB Upload & Validation | User-facing | — |
| PRECHECK | Pre-Submission Analysis | User-facing | — |
| CONFIG | Translation Configuration | User-facing | — |
| JOBS | Job List & Download | User-facing | — |
| PROGRESS | Progress & ETA | User-facing | — |
| ERROR-UX | Error Handling & Retry | User-facing | — |
| INGEST | EPUB Ingestion & Language Detection | Pipeline | Ingestion |
| SEGMENT | Text Segmentation | Pipeline | Segmentation |
| TRANSLATE | AI Translation | Pipeline | Translation |
| CONSISTENCY | Translation Consistency Memory | Pipeline | Translation (support) |
| FORMAT | Output Formatting | Pipeline | Formatting |
| EXPORT | EPUB Export | Pipeline | Export |
| QUEUE | Job Queue & Orchestration | Platform | — |
| STORAGE | Object Storage | Platform | — |
| QUOTA | Credits & Usage Limits | Platform | — |
| RETENTION | Retention & Cleanup | Platform | — |
| COST | Cost Control | Platform | — |
| TELEMETRY | Observability & Quality | Platform | — |
| SECURITY | Security & Privacy | Platform | — |
| ADMIN | Admin Panel | Platform | — |

---

## Cross-Reference: Capability → Key Documents

| Capability | PRD | ARCHITECTURE | DECISIONS | PIPELINE_CONTRACTS |
|---|---|---|---|---|
| AUTH | §Delivery Model | §Authentication Boundary | DEC-001, DEC-002 | — |
| UPLOAD | §Upload Experience | §Submission Flow | DEC-004 | — |
| PRECHECK | §Upload Experience | §Submission Flow | — | — |
| CONFIG | §Translation Options | — | — | — |
| JOBS | §Job Lifecycle, §Jobs List | §Download Flow | — | — |
| PROGRESS | §Job Lifecycle | §Progress And ETA Model | DEC-010 | — |
| ERROR-UX | §Error Handling | §Failure Taxonomy | DEC-007 | — |
| INGEST | §EPUB Structure, §Translation Options | §Ingestion | DEC-004 | §Ingestion |
| SEGMENT | §Segmentation Model | §Segmentation | DEC-005 | §Segmentation |
| TRANSLATE | §Product Modes | §Translation | DEC-003, DEC-005 | §Translation |
| CONSISTENCY | §Translation Consistency | §Consistency Strategy | DEC-005 | — |
| FORMAT | §Product Modes | §Formatting | — | §Formatting |
| EXPORT | §Output Metadata | §Export | — | §Export |
| QUEUE | §Job Lifecycle | §Worker Runtime | DEC-001, DEC-007 | — |
| STORAGE | §Storage Policy | §Object Storage | DEC-004 | — |
| QUOTA | §Credits & Usage Limits | §Quota Enforcement | DEC-002, DEC-006 | — |
| RETENTION | §Storage Policy | §Retention And File Lifecycle | DEC-004 | — |
| COST | §Credits & Usage Limits | §Cost Architecture | DEC-006 | — |
| TELEMETRY | — | §Telemetry | DEC-008 | — |
| SECURITY | §Storage Policy | §Security Privacy | DEC-004 | — |
| ADMIN | §MVP Scope | §Infrastructure Components | DEC-002 | — |
