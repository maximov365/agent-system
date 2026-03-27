# Unfolda — Feature Specifications

Status: draft
Version: 0.2
Last updated: 2026-03-16

---

## Purpose

This document contains **individual feature specifications** for every capability in the Unfolda MVP.

Each feature maps 1:1 to a capability block defined in `docs/FEATURE_MAP.md` and follows a standardized structure derived from `docs/FEATURE_TEMPLATE.md`.

Sources:

- `docs/PRD.md` — product requirements
- `docs/FEATURE_MAP.md` — capability blocks, dependencies, slices
- `docs/ARCHITECTURE.md` — architectural model
- `docs/DECISIONS.md` — accepted decisions
- `docs/PIPELINE_CONTRACTS.md` — stage contracts

---

## How to read this document

Each feature includes:

| Section | Purpose |
|---|---|
| Summary | What the feature does in 2–4 sentences |
| Goals | What the feature achieves |
| Non-Goals | What the feature explicitly excludes |
| User Flow | High-level interaction flow (user-facing features only) |
| Functional Requirements | Required behavior |
| MVP Slice | Smallest version that delivers value |
| Constraints | Architectural and product constraints |
| Success Criteria | How completion is verified |
| Open Questions | Unresolved items |
| Tasks | Placeholder for implementation task IDs |

Features are grouped by domain: **User-Facing**, **Processing Pipeline**, **Platform**.

Cross-cutting policies that apply to multiple features are defined once in the **Cross-Cutting Policies** section below and referenced from individual features.

---

# Cross-Cutting Policies

The following policies apply across multiple features. They are defined here to avoid duplication and ensure consistency. Individual features reference these policies where relevant.

---

## POLICY-VERSION — Job Run Version Stamping

Every `job_run` must record a complete version snapshot so that results can be reproduced and regressions traced.

**Required version markers per `job_run`:**

| Marker | Source |
|---|---|
| `prompt_version` | Prompt template version used for translation/explanation |
| `model_provider` | LLM provider identifier |
| `model_name` | Model name or alias |
| `model_version` | Model version or checkpoint |
| `pipeline_contract_version` | Version from `PIPELINE_CONTRACTS.md` |
| `segmentation_version` | Segmentation logic version |
| `quality_check_version` | Quality check ruleset version |
| `credit_policy_version` | Credit multiplier and reservation logic version |
| `cost_policy_version` | Internal cost cap and estimation logic version |

**Rules:**

- All markers are recorded at run start and never silently upgraded for in-flight runs (DEC-009)
- Version markers are included in telemetry events and available in admin/support views
- A change in any marker for the same input may produce different output — this is expected and traceable

**Applies to:** QUEUE, TRANSLATE, QUOTA, COST, TELEMETRY

---

## POLICY-IDEMPOTENCY — Submission & Idempotency

Protect against duplicate job creation from double-clicks, browser retries, or network hiccups.

**Rules:**

- The client generates a `client_submission_id` (UUID) before sending the CreateJob request
- The API treats CreateJob as idempotent within a short deduplication window (e.g. 60 seconds): same `client_submission_id` → same job returned, no double creation
- Credit reservation is tied to the job, not the request — duplicate requests do not reserve credits twice
- If a job already exists for the same user in an active state, new submissions are rejected (one active job rule)
- Upload deduplication is not required — the same EPUB may be uploaded and processed multiple times with different settings

**Applies to:** CONFIG (submission), QUEUE (job creation), QUOTA (credit reservation)

---

## POLICY-CANCELLATION — Cancellation Semantics

Cancellation is best-effort and takes effect at safe checkpoints. The policy is defined per pipeline stage to remove ambiguity.

**Per-stage cancellation behavior:**

| Stage | Cancellable? | Checkpoint |
|---|---|---|
| INGEST | Yes | Before INGEST starts; during INGEST if no significant work committed |
| SEGMENT | Yes | Before SEGMENT starts; between chapters if chunked |
| TRANSLATE | Yes | Before the next provider call; **never mid-provider-call** |
| FORMAT | Finish-fast | Stage is deterministic and fast — run to completion rather than cancel mid-stage |
| EXPORT | Finish-fast | Stage is deterministic and fast — run to completion rather than cancel mid-stage |

**Cancellation lifecycle events:**

| Event | Meaning |
|---|---|
| `cancel_requested` | User or admin initiated cancellation |
| `cancellation_acknowledged` | Worker has seen the request and will stop at the next safe checkpoint |
| `cancelled_at_safe_checkpoint` | Worker has stopped; job transitions to `cancelled` |

**Rules:**

- Provider calls are non-interruptible — cancellation waits for the current call to complete
- If the current stage is finish-fast, it completes before the job transitions to `cancelled`
- Reserved credits are refunded idempotently on cancellation (DEC-006, DEC-012)
- The elapsed time between `cancel_requested` and `cancelled_at_safe_checkpoint` depends on provider call duration and stage nature; this is communicated to the user

**Applies to:** QUEUE, TRANSLATE, ERROR-UX, TELEMETRY

---

## POLICY-RETRY — Retry Taxonomy

Failures are classified into explicit categories that determine retry eligibility, backoff behavior, and escalation.

**Failure classification:**

| Class | Retryable? | Max retries | Backoff | Requires review? |
|---|---|---|---|---|
| `provider_transient` | Yes | 3 | Exponential with jitter | No |
| `provider_rate_limited` | Yes | 5 | Rate-limit-aware backoff | No |
| `provider_timeout` | Yes | 3 | Exponential with jitter | No |
| `provider_malformed_response` | Yes (once) | 1 | Immediate | If repeated |
| `content_deterministic` | No | — | — | Yes |
| `input_corrupt` | No | — | — | No (reject) |
| `policy_reject` | No | — | — | No (user-visible) |
| `internal_bug` | No | — | — | Yes |
| `infra_transient` | Yes | 3 | Exponential with jitter | No |
| `infra_persistent` | No | — | — | Yes |

**Rules:**

- Retries preserve `batch_index`, `input_hash`, `prompt_version`, `pipeline_version`, and `provider_configuration_version` (DEC-007)
- Retry budgets are bounded per job_run (DEC-007)
- Poison jobs (repeated failures) move to quarantine
- Failure class is recorded in telemetry and visible in admin

**Applies to:** QUEUE, TRANSLATE, COST, TELEMETRY, ERROR-UX

---

## POLICY-COMPLETION — Strict All-or-Nothing Completion

**MVP policy:** a job is `completed` only if all paragraphs are successfully translated and exported.

If any batch fails after exhausting retry budget, the entire job fails. No partial or degraded output is delivered.

**Rationale:** partial output creates ambiguous quality expectations and complicates credit settlement. For MVP, strict all-or-nothing is simpler and safer.

**Future direction:** controlled degraded completion (e.g. skip a single failed paragraph with a placeholder) may be considered post-MVP if data shows specific failure patterns that affect otherwise-successful books.

**Applies to:** QUEUE, TRANSLATE, FORMAT, EXPORT, ERROR-UX

---

## POLICY-FINGERPRINT — Book & Artifact Fingerprinting

Content-safe fingerprints for diagnostics, deduplication, and corruption detection.

**Required fingerprints:**

| Artifact | Fingerprint | Purpose |
|---|---|---|
| Source EPUB | SHA-256 of uploaded file | Detect re-uploads, verify integrity |
| Normalized document | SHA-256 of normalized text + structure | Detect INGEST changes, enable pipeline reproducibility checks |
| Output EPUB | SHA-256 of generated file | Verify delivery integrity |
| Translation batch artifact | SHA-256 per batch | Detect corruption, verify resumability |

**Rules:**

- Fingerprints are metadata only — stored in DB, never derived from raw text at query time
- Fingerprints must not leak book content (SHA-256 is one-way)
- Used for diagnostics and analytics, not for content-based deduplication of user uploads (users may legitimately process the same book with different settings)

**Applies to:** UPLOAD, INGEST, TRANSLATE, EXPORT, STORAGE, TELEMETRY

---

## POLICY-SCHEMA — Pipeline Artifact Schema Versioning

Structured artifacts produced by pipeline stages must carry an explicit schema version for resumability and backward compatibility.

**Rules:**

- Each pipeline stage output artifact includes a `schema_version` field
- Schema versions follow semantic versioning: `major.minor`
- A `major` version change is a breaking change — in-flight jobs using the old schema cannot resume with the new version
- A `minor` version change is backward-compatible — in-flight jobs can continue
- When a breaking schema change ships, in-flight jobs must either: complete on the old schema, or be failed and retried from scratch
- `pipeline_contract_version` recorded per `job_run` (POLICY-VERSION) enables tracing which schema was used

**Applies to:** INGEST, SEGMENT, TRANSLATE, FORMAT, EXPORT, QUEUE

---

## POLICY-PROMPT-BUDGET — Prompt Input Budget Accounting

Before each LLM provider call, compute the full token budget to prevent context window overflow.

