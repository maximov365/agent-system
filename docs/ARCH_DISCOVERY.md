# Architecture Discovery for Unfolda

Status: draft
Last updated: 2026-03-08

This document captures the MVP discovery recommendations derived from `docs/PRD.md`.
Its purpose is to define the simplest viable technical direction that should inform `docs/ARCHITECTURE.md` and later concrete entries in `docs/DECISIONS.md`.

## Scope

This discovery focuses on the architectural decisions that materially affect:

- system shape
- pipeline execution
- operational complexity
- LLM integration
- storage and retention behavior
- progress reporting
- MVP kill-risk containment
- SaaS tenancy and quota boundaries
- security, privacy, and compliance posture
- cost control and observability
- canonical system-of-record modeling

## Current State

- `docs/ARCHITECTURE.md`: empty
- `docs/TASKS.md`: empty
- `docs/DECISIONS.md`: empty

This means the project is effectively making its first architecture-level choices from a clean slate.

## Global Assumption

- The project is still at pre-implementation MVP stage, so recommendations should favor speed of validation, low operational burden, and high reversibility over maximum long-term sophistication.

## Recommended Baseline Architecture

The recommended baseline architecture for MVP is:

- web frontend: `Next.js` with TypeScript for upload flow, auth UI, job list, progress, and admin screens
- API backend: `FastAPI` in Python for job management, validation endpoints, and pipeline orchestration APIs
- background processing: Python worker process using a lightweight Redis-backed queue
- database: `PostgreSQL` for users, jobs, quotas, status history, and metadata
- queue broker: `Redis`
- object storage: S3-compatible storage with signed URLs
- pipeline shape: explicit stage modules following `ingestion -> segmentation -> translation -> formatting -> export`
- translation integration: a single-provider adapter in MVP, with prompts externalized in `prompts/`
- consistency mechanism: job-scoped terminology memory plus rolling chapter context, not persistent global memory
- long-book execution model: paragraph-visible output with internal chunking, chapter checkpoints, and resumable progress
- progress reporting: stage-weighted progress plus throughput-based ETA
- SaaS isolation model: shared infrastructure with strict per-user ownership, storage namespacing, quota gates, and audit trails
- privacy boundary: no raw book text in logs, short-lived artifacts, scoped support access, and provider data controls
- cost architecture: pre-run estimation, hard per-job caps, token accounting, prompt budgets, and bounded retry budgets
- operational model: worker concurrency caps, backpressure, retry classes, poison-job quarantine, and pipeline-versioned runs
- observability model: structured logs, per-job timeline, stage timings, provider latency metrics, token metrics, throughput metrics, and stuck-job detection
- quality validation model: evaluation dataset, automated quality checks, benchmark runs, and regression detection before launch-impacting changes
- canonical artifact model: Postgres metadata as system of record, object storage for binaries and resumable structured artifacts

This stack best balances product fit, implementation speed, architecture safety, and future extensibility without introducing premature platform complexity.

It also assumes that MVP success depends not only on picking the right stack, but on containing the main failure modes of an LLM-backed SaaS product: quality collapse, provider throttling, cost explosion, malformed content, resumability errors, and privacy mistakes.

---

## Discovery Question
What foundational application stack should support the MVP?

## Prior Decisions
None found in `docs/DECISIONS.md`.

## Context
Unfolda is a web SaaS product with a mobile-first frontend, Google login, async background processing, object storage, and a pipeline-heavy backend centered on EPUB parsing and LLM-driven translation. The stack choice must optimize for a strong product UI while keeping the book-processing pipeline easy to implement and test.

## Options Considered
1. Django monolith with Python workers
2. Full TypeScript stack with `Next.js` and Node.js workers
3. `Next.js` frontend with `FastAPI` backend and Python worker

## Comparison

### Option 1 - Django monolith with Python workers
- pros:
  - strong fit for relational data, admin tooling, and backend workflows
  - Python ecosystem is favorable for EPUB parsing and text-processing work
  - simpler backend language story than a polyglot split
- cons:
  - weaker fit for a polished mobile-first product UI than a React-based frontend
  - frontend interactivity, upload UX, and progress-heavy screens become more awkward
  - product iteration speed on client-side UX is lower
- dependency friendliness: good
- implementation simplicity: medium
- operational simplicity: medium
- value-to-complexity: medium
- reversibility: medium
- pipeline fit: fits cleanly
- MVP fit: acceptable, but biased toward backend convenience over product UX
- long-term fit: acceptable if the product remains backend-heavy

### Option 2 - Full TypeScript stack with `Next.js` and Node.js workers
- pros:
  - single language across web and backend
  - very strong frontend developer experience
  - simple shared types across app and API
- cons:
  - weaker ecosystem for EPUB manipulation and book-processing pipelines than Python
  - translation pipeline logic risks becoming less ergonomic to test and evolve
  - more likely to require library workarounds around parsing and content transformation
- dependency friendliness: medium
- implementation simplicity: medium
- operational simplicity: medium
- value-to-complexity: medium
- reversibility: medium
- pipeline fit: requires adaptation
- MVP fit: acceptable if frontend speed is the only priority
- long-term fit: weaker for a product whose core differentiator is text-processing quality

### Option 3 - `Next.js` frontend with `FastAPI` backend and Python worker
- pros:
  - best fit for the actual product split: UX-heavy frontend plus pipeline-heavy backend
  - Python is a strong default for EPUB parsing, validation, pipeline testing, and LLM orchestration
  - `Next.js` fits the mobile-first upload, status, and download experience well
  - keeps domain-heavy pipeline logic in the language most suited to it
- cons:
  - two runtimes increase architectural surface area
  - auth/session integration needs explicit design
  - requires discipline to avoid duplicating validation between frontend and backend
- dependency friendliness: good
- implementation simplicity: medium
- operational simplicity: medium
- value-to-complexity: high
- reversibility: easy
- pipeline fit: fits cleanly
- MVP fit: strong
- long-term fit: strong

## Decision Quality Score
Scoring rule:
1 = poor
3 = acceptable
5 = strong
Scores support reasoning but do not determine the decision automatically.

### Option 1 - Django monolith with Python workers
- MVP fit: 3
- architecture fit: 4
- implementation simplicity: 4
- reversibility: 3
- dependency friendliness: 4
- operational simplicity: 4
- testability: 4
- long-term fit: 3

### Option 2 - Full TypeScript stack with `Next.js` and Node.js workers
- MVP fit: 3
- architecture fit: 3
- implementation simplicity: 3
- reversibility: 3
- dependency friendliness: 3
- operational simplicity: 4
- testability: 3
- long-term fit: 3

### Option 3 - `Next.js` frontend with `FastAPI` backend and Python worker
- MVP fit: 5
- architecture fit: 5
- implementation simplicity: 4
- reversibility: 4
- dependency friendliness: 4
- operational simplicity: 3
- testability: 5
- long-term fit: 5

## Decision Stability
stable

## Recommendation
Choose Option 3: `Next.js` for the web product surface, `FastAPI` for the backend API, and a Python worker for the processing pipeline.

## Score Interpretation
Option 3 wins because Unfolda is not a generic CRUD SaaS. Its core value depends on EPUB processing, structured pipeline behavior, and controlled LLM orchestration, which are more naturally implemented in Python, while the user-facing upload and progress experience is better served by `Next.js`.

## Why This Is the Simplest Viable Choice
It keeps each major concern in the most natural runtime without introducing heavyweight platform choices such as microservices or workflow engines.

## Risks / Trade-offs
- Auth boundaries between frontend and backend must be explicit.
- Shared types and validation schemas need discipline.
- Deployment will involve more moving parts than a monolith.

## Follow-up Implications
- `docs/ARCHITECTURE.md` should describe a two-runtime but still single-product architecture.
- API contracts between the web app and backend should be kept narrow and explicit.
- The backend and worker should live in the same Python codebase to avoid unnecessary service sprawl.

## Should This Go Into DECISIONS.md?
- yes - record now

## Optional Follow-ups
- Define the auth/session boundary between web app and backend before implementation begins.
- Define the minimum API surface for upload, job status, retry, and download.

## Assumptions Made
- The team values product UX and pipeline quality more than single-language purity.

## Recommended Next Step
Architect should turn this into a concrete component diagram and module boundary plan.

---

## Discovery Question
What job execution model should run long book-processing tasks for MVP?

## Prior Decisions
None found in `docs/DECISIONS.md`.

## Context
The PRD requires background jobs, one active job per user, retries within the retention window, progress reporting, ETA, and clear terminal states. The queue choice must support long-running tasks without forcing the team into a workflow engine too early.

## Options Considered
1. Postgres-driven custom worker polling
2. Redis-backed lightweight queue with Python workers
3. Heavy workflow system such as Celery-first orchestration or Temporal

## Comparison

### Option 1 - Postgres-driven custom worker polling
- pros:
  - minimal external infrastructure
  - simple to understand initially
  - jobs table is naturally aligned with product state
- cons:
  - queue semantics, retries, backoff, stuck-job recovery, and worker coordination must be built manually
  - becomes fragile quickly once processing times become long
  - pushes infrastructure complexity into application code
- dependency friendliness: strong
- implementation simplicity: low
- operational simplicity: medium
- value-to-complexity: low
- reversibility: medium
- pipeline fit: requires adaptation
- MVP fit: weak
- long-term fit: weak

### Option 2 - Redis-backed lightweight queue with Python workers
- pros:
  - simple, proven pattern for async background jobs
  - keeps orchestration explicit without overengineering
  - integrates cleanly with a jobs table in Postgres as the source of truth
  - enough for retries, worker isolation, and long-running task execution
- cons:
  - introduces Redis as an extra component
  - requires explicit progress persistence in the database
  - less feature-rich than heavyweight workflow engines
- dependency friendliness: good
- implementation simplicity: high
- operational simplicity: medium
- value-to-complexity: high
- reversibility: easy
- pipeline fit: fits cleanly
- MVP fit: strong
- long-term fit: acceptable

### Option 3 - Heavy workflow system such as Celery-first orchestration or Temporal
- pros:
  - rich retry and orchestration features
  - strong support for complex workflows, branching, and recovery
  - good path if pipeline fan-out grows significantly
- cons:
  - too much operational and conceptual overhead for the MVP stage
  - increases architecture surface before real workflow pain is proven
  - encourages platform complexity early
- dependency friendliness: medium
- implementation simplicity: low
- operational simplicity: low
- value-to-complexity: medium
- reversibility: hard
- pipeline fit: fits cleanly, but overshoots MVP needs
- MVP fit: weak
- long-term fit: strong only if workflow complexity grows materially