**Budget components:**

| Component | Description |
|---|---|
| System prompt | Fixed system instruction tokens |
| Instruction prompt | Stage-specific instruction tokens |
| Consistency memory | Terminology map + entity registry + chapter context |
| Current batch | Source text tokens for the current translation batch |
| Reserved output budget | Expected output token allocation |
| Safety margin | Buffer for tokenizer variance and response overhead |

**Rules:**

- Total of all components must fit within the effective model context window
- If consistency memory grows too large, it must be trimmed (oldest/least-relevant entries) rather than overflowing the context
- Batch shaping (SEGMENT) must account for the expected overhead from consistency memory and prompts
- Budget breakdown is logged per batch in telemetry at debug level

**Applies to:** TRANSLATE, SEGMENT (batch planning), COST, CONSISTENCY

---

## POLICY-PRIVACY — Content Privacy & No-Raw-Text Rule

**Rule:** raw book text must never appear in logs, traces, analytics payloads, error payloads, admin views, or telemetry events.

This is an absolute rule with no MVP exceptions (DEC-004).

**Permitted:**

- Metadata (word counts, language codes, chapter counts, fingerprints)
- Structured quality signals (translation length ratio, untranslated segment flags)
- Aggregated statistics

**Not permitted:**

- Raw paragraphs in log messages
- Source text in error payloads
- Translated text in analytics events
- Book content in admin panel views

**Applies to:** all features

---

## POLICY-AUDIT — Audit Event Requirements

The following actions must produce durable audit events:

- Credit grants, balance adjustments, reservations, consumptions, refunds
- Admin actions (user management, credit changes, configuration changes)
- Job state transitions
- Signed URL issuance
- Policy rejections (credit insufficient, cost cap, DRM, abuse)
- Retries and cancellation requests
- Expensive provider activity
- Exceptional raw-content access (break-glass)

Audit events are stored durably and are never silently dropped.

**Applies to:** QUOTA, ADMIN, QUEUE, SECURITY, TELEMETRY

---

## POLICY-ANALYTICS — Product Analytics Event Tracking

Track user behavior and product usage for product decisions, funnel analysis, and feature prioritization.

**Core product events:**

| Event | Trigger | Key properties |
|---|---|---|
| `user_registered` | First Google login | `user_id`, `timestamp` |
| `user_signed_in` | Subsequent login | `user_id`, `timestamp` |
| `upload_started` | User initiates file upload | `user_id`, `file_size` |
| `upload_completed` | File successfully uploaded and validated | `user_id`, `file_size`, `word_count_estimate`, `source_language` |
| `upload_failed` | Validation fails | `user_id`, `failure_reason` (DRM, size, format, structure) |
| `config_viewed` | User reaches the config screen | `user_id`, `source_language`, `word_count_estimate` |
| `config_changed` | User modifies a config option | `user_id`, `option_name`, `new_value` |
| `job_submitted` | User confirms and submits | `user_id`, `job_id`, `mode`, `target_language`, `style`, `level`, `credit_cost` |
| `job_submission_blocked` | Insufficient credits or policy reject | `user_id`, `block_reason` |
| `job_completed` | Job finishes successfully | `user_id`, `job_id`, `mode`, `processing_duration`, `credits_consumed` |
| `job_failed` | Job reaches failed state | `user_id`, `job_id`, `failure_class`, `stage` |
| `job_cancelled` | Job cancelled by user | `user_id`, `job_id`, `cancelled_at_stage` |
| `download_started` | User clicks download | `user_id`, `job_id` |
| `download_completed` | Signed URL served | `user_id`, `job_id` |
| `retry_initiated` | User clicks retry | `user_id`, `job_id`, `original_failure_class` |
| `credit_history_viewed` | User opens credit transaction history | `user_id` |
| `page_viewed` | User navigates to a screen | `user_id`, `page_name` |

**Rules:**

- Analytics events must never contain raw book content (POLICY-PRIVACY)
- Analytics events are separate from operational telemetry (TELEMETRY) — they serve product decisions, not debugging
- Analytics events should be fire-and-forget — failures in analytics must not block user actions
- Analytics event schema should be versioned and documented
- User consent for analytics tracking must be obtained where legally required

**Applies to:** AUTH, UPLOAD, PRECHECK, CONFIG, JOBS, QUOTA, ERROR-UX

---

## POLICY-COPYRIGHT — Copyright & Acceptable Use

**Rules:**

- Users must accept terms of service that include a declaration that they have the right to process the uploaded file
- The service does not circumvent DRM or copy protection
- The service may reject or suspend accounts exhibiting abusive usage patterns
- Retention and privacy policies are clearly communicated in the UI before upload
- The service does not store or redistribute book content beyond the defined retention window
- Generated output includes a disclaimer page stating it is AI-generated and not an official translation

**MVP implementation:**

- Terms acceptance on first login (checkbox or implicit via ToS link)
- DRM rejection at upload validation
- Disclaimer page injected in output EPUB (FEAT-EXPORT)
- Abuse detection is manual/admin-driven for MVP; automated detection is post-MVP

**Applies to:** AUTH, UPLOAD, EXPORT, SECURITY, ADMIN

---

# Quality & Launch Readiness

---

## Quality Gates

Minimum quality thresholds that must be met before MVP launch. These are evaluated using the quality benchmark infrastructure defined in FEAT-TELEMETRY.

| Gate | Metric | Threshold | Notes |
|---|---|---|---|
| Language detection accuracy | Correct source language for MVP language list | ≥ 95% | Evaluated on benchmark corpus |
| Structural preservation | Output EPUB preserves chapter/spine structure | ≥ 98% pass rate | Across benchmark books |
| Paragraph completeness | No missing paragraphs in output vs input | ≥ 99% | Per-book check |
| Hallucination rate | Paragraphs with content not present in source | ≤ 1% | Estimated via automated heuristics |
| Reader compatibility | Output opens correctly in target readers (Apple Books, Moon Reader, KOReader) | ≥ 95% pass rate | Manual + automated checks |
| Retry recovery | Failed-then-retried jobs complete successfully | ≥ 90% | For provider-transient failures |
| Credit accuracy | Reserved credits match consumed credits (±5%) | ≥ 95% of jobs | Pre-submission estimate vs actual |
| End-to-end success | Typical book (50k–100k words) completes without failure | ≥ 90% | Across benchmark set |

These thresholds are initial targets. Exact values may be adjusted based on benchmark results before launch.

---

## Source Language Confidence Policy

Source language auto-detection may have varying confidence levels. The policy defines UX behavior per confidence tier.

| Confidence | UX behavior |
|---|---|
| High (≥ 90%) | Auto-fill source language; user can override |
| Medium (60–89%) | Yellow warning; editable field; user should confirm |
| Low (< 60%) | Explicit user confirmation required before proceeding |

**Rules:**

- Confidence is computed by PRECHECK, not by the user
- User override always takes precedence regardless of confidence
- User override is passed to INGEST and TRANSLATE as the authoritative source language
- Low-confidence detection triggers a telemetry event for quality monitoring
- Confidence thresholds are configurable (exact values TBD per Architect)

---

## Language Pair Support Matrix

Not all language pairs perform equally. The MVP defines an explicit support matrix.

**Support tiers:**

| Tier | Meaning | UX |
|---|---|---|
| Supported | Validated and quality-tested for MVP | Available without warning |
| Experimental | May work but not quality-validated | Available with a "quality may vary" warning |
| Unsupported | Not available in MVP | Not selectable |

**MVP matrix approach:**

- The 14 MVP languages define the selectable source and target options
- High-confidence pairs (e.g. common European languages ↔ English) are **Supported**
- Less common pairs (e.g. Japanese → Serbian) are **Experimental**
- Pairs involving non-MVP languages are **Unsupported**

**The exact tier assignment per pair** is deferred to a Product/QA decision based on benchmark results. The matrix structure and UX behavior should be implemented first; tier data is configuration.

**Rules:**

- The support matrix is stored as configuration, not hardcoded
- Experimental pairs show a user-facing warning before submission
- Mode may affect tier — Guided Mode on an Experimental pair may perform worse than Translate Mode on the same pair
- The matrix is versioned and included in telemetry for quality tracking

---

## Definition of Done — Per Capability

Every capability is considered "done" for MVP when all of the following are satisfied:

| Criterion | Description |
|---|---|
| Functional requirements met | All items in the feature's Functional Requirements section pass |
| Success criteria verified | All items in the feature's Success Criteria section pass |
| Tests implemented | Unit and integration tests cover core paths and key failure modes |
| Telemetry present | Relevant telemetry events are emitted and correlate with `job_id`/`job_run_id` |
| Failure modes covered | Error handling follows POLICY-RETRY taxonomy; user-facing errors are clear |
| Cross-cutting policies respected | Applicable policies (versioning, idempotency, privacy, audit) are implemented |
| Documentation updated | `docs/TASKS.md` tasks marked complete; any architecture changes reflected in docs |
| Contract validated | Pipeline stages pass contract validation against `PIPELINE_CONTRACTS.md` |
| Admin/support visibility | Relevant data is visible in admin panel and job timeline |
| Review passed | Reviewer agent has approved the implementation |