## Decision Quality Score
Scoring rule:
1 = poor
3 = acceptable
5 = strong
Scores support reasoning but do not determine the decision automatically.

### Option 1 - Postgres-driven custom worker polling
- MVP fit: 2
- architecture fit: 3
- implementation simplicity: 2
- reversibility: 3
- dependency friendliness: 5
- operational simplicity: 3
- testability: 3
- long-term fit: 2

### Option 2 - Redis-backed lightweight queue with Python workers
- MVP fit: 5
- architecture fit: 5
- implementation simplicity: 4
- reversibility: 4
- dependency friendliness: 4
- operational simplicity: 4
- testability: 4
- long-term fit: 4

### Option 3 - Heavy workflow system such as Celery-first orchestration or Temporal
- MVP fit: 2
- architecture fit: 4
- implementation simplicity: 2
- reversibility: 2
- dependency friendliness: 3
- operational simplicity: 2
- testability: 4
- long-term fit: 4

## Decision Stability
stable

## Recommendation
Choose Option 2: a lightweight Redis-backed queue, with Postgres as the authoritative job-state store and a Python worker executing the pipeline.

## Score Interpretation
This option gives Unfolda real queue semantics without turning the MVP into infrastructure work. It supports the PRD requirements directly while keeping the orchestration logic explicit and testable.

## Why This Is the Simplest Viable Choice
It adds only one new infrastructure component beyond the database, while avoiding both homemade queue complexity and premature workflow-engine adoption.

## Risks / Trade-offs
- Progress and ETA tracking must be explicitly modeled in the database.
- Job idempotency must be designed carefully at stage boundaries.
- Cleanup and retention expiry should be implemented as explicit scheduled tasks.

## Follow-up Implications
- Enforce the "one active job per user" rule in the API and the database.
- Treat the jobs table as product truth and Redis as execution plumbing.
- Keep retries bounded and stage-aware, not implicit.

## Should This Go Into DECISIONS.md?
- yes - record now

## Optional Follow-ups
- Standardize job states, retry semantics, and cleanup flows before coding.
- Define worker heartbeat and stuck-job detection rules.

## Assumptions Made
- MVP workload is moderate enough that one queue and one worker pool are sufficient.

## Recommended Next Step
Architect should define the job state model, retry policy, and queue integration boundaries.

---

## Discovery Question
What storage approach should handle uploads, generated EPUB files, downloads, and retention?

## Prior Decisions
None found in `docs/DECISIONS.md`.

## Context
The PRD requires temporary storage of uploaded and generated EPUB files, deletion after a retention window, retry support while the original file still exists, and long-term retention of metadata only. The storage solution must be reliable, easy to clean up, and not tightly coupled to one deployment environment.

## Options Considered
1. Local filesystem storage on application hosts
2. S3-compatible object storage with signed URLs
3. Managed BaaS storage tightly coupled to a platform provider

## Comparison

### Option 1 - Local filesystem storage on application hosts
- pros:
  - simplest possible initial setup
  - no external object storage dependency
  - easy local development story
- cons:
  - fragile in distributed or containerized deployments
  - retention cleanup and download delivery become operationally awkward
  - harder to separate API, worker, and web runtimes safely
- dependency friendliness: strong
- implementation simplicity: medium
- operational simplicity: low
- value-to-complexity: low
- reversibility: medium
- pipeline fit: requires adaptation
- MVP fit: weak outside single-host experiments
- long-term fit: weak

### Option 2 - S3-compatible object storage with signed URLs
- pros:
  - clear fit for temporary binary file storage
  - supports explicit lifecycle management and cleanup jobs
  - easy to serve downloads via signed URLs without passing binaries through the app layer
  - reversible across providers as long as the interface remains S3-compatible
- cons:
  - introduces an external storage service
  - requires explicit metadata tracking and deletion workflow
  - local development needs either MinIO or equivalent emulation
- dependency friendliness: good
- implementation simplicity: high
- operational simplicity: medium
- value-to-complexity: high
- reversibility: easy
- pipeline fit: fits cleanly
- MVP fit: strong
- long-term fit: strong

### Option 3 - Managed BaaS storage tightly coupled to a platform provider
- pros:
  - quick initial setup
  - simple integration if the rest of the stack already depends on that provider
  - may reduce operational effort early
- cons:
  - tighter vendor lock-in
  - weaker portability if backend architecture evolves
  - less aligned with a clean infrastructure boundary
- dependency friendliness: medium
- implementation simplicity: medium
- operational simplicity: medium
- value-to-complexity: medium
- reversibility: medium
- pipeline fit: fits cleanly
- MVP fit: acceptable
- long-term fit: acceptable, but less flexible

## Decision Quality Score
Scoring rule:
1 = poor
3 = acceptable
5 = strong
Scores support reasoning but do not determine the decision automatically.

### Option 1 - Local filesystem storage on application hosts
- MVP fit: 2
- architecture fit: 2
- implementation simplicity: 3
- reversibility: 3
- dependency friendliness: 5
- operational simplicity: 2
- testability: 3
- long-term fit: 1

### Option 2 - S3-compatible object storage with signed URLs
- MVP fit: 5
- architecture fit: 5
- implementation simplicity: 4
- reversibility: 5
- dependency friendliness: 4
- operational simplicity: 4
- testability: 4
- long-term fit: 5

### Option 3 - Managed BaaS storage tightly coupled to a platform provider
- MVP fit: 3
- architecture fit: 3
- implementation simplicity: 4
- reversibility: 3
- dependency friendliness: 3
- operational simplicity: 4
- testability: 3
- long-term fit: 3

## Decision Stability
stable

## Recommendation
Choose Option 2: S3-compatible object storage with signed URLs. Use an S3-style storage adapter in the codebase. For MVP, default to AWS S3 in production and MinIO-compatible local development.

## Score Interpretation
This option directly matches the PRD lifecycle rules while keeping storage isolated from domain logic and avoiding deployment fragility.

## Why This Is the Simplest Viable Choice
It is the lowest-risk path that cleanly supports temporary binary storage, file deletion, retries, and user downloads without overcomplicating the application layer.

## Risks / Trade-offs
- Cleanup logic must be explicit and reliable.
- Signed URL expiration rules need coordination with the retention policy.
- Metadata and object keys must be modeled carefully to avoid orphaned files.

## Follow-up Implications
- Store only file references and metadata in Postgres, never book content.
- Define separate object keys for source upload and generated output.
- Implement deletion as an explicit retention cleanup workflow, not an implicit side effect.

## Should This Go Into DECISIONS.md?
- yes - record now

## Optional Follow-ups
- Define the object key naming scheme and retention cleanup strategy.
- Decide whether the generated file is deleted immediately after first download or only marked eligible for cleanup.

## Assumptions Made
- The MVP will deploy in an environment where object storage is readily available.

## Recommended Next Step
Architect should define the storage adapter contract and file lifecycle state transitions.

---

## Discovery Question
How should the system process very long books while preserving paragraph-based output and staying within model context limits?

## Prior Decisions
None found in `docs/DECISIONS.md`.

## Context
The PRD explicitly requires paragraph-based output, support for books in the 50,000 to 100,000 word range, structure preservation, progress reporting, and translation consistency across the book. The solution must handle context-window limits without collapsing the pipeline or losing reproducibility.

## Options Considered
1. Translate full chapters or the entire book in large prompts
2. Translate each paragraph independently with no higher-level batching
3. Keep paragraph-visible output, but process token-bounded batches inside chapter-scoped checkpoints

## Comparison

### Option 1 - Translate full chapters or the entire book in large prompts
- pros:
  - stronger immediate context for consistency
  - conceptually simple on paper
  - may reduce the need for explicit memory structures
- cons:
  - brittle for long books and variable chapter sizes
  - expensive and hard to recover when a large call fails
  - weak fit for resumability and predictable progress reporting
- dependency friendliness: strong
- implementation simplicity: low
- operational simplicity: low
- value-to-complexity: low
- reversibility: medium
- pipeline fit: conflicts
- MVP fit: weak
- long-term fit: weak

### Option 2 - Translate each paragraph independently with no higher-level batching
- pros:
  - easy to parallelize conceptually
  - deterministic segmentation behavior
  - straightforward checkpointing
- cons:
  - poor translation consistency across names, tone, and references
  - loses useful chapter context
  - likely produces visibly inconsistent output for books
- dependency friendliness: strong
- implementation simplicity: high
- operational simplicity: medium
- value-to-complexity: medium
- reversibility: easy
- pipeline fit: fits cleanly
- MVP fit: weak because quality risk is high
- long-term fit: weak

### Option 3 - Keep paragraph-visible output, but process token-bounded batches inside chapter-scoped checkpoints
- pros:
  - preserves the PRD requirement that users see paragraph-based output
  - supports long books by bounding work into manageable chunks
  - enables resumability, progress tracking, and partial recovery
  - keeps chapter context available without requiring whole-book prompts
- cons:
  - needs explicit batching logic and checkpoint metadata
  - requires a consistency mechanism across batches
  - ETA logic becomes stage- and throughput-aware rather than trivial
- dependency friendliness: good
- implementation simplicity: medium
- operational simplicity: medium
- value-to-complexity: high
- reversibility: easy
- pipeline fit: fits cleanly
- MVP fit: strong
- long-term fit: strong

## Decision Quality Score
Scoring rule:
1 = poor
3 = acceptable
5 = strong
Scores support reasoning but do not determine the decision automatically.

### Option 1 - Translate full chapters or the entire book in large prompts
- MVP fit: 1
- architecture fit: 1
- implementation simplicity: 2
- reversibility: 3
- dependency friendliness: 5
- operational simplicity: 1
- testability: 2
- long-term fit: 1

### Option 2 - Translate each paragraph independently with no higher-level batching
- MVP fit: 2
- architecture fit: 4
- implementation simplicity: 5
- reversibility: 5
- dependency friendliness: 5
- operational simplicity: 4
- testability: 5
- long-term fit: 2

### Option 3 - Keep paragraph-visible output, but process token-bounded batches inside chapter-scoped checkpoints
- MVP fit: 5
- architecture fit: 5
- implementation simplicity: 4
- reversibility: 4
- dependency friendliness: 4
- operational simplicity: 4
- testability: 4
- long-term fit: 5

## Decision Stability
stable

## Recommendation
Choose Option 3: preserve paragraph boundaries for user-visible output, but internally process books as chapter-scoped, token-bounded translation batches with explicit checkpoints.

## Score Interpretation
This is the only option that satisfies the PRD's quality, progress, resumability, and size requirements at the same time without violating the pipeline model.

## Why This Is the Simplest Viable Choice
It adds only the batching and checkpointing logic that the product truly needs, instead of relying on oversized prompts or accepting low-quality independent paragraph translation.

## Risks / Trade-offs
- Chunking heuristics must remain deterministic.
- Chapter boundaries are not always equal in size or complexity.
- Retries must not corrupt partially completed batch state.

## Follow-up Implications
- Segmentation should produce paragraph-level structures plus internal batch metadata.
- Translation should operate on bounded batches, not the full book.
- Job progress should be derived from completed batches and stage weights.

## Should This Go Into DECISIONS.md?
- yes - record now

## Optional Follow-ups
- Define batch sizing in tokens rather than raw character count.
- Add explicit checkpoint entities per chapter or per translation batch.

## Assumptions Made
- EPUB structure will usually provide chapter-like boundaries, even if cleanup is sometimes needed.

## Recommended Next Step
Architect should define the intermediate representations for paragraphs, batches, and checkpoints.

---

## Discovery Question
What consistency mechanism should preserve names, terms, gender, and translation choices across segments?

## Prior Decisions
None found in `docs/DECISIONS.md`.

## Context
The PRD requires consistency across the entire book, but also keeps the pipeline deterministic where practical and avoids hidden state. The consistency mechanism must improve translation quality without introducing a permanent global knowledge system too early.

## Options Considered
1. Rolling raw context only
2. Persistent cross-book glossary and memory store from day one
3. Job-scoped consistency memory with terminology map, named-entity registry, and rolling chapter context

## Comparison

### Option 1 - Rolling raw context only
- pros:
  - simplest possible implementation
  - no separate memory structures to manage
  - easy to prototype quickly
- cons:
  - weak control over recurring names and terminology
  - fragile when batch boundaries shift
  - hard to test or inspect consistency behavior
- dependency friendliness: strong
- implementation simplicity: high
- operational simplicity: high
- value-to-complexity: medium
- reversibility: easy
- pipeline fit: requires adaptation
- MVP fit: acceptable only for a prototype
- long-term fit: weak

### Option 2 - Persistent cross-book glossary and memory store from day one
- pros:
  - could support richer future product features
  - opens a path toward user-managed glossaries later
  - may improve repeated terminology across jobs
- cons:
  - outside MVP scope
  - introduces product and privacy complexity early
  - risks hidden state affecting reproducibility across jobs
- dependency friendliness: medium
- implementation simplicity: low
- operational simplicity: low
- value-to-complexity: low
- reversibility: hard
- pipeline fit: requires adaptation
- MVP fit: weak
- long-term fit: strong only if glossary features become core

### Option 3 - Job-scoped consistency memory with terminology map, named-entity registry, and rolling chapter context
- pros:
  - directly matches the PRD requirement without introducing cross-book persistence
  - keeps state explicit, inspectable, and scoped to one job
  - supports consistent names and terms while preserving reproducibility boundaries
  - aligns with checkpointed batch processing
- cons:
  - requires explicit state modeling in translation orchestration
  - memory extraction logic must be controlled and bounded
  - prompt design and validation need care
- dependency friendliness: good
- implementation simplicity: medium
- operational simplicity: medium
- value-to-complexity: high
- reversibility: easy
- pipeline fit: fits cleanly
- MVP fit: strong
- long-term fit: strong

## Decision Quality Score
Scoring rule:
1 = poor
3 = acceptable
5 = strong
Scores support reasoning but do not determine the decision automatically.

### Option 1 - Rolling raw context only
- MVP fit: 3
- architecture fit: 3
- implementation simplicity: 5
- reversibility: 5
- dependency friendliness: 5
- operational simplicity: 5
- testability: 2
- long-term fit: 2

### Option 2 - Persistent cross-book glossary and memory store from day one
- MVP fit: 1
- architecture fit: 2
- implementation simplicity: 1
- reversibility: 2
- dependency friendliness: 2
- operational simplicity: 2
- testability: 2
- long-term fit: 4

### Option 3 - Job-scoped consistency memory with terminology map, named-entity registry, and rolling chapter context
- MVP fit: 5
- architecture fit: 5
- implementation simplicity: 4
- reversibility: 4
- dependency friendliness: 4
- operational simplicity: 4
- testability: 4
- long-term fit: 5

## Decision Stability
revisit after MVP

## Recommendation
Choose Option 3: a transient, job-scoped consistency memory that is generated during processing and passed forward between translation batches.

## Score Interpretation
Option 3 gives the MVP the consistency benefits it needs without creating global hidden state or prematurely building user glossary features that the PRD explicitly places outside MVP.

## Why This Is the Simplest Viable Choice
It is the smallest memory system that solves the actual product requirement: maintain consistent translation decisions within a single book-processing job.

## Risks / Trade-offs
- Prompt design may overfit if the memory becomes too verbose.
- Memory extraction should stay bounded and structured.
- The exact schema may need iteration after a small benchmark.

## Follow-up Implications
- Store consistency memory as explicit translation-stage artifacts, not as implicit runtime state.
- Treat the memory as part of job-scoped processing data, not user data.
- Keep the formatting and export stages unaware of how consistency was produced.

## Should This Go Into DECISIONS.md?
- yes - record after implementation confirms the exact memory shape

## Optional Follow-ups
- Define the minimum memory schema: entities, preferred term mappings, unresolved ambiguities, and short context summary.
- Benchmark how much memory actually improves quality on 2 to 3 representative books.

## Assumptions Made
- Cross-book glossary persistence is not needed for MVP quality.

## Recommended Next Step
Architect should define the consistency-memory schema and how it flows through translation batches.

---

## Discovery Question
What LLM integration strategy should the MVP translation stage use?

## Prior Decisions
None found in `docs/DECISIONS.md`.

## Context
The PRD requires context-aware translation, explanation generation, consistency across segments, and reproducible processing. At the same time, the project guardrails explicitly prohibit hardcoding model names in implementation logic and require prompts to live in `prompts/`.

## Options Considered
1. Hardcode one provider and model directly into the implementation
2. Single-provider adapter architecture with provider and model configured externally
3. Multi-provider routing and specialized model orchestration from day one

## Comparison

### Option 1 - Hardcode one provider and model directly into the implementation
- pros:
  - quickest to start
  - minimal abstraction
  - very easy to prototype
- cons:
  - violates project guidance around configuration
  - creates immediate vendor lock-in in code paths
  - makes testing and future replacement harder
- dependency friendliness: medium
- implementation simplicity: medium
- operational simplicity: medium
- value-to-complexity: low
- reversibility: hard
- pipeline fit: conflicts
- MVP fit: weak
- long-term fit: weak

### Option 2 - Single-provider adapter architecture with provider and model configured externally
- pros:
  - keeps the MVP simple while preserving clean boundaries
  - follows the rule that model choice should be configuration, not embedded logic
  - allows later provider replacement without forcing multi-provider complexity now
  - supports prompt externalization and bounded retry behavior
- cons:
  - slightly more upfront design than hardcoding
  - still requires one concrete provider choice for the first release
  - benchmark work is needed before final provider lock-in
- dependency friendliness: good
- implementation simplicity: high
- operational simplicity: medium
- value-to-complexity: high
- reversibility: easy
- pipeline fit: fits cleanly
- MVP fit: strong
- long-term fit: strong

### Option 3 - Multi-provider routing and specialized model orchestration from day one
- pros:
  - potentially better cost or quality optimization later
  - may reduce dependency risk across vendors
  - flexible for future experimentation
- cons:
  - too much abstraction for the MVP stage
  - increases prompt management, testing, and failure modes early
  - complicates reproducibility and operational debugging
- dependency friendliness: low
- implementation simplicity: low
- operational simplicity: low
- value-to-complexity: medium
- reversibility: medium
- pipeline fit: requires adaptation
- MVP fit: weak
- long-term fit: strong only if multi-provider strategy becomes necessary

## Decision Quality Score
Scoring rule:
1 = poor
3 = acceptable
5 = strong
Scores support reasoning but do not determine the decision automatically.

### Option 1 - Hardcode one provider and model directly into the implementation
- MVP fit: 2
- architecture fit: 1
- implementation simplicity: 3
- reversibility: 1
- dependency friendliness: 2
- operational simplicity: 3
- testability: 2
- long-term fit: 1

### Option 2 - Single-provider adapter architecture with provider and model configured externally
- MVP fit: 5
- architecture fit: 5
- implementation simplicity: 4
- reversibility: 5
- dependency friendliness: 4
- operational simplicity: 4
- testability: 4
- long-term fit: 5

### Option 3 - Multi-provider routing and specialized model orchestration from day one
- MVP fit: 2
- architecture fit: 3
- implementation simplicity: 2
- reversibility: 3
- dependency friendliness: 2
- operational simplicity: 2
- testability: 2
- long-term fit: 4

## Decision Stability
revisit after MVP

## Recommendation
Choose Option 2: build a single-provider adapter boundary for MVP, keep prompts externalized, configure provider and model outside implementation logic, and avoid multi-provider routing until real pain justifies it.

## Score Interpretation
This approach satisfies the guardrails and keeps the architecture clean without turning the MVP into a provider abstraction project.

## Why This Is the Simplest Viable Choice
It is just enough indirection to keep the system maintainable, but not so much that the team spends time designing for hypothetical provider switching.

## Risks / Trade-offs
- A concrete provider still needs to be chosen before implementation.
- Benchmarking must happen early enough to avoid delaying build work.
- Translation and explanation quality may differ enough that prompt variants are still needed.

## Follow-up Implications
- Prompt templates must live in `prompts/`.
- Retry behavior must be explicit and bounded.
- The translation module should depend on a provider interface, not vendor SDKs directly.

## Should This Go Into DECISIONS.md?
- yes - record after a short provider benchmark confirms the initial vendor choice

## Optional Follow-ups
- Run a small benchmark on 2 to 3 representative books before selecting the initial provider.
- Define whether Guided Mode explanation generation uses the same model or a cheaper secondary model later.

## Assumptions Made
- The MVP can succeed with one primary provider if quality is strong enough.

## Recommended Next Step
Architect should define the translation provider interface and the benchmark criteria for selecting the initial provider.

---

## Discovery Question
How should source-language detection work for MVP?

## Prior Decisions
None found in `docs/DECISIONS.md`.

## Context
The PRD says source language is auto-detected but may be overridden manually. It also lists supported language pairs and expects predictable behavior. The detection strategy should avoid unnecessary LLM calls while handling edge cases such as multilingual front matter, quotes, or malformed EPUB sections.