---

## Ownership Template

Each feature should have assigned owners before implementation begins. For MVP, ownership is tracked at the feature level.

| Role | Responsibility |
|---|---|
| Product owner | Defines acceptance criteria and priority; resolves ambiguities |
| Engineering owner | Implements the feature; owns technical decisions within scope |
| QA owner | Validates success criteria and quality gates |
| Architecture reviewer | Ensures architectural compliance; reviews cross-cutting impact |

_Ownership assignments are tracked in `docs/TASKS.md` when features are broken into implementation tasks._

---

# User-Facing Features

---

## FEAT-AUTH — Authentication

**Capability:** AUTH
**Priority:** high
**Pipeline stage:** —
**Dependencies:** — (foundational)
**Slices:** UI, API, Policy, Tests
**Ref:** PRD §Delivery Model, ARCH §Authentication Boundary, DEC-001, DEC-002

### Summary

Authenticate users via Google OAuth and enforce identity at the API boundary. Every API call must resolve to an authenticated `user_id`. Unauthenticated requests are rejected before reaching any business logic.

### Goals

- Allow users to sign in with Google
- Issue a session or token for subsequent API calls
- Resolve `user_id` at the API boundary for every request
- Provision a new user record and initial credit grant on first login

### Non-Goals

- Additional auth providers (Apple, email/password) — post-MVP
- User profile management or settings page
- Password-based login
- Role-based access control beyond admin/user distinction

### User Flow

1. User opens Unfolda in a browser.
2. User clicks "Sign in with Google."
3. Google OAuth flow completes.
4. User is redirected to the main screen with an active session.
5. On first login, user record is created and initial credit balance is granted.

### Functional Requirements

- Google OAuth 2.0 flow via Next.js
- API boundary resolves `user_id` from session/token on every request
- Unauthenticated requests return 401
- First-login provisions: user record + credit account with admin-configured initial grant
- Terms of service acceptance on first login (POLICY-COPYRIGHT)
- Session persists across browser refreshes within a reasonable window
- Logout clears session

### MVP Slice

Google login only. Single session mechanism. No profile page. Admin/user distinction via a simple flag or allowlist.

### Constraints

- Must follow the authentication boundary defined in ARCH §Authentication Boundary
- Must use the Next.js ↔ FastAPI boundary defined in DEC-001
- Must not store Google credentials beyond what is needed for session management

### Success Criteria

- User can sign in with Google and receive an authenticated session
- All API endpoints reject unauthenticated requests
- First login creates a user record with initial credit balance
- Session survives browser refresh

### Open Questions

- Exact authentication mechanism between Next.js and FastAPI (→ Architect)

### Tasks

- TASK-1 — Create users and user_credit_account database schema
- TASK-2 — Configure Google OAuth and NextAuth.js in Next.js
- TASK-3 — Implement FastAPI JWT authentication middleware
- TASK-4 — Implement user provisioning on first login
- TASK-5 — Implement admin flag and admin route guard
- TASK-6 — Implement auth analytics instrumentation

---

## FEAT-UPLOAD — EPUB Upload & Validation

**Capability:** UPLOAD
**Priority:** high
**Pipeline stage:** —
**Dependencies:** AUTH, STORAGE, SECURITY
**Slices:** UI, API, Storage, Policy, Tests
**Ref:** PRD §Upload Experience, ARCH §Submission Flow, DEC-004

### Summary

Accept an EPUB file from the user via file picker or drag-and-drop, validate it (format, size, structure, DRM), and store it as an input artifact in object storage. Validation errors are shown immediately. The EPUB is not parsed for content at this stage.

### Goals

- Accept EPUB files via file picker and drag-and-drop
- Validate file format, size (max 50 MB), EPUB structure, and DRM absence
- Store validated EPUB in object storage with artifact metadata in DB
- Show clear validation errors immediately

### Non-Goals

- Parsing EPUB content for translation
- Invoking LLMs
- Segmentation or content transformation
- Accepting non-EPUB formats

### User Flow

1. User is on the upload screen (authenticated).
2. User selects an EPUB via file picker or drags it onto the upload area.
3. Client uploads the file (via signed URL from API → object storage).
4. API validates format, size, structure, and DRM.
5. If validation fails → clear error message shown immediately.
6. If validation passes → file stored, artifact metadata written to DB, user proceeds to PRECHECK/CONFIG.

### Functional Requirements

- File upload via signed URL (client → object storage)
- Server-side validation: MIME type, file extension, size ≤ 50 MB, valid EPUB structure
- DRM detection and rejection with clear user-facing message
- Malformed EPUB: attempt recovery for minor issues; reject severely broken files
- Artifact metadata recorded in DB (file size, upload time, user_id, artifact_id)
- Upload progress indicator in UI
- Source EPUB fingerprint (SHA-256) computed and stored as metadata (POLICY-FINGERPRINT)

### Abuse & Safety Protection

EPUB files are ZIP containers and may be crafted to exploit parsers. The following protections are required:

| Protection | Limit | Rationale |
|---|---|---|
| Zip bomb detection | Archive expansion ratio ≤ 100:1 | Prevent memory exhaustion |
| File count inside EPUB | ≤ 10,000 entries | Prevent filesystem abuse |
| Max HTML/XHTML files | ≤ 1,000 content documents | Prevent parser overload |
| Max chapter count | ≤ 500 spine items | Reasonable book structure limit |
| Parser timeout | ≤ 30 seconds for structure validation | Prevent hung validation |
| Malformed CSS/HTML tolerance | Best-effort parse with bounded error count | Prevent infinite error loops |
| Total uncompressed size | ≤ 200 MB | Prevent memory exhaustion from large embedded assets |

These limits are configurable and may be adjusted based on operational experience.

### MVP Slice

Single file upload. File picker and drag-and-drop. Basic EPUB validation. Abuse protection. No batch upload.

### Constraints

- Must use signed URLs for upload (ARCH §Submission Flow)
- Must follow storage key namespace: `users/{user_id}/jobs/{job_id}/source_epub/{artifact_id}`
- Must reject DRM-protected files (PRD, DEC-004)
- Must enforce abuse/safety limits (see table above)

### Success Criteria

- User can upload an EPUB via file picker and drag-and-drop
- Invalid files (wrong format, too large, DRM, severely malformed) are rejected with clear messages
- Zip bombs and oversized archives are rejected
- Files exceeding internal limits (file count, chapter count, expansion ratio) are rejected
- Valid files are stored in object storage with DB metadata and fingerprint
- Upload progress is visible in the UI

### Open Questions

_None._

### Tasks

TASK-33, TASK-34, TASK-35, TASK-36

---

## FEAT-PRECHECK — Pre-Submission Analysis

**Capability:** PRECHECK
**Priority:** high
**Pipeline stage:** —
**Dependencies:** UPLOAD, STORAGE
**Slices:** API, Domain, Telemetry, Tests
**Ref:** PRD §Upload Experience, ARCH §Submission Flow, DEC-011

### Summary

Perform a fast, read-only inspection of the uploaded EPUB to extract metadata needed for the CONFIG screen and credit cost estimation. This runs between upload and job configuration, without invoking the full pipeline or LLMs.

### Goals

- Detect source language (preview)
- Estimate word count
- Extract EPUB structure summary
- Provide submission-relevant metadata for CONFIG and credit estimation
- Complete fast enough to not delay the CONFIG screen

### Non-Goals