## Options Considered
1. Whole-book detection only
2. Per-segment detection for all segments
3. Whole-book primary detection with targeted anomaly checks and manual override

## Comparison

### Option 1 - Whole-book detection only
- pros:
  - simplest implementation
  - deterministic and cheap
  - fits naturally into ingestion
- cons:
  - weak on multilingual or noisy books
  - may misclassify books with unusual front matter or mixed-language sections
  - gives the system fewer ways to flag suspicious cases
- dependency friendliness: strong
- implementation simplicity: high
- operational simplicity: high
- value-to-complexity: medium
- reversibility: easy
- pipeline fit: fits cleanly
- MVP fit: acceptable
- long-term fit: acceptable

### Option 2 - Per-segment detection for all segments
- pros:
  - highest theoretical granularity
  - can capture multilingual content precisely
  - may help with odd or malformed source files
- cons:
  - unnecessary complexity for most books
  - adds noise and inconsistency across the pipeline
  - complicates both segmentation and translation configuration
- dependency friendliness: medium
- implementation simplicity: low
- operational simplicity: low
- value-to-complexity: low
- reversibility: medium
- pipeline fit: requires adaptation
- MVP fit: weak
- long-term fit: acceptable only for multilingual-specialized products

### Option 3 - Whole-book primary detection with targeted anomaly checks and manual override
- pros:
  - keeps the main path simple and deterministic
  - handles low-confidence or suspicious-content edge cases explicitly
  - matches the PRD requirement that users can override detection
  - avoids spreading language detection complexity through the whole pipeline
- cons:
  - needs a confidence threshold and anomaly heuristic
  - some edge cases may still require user correction
  - slightly more work than pure whole-book detection
- dependency friendliness: good
- implementation simplicity: medium
- operational simplicity: high
- value-to-complexity: high
- reversibility: easy
- pipeline fit: fits cleanly
- MVP fit: strong
- long-term fit: strong

## Decision Quality Score
Scoring rule:
1 = poor
3 = acceptable
5 = strong
Scores support reasoning but do not determine the decision automatically.

### Option 1 - Whole-book detection only
- MVP fit: 3
- architecture fit: 4
- implementation simplicity: 5
- reversibility: 5
- dependency friendliness: 5
- operational simplicity: 5
- testability: 4
- long-term fit: 3

### Option 2 - Per-segment detection for all segments
- MVP fit: 1
- architecture fit: 2
- implementation simplicity: 1
- reversibility: 3
- dependency friendliness: 3
- operational simplicity: 2
- testability: 2
- long-term fit: 3

### Option 3 - Whole-book primary detection with targeted anomaly checks and manual override
- MVP fit: 5
- architecture fit: 5
- implementation simplicity: 4
- reversibility: 5
- dependency friendliness: 4
- operational simplicity: 5
- testability: 4
- long-term fit: 5

## Decision Stability
stable

## Recommendation
Choose Option 3: perform primary language detection once during ingestion, expose the result before job confirmation, and only run targeted anomaly checks when confidence is low or sections appear suspiciously multilingual.

## Score Interpretation
This approach keeps the default path cheap and predictable while still covering the main failure modes the PRD is likely to encounter.

## Why This Is the Simplest Viable Choice
It preserves a clean ingestion responsibility and avoids making every downstream stage language-detection-aware.

## Risks / Trade-offs
- Confidence heuristics need calibration.
- Some multilingual books may still need manual correction.
- Detection should avoid being confused by small metadata or disclaimer fragments.

## Follow-up Implications
- Language detection belongs in ingestion, not translation.
- The detected source language should be stored in normalized document metadata and job settings.
- The UI should allow override before the job is queued.

## Should This Go Into DECISIONS.md?
- yes - record now

## Optional Follow-ups
- Define how low-confidence detection is surfaced to the user.
- Decide whether anomaly checks operate at chapter level or selected text sample level.

## Assumptions Made
- Most MVP books are predominantly single-language even if a few segments differ.

## Recommended Next Step
Architect should define the ingestion contract fields for detected language, confidence, and user override.

---

## Discovery Question
How should progress and ETA be modeled for user-visible job tracking?

## Prior Decisions
None found in `docs/DECISIONS.md`.

## Context
The PRD makes progress transparency a core product principle. Users must see progress and ETA while the pipeline runs, and they must be able to close the browser and return later. This requires a stable architecture for status reporting that does not depend on a live browser session.

## Options Considered
1. Fixed percentages per status only
2. Stream low-level worker activity directly into the UI
3. Stage-weighted progress with throughput-based ETA persisted in job metadata

## Comparison

### Option 1 - Fixed percentages per status only
- pros:
  - very simple to implement
  - easy to reason about
  - minimal data modeling
- cons:
  - ETA quality is poor
  - gives little feedback during long translation phases
  - may feel misleading for long books
- dependency friendliness: strong
- implementation simplicity: high
- operational simplicity: high
- value-to-complexity: medium
- reversibility: easy
- pipeline fit: fits cleanly
- MVP fit: acceptable for a prototype, weak for product quality
- long-term fit: weak

### Option 2 - Stream low-level worker activity directly into the UI
- pros:
  - potentially rich live feedback
  - could reflect actual runtime behavior in detail
  - attractive for debugging
- cons:
  - too tightly couples workers and frontend delivery
  - brittle when users disconnect
  - mixes execution details with product status
- dependency friendliness: medium
- implementation simplicity: low
- operational simplicity: low
- value-to-complexity: low
- reversibility: medium
- pipeline fit: requires adaptation
- MVP fit: weak
- long-term fit: weak

### Option 3 - Stage-weighted progress with throughput-based ETA persisted in job metadata
- pros:
  - matches the PRD requirement for reconnectable progress tracking
  - keeps job status durable and UI-independent
  - can become more accurate as batches complete
  - cleanly fits pipeline stages and checkpointed execution
- cons:
  - requires explicit progress-weight design
  - ETA will still be approximate, especially early in the run
  - progress math needs calibration from real books
- dependency friendliness: good
- implementation simplicity: medium
- operational simplicity: high
- value-to-complexity: high
- reversibility: easy
- pipeline fit: fits cleanly
- MVP fit: strong
- long-term fit: strong

## Decision Quality Score
Scoring rule:
1 = poor
3 = acceptable
5 = strong
Scores support reasoning but do not determine the decision automatically.

### Option 1 - Fixed percentages per status only
- MVP fit: 3
- architecture fit: 4
- implementation simplicity: 5
- reversibility: 5
- dependency friendliness: 5
- operational simplicity: 5
- testability: 5
- long-term fit: 2

### Option 2 - Stream low-level worker activity directly into the UI
- MVP fit: 1
- architecture fit: 2
- implementation simplicity: 1
- reversibility: 3
- dependency friendliness: 3
- operational simplicity: 1
- testability: 2
- long-term fit: 2

### Option 3 - Stage-weighted progress with throughput-based ETA persisted in job metadata
- MVP fit: 5
- architecture fit: 5
- implementation simplicity: 4
- reversibility: 5
- dependency friendliness: 4
- operational simplicity: 5
- testability: 4
- long-term fit: 5

## Decision Stability
stable

## Recommendation
Choose Option 3: model progress and ETA as durable job metadata derived from stage completion and observed throughput, not from live worker streaming.

## Score Interpretation
This is the only option that cleanly supports async processing, page reloads, and long-running jobs without coupling the user experience to worker internals.

## Why This Is the Simplest Viable Choice
It gives the product the visibility it needs while keeping workers, APIs, and UI loosely coupled.

## Risks / Trade-offs
- ETA will be rough early in a job.
- Stage weights need tuning based on real runs.
- The UI must communicate that ETA is approximate.

## Follow-up Implications
- Persist progress snapshots in the jobs table.
- Track translated batch counts, completed stages, and timing metrics.
- Keep websocket or polling transport separate from how progress is computed.

## Should This Go Into DECISIONS.md?
- yes - record now

## Optional Follow-ups
- Define initial stage weights for validating, queued, processing by pipeline stage, completed, failed, and expired.
- Decide whether the frontend uses polling first and websockets later.

## Assumptions Made
- ETA accuracy can improve iteratively after the first real book-processing runs.

## Recommended Next Step
Architect should define the job progress schema and the first ETA calculation strategy.

---

## Consolidated Recommendation

If Unfolda wants the simplest viable architecture for MVP, it should adopt the following combined direction:

- `Next.js` for the user-facing web app
- `FastAPI` plus a Python worker for backend and pipeline execution
- `PostgreSQL` as the system-of-record database
- `Redis` as the lightweight queue broker
- S3-compatible object storage with signed URLs
- explicit pipeline modules matching `ingestion -> segmentation -> translation -> formatting -> export`
- paragraph-visible outputs, internal batch processing, and chapter-scoped checkpoints
- job-scoped consistency memory rather than persistent glossary infrastructure
- single-provider LLM adapter with externalized prompts and config-driven model selection
- ingestion-level language detection with anomaly fallback and manual override
- durable progress and ETA persisted as job metadata

## Why This Combined Direction Is Best For MVP

This direction is the best overall fit because it:

- respects the pipeline guardrails and keeps stage boundaries explicit
- optimizes for the actual hard part of the product: book-processing quality
- avoids premature complexity such as multi-provider orchestration, persistent glossary systems, or heavyweight workflow engines
- remains highly reversible if the product later needs deeper scaling or more advanced workflow control

## Recommended Decision Recording Order

The following should be recorded in `docs/DECISIONS.md` early because they strongly shape the system:

1. application stack split: `Next.js` + `FastAPI` + Python worker
2. queue strategy: Redis-backed lightweight queue
3. storage strategy: S3-compatible object storage
4. long-book strategy: paragraph-visible batches with checkpoints
5. progress strategy: durable stage-weighted progress and ETA

The following can be recorded after a short benchmark or architecture spike:

1. exact LLM provider choice
2. exact consistency-memory schema
3. exact anomaly strategy for language detection

## Recommended Next Step

Create `docs/ARCHITECTURE.md` from this document by turning the recommended direction into:

- component boundaries
- pipeline module boundaries
- data flow diagrams
- job and storage lifecycle definitions
- core contracts between web app, API, worker, database, queue, and object storage

---

## Discovery Question
What failure modes are most likely to kill the MVP even if the baseline stack choice is correct?

## Prior Decisions
None found in `docs/DECISIONS.md`.

## Context
For Unfolda, the biggest architecture risk is not picking the wrong framework. The bigger risk is building a technically clean system that still fails operationally or economically because:

- LLM latency and quality vary by provider load, language pair, and book genre
- rate limits or throttling can stall long-running jobs
- long books can blow up inference cost unexpectedly
- malformed EPUBs can poison the pipeline before useful work starts
- partial failures can leave jobs in ambiguous or duplicated states
- consistency memory can drift and degrade translation quality over time
- poor translation quality can make the product fail even if every component is "working"

## Options Considered
1. Reactive MVP with generic retries and broad monitoring only
2. Enterprise-grade resilience for every risk from day one
3. Risk-contained MVP with explicit kill-risk guardrails at provider, content, cost, and state boundaries

## Comparison

### Option 1 - Reactive MVP with generic retries and broad monitoring only
- pros:
  - fast to start
  - minimal upfront architecture work
  - fewer decisions before implementation
- cons:
  - lets the highest-impact failures appear in production first
  - encourages hidden state corruption and duplicate work
  - weak protection against cost spikes or poor quality
- dependency friendliness: strong
- implementation simplicity: high
- operational simplicity: low
- value-to-complexity: low
- reversibility: medium
- pipeline fit: requires adaptation
- MVP fit: weak
- long-term fit: weak

### Option 2 - Enterprise-grade resilience for every risk from day one
- pros:
  - strongest theoretical safety
  - broadest observability and control surface
  - lower chance of missing a risk class
- cons:
  - overbuilds before real traffic and benchmark data exist
  - pushes the MVP into platform engineering
  - slows validation of the actual product value
- dependency friendliness: medium
- implementation simplicity: low
- operational simplicity: low
- value-to-complexity: medium
- reversibility: medium
- pipeline fit: fits cleanly
- MVP fit: weak
- long-term fit: strong

### Option 3 - Risk-contained MVP with explicit kill-risk guardrails at provider, content, cost, and state boundaries
- pros:
  - targets the actual failure modes most likely to break the product
  - keeps the architecture lightweight while making the riskiest boundaries explicit
  - supports clearer operational playbooks and launch criteria
  - gives Product and Architect a shared risk register instead of implicit assumptions
- cons:
  - requires more up-front modeling than a purely stack-driven discovery
  - some guardrails will need calibration after real-book benchmarks
  - quality risk still requires empirical validation, not just design
- dependency friendliness: good
- implementation simplicity: medium
- operational simplicity: medium
- value-to-complexity: high
- reversibility: easy
- pipeline fit: fits cleanly
- MVP fit: strong
- long-term fit: strong

## Decision Quality Score
Scoring rule:
1 = poor
3 = acceptable
5 = strong
Scores support reasoning but do not determine the decision automatically.

### Option 1 - Reactive MVP with generic retries and broad monitoring only
- MVP fit: 2
- architecture fit: 2
- implementation simplicity: 5
- reversibility: 4
- dependency friendliness: 5
- operational simplicity: 2
- testability: 2
- long-term fit: 2

### Option 2 - Enterprise-grade resilience for every risk from day one
- MVP fit: 2
- architecture fit: 4
- implementation simplicity: 1
- reversibility: 3
- dependency friendliness: 3
- operational simplicity: 2
- testability: 4
- long-term fit: 5

### Option 3 - Risk-contained MVP with explicit kill-risk guardrails at provider, content, cost, and state boundaries
- MVP fit: 5
- architecture fit: 5
- implementation simplicity: 4
- reversibility: 5
- dependency friendliness: 4
- operational simplicity: 4
- testability: 5
- long-term fit: 4

## Decision Stability
stable

## Recommendation
Choose Option 3. Treat the following as first-class MVP architecture risks that require explicit controls before build-out:

- provider throttling and timeout volatility
- translation quality failure on representative books
- malformed EPUB parsing and validation failures
- resumability after partial provider or worker failure
- duplicate retry execution and corrupted partial state
- cost explosion on long books or repeated retries
- consistency-memory drift across batches

## Score Interpretation
Option 3 wins because it adds only the controls that are disproportionally valuable for an LLM-heavy SaaS product, instead of either hoping problems stay small or overbuilding for hypothetical scale.

## Why This Is the Simplest Viable Choice
It is the smallest approach that turns the main product-killing risks into explicit architecture boundaries rather than launch-time surprises.

## Risks / Trade-offs
- Quality still needs benchmark-based acceptance criteria.
- Some risk controls will increase implementation scope for MVP.
- Risk ownership must stay explicit across Product, Architect, and Builder work.

## Follow-up Implications
- Add a benchmark gate for translation quality before MVP launch.
- Maintain a representative evaluation dataset across key language pairs, modes, and book types.
- Add automated quality checks and regression detection for prompt, provider, and pipeline changes.
- Classify failures into provider, content, system, and policy classes.
- Define batch-level idempotency and resumability before implementing worker retries.
- Track cost and quality regressions across prompt or provider changes.

## Should This Go Into DECISIONS.md?
- yes - record now

## Optional Follow-ups
- Add a one-page MVP risk register derived from this section into `docs/DECISIONS.md` or `docs/ARCHITECTURE.md`.
- Define launch-blocking metrics for quality, failure rate, stuck jobs, and cost per completed book.

## Assumptions Made
- The team prefers an MVP that is deliberately risk-contained over one that is merely easy to start.

## Recommended Next Step
Architect should turn these kill risks into concrete control points in the runtime and data model.

---

## Discovery Question
How should MVP define SaaS tenancy boundaries, quota enforcement, abuse prevention, and auditability?

## Prior Decisions
None found in `docs/DECISIONS.md`.

## Context
Unfolda is not only a pipeline application. It is a SaaS product that accepts user uploads, enforces usage limits, isolates user jobs, and needs admin visibility into expensive operations. If tenancy and audit boundaries stay implicit, cost leaks, support mistakes, and accidental cross-user access become much more likely.

## Options Considered
1. Shared SaaS with mostly application-level ownership checks
2. Strong isolation through dedicated infrastructure per user
3. Shared SaaS with explicit per-user ownership, storage namespacing, quota gates, abuse controls, and audit events

## Comparison

### Option 1 - Shared SaaS with mostly application-level ownership checks
- pros:
  - fast to implement
  - minimal schema design
  - low conceptual overhead
- cons:
  - too easy for ownership checks to become inconsistent
  - weak basis for auditability and support tooling
  - abuse prevention and quota enforcement remain scattered
- dependency friendliness: strong
- implementation simplicity: high
- operational simplicity: medium
- value-to-complexity: medium
- reversibility: medium
- pipeline fit: requires adaptation
- MVP fit: acceptable only for an internal prototype
- long-term fit: weak

### Option 2 - Strong isolation through dedicated infrastructure per user
- pros:
  - strongest isolation story
  - easier to reason about blast radius
  - may simplify some compliance narratives later
- cons:
  - operationally heavy for MVP
  - poor fit for manual quota management and a single shared product surface
  - adds platform work before demand is proven
- dependency friendliness: low
- implementation simplicity: low
- operational simplicity: low
- value-to-complexity: low
- reversibility: hard
- pipeline fit: fits cleanly
- MVP fit: weak
- long-term fit: acceptable for enterprise-only products, not for this MVP

### Option 3 - Shared SaaS with explicit per-user ownership, storage namespacing, quota gates, abuse controls, and audit events
- pros:
  - matches the PRD delivery model and manual-admin quota model
  - supports per-user isolation without dedicated infrastructure
  - gives clean hooks for future billing and cost attribution
  - keeps support and admin tooling compatible with least-privilege access
- cons:
  - needs more deliberate schema and API design than soft tenancy
  - requires ownership checks at every storage and job boundary
  - abuse controls need tuning after real traffic starts
- dependency friendliness: good
- implementation simplicity: medium
- operational simplicity: high
- value-to-complexity: high
- reversibility: easy
- pipeline fit: fits cleanly
- MVP fit: strong
- long-term fit: strong

## Decision Quality Score
Scoring rule:
1 = poor
3 = acceptable
5 = strong
Scores support reasoning but do not determine the decision automatically.

### Option 1 - Shared SaaS with mostly application-level ownership checks
- MVP fit: 2
- architecture fit: 2
- implementation simplicity: 5
- reversibility: 3
- dependency friendliness: 5
- operational simplicity: 3
- testability: 2
- long-term fit: 2

### Option 2 - Strong isolation through dedicated infrastructure per user
- MVP fit: 1
- architecture fit: 4
- implementation simplicity: 1
- reversibility: 2
- dependency friendliness: 2
- operational simplicity: 1
- testability: 4
- long-term fit: 3

### Option 3 - Shared SaaS with explicit per-user ownership, storage namespacing, quota gates, abuse controls, and audit events
- MVP fit: 5
- architecture fit: 5
- implementation simplicity: 4
- reversibility: 5
- dependency friendliness: 4
- operational simplicity: 5
- testability: 4
- long-term fit: 5

## Decision Stability
stable

## Recommendation
Choose Option 3. The MVP should be modeled as a shared SaaS with strong logical isolation, not as a soft multi-user app and not as per-user infrastructure.

## Score Interpretation
This option gives Unfolda the minimum production SaaS boundaries it needs: ownership clarity, quota enforcement, abuse resistance, and auditable expensive operations.

## Why This Is the Simplest Viable Choice
It preserves a simple shared deployment while making the most important user and cost boundaries explicit from day one.

## Risks / Trade-offs
- Every primary entity must carry an owner boundary.
- Admin tooling must not bypass ownership and audit rules casually.
- Abuse controls such as upload rate limits and active-job limits will need tuning.

## Follow-up Implications
- Every canonical entity should carry `user_id` ownership or be reachable through an owning job.
- Object storage keys should be namespaced by user and job, not only by random IDs.
- Quota enforcement should happen before queue admission and again before expensive translation work begins.
- Add audit events for quota changes, retries, admin actions, signed URL issuance, and expensive provider calls.
- Add early abuse controls: file-size caps, MIME validation, one active job per user, and rate limits on upload and retry endpoints.

## Should This Go Into DECISIONS.md?
- yes - record now

## Optional Follow-ups
- Decide whether the data model should remain user-scoped only in MVP or reserve space for future organization-level ownership.
- Define the minimum admin/support permissions matrix.

## Assumptions Made
- MVP tenancy is user-level, not team-level or organization-level.

## Recommended Next Step
Architect should define canonical ownership fields, quota checkpoints, and audit event classes.

---

## Discovery Question
How should MVP define the security, privacy, and compliance boundary for uploaded books and external LLM providers?

## Prior Decisions
None found in `docs/DECISIONS.md`.