- Full content parsing for translation
- Segmentation
- LLM invocation
- Replacing INGEST as a pipeline stage
- Producing canonical pipeline artifacts
- Making credit policy decisions (that is QUOTA's responsibility)

### User Flow

1. Upload completes successfully.
2. PRECHECK runs automatically (no user action required).
3. Results are available when the CONFIG screen loads.

### Functional Requirements

- Read-only EPUB inspection: extract text for language detection and word counting
- Source language detection using a lightweight heuristic or library (no LLM), with **confidence score** per §Source Language Confidence Policy
- Word count estimation (approximate, sufficient for credit cost calculation)
- EPUB structure summary (chapter count, presence of images/footnotes)
- Results persisted as submission metadata (not as pipeline artifacts)
- Telemetry events for PRECHECK timing and any anomalies (e.g. malformed structure, low-confidence language detection)

### MVP Slice

Language detection preview + word count estimate. Structure summary is optional for MVP but useful for UX.

### Constraints

- Must be read-only — no EPUB modification (DEC-011)
- Must not produce canonical pipeline artifacts (DEC-011)
- Pre-submission metadata is advisory; authoritative metadata comes from INGEST (DEC-011)
- Must not invoke LLMs

### Success Criteria

- Source language is detected correctly for common languages in the MVP list
- Word count estimate is within reasonable accuracy for credit calculation
- PRECHECK completes within a few seconds for typical EPUBs
- CONFIG screen has word count and language data available on load

### Open Questions

- Exact language detection library or heuristic (→ Architect)

### Tasks

TASK-37, TASK-38, TASK-39, TASK-40

---

## FEAT-CONFIG — Translation Configuration

**Capability:** CONFIG
**Priority:** high
**Pipeline stage:** —
**Dependencies:** AUTH, PRECHECK, QUOTA (credit eligibility check)
**Slices:** UI, API, Policy, Tests
**Ref:** PRD §Translation Options, PRD §Supported Languages

### Summary

Present translation options to the user and produce a validated, normalized job settings object. The CONFIG screen shows estimated credit cost and blocks submission if the credit balance is insufficient.

### Goals

- Let user select mode, target language, style, level, and explanation depth
- Show pre-submission info: word count, processing time estimate, credit cost
- Block submission when credit balance is insufficient
- Validate configuration at the API boundary
- Produce a normalized job configuration object

### Non-Goals

- User-editable glossaries or prompt customization
- Per-chapter configuration
- Custom model or provider selection

### User Flow

1. After PRECHECK completes, user sees the CONFIG screen.
2. Source language is pre-filled (from PRECHECK); user can override.
3. User selects: mode (Translate / Guided), target language, style, level, explanation depth.
4. UI displays: estimated word count, approximate processing time, estimated credit cost.
5. If balance is sufficient → user confirms → job is created, credits reserved.
6. If balance is insufficient → submission is blocked with a clear message.

### Functional Requirements

- Mode selection: Translate / Guided
- Target language selection: 14 MVP languages
- Source language: auto-detected by PRECHECK, overridable by user
- Source language confidence display per §Source Language Confidence Policy (high → auto-fill, medium → warning, low → explicit confirm)
- Language pair tier display per §Language Pair Support Matrix (Experimental pairs show a quality warning)
- Translation style: literal / natural
- User language level: A1 / A2 / B1 / B2 / C1
- Explanation depth: minimal / standard / detailed (Guided Mode only)
- Credit cost estimation based on word count, mode, and settings (from QUOTA)
- Config validation at the API boundary; invalid combinations rejected before job creation
- Normalized job configuration persisted with the job record
- Submission uses `client_submission_id` for idempotent CreateJob (POLICY-IDEMPOTENCY)

### MVP Slice

All options available. Credit cost shown. Language confidence UX. Experimental pair warning. No advanced configuration.

### Constraints

- Explanation depth only applies to Guided Mode
- Config must be validated at the API boundary (FEATURE_MAP §CONFIG)
- Credit cost estimation depends on PRECHECK metadata and QUOTA multipliers
- Language pair support matrix is configuration-driven, not hardcoded
- Submission idempotency per POLICY-IDEMPOTENCY

### Success Criteria

- User can select all translation options
- Credit cost is shown before confirmation and matches the configured mode/settings
- Source language confidence is displayed per policy (high/medium/low)
- Experimental language pairs show a quality warning
- Submission is blocked when credits are insufficient
- Duplicate submission (double-click) does not create a second job
- Invalid configurations are rejected with clear messages
- Job record contains the normalized configuration

### Open Questions

- What are the credit conversion multipliers per mode? (→ Product / Architect)
- Exact language pair tier assignments (→ Product / QA, based on benchmarks)

### Tasks

TASK-41, TASK-42, TASK-43, TASK-44, TASK-45, TASK-46

---

## FEAT-JOBS — Job List & Download

**Capability:** JOBS
**Priority:** high
**Pipeline stage:** —
**Dependencies:** AUTH, QUEUE, STORAGE, SECURITY
**Slices:** UI, API, Tests
**Ref:** PRD §Jobs List, PRD §Job Lifecycle, ARCH §Download Flow

### Summary

Show the user a list of their submitted jobs with statuses, progress, and download links. Completed jobs are downloadable via short-lived signed URLs. The list reflects all job states including active, completed, failed, cancelled, and expired.

### Goals

- Show all user jobs with current status
- Show progress and ETA for active jobs
- Provide download link for completed jobs
- Clearly distinguish all terminal states (completed, failed, cancelled, expired)

### Non-Goals

- Built-in EPUB reader
- Reading progress tracking
- Job sharing or public links
- Sorting, filtering, or search (can be added later)

### User Flow

1. User navigates to the jobs list.
2. Each job shows: title, mode, target language, status, progress/ETA (if active), download link (if completed).
3. User clicks download → receives the generated EPUB via signed URL.
4. Failed jobs show error message and retry button (if eligible).
5. Expired jobs are shown with metadata only (no download).

### Functional Requirements

- Jobs list endpoint returns all jobs for the authenticated user
- Each job includes: book title, mode, target language, status, timestamps
- Active jobs include progress percentage and ETA
- Completed jobs include a download action that returns a short-lived signed URL
- Failed jobs include the error message and retry eligibility
- Cancelled jobs are visually distinct from failed jobs
- Expired jobs shown as metadata-only
- List ordered by submission time (newest first)

### Job Receipt

After submission, the user sees a structured job receipt confirming all parameters:

| Field | Source |
|---|---|
| Book title | Extracted from EPUB metadata |
| Source language | PRECHECK detection or user override |
| Target language | User selection |
| Mode | Translate / Guided |
| Translation style | literal / natural |
| Estimated credits | Credit cost from QUOTA |
| Credits reserved | Actual reserved amount |
| Submission time | Timestamp |
| Retention expiry | Calculated from submission time + retention window |
| Retry eligibility | "Within retention window" or "Re-upload required after expiry" |

The receipt is shown immediately after submission and is also accessible from the job detail view.

### MVP Slice

Flat list of all jobs. Job receipt on submission. No pagination for MVP (expect low job counts per user). Download via signed URL.

### Constraints

- Download URLs must be short-lived and object-scoped (DEC-004)
- Job state is owned by QUEUE; JOBS reads via API
- MVP enforces one active job per user; the data model should support a configurable `max_concurrent_jobs` per user for future flexibility (default: 1)

### Success Criteria

- User sees all their jobs with correct statuses
- Job receipt is shown after submission with all key parameters
- Download works for completed jobs
- Failed jobs show error message; retry is available when eligible
- Cancelled jobs are clearly distinguished from failures
- Expired jobs show metadata without download link

### Open Questions

_None._

### Tasks

- TASK-47 — Extend JobResponse with job-receipt fields + download-url endpoint
- TASK-48 — Tests for FEAT-JOBS (receipt fields + download endpoint)

---

## FEAT-PROGRESS — Progress & ETA

**Capability:** PROGRESS
**Priority:** medium
**Pipeline stage:** —
**Dependencies:** QUEUE, TELEMETRY
**Slices:** UI, API, Domain, Worker, Tests
**Ref:** PRD §Job Lifecycle, ARCH §Progress And ETA Model, DEC-010

### Summary

Provide durable, backend-owned progress tracking for active jobs. The user sees percentage progress and estimated time remaining. Progress survives browser refresh, reconnect, and retries.

### Goals

- Show progress percentage and ETA for active jobs
- Persist progress in DB (not in browser or worker memory)
- Survive browser refresh, reconnect, and retries
- Improve ETA accuracy as more throughput data becomes available

### Non-Goals

- Live streaming from worker to browser
- Sub-second updates
- Per-paragraph progress granularity
- Client-side progress computation

### User Flow

1. User submits a job and sees it enter "processing" state.
2. Progress bar shows percentage and ETA.
3. User closes browser.
4. User returns later → progress is still visible and up to date.

### Functional Requirements

- Worker persists progress snapshots at regular intervals (stage transitions, batch completions)
- Progress model: stage-weighted progress across the pipeline
- ETA: throughput-informed, smoothed using rolling averages
- API endpoint returns current progress and ETA for a given job
- UI polls or uses a lightweight refresh mechanism
- Progress model is backend/domain-owned; worker only emits persisted snapshots

### MVP Slice

Polling-based progress. Stage-weighted percentage. Throughput-informed ETA (may be approximate early in a run).

### Constraints

- Progress computation must not depend on a live browser session (DEC-010)
- Progress data lives in PostgreSQL as canonical job state
- Support tooling can inspect the same progress state

### Success Criteria

- User sees progress percentage and ETA for active jobs
- Progress survives browser refresh and reconnect
- ETA improves in accuracy as more batches complete
- Support can inspect progress state

### Open Questions

_None._

### Tasks

_To be filled during task breakdown._

---

## FEAT-ERROR-UX — Error Handling & Retry

**Capability:** ERROR-UX
**Priority:** high
**Pipeline stage:** —
**Dependencies:** AUTH, QUEUE, STORAGE
**Slices:** UI, API, Policy, Tests
**Ref:** PRD §Error Handling, ARCH §Failure Taxonomy, DEC-007

### Summary

Present clear, structured error feedback to users for validation failures, processing failures, and policy rejections. Support job retry within the retention window. Ensure failed and cancelled jobs refund reserved credits.

### Goals

- Show clear, actionable error messages for all failure types
- Support retry for failed jobs within the retention window
- Ensure credit refund on failure and cancellation
- Guarantee every job reaches a terminal state

### Non-Goals

- Automatic retry without user action
- Partial result delivery
- Error recovery inside pipeline stages
- Technical stack traces shown to users

### User Flow

1. **Validation error:** user uploads an invalid EPUB → immediate clear error → user can fix and re-upload.
2. **Processing failure:** job fails during processing → job list shows "failed" with a message → user can retry if within retention window.
3. **Policy rejection:** credit balance insufficient or cost cap exceeded → clear message before submission.
4. **Cancellation:** user requests cancellation → job transitions to "cancelled" → credits refunded.

### Functional Requirements

- Validation errors shown immediately with specific reason (format, size, DRM, structure)
- Processing failures produce structured, user-readable error messages
- Policy failures (insufficient credits, cost cap) shown with clear reason and guidance
- Retry action available for failed jobs within retention window
- Retry uses original uploaded file if still available; otherwise prompts re-upload
- Failed and cancelled jobs do not consume credits — reserved credits refunded
- Every job reaches a terminal state (completed, failed, cancelled, expired) — no silent drops
- Error messages never expose raw book content or internal stack traces

### MVP Slice

All error types handled. Retry for failed jobs. Credit refund on failure/cancellation.

### Constraints

- Error messages must not contain raw book text (DEC-004)
- Retry only for provider-transient and infrastructure failures, not for content-deterministic failures (DEC-007)
- Credit refunds must be idempotent per job_run

### Success Criteria

- Validation errors are shown immediately with clear messages
- Processing failures show user-readable error messages
- Retry works within retention window
- Credits are refunded on failure and cancellation
- No jobs are silently dropped

### Open Questions

_None._

### Tasks

_To be filled during task breakdown._

---

# Processing Pipeline Features

---

## FEAT-INGEST — EPUB Ingestion & Language Detection

**Capability:** INGEST
**Priority:** high
**Pipeline stage:** Ingestion
**Dependencies:** STORAGE
**Slices:** Domain, Worker, Storage, Tests
**Contract:** `docs/PIPELINE_CONTRACTS.md` §Ingestion
**Ref:** ARCH §Ingestion, DEC-004

### Summary

Parse the uploaded EPUB, extract text and structure, detect source language, and produce a normalized document representation. This is the first pipeline stage and runs as part of job execution, not during upload.

### Goals

- Parse EPUB structure: spine, chapters, images, footnotes, links, CSS references
- Extract text content per chapter
- Detect source language at the book level
- Produce a normalized document with word count and structural metadata
- Handle malformed EPUBs with best-effort recovery

### Non-Goals

- Calling LLMs
- Segmenting content (that is SEGMENT)
- Translating content
- Formatting output
- Replacing PRECHECK for pre-submission analysis

### Functional Requirements

- Parse valid EPUB 2/3 files
- Extract text preserving paragraph boundaries and chapter structure
- Preserve references to images, footnotes, links, and CSS
- Book-level source language detection; low confidence triggers anomaly event
- Word count computation (authoritative, used for analytics and policy tuning)
- Malformed input: attempt recoverable text extraction with best-effort structure preservation
- Output: normalized document representation matching `PIPELINE_CONTRACTS.md` §Ingestion output schema
- Output artifact includes `schema_version` per POLICY-SCHEMA
- Normalized document fingerprint computed and stored (POLICY-FINGERPRINT)
- Structured artifact persisted in object storage for downstream stages

### MVP Slice

Standard EPUB 2/3 parsing. Language detection. Word count. Chapter and paragraph extraction. Best-effort malformed handling.

### Constraints

- Must follow the stage contract in `PIPELINE_CONTRACTS.md` §Ingestion
- Output is the canonical document representation for all downstream stages
- Must not invoke LLMs
- Authoritative metadata may differ from PRECHECK estimates (DEC-011)

### Success Criteria

- Well-formed EPUBs are parsed correctly (structure, text, metadata)
- Source language is detected correctly for MVP languages
- Word count is accurate
- Malformed EPUBs produce best-effort output or a clear rejection
- Output conforms to the stage contract

### Open Questions

_None._

### Tasks

- TASK-22 — Define ingestion data models
- TASK-23 — Implement EPUB parser and language detector
- TASK-24 — Implement ingestion stage entry point and integration tests

---

## FEAT-SEGMENT — Text Segmentation

**Capability:** SEGMENT
**Priority:** high
**Pipeline stage:** Segmentation
**Dependencies:** INGEST
**Slices:** Domain, Worker, Tests
**Contract:** `docs/PIPELINE_CONTRACTS.md` §Segmentation
**Ref:** PRD §Segmentation Model, ARCH §Segmentation, DEC-005

### Summary

Split the normalized document into paragraph-level processing units with chapter references, token estimates, and batch-planning metadata. Large paragraphs may be split internally for LLM context limits, but the user-visible unit is always the paragraph.

### Goals

- Produce paragraph-level segments with stable identifiers
- Include chapter references and structural context per segment
- Compute token estimates for batch planning
- Generate batch-planning metadata respecting LLM context limits

### Non-Goals

- Rewriting or modifying text meaning
- Calling LLMs
- Formatting output
- Modifying document structure

### Functional Requirements

- Segment at paragraph boundaries as the primary visible unit
- Large paragraphs: internal sub-segmentation for LLM context limits, reassembled to paragraph level in output
- Each segment includes: stable ID, chapter reference, paragraph index, token estimate, text content
- Batch-planning metadata: group segments into batches respecting `max_tokens_per_request` and `target_tokens_per_request`
- Segment identifiers must be deterministic and stable for the same document (DEC-009)
- Output: segment collection matching `PIPELINE_CONTRACTS.md` §Segmentation output schema

### MVP Slice

Paragraph-level segmentation. Token estimation. Batch-planning metadata.

### Constraints

- Must follow the stage contract in `PIPELINE_CONTRACTS.md` §Segmentation
- Segment IDs must be deterministic for resumability and quality checks (DEC-009)
- Batch targets should stay within 30-60% of effective model context window (DEC-005)

### Success Criteria

- Paragraphs are correctly identified and segmented
- Token estimates are reasonably accurate
- Batch-planning metadata enables efficient LLM batching
- Segment IDs are stable across runs for the same document

### Open Questions

_None._

### Tasks

- TASK-49 — Segmentation models, stage, batch planner, orchestrator integration
- TASK-50 — Tests for segmentation stage

---

## FEAT-TRANSLATE — AI Translation

**Capability:** TRANSLATE
**Priority:** high
**Pipeline stage:** Translation
**Dependencies:** SEGMENT, CONSISTENCY, COST, STORAGE, TELEMETRY
**Slices:** Domain, Worker, Storage, Telemetry, Tests
**Contract:** `docs/PIPELINE_CONTRACTS.md` §Translation
**Ref:** ARCH §Translation, DEC-003, DEC-005

### Summary

Translate paragraph-level segments into the target language using an LLM. This is the only pipeline stage that invokes LLMs. In Guided Mode, translation and explanation generation may run as separate internal passes. Translation batches are the primary resumable unit.

### Goals

- Produce translated text for every paragraph
- In Guided Mode, also produce explanations (idioms, cultural context)
- Maintain translation consistency via CONSISTENCY memory
- Support resumability at translation batch boundaries
- Respect cost caps and token budgets

### Non-Goals

- Changing segmentation boundaries
- Embedding presentation formatting (that is FORMAT)
- Hiding retries from the operations model
- Multi-provider routing
- User-editable glossaries

### Functional Requirements

- Chapter-scoped, token-bounded translation batches
- Translate Mode: full context-aware translation per paragraph
- Guided Mode: translation + explanation generation (may use separate passes)
- Prompts loaded from `prompts/` directory (externalized)
- Provider and model from configuration, not hardcoded
- Each batch receives consistency memory (terminology, entities, chapter context)
- Translation batch is the primary resumable unit; persisted at explicit checkpoints
- Each provider call produces a `cost_ledger_entry`
- Prompt input budget accounting before each provider call (POLICY-PROMPT-BUDGET)
- Batch-level telemetry: timing, token usage, provider latency
- Non-LLM quality checks: untranslated segment detection, language mismatch, short translation detection, hallucinated paragraph detection (DEC-005)
- Translation batch artifacts include fingerprints (POLICY-FINGERPRINT)
- Job run fully version-stamped (POLICY-VERSION)
- Output: translated segment collection matching `PIPELINE_CONTRACTS.md` §Translation output schema

### MVP Slice

Single provider. Both modes. Batch-level resumability. Consistency memory. Basic quality checks.

### Constraints

- Only pipeline stage allowed to invoke LLMs (DEC-003)
- Prompts must live in `prompts/` (DEC-003)
- Provider retries must be explicit and bounded (DEC-003)
- Provider payloads scoped to current batch + required context only (DEC-004)
- Translation style and user level must affect prompt behavior
- Batch targets within 30-60% of effective context window (DEC-005)

### Success Criteria

- Translate Mode produces coherent, context-aware translations
- Guided Mode produces translations + relevant explanations
- Translation options (style, level, depth) visibly affect output
- Consistency is maintained across batches (names, terms, gender)
- Processing resumes correctly after interruption at batch boundary
- Quality checks flag obvious failures
- A typical book (50k–100k words) processes without failure

### Open Questions

- Exact LLM provider and model for MVP (→ Discovery)
- Exact consistency-memory schema details (→ Architect)

### Tasks

- TASK-51: Translation models, consistency, quality, prompt loader, provider, stage
- TASK-52: Orchestrator integration, prompt YAML templates, requirements.txt
- TASK-53: Tests for translation stage

---

## FEAT-CONSISTENCY — Translation Consistency Memory

**Capability:** CONSISTENCY
**Priority:** high
**Pipeline stage:** Translation (support)
**Dependencies:** — (data coupling with TRANSLATE; no capability-level dependency)
**Slices:** Domain, Storage, Tests
**Ref:** PRD §Translation Consistency, ARCH §Consistency Strategy, DEC-005

### Summary

Maintain coherent translation across the entire book within a single job. The consistency memory accumulates terminology, named entities, and chapter context across translation batches, ensuring names, terms, and gender remain consistent throughout.

### Goals

- Build and maintain a terminology map across translation batches
- Track named entities and their established translations
- Provide rolling chapter context summary
- Flag unresolved ambiguities for attention
- Persist consistency state for resumability

### Non-Goals

- User-editable glossary
- Cross-book memory or persistent knowledge base
- Independent pipeline stage status

### Functional Requirements

- Job-scoped consistency memory initialized at job start
- Updated after each translation batch with: new terms, entities, resolved translations
- Terminology map: source term → target translation with context
- Named-entity registry: characters, places, organizations with consistent renderings
- Rolling chapter context summary: key plot/topic points for translation context
- Unresolved ambiguity notes: flagged items for potential future improvement
- May be persisted as structured artifact for resumability
- Follows job retention window for cleanup

### MVP Slice

Terminology map + named-entity registry + rolling context summary. Persisted for resumability.

### Constraints

- Supports TRANSLATE but is not an independent pipeline stage
- No separate stage contract in `PIPELINE_CONTRACTS.md`
- Job-scoped; not reused across books (DEC-005)
- Consistency-memory schema details to be finalized by Architect

### Success Criteria

- Character names are translated consistently throughout the book
- Gendered terms remain correct across chapters
- Domain-specific terminology is uniform
- Previously established translations are not contradicted later
- Consistency memory can be resumed after interruption

### Open Questions

- Exact consistency-memory schema details (→ Architect)

### Tasks

_To be filled during task breakdown._

---

## FEAT-FORMAT — Output Formatting

**Capability:** FORMAT
**Priority:** high
**Pipeline stage:** Formatting
**Dependencies:** TRANSLATE
**Slices:** Domain, Worker, Tests
**Contract:** `docs/PIPELINE_CONTRACTS.md` §Formatting
**Ref:** PRD §Product Modes, ARCH §Formatting

### Summary

Assemble translated segments into mode-specific reading structures. Translate Mode replaces original paragraphs with translations. Guided Mode creates a 4-block structure per paragraph. This stage is deterministic and does not invoke LLMs.

### Goals

- Produce structured reading output ready for EPUB reconstruction
- Apply mode-specific formatting rules
- Preserve paragraph order and chapter structure

### Non-Goals

- Translating text (that is TRANSLATE)
- Modifying segment content
- Calling LLMs
- Changing segmentation boundaries
- EPUB assembly (that is EXPORT)

### Functional Requirements

- Translate Mode: translated paragraph replaces original
- Guided Mode: 4-block structure per paragraph:
  1. Original text
  2. Translation
  3. Explanations
  4. Original text (shown again)
- Deterministic output — no randomness or LLM calls
- Preserve paragraph order and chapter structure
- Output: formatted document matching `PIPELINE_CONTRACTS.md` §Formatting output schema

### MVP Slice

Both modes fully implemented. Deterministic formatting.

### Constraints

- Must follow the stage contract in `PIPELINE_CONTRACTS.md` §Formatting
- Must not invoke LLMs (DEC-003)
- Must not alter translated text content

### Success Criteria

- Translate Mode output contains translated paragraphs in correct order
- Guided Mode output contains all four blocks per paragraph in correct order
- Output preserves chapter structure
- Formatting is deterministic — same input always produces same output

### Open Questions

_None._

### Tasks

- TASK-54: Formatting models, stage, orchestrator integration, version bump
- TASK-55: Tests for formatting stage

---

## FEAT-EXPORT — EPUB Export

**Capability:** EXPORT
**Priority:** high
**Pipeline stage:** Export
**Dependencies:** FORMAT, INGEST (for original structure), STORAGE
**Slices:** Domain, Worker, Storage, Tests
**Contract:** `docs/PIPELINE_CONTRACTS.md` §Export
**Ref:** PRD §EPUB Structure Preservation, PRD §Output Metadata, ARCH §Export

### Summary

Reconstruct a valid EPUB from the formatted output and the original EPUB structure. The generated EPUB preserves book structure, injects output metadata, and is stored in object storage for download.

### Goals

- Produce a valid, downloadable EPUB
- Preserve original book structure (spine, chapters, images, footnotes, links, CSS)
- Inject output metadata (title suffix, author, language, description, disclaimer page)
- Store the result in object storage

### Non-Goals

- Translating text (done in earlier stages)
- Reformatting content beyond mode-specific structure
- Calling LLMs
- Producing non-EPUB formats (MOBI, PDF)

### Functional Requirements

- Reconstruct EPUB from formatted document + original EPUB structure
- Preserve: spine order, chapter structure, images, footnotes, links, CSS
- Inject metadata:
  - Title: original title + mode/language suffix (e.g. "Il Nome della Rosa — Guided, EN")
  - Author: original author preserved
  - Language: set to target language
  - Description: note about AI-generated content
  - Disclaimer page: inserted at the beginning of the book
- Generated EPUB stored in object storage as `output_epub` artifact
- Output EPUB fingerprint (SHA-256) computed and stored (POLICY-FINGERPRINT)
- Disclaimer page per POLICY-COPYRIGHT
- Artifact metadata recorded in DB

### MVP Slice

Full EPUB reconstruction with metadata injection and disclaimer. Both modes supported.

### Constraints

- Must follow the stage contract in `PIPELINE_CONTRACTS.md` §Export
- Output must render correctly in standard EPUB readers (Apple Books, Moon Reader, KOReader)
- Must not invoke LLMs
- Storage key: `users/{user_id}/jobs/{job_id}/output_epub/{artifact_id}`

### Success Criteria

- Generated EPUB is valid and opens in standard EPUB readers
- Book structure is preserved (spine, chapters, images, footnotes, links, CSS)
- Metadata is correctly injected (title suffix, author, language, description, disclaimer)
- Output feels like a proper book, not a raw text dump

### Open Questions

_None._

### Tasks

- TASK-56: Export models, epub_builder, stage, storage extension, orchestrator integration, version bump
- TASK-57: Tests for export stage

---

# Platform Features

---

## FEAT-QUEUE — Job Queue & Orchestration

**Capability:** QUEUE
**Priority:** high
**Pipeline stage:** —
**Dependencies:** STORAGE, COST, TELEMETRY, RETENTION
**Slices:** API, Worker, Domain, Storage, Telemetry, Tests
**Ref:** ARCH §Worker Runtime, ARCH §Job Lifecycle State Machine, DEC-001, DEC-007

### Summary

Orchestrate pipeline execution as background jobs with reliable state management. Redis provides queue signaling, PostgreSQL owns canonical state. Workers execute pipeline stages in order with explicit checkpoints, leases, and heartbeats.

### Goals

- Execute pipeline stages in order as background jobs
- Manage job lifecycle state machine (validating → queued → processing → terminal)
- Enforce one active job per user
- Provide reliable checkpoint persistence and resumability
- Handle worker failures, stuck jobs, and poison inputs

### Non-Goals

- Containing pipeline stage logic
- Calling LLMs directly
- Business ownership of content transformation rules
- Heavy workflow engine

### Functional Requirements

- Redis as queue broker (signaling only, non-canonical)
- PostgreSQL as canonical state store for all job state
- Worker runtime: Python workers executing pipeline stages
- Job lifecycle: validating → queued → processing → completed/failed/cancelled → expired
- Lease model: explicit lease ownership, heartbeats, expiry detection
- One active job per user at most
- Checkpoint persistence at stage and batch boundaries
- Cancellation: per-stage semantics defined in POLICY-CANCELLATION (DEC-012)
- Failure classification: per POLICY-RETRY taxonomy (DEC-007)
- Retry only for retryable failure classes per POLICY-RETRY
- Poison jobs move to quarantine or non-retrying failure state
- Strict all-or-nothing completion per POLICY-COMPLETION
- Backpressure when budgets are saturated
- Job run version-stamped per POLICY-VERSION
- Timeline events emitted for all state transitions

### MVP Slice

Single worker type. Redis + PostgreSQL. Full lifecycle state machine. Lease-based ownership. Basic retry and quarantine.

### Constraints

- Canonical state in PostgreSQL only (DEC-009)
- Redis is non-canonical — worker memory is ephemeral
- Operations model from DEC-007 must be followed
- Deployment changes must preserve in-flight compatibility or drain workers

### Success Criteria

- Jobs progress through the complete lifecycle state machine
- One active job per user enforced
- Worker failures are detected and handled (lease expiry)
- Checkpoint resumability works after interruption
- Stuck and poison jobs are quarantined
- Timeline events are emitted for all transitions

### Open Questions

_None._

### Tasks

- TASK-25 — Job/JobRun/Document/TranslationBatch DB models and migrations
- TASK-26 — Credit service for job lifecycle
- TASK-27 — Queue broker and job domain service
- TASK-28 — Job API endpoints
- TASK-29 — Worker orchestrator and lease management

---

## FEAT-STORAGE — Object Storage

**Capability:** STORAGE
**Priority:** high
**Pipeline stage:** —
**Dependencies:** SECURITY
**Slices:** API, Storage, Policy, Tests
**Ref:** ARCH §Object Storage, ARCH §Storage Key Namespace, DEC-004

### Summary

Temporary storage for binary and structured artifacts. Stores uploaded EPUBs, generated EPUBs, translation batch artifacts, and optional consistency snapshots. Access is via short-lived signed URLs.

### Goals

- Store and serve uploaded files, generated outputs, and structured resumable artifacts
- Provide short-lived, purpose-specific signed URLs for access
- Maintain artifact metadata in DB as canonical source of truth
- Support the storage key namespace convention

### Non-Goals

- Long-term content retention (that is explicitly prevented)
- Serving as canonical state store (PostgreSQL is canonical)
- Replacing database for metadata

### Functional Requirements

- S3-compatible object storage
- Artifact classes: `source_epub`, `output_epub`, `translation_batch_artifact`, optional `consistency_memory_snapshot`
- Key namespace: `users/{user_id}/jobs/{job_id}/{artifact_type}/{artifact_id}`
- Signed URLs: object-scoped, short-lived, purpose-specific
- Artifact metadata in PostgreSQL; artifacts without DB records are not canonical
- Upload: client → signed URL → object storage
- Download: signed URL issued by API → client downloads from object storage

### MVP Slice

S3-compatible storage. Signed URL upload/download. Four artifact classes. DB-backed metadata.

### Constraints

- Must follow storage key namespace (ARCH §Storage Key Namespace)
- Signed URLs must be short-lived and purpose-specific (DEC-004)
- Raw book text must never appear in logs (DEC-004)

### Success Criteria

- Files are stored and retrievable via signed URLs
- Artifact metadata is consistent between DB and object storage
- Key namespace convention is followed
- Signed URLs expire correctly

### Open Questions

- What object storage provider? (→ Discovery)

### Tasks

- TASK-12 — Create artifact metadata DB model and migration
- TASK-13 — Implement StorageClient adapter (boto3 wrapper)
- TASK-14 — Implement StorageService domain layer
- TASK-15 — Storage API endpoints and integration tests

---

## FEAT-QUOTA — Credits & Usage Limits

**Capability:** QUOTA
**Priority:** high
**Pipeline stage:** —
**Dependencies:** AUTH, ADMIN, COST
**Slices:** UI, API, Domain, Policy, Admin, Tests
**Ref:** PRD §Credits & Usage Limits, ARCH §Quota Enforcement, DEC-002, DEC-006

### Summary

Manage user credit balances and enforce spending limits. Credits are an abstract unit converted from word count, mode, and settings. Users see their balance, per-job cost, and transaction history. Admin manages grants and adjustments.

### Goals

- Maintain per-user credit balances
- Calculate credit cost for a given job configuration
- Reserve credits on job submission
- Consume credits on success, refund on failure/cancellation
- Show credit balance and transaction history to users
- Support future payment integration without pipeline changes

### Non-Goals

- Self-service credit purchase (payment provider) — post-MVP
- Automated billing
- Monthly resets
- Monetary price display to users

### User Flow

1. User registers → receives initial credit grant.
2. User configures a job → sees estimated credit cost.
3. User confirms → credits reserved.
4. Job completes → credits consumed.
5. Job fails → credits refunded.
6. User views credit balance and transaction history.

### Functional Requirements

- Credit unit: abstract, converted from source word count + mode + settings
- Mode multipliers: admin-configurable (Guided Mode costs more)
- Initial grant: configurable amount on registration
- Credit balance visible in UI at all times (e.g. header)
- Credit cost estimate before job confirmation
- Reservation: credits reserved on job submission
- Consumption: reserved credits consumed on successful completion
- Refund: reserved credits refunded on failure or cancellation
- Idempotency: reservations, consumptions, and refunds idempotent per `job_run`
- Transaction history: user sees grant, reservation, consumption, refund events
- Enforcement: checked before queue admission + before expensive translation work
- Admin: grant credits, adjust balances, view credit history (see FEAT-ADMIN)

### MVP Slice

Full credit lifecycle. Admin-managed. No payment provider.

### Constraints

- Credits model separate from internal LLM cost accounting (DEC-006)
- User-confirmed reservation based on pre-submission estimate; authoritative ingestion metadata must not silently increase reserved amount (DEC-006, DEC-011)
- Idempotent per `job_run` (DEC-006)

### Success Criteria

- Users see their credit balance at all times
- Credit cost is shown before job confirmation
- Credits are correctly reserved, consumed, and refunded
- Failed/cancelled jobs refund credits
- Transaction history shows all credit events
- Admin can manage balances

### Open Questions

- Default initial credit grant amount for MVP (→ Product)
- Credit conversion multipliers per mode (→ Product / Architect)

### Tasks

_To be filled during task breakdown._

---

## FEAT-RETENTION — Retention & Cleanup

**Capability:** RETENTION
**Priority:** medium
**Pipeline stage:** —
**Dependencies:** STORAGE, QUEUE, TELEMETRY
**Slices:** Worker, Storage, Domain, Telemetry, Tests
**Ref:** PRD §Storage Policy, ARCH §Retention And File Lifecycle, DEC-004

### Summary

Manage file lifecycle to ensure no long-term content retention. Delete content-bearing artifacts after the retention window while preserving metadata. This is a legal and privacy requirement.

### Goals

- Delete uploaded EPUBs after terminal state + retention window
- Delete generated EPUBs after retention expiry (not on first download — see Retention UX note)
- Delete intermediate artifacts per job retention rules
- Retain metadata only (no book content) long-term
- Never delete artifacts for retry-eligible jobs

### Non-Goals

- Real-time deletion
- Content archival
- Backup management

### Functional Requirements

- Dedicated scheduled cleanup task
- Uploaded EPUB: deleted after terminal state + retention window
- Generated EPUB: deleted after retention expiry (kept available for multiple downloads within the window)
- Intermediate artifacts: follow job retention window
- Long-term: metadata only (no book content)

**Retention UX note:** deleting the generated EPUB after the first download is risky — the user may not have saved the file, or the download may have failed silently. For MVP, generated EPUBs are retained until the retention window expires, allowing multiple downloads. This is safer for UX and simpler to implement. Post-MVP, download tracking may enable more aggressive cleanup if needed.
- Cleanup is idempotent
- Must not delete artifacts for retry-eligible jobs
- Emit `cleanup_started` and `cleanup_completed` timeline events
- Transition jobs to `expired` state after all content is deleted

### MVP Slice

Scheduled cleanup task. All retention rules enforced. Telemetry events.

### Constraints

- Legal and privacy requirement (PRD §Storage Policy)
- Must not delete files for retry-eligible jobs
- Must respect the retention window duration (exact duration TBD)

### Success Criteria

- Files are deleted according to the retention policy
- No book content is retained beyond the retention window
- Retry-eligible jobs retain their files
- Metadata survives cleanup
- Timeline events are emitted for cleanup operations

### Open Questions

- Exact retention window duration (→ Product)

### Tasks

- TASK-30 — Add retention_deadline to Job model and migration
- TASK-31 — Retention policy service and orchestrator integration
- TASK-32 — CleanupWorker implementation and integration tests

---

## FEAT-COST — Internal Cost Control

**Capability:** COST
**Priority:** medium
**Pipeline stage:** —
**Dependencies:** TELEMETRY
**Slices:** Domain, Worker, Policy, Telemetry, Tests
**Ref:** ARCH §Cost Architecture, DEC-006

### Summary

Internal cost accounting and protection layer for LLM-backed processing. Tracks actual token costs, enforces hard caps, and prevents economically unsafe jobs from running. Separate from user-facing credits (QUOTA).

### Goals

- Estimate cost before job execution
- Enforce hard cost caps at per-job, per-user, and per-retry levels
- Account for actual token usage per batch and per run
- Reject jobs exceeding limits with clear policy reasons

### Non-Goals

- Pricing logic, credit conversion, or user billing (QUOTA's responsibility)
- User-facing cost display
- Real-time cost dashboard

### Functional Requirements

- Pre-run cost estimation: word count × mode × language pair × expected passes
- Hard caps: per-job, per-user cost period, per-retry budget
- Each provider call produces a `cost_ledger_entry` (tokens in, tokens out, estimated cost)
- Batch-level and run-level cost aggregation
- When internal cost threshold exceeded → fail safely with clear policy reason
- Prompt budget discipline: track prompt template size vs available context
- Bounded retry budgets (DEC-007)

### MVP Slice

Pre-run estimation. Per-job hard cap. Token accounting per batch. Cost ledger entries.

### Constraints

- Separate from user-facing credits (DEC-006)
- Every cost-significant provider interaction must produce a `cost_ledger_entry` (DEC-006)
- Prompt growth and multiplier changes are architecture-relevant (DEC-006)

### Success Criteria

- Pre-run estimation prevents obviously oversized jobs from starting
- Hard caps stop runaway jobs
- Token usage is tracked per batch and per run
- Cost ledger entries are produced for every provider call

### Open Questions

_None._

### Tasks

- TASK-19 — Create cost_ledger_entry DB model and migration
- TASK-20 — Implement cost estimator and hard cap enforcement
- TASK-21 — Implement cost ledger service

---

## FEAT-TELEMETRY — Observability & Quality Validation

**Capability:** TELEMETRY
**Priority:** medium
**Pipeline stage:** —
**Dependencies:** — (foundational)
**Slices:** Domain, Worker, Telemetry, Tests
**Ref:** ARCH §Telemetry And Quality Validation, DEC-008

### Summary

Structured telemetry for operations, debugging, and quality regression detection. Provides structured logs, durable job timelines, metrics, and benchmark infrastructure. All events correlate with `job_id` and `job_run_id`.

### Goals

- Enable operations monitoring and debugging
- Provide durable per-job timeline for support and inspection
- Track performance metrics (latency, throughput, token usage)
- Support quality regression detection via benchmarks
- Ensure no raw book content in telemetry

### Non-Goals

- Raw-text debugging
- Full distributed tracing stack in MVP
- Real-time alerting platform

### Functional Requirements

- Structured logs with consistent format
- Durable per-job timeline stored in DB
- 16+ timeline event types from `job_created` through `job_expired` (DEC-008)
- Credit-related events: `credit_reserved`, `credit_consumed`, `credit_refunded`
- Stage timings, provider latency, throttling metrics, token usage
- Throughput, retry, error-class, stuck-job, and quarantine metrics
- All events correlate with `job_id` and `job_run_id`
- Quality telemetry: evaluation dataset, benchmark runs, regression detection
- No raw book text in any telemetry output (DEC-004)

### MVP Slice

Structured logs. Job timeline. Key metrics. Benchmark infrastructure (evaluation dataset + comparable runs).

### Constraints

- Must be metadata-only — no raw book text (DEC-004)
- Telemetry schema is a first-class implementation task (DEC-008)
- Must respect no-raw-text rule across all output channels

### Success Criteria

- Job timeline is complete and inspectable for any job
- Metrics are available for operations monitoring
- No raw book content appears in logs, metrics, or events
- Quality benchmarks can detect regressions before deployment

### Open Questions

- Exact benchmark thresholds for launch quality gates (→ deferred per DECISIONS)

### Tasks

- TASK-16 — Create job_event DB model and migration
- TASK-17 — Implement timeline event emitter
- TASK-18 — Implement benchmark infrastructure

---

## FEAT-SECURITY — Security & Privacy

**Capability:** SECURITY
**Priority:** high
**Pipeline stage:** —
**Dependencies:** — (cross-cutting)
**Slices:** Policy, API, Storage, Tests
**Ref:** ARCH §Security Privacy And Compliance Boundary, DEC-004

### Summary

Protect user content from leakage, unauthorized access, and misuse across all system boundaries. Enforce content rules, DRM rejection, scoped provider payloads, and audited access.

### Goals

- Prevent raw book content from appearing in logs, traces, analytics, or errors
- Enforce DRM rejection
- Scope provider payloads to current batch + bounded context only
- Ensure signed URLs are short-lived and purpose-specific
- Audit admin access to user data

### Non-Goals

- Full penetration testing framework
- SOC 2 compliance in MVP
- Encryption at rest beyond provider defaults

### Functional Requirements

- Content rule: raw book text never in logs, traces, analytics, or error payloads
- DRM: detected and rejected at validation; never circumvented
- Provider boundary: payload scoped to current batch + bounded context only
- Training opt-out: provider config should disable training on customer content
- Admin access: metadata-only — the admin panel does **not** provide raw-content access
- Exceptional raw-content access: only via break-glass procedure outside the admin UI; time-bounded, purpose-limited, audited, and logged as a security event
- Copyright/acceptable-use enforcement per POLICY-COPYRIGHT
- Signed URLs: object-scoped, short-lived, purpose-specific
- Ownership enforcement: every request resolves to authenticated `user_id`
- Users can only access their own data

### MVP Slice

Core content protection. DRM rejection. Signed URL policy. Admin audit. Ownership enforcement.

### Constraints

- No-raw-text rule is absolute (DEC-004)
- Provider data handling must be reviewed (DEC-004)
- All audit events must be durable

### Success Criteria

- No raw book content in any logs, traces, or error messages
- DRM-protected files are rejected
- Signed URLs expire as configured
- Admin access to content is audited
- Users cannot access other users' data

### Open Questions

_None._

### Tasks

- TASK-7 — Add no-raw-text security guard for logs and errors
- TASK-8 — Enforce object ownership checks at API boundary
- TASK-9 — Implement signed URL policy enforcement
- TASK-10 — Add provider payload boundary validation
- TASK-11 — Implement security audit events and break-glass log
- FIX-1 — Replace length heuristic in payload_guard with explicit key-based policy

---

## FEAT-ADMIN — Admin Panel

**Capability:** ADMIN
**Priority:** medium
**Pipeline stage:** —
**Dependencies:** AUTH, QUOTA, QUEUE, TELEMETRY, SECURITY
**Slices:** UI, API, Policy, Admin, Tests
**Ref:** PRD §Credits & Usage Limits, PRD §MVP Scope, ARCH §Infrastructure Components, DEC-002

### Summary

Minimal admin interface for managing user credit balances, configuring credit settings, and monitoring job execution. Admin access is protected and audited.

### Goals

- Manage user credit balances (grant, adjust, view history)
- Configure credit settings (initial grant amount, mode multipliers)
- Monitor jobs (list, statuses, timelines, error details)
- Never bypass ownership, retention, audit, or privacy controls

### Non-Goals

- Payment provider management
- Self-service billing dashboard
- Public-facing dashboard
- Raw book content access (metadata-only by default)

### User Flow

1. Admin authenticates (same Google login, admin flag).
2. Admin views user list with credit balances.
3. Admin grants credits or adjusts balance for a user.
4. Admin views job list with statuses, timelines, and errors.
5. Admin configures initial credit grant and mode multipliers.

### Functional Requirements

- Admin authentication: admin flag or allowlist on the same auth mechanism
- User list: view all users with credit balances and job counts
- Credit management: grant credits, adjust balance, view credit transaction history per user
- Initial credit grant configuration: admin-configurable amount for new users
- Mode multipliers: configure credit-to-word-count multipliers per mode (Translate / Guided)
- Job monitoring: view job list, statuses, timelines, error details
- All admin actions produce audit events
- Admin panel provides **no raw-content access** — all views are metadata-only
- Exceptional raw-content access is handled via break-glass procedure outside the admin UI (FEAT-SECURITY)
- All admin actions produce audit events (POLICY-AUDIT)

### MVP Slice

User list + credit management + job monitoring. Basic UI. No advanced analytics.

### Constraints

- Must not bypass ownership, retention, audit, or privacy controls (FEATURE_MAP §ADMIN)
- All actions audited (DEC-002)
- Metadata-only view by default (DEC-004)

### Success Criteria

- Admin can view users and their credit balances
- Admin can grant and adjust credits
- Admin can configure initial credit grant and mode multipliers
- Admin can view jobs with statuses and error details
- All admin actions are audited
- Raw book content is not accessible through admin panel (break-glass only, outside UI)

### Open Questions

- Exact initial credit grant amount (→ Product)
- Exact credit conversion multipliers (→ Product / Architect)

### Tasks

_To be filled during task breakdown._