## Context
Unfolda receives copyrighted book files, extracts text, sends user content to an external LLM provider, and temporarily stores uploaded and generated artifacts. This is one of the highest-risk architecture zones. The MVP must clearly define what data is stored, where it is stored, what is sent to providers, what is logged, who can access it, and when it is deleted.

## Options Considered
1. Default external-provider integration with loose logging and ad hoc retention controls
2. Self-hosted models only so no source text leaves the platform boundary
3. External provider allowed, but with strict data minimization, no raw-text logging, scoped access, and explicit retention controls

## Comparison

### Option 1 - Default external-provider integration with loose logging and ad hoc retention controls
- pros:
  - fastest to prototype
  - lowest upfront architecture work
  - easiest debugging during early development
- cons:
  - unacceptable privacy and compliance ambiguity
  - high risk of raw-text leakage through logs or support tooling
  - weak contractual control over provider-side usage
- dependency friendliness: medium
- implementation simplicity: high
- operational simplicity: low
- value-to-complexity: low
- reversibility: medium
- pipeline fit: conflicts
- MVP fit: weak
- long-term fit: weak

### Option 2 - Self-hosted models only so no source text leaves the platform boundary
- pros:
  - strongest data-control narrative
  - simpler provider-contract story
  - avoids third-party training concerns
- cons:
  - much higher infrastructure and quality risk for MVP
  - likely weaker output quality across supported languages
  - shifts risk from privacy to model quality and operations
- dependency friendliness: low
- implementation simplicity: low
- operational simplicity: low
- value-to-complexity: low
- reversibility: medium
- pipeline fit: fits cleanly
- MVP fit: weak
- long-term fit: acceptable only if model quality and infra maturity improve materially

### Option 3 - External provider allowed, but with strict data minimization, no raw-text logging, scoped access, and explicit retention controls
- pros:
  - realistic for MVP quality goals
  - keeps the privacy boundary explicit and reviewable
  - allows strong internal handling rules even when using a third-party model
  - aligns with the PRD storage policy and legal sensitivity of book content
- cons:
  - requires disciplined observability design
  - provider selection must include contractual data-use review
  - support workflows become more constrained by design
- dependency friendliness: good
- implementation simplicity: medium
- operational simplicity: medium
- value-to-complexity: high
- reversibility: medium
- pipeline fit: fits cleanly
- MVP fit: strong
- long-term fit: strong

## Decision Quality Score
Scoring rule:
1 = poor
3 = acceptable
5 = strong
Scores support reasoning but do not determine the decision automatically.

### Option 1 - Default external-provider integration with loose logging and ad hoc retention controls
- MVP fit: 1
- architecture fit: 1
- implementation simplicity: 5
- reversibility: 3
- dependency friendliness: 3
- operational simplicity: 2
- testability: 1
- long-term fit: 1

### Option 2 - Self-hosted models only so no source text leaves the platform boundary
- MVP fit: 1
- architecture fit: 4
- implementation simplicity: 1
- reversibility: 3
- dependency friendliness: 1
- operational simplicity: 1
- testability: 3
- long-term fit: 3

### Option 3 - External provider allowed, but with strict data minimization, no raw-text logging, scoped access, and explicit retention controls
- MVP fit: 5
- architecture fit: 5
- implementation simplicity: 4
- reversibility: 4
- dependency friendliness: 4
- operational simplicity: 4
- testability: 4
- long-term fit: 5

## Decision Stability
stable

## Recommendation
Choose Option 3. The MVP should allow external LLM providers, but only inside a tightly defined data-handling boundary.

## Score Interpretation
This option is the only realistic path that preserves both output quality ambitions and a credible privacy posture for a product that processes third-party book content.

## Why This Is the Simplest Viable Choice
It avoids the unrealistic operational burden of self-hosting while still treating book content as sensitive and limiting its spread across the system.

## Risks / Trade-offs
- Provider contract review becomes part of architecture selection.
- Debugging becomes harder when raw text is intentionally hidden from logs.
- Intermediate artifact retention needs explicit operational rules.

## Follow-up Implications
- Raw uploaded EPUBs and generated EPUBs live only in object storage and follow retention cleanup rules.
- Raw book text must not be logged in application logs, worker logs, traces, analytics, or error payloads.
- Provider payloads should include only the text and metadata needed for the current batch, not the full book.
- Raw provider responses should not be stored long-term; store normalized batch results or structured errors instead.
- Intermediate structured artifacts used for resumability should follow the same retention window as the job and be deleted with it.
- Signed URLs must be object-scoped, short-lived, and purpose-specific.
- Secrets must be managed outside the codebase and rotated without code changes.
- Provider choice should prefer configurations or contracts that disable training on customer data where available.
- Support and admin tooling should default to metadata-only views; any exceptional raw-content access should be time-bounded and audited.

## Should This Go Into DECISIONS.md?
- yes - record now

## Optional Follow-ups
- Define whether structured intermediate artifacts should be encrypted at rest separately from final uploads and outputs.
- Define the exact signed URL TTL policy for upload and download flows.

## Assumptions Made
- An external provider with acceptable contractual data controls is available for MVP.

## Recommended Next Step
Architect should define the exact data classes, storage locations, retention rules, and access controls for each class.

---

## Discovery Question
How should MVP control and observe per-job inference cost?

## Prior Decisions
None found in `docs/DECISIONS.md`.

## Context
The PRD already hints at internal processing limits, manual quota management, and a need to protect against unexpected LLM cost. For an LLM-backed SaaS, stack quality is not enough. The architecture must prevent jobs that are valid technically but uneconomic operationally.

## Options Considered
1. Rely mostly on source-word quota and rough file-size limits
2. Observe cost after the fact and tune manually
3. Use a layered cost architecture with estimation, hard caps, token accounting, prompt budgets, and bounded retry budgets

## Comparison

### Option 1 - Rely mostly on source-word quota and rough file-size limits
- pros:
  - simple to explain to users
  - aligned with the PRD quota model
  - easy to implement early
- cons:
  - source words are only an approximation of actual LLM cost
  - does not control retry amplification or explanation-pass inflation
  - weak visibility into unit economics per completed job
- dependency friendliness: strong
- implementation simplicity: high
- operational simplicity: medium
- value-to-complexity: medium
- reversibility: easy
- pipeline fit: requires adaptation
- MVP fit: weak
- long-term fit: weak

### Option 2 - Observe cost after the fact and tune manually
- pros:
  - very low upfront design cost
  - preserves maximum implementation freedom initially
  - useful as a supplementary analytics layer later
- cons:
  - too late to prevent uneconomic jobs
  - does not protect against prompt bloat or runaway retries
  - weak basis for future pricing and quota design
- dependency friendliness: strong
- implementation simplicity: high
- operational simplicity: low
- value-to-complexity: low
- reversibility: easy
- pipeline fit: requires adaptation
- MVP fit: weak
- long-term fit: weak

### Option 3 - Use a layered cost architecture with estimation, hard caps, token accounting, prompt budgets, and bounded retry budgets
- pros:
  - directly addresses the main unit-economics risk
  - supports both pre-run rejection and in-run stopping decisions
  - creates a clean path toward billing, pricing, and plan-based limits later
  - makes provider and prompt changes economically observable
- cons:
  - needs explicit accounting and threshold design
  - estimates will be imperfect early on
  - cost controls may reject some jobs users expect to be processable
- dependency friendliness: good
- implementation simplicity: medium
- operational simplicity: medium
- value-to-complexity: high
- reversibility: easy
- pipeline fit: fits cleanly
- MVP fit: strong
- long-term fit: strong

## Decision Quality Score
Scoring rule:
1 = poor
3 = acceptable
5 = strong
Scores support reasoning but do not determine the decision automatically.

### Option 1 - Rely mostly on source-word quota and rough file-size limits
- MVP fit: 2
- architecture fit: 3
- implementation simplicity: 5
- reversibility: 5
- dependency friendliness: 5
- operational simplicity: 3
- testability: 3
- long-term fit: 2

### Option 2 - Observe cost after the fact and tune manually
- MVP fit: 1
- architecture fit: 2
- implementation simplicity: 5
- reversibility: 5
- dependency friendliness: 5
- operational simplicity: 2
- testability: 3
- long-term fit: 2

### Option 3 - Use a layered cost architecture with estimation, hard caps, token accounting, prompt budgets, and bounded retry budgets
- MVP fit: 5
- architecture fit: 5
- implementation simplicity: 4
- reversibility: 5
- dependency friendliness: 4
- operational simplicity: 4
- testability: 4
- long-term fit: 5

## Decision Stability
stable

## Recommendation
Choose Option 3. The MVP should implement cost control as a dedicated architecture concern, not as an afterthought to quota management.

## Score Interpretation
This option wins because it is the only one that can keep unit economics visible and bounded while the product still depends on a variable-cost external model.

## Why This Is the Simplest Viable Choice
It adds just enough accounting and policy to stop obviously uneconomic jobs without forcing a full billing platform into MVP.

## Risks / Trade-offs
- Early cost estimates will need iteration.
- Hard caps can create support friction if users hit them unexpectedly.
- Prompt budget discipline must be maintained as prompts evolve.

## Follow-up Implications
- Estimate cost before queue admission using word count, mode, language pair, and expected pass count.
- Enforce hard caps at three layers: per job, per user quota period, and per retry budget.
- Record token usage and estimated provider cost for every translation batch and every run.
- Define prompt budget targets per mode so prompt growth is visible and reviewable.
- When cost thresholds are exceeded, fail safely with a clear policy error instead of silently continuing.
- Separate user quota accounting from actual inference-cost accounting; both matter and they are not the same.

## Should This Go Into DECISIONS.md?
- yes - record now

## Optional Follow-ups
- Decide whether Guided Mode should have a stricter default cost cap than Translate Mode.
- Define whether the UI should show only eligibility and estimate ranges or a more explicit cost forecast later.

## Assumptions Made
- The MVP needs cost observability even before formal billing exists.

## Recommended Next Step
Architect should define the cost-estimation formula, accounting fields, and cap-enforcement checkpoints.

---

## Discovery Question
How should MVP handle the operational reality of long-running asynchronous jobs?

## Prior Decisions
None found in `docs/DECISIONS.md`.

## Context
Async jobs that process whole books are not ordinary background tasks. They require explicit handling for concurrency, backpressure, stuck jobs, poison inputs, retry classification, cancellation, deploy safety, and reproducibility across runtime changes. Without these controls, even a good queue choice can still produce unreliable operations.

## Options Considered
1. Lightweight queue plus generic retries and minimal operations policy
2. Heavy workflow platform to absorb all operational complexity
3. Lightweight queue with an explicit job operations model: concurrency caps, backpressure, retry classes, dead-letter quarantine, cancellation semantics, and versioned runs

## Comparison

### Option 1 - Lightweight queue plus generic retries and minimal operations policy
- pros:
  - easy to start
  - low design overhead
  - may be enough for short and cheap jobs
- cons:
  - weak handling for poison jobs, duplicate retries, and stuck workers
  - poor operational clarity under provider throttling
  - reproducibility degrades when prompts or configs change mid-flight
- dependency friendliness: strong
- implementation simplicity: high
- operational simplicity: low
- value-to-complexity: low
- reversibility: medium
- pipeline fit: requires adaptation
- MVP fit: weak
- long-term fit: weak

### Option 2 - Heavy workflow platform to absorb all operational complexity
- pros:
  - rich workflow controls and recovery semantics
  - strong support for retries and orchestration history
  - may help if future workflows branch heavily
- cons:
  - too much platform complexity for MVP
  - pushes the team into workflow-engine adoption before core product risk is reduced
  - can obscure rather than simplify the first architecture
- dependency friendliness: medium
- implementation simplicity: low
- operational simplicity: medium
- value-to-complexity: medium
- reversibility: hard
- pipeline fit: fits cleanly
- MVP fit: weak
- long-term fit: acceptable

### Option 3 - Lightweight queue with an explicit job operations model: concurrency caps, backpressure, retry classes, dead-letter quarantine, cancellation semantics, and versioned runs
- pros:
  - keeps the queue simple while making operations explicit
  - supports the real failure modes of long LLM jobs
  - preserves reproducibility and safer deploys through run versioning
  - scales operationally without forcing a workflow platform early
- cons:
  - requires deliberate job-state and run-state design
  - some policy values will need tuning with production data
  - more operational modeling than a naive queue setup
- dependency friendliness: good
- implementation simplicity: medium
- operational simplicity: medium
- value-to-complexity: high
- reversibility: easy
- pipeline fit: fits cleanly
- MVP fit: strong
- long-term fit: strong

## Decision Quality Score
Scoring rule:
1 = poor
3 = acceptable
5 = strong
Scores support reasoning but do not determine the decision automatically.

### Option 1 - Lightweight queue plus generic retries and minimal operations policy
- MVP fit: 2
- architecture fit: 2
- implementation simplicity: 5
- reversibility: 4
- dependency friendliness: 5
- operational simplicity: 2
- testability: 2
- long-term fit: 2

### Option 2 - Heavy workflow platform to absorb all operational complexity
- MVP fit: 2
- architecture fit: 4
- implementation simplicity: 2
- reversibility: 2
- dependency friendliness: 3
- operational simplicity: 3
- testability: 4
- long-term fit: 4

### Option 3 - Lightweight queue with an explicit job operations model: concurrency caps, backpressure, retry classes, dead-letter quarantine, cancellation semantics, and versioned runs
- MVP fit: 5
- architecture fit: 5
- implementation simplicity: 4
- reversibility: 5
- dependency friendliness: 4
- operational simplicity: 4
- testability: 4
- long-term fit: 5

## Decision Stability
stable

## Recommendation
Choose Option 3. Keep the queue lightweight, but formalize operations behavior as part of the architecture rather than leaving it implicit in worker code.

## Score Interpretation
This option contains the real runtime risks of long-lived book jobs without overcommitting the product to a heavyweight workflow engine.

## Why This Is the Simplest Viable Choice
It keeps infrastructure modest while still defining the controls that actually decide whether long-running jobs are safe to operate.

## Risks / Trade-offs
- Operations policy now becomes part of architecture, not just implementation detail.
- Concurrency must be tuned against provider throughput, not only CPU.
- Cancellation may only be safe at batch boundaries, not mid-provider call.

## Follow-up Implications
- Concurrency should be limited by provider throughput budget and memory footprint, not just worker count.
- Add backpressure controls so new jobs stop entering translation when provider or worker budgets are saturated.
- Use failure classes such as transient provider, deterministic content, system, and policy failure.
- Poison jobs should move to a quarantine or dead-letter state rather than retry indefinitely.
- Stuck jobs need heartbeats, lease expiry, and explicit recovery rules.
- Cancellation should be best-effort and take effect at safe checkpoints.
- Every run should persist pipeline version, prompt version, provider config version, and worker code version markers where practical.
- Deploy and migration strategy should preserve in-flight compatibility or drain workers before incompatible changes.

## Should This Go Into DECISIONS.md?
- yes - record now

## Optional Follow-ups
- Define the maximum in-flight provider requests per worker and globally.
- Define a dedicated terminal state or reason code for poison jobs.

## Assumptions Made
- The MVP will still have enough concurrency and job duration for operational policy to matter before scale becomes large.

## Recommended Next Step
Architect should define the worker lease model, retry taxonomy, and run-versioning fields.

---

## Discovery Question
How should MVP observe pipeline execution, cost, and quality?

## Prior Decisions
None found in `docs/DECISIONS.md`.

## Context
LLM pipelines are hard to debug if the system only records coarse job states. Unfolda needs enough telemetry to answer practical questions such as:

- why a specific job is slow, stuck, or expensive
- which pipeline stage is failing or regressing
- whether provider latency or throttling is causing backlog
- whether a prompt or provider change degraded output quality
- whether throughput and retry behavior still match cost assumptions

The MVP does not need a full observability platform, but it does need structured telemetry that is durable enough for support, architecture review, and launch decisions.

## Options Considered
1. Minimal status-level visibility with logs only for failures
2. Full distributed-tracing and analytics platform from day one
3. Structured MVP telemetry with durable job timeline, stage and provider metrics, token and throughput metrics, and benchmark-based quality regression detection

## Comparison

### Option 1 - Minimal status-level visibility with logs only for failures
- pros:
  - lowest implementation effort
  - easy to start
  - little metrics design upfront
- cons:
  - weak debugging for long-running jobs
  - poor visibility into cost drivers and provider behavior
  - does not support quality regression detection in a disciplined way
- dependency friendliness: strong
- implementation simplicity: high
- operational simplicity: low
- value-to-complexity: low
- reversibility: easy
- pipeline fit: requires adaptation
- MVP fit: weak
- long-term fit: weak

### Option 2 - Full distributed-tracing and analytics platform from day one
- pros:
  - strongest possible observability surface
  - rich debugging and performance analysis
  - broad future flexibility
- cons:
  - overbuilt for MVP
  - instrumentation burden becomes too high too early
  - weak value if quality and product validation are not yet stable
- dependency friendliness: medium
- implementation simplicity: low
- operational simplicity: medium
- value-to-complexity: medium
- reversibility: medium
- pipeline fit: fits cleanly
- MVP fit: weak
- long-term fit: strong

### Option 3 - Structured MVP telemetry with durable job timeline, stage and provider metrics, token and throughput metrics, and benchmark-based quality regression detection
- pros:
  - gives enough signal to debug real pipeline problems
  - makes cost and performance visible at the same boundaries where control decisions happen
  - supports benchmark-gated quality validation instead of subjective spot checking
  - keeps telemetry architecture proportional to MVP scope
- cons:
  - requires explicit event and metric schemas
  - some telemetry fields will need iteration after the first real runs
  - quality checks still need careful dataset curation
- dependency friendliness: good
- implementation simplicity: medium
- operational simplicity: high
- value-to-complexity: high
- reversibility: easy
- pipeline fit: fits cleanly
- MVP fit: strong
- long-term fit: strong

## Decision Quality Score
Scoring rule:
1 = poor
3 = acceptable
5 = strong
Scores support reasoning but do not determine the decision automatically.

### Option 1 - Minimal status-level visibility with logs only for failures
- MVP fit: 1
- architecture fit: 2
- implementation simplicity: 5
- reversibility: 5
- dependency friendliness: 5
- operational simplicity: 2
- testability: 2
- long-term fit: 1

### Option 2 - Full distributed-tracing and analytics platform from day one
- MVP fit: 2
- architecture fit: 4
- implementation simplicity: 2
- reversibility: 3
- dependency friendliness: 3
- operational simplicity: 3
- testability: 4
- long-term fit: 5

### Option 3 - Structured MVP telemetry with durable job timeline, stage and provider metrics, token and throughput metrics, and benchmark-based quality regression detection
- MVP fit: 5
- architecture fit: 5
- implementation simplicity: 4
- reversibility: 5
- dependency friendliness: 4
- operational simplicity: 5
- testability: 5
- long-term fit: 5

## Decision Stability
stable

## Recommendation
Choose Option 3. The MVP should treat observability as a first-class architecture concern with two linked scopes:

- runtime telemetry for pipeline execution and cost
- benchmark telemetry for translation quality and regression detection

## Score Interpretation
This option wins because it gives the team the minimum telemetry needed to operate, debug, and improve an LLM pipeline without prematurely adopting a heavy observability stack.

## Why This Is the Simplest Viable Choice
It instruments the boundaries that already matter to the architecture: jobs, stages, provider calls, batches, costs, and benchmark runs.

## Risks / Trade-offs
- Telemetry design must avoid leaking raw book text.
- Metric cardinality needs care so the MVP does not create noisy or expensive telemetry.
- Quality automation will not replace human review; it should focus on regression detection and launch gating.

## Follow-up Implications
- Use structured logs with stable fields for `job_id`, `job_run_id`, `user_id`, `stage`, `batch_index`, `provider`, `error_class`, and version markers.
- Persist a per-job timeline so support and engineering can reconstruct the lifecycle of validation, queueing, processing, retries, completion, and cleanup.
- Record stage timings and batch throughput metrics for segmentation, translation, formatting, and export.
- Record provider latency, throttling, retry, and timeout metrics separately from application failures.
- Record token usage and estimated cost metrics at batch and run levels.
- Record error taxonomy metrics by provider, content, system, and policy failure classes.
- Record stuck-job detection metrics such as missing heartbeat age, lease expiry count, and quarantine count.
- Maintain an evaluation dataset that covers representative language pairs, modes, and book shapes for MVP.
- Add automated quality checks that produce comparable scores across benchmark runs.
- Add regression detection that compares the latest benchmark run with the current baseline before high-impact prompt, provider, or pipeline changes ship.

## Should This Go Into DECISIONS.md?
- yes - record now

## Optional Follow-ups
- Decide whether the first MVP transport for metrics is log-derived, direct database event records, or both.
- Define the minimum benchmark cadence: on provider changes, on prompt changes, and before release candidates.

## Assumptions Made
- The MVP can use a compact telemetry model without needing full distributed tracing immediately.

## Recommended Next Step
Architect should define the telemetry schema, the per-job timeline model, and the quality benchmark entity model.

## Recommended Telemetry Surface

The minimum telemetry surface for MVP should include:

- structured logs
- per-job timeline
- stage timings
- provider latency metrics
- token usage metrics
- error taxonomy metrics
- batch throughput metrics
- stuck job detection metrics

## Recommended Quality Validation Model

The minimum quality-validation model for MVP should include:

- `evaluation_dataset`: curated benchmark inputs representing target language pairs, modes, and content styles
- `quality_benchmark_run`: one benchmark execution against a specific pipeline version, prompt version, and provider configuration
- `quality_score`: normalized score records produced by automated checks for one benchmark run
- `quality_regression_alert`: emitted when the latest benchmark run falls below allowed deltas from the active baseline

The quality-validation workflow should be:

- run benchmarks on prompt changes, provider changes, and release candidates
- compute stable automated quality checks against the evaluation dataset
- compare new scores against the active baseline
- block or flag rollout when regressions exceed allowed thresholds

---

## Discovery Question
What should be the canonical system-of-record model for jobs, documents, pipeline artifacts, and resumability?

## Prior Decisions
None found in `docs/DECISIONS.md`.

## Context
The current document already recommends Postgres as the system of record and Redis as execution plumbing. That direction is correct, but not yet operationally complete. The architecture still needs a clear answer for:

- which entities are canonical
- where intermediate artifacts live
- what the resumable unit is
- where the idempotency boundary sits
- how pipeline and prompt versions are attached to runs
- how jobs, documents, artifacts, and batches relate to one another

## Options Considered
1. Runtime-centric model where the queue and worker memory carry most execution state
2. Relational model where all artifacts, including large intermediates, are stored directly in Postgres
3. Hybrid canonical model: Postgres for metadata and state, object storage for binaries and structured resumable artifacts, queue only for execution signaling

## Comparison

### Option 1 - Runtime-centric model where the queue and worker memory carry most execution state
- pros:
  - minimal schema upfront
  - easy to prototype
  - little storage design work early
- cons:
  - weak resumability
  - poor auditability and debugging
  - high risk of duplicate or corrupted state after worker failure
- dependency friendliness: strong
- implementation simplicity: high
- operational simplicity: low
- value-to-complexity: low
- reversibility: medium
- pipeline fit: conflicts
- MVP fit: weak
- long-term fit: weak

### Option 2 - Relational model where all artifacts, including large intermediates, are stored directly in Postgres
- pros:
  - one primary persistence technology
  - simple query surface for metadata and artifacts together
  - strong transactional semantics for small records
- cons:
  - poor fit for binary files and potentially large structured intermediate payloads
  - increases database bloat and migration risk
  - mixes metadata concerns with heavyweight artifact storage
- dependency friendliness: medium
- implementation simplicity: medium
- operational simplicity: medium
- value-to-complexity: medium
- reversibility: medium
- pipeline fit: requires adaptation
- MVP fit: acceptable but not ideal
- long-term fit: weak

### Option 3 - Hybrid canonical model: Postgres for metadata and state, object storage for binaries and structured resumable artifacts, queue only for execution signaling
- pros:
  - cleanly separates metadata, execution state, and heavyweight artifacts
  - supports resumability, idempotency, and retention cleanup
  - aligns with the PRD storage policy and async job model
  - keeps Redis non-canonical and replaceable
- cons:
  - requires disciplined key and state modeling
  - more than one persistence boundary must be kept consistent
  - artifact cleanup needs explicit lifecycle ownership
- dependency friendliness: good
- implementation simplicity: medium
- operational simplicity: medium
- value-to-complexity: high
- reversibility: easy
- pipeline fit: fits cleanly
- MVP fit: strong
- long-term fit: strong

## Decision Quality Score
Scoring rule:
1 = poor
3 = acceptable
5 = strong
Scores support reasoning but do not determine the decision automatically.

### Option 1 - Runtime-centric model where the queue and worker memory carry most execution state
- MVP fit: 1
- architecture fit: 1
- implementation simplicity: 5
- reversibility: 3
- dependency friendliness: 5
- operational simplicity: 2
- testability: 2
- long-term fit: 1

### Option 2 - Relational model where all artifacts, including large intermediates, are stored directly in Postgres
- MVP fit: 3
- architecture fit: 3
- implementation simplicity: 3
- reversibility: 3
- dependency friendliness: 3
- operational simplicity: 3
- testability: 4
- long-term fit: 2

### Option 3 - Hybrid canonical model: Postgres for metadata and state, object storage for binaries and structured resumable artifacts, queue only for execution signaling
- MVP fit: 5
- architecture fit: 5
- implementation simplicity: 4
- reversibility: 5
- dependency friendliness: 4
- operational simplicity: 4
- testability: 5
- long-term fit: 5

## Decision Stability
stable

## Recommendation
Choose Option 3. The MVP should adopt a hybrid canonical model with explicit ownership and lifecycle rules.

## Score Interpretation
This option provides the operational clarity missing from a queue-only model and avoids overloading Postgres with large transient artifact payloads.

## Why This Is the Simplest Viable Choice
It stores each class of data in the simplest appropriate place while keeping canonical truth in one durable metadata system.

## Risks / Trade-offs
- Artifact and metadata consistency rules must be documented clearly.
- Cleanup mistakes can produce orphaned objects.
- The resumable unit and idempotency key design must be precise.

## Follow-up Implications
- Treat `job` and `job_run` as separate concepts: the user-facing request and the concrete executable run.
- Treat the translation batch as the primary resumable unit, not the entire job and not individual provider calls.
- Treat the idempotency boundary as `job_run_id + batch_index + pipeline_version + input_hash`.
- Persist run metadata and state transitions in Postgres even when artifacts live in object storage.
- Store intermediate structured artifacts as versioned objects, not as implicit worker memory.
- Attach pipeline version, prompt version, and provider config version to every job run.

## Should This Go Into DECISIONS.md?
- yes - record now

## Optional Follow-ups
- Decide whether formatting-stage intermediates also need resumable artifacts or only translation batches do.
- Define whether a failed batch retains its last normalized error payload for support and debugging.

## Assumptions Made
- Translation batches are the dominant resumability boundary for MVP.

## Recommended Next Step
Architect should turn this into a concrete entity and artifact contract before any worker implementation begins.

## Recommended Canonical Model

The minimum canonical entity model for MVP should be:

- `user`: authenticated account and ownership root
- `user_quota_account`: manual quota allocation, remaining quota, and adjustment history
- `job`: user-submitted transformation request and user-visible lifecycle
- `job_run`: concrete execution attempt for a job, including pipeline version and runtime configuration
- `document`: normalized metadata about the uploaded book and detected language state
- `artifact`: metadata record for stored objects such as source upload, translated batch artifact, and generated EPUB
- `translation_batch`: canonical progress and resumability record for one batch within a run
- `job_event`: audit and support timeline of state changes, retries, admin actions, and policy events
- `cost_ledger_entry`: token usage and estimated provider cost at batch or run granularity

The recommended storage split is:

- Postgres: canonical metadata, ownership, states, quotas, events, batch records, cost records
- object storage: uploaded EPUB, generated EPUB, structured batch artifacts needed for resumability
- Redis: non-canonical execution signaling only
- worker memory: ephemeral processing state only

The recommended relational shape is:

- one `user` owns many `jobs`
- one `job` points to one input `artifact`
- one `job` may have many `job_runs`, but only one active run in MVP
- one `job_run` owns many `translation_batch` records
- one `translation_batch` may reference one or more intermediate `artifact` records
- one successful `job_run` produces one output `artifact`
- all major transitions emit `job_event` records
- all expensive provider activity emits `cost_ledger_entry` records

The recommended lifecycle semantics are:

- resumable unit: one translation batch
- idempotency boundary: one batch result for one run and one input hash under one pipeline version
- canonical progress boundary: completed translation batches and completed pipeline stages
- canonical retention owner: the job and its terminal-state retention policy
- canonical reproducibility markers: pipeline version, prompt version, provider config version, and model alias

---

## Updated Consolidated Recommendation

The MVP baseline should now be interpreted as a combined architecture and control model:

- `Next.js` for the user-facing web app
- `FastAPI` plus a Python worker for backend and pipeline execution
- `PostgreSQL` as the canonical metadata and state store
- `Redis` as lightweight non-canonical execution plumbing
- S3-compatible object storage for uploads, outputs, and resumable structured artifacts
- explicit pipeline modules matching `ingestion -> segmentation -> translation -> formatting -> export`
- paragraph-visible outputs with internal translation batches and chapter-scoped checkpoints
- job-scoped consistency memory rather than persistent cross-book memory
- single-provider LLM adapter with externalized prompts and config-driven model selection
- ingestion-level language detection with anomaly fallback and manual override
- durable progress and ETA persisted as job metadata
- strong logical per-user tenancy boundaries, audit events, quota gates, and abuse controls
- strict privacy boundaries: no raw-text logging, scoped provider payloads, short-lived artifacts, and controlled support access
- layered cost controls: pre-run estimation, hard caps, token accounting, prompt budgets, and retry budgets
- explicit operations policy: concurrency caps, backpressure, retry classes, stuck-job recovery, poison-job quarantine, safe cancellation, and versioned runs
- structured observability: logs, job timeline, timings, provider metrics, token metrics, throughput metrics, and stuck-job detection
- quality validation: evaluation dataset, automated checks, benchmark runs, and regression alerts
- hybrid canonical artifact model with batch-level resumability and explicit idempotency boundaries

## Updated Decision Recording Order

The following should now be recorded in `docs/DECISIONS.md` early because they define the real MVP operating model, not just the implementation stack:

1. application stack split: `Next.js` + `FastAPI` + Python worker
2. SaaS isolation model: ownership boundaries, quota gates, audit events, abuse controls
3. storage and privacy boundary: object storage strategy, retention, raw-text logging prohibition, provider data rules
4. cost-control architecture: estimation, caps, token accounting, retry budgets
5. observability and quality-validation model: telemetry schema, benchmark runs, regression detection
6. operations model: concurrency, backpressure, retry taxonomy, quarantine, versioned runs
7. canonical artifact model: `job`, `job_run`, `artifact`, `translation_batch`, and idempotency boundaries
8. long-book strategy: paragraph-visible batches with checkpoints
9. progress strategy: durable stage-weighted progress and ETA

The following can still be recorded after a short benchmark or architecture spike:

1. exact LLM provider choice
2. exact consistency-memory schema
3. exact anomaly strategy for language detection
4. exact quality benchmark thresholds for launch
