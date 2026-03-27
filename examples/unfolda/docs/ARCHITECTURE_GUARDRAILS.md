# Architecture Guardrails

This document defines the architectural constraints that all agents must respect when working on **Unfolda**.

Its purpose is to prevent architecture drift, reduce accidental complexity, and keep the system aligned with the intended **pipeline-based, SaaS architecture**.

These rules complement `docs/ARCHITECTURE.md`.

If a proposed change conflicts with any guardrail in this document, the change must **not proceed** without explicit approval and updates to:

- `docs/ARCHITECTURE.md`
- `docs/DECISIONS.md`

---

# Rule Precedence

If guidance conflicts across project documents, use the following priority order:

1. `docs/ARCHITECTURE_GUARDRAILS.md`
2. `docs/ARCHITECTURE.md`
3. `docs/DECISIONS.md`
4. task-specific implementation plans
5. task descriptions

> Note: `AGENTS.md` and `.cursor/rules.md` define agent workflow rules, not architectural constraints, and are not part of this precedence order.

If a lower-priority artifact conflicts with a higher-priority rule, **stop and escalate**.

Agents must not override architecture constraints based on task descriptions alone.

---

# 1. Core Architecture Invariants

The system is built around a deterministic processing pipeline: `ingestion → segmentation → translation → formatting → export`

This pipeline is the backbone of the system.

The following invariants must always hold:

- pipeline stages must remain conceptually distinct
- each stage must have **explicit inputs and outputs**
- stage contracts must remain **stable and well-defined**
- stages must remain **independently testable**
- changes must not break existing test coverage for affected stages
- new stage behavior must remain independently testable
- domain logic must remain separate from infrastructure
- errors must be raised at stage boundaries, not silently swallowed
- error messages must not leak sensitive input content

No change should weaken these invariants without explicit architectural approval.

---

# 2. Pipeline Guardrails

The pipeline must not be bypassed or collapsed for convenience.

Allowed:

- adding helper functions within a stage
- refining stage interfaces
- improving deterministic behavior within a stage
- improving internal validation or data normalization

Not allowed without explicit approval:

- merging pipeline stages
- skipping a stage by directly calling a later stage
- introducing hidden cross-stage dependencies
- introducing side effects across stage boundaries
- adding a new pipeline stage
- changing a stage contract

Adding a new pipeline stage requires:

- explicit approval
- an update to `docs/ARCHITECTURE.md`
- a decision entry in `docs/DECISIONS.md`

---

# 3. Module Boundaries

Modules must remain **focused and cohesive**.

Prefer:

- small modules with clear responsibilities
- explicit interfaces between layers
- predictable data flow
- local reasoning within a module

Avoid:

- large mixed-responsibility files
- utility modules that accumulate unrelated logic
- implicit behavior across multiple modules
- parallel implementations of the same responsibility

Prefer extending existing modules over creating new ones, unless a new module clearly improves separation of concerns.

---

# 4. Domain Logic vs Side Effects

Domain logic should remain **as pure as practical**.

Pure domain logic includes:

- data transformations
- validation
- formatting
- deterministic computations
- data structure definitions

Side effects must remain at system boundaries, including:

- filesystem access
- model calls
- network access
- external service integration
- persistence
- runtime logging

Do not mix domain logic and infrastructure logic in the same module unless there is a strong justification.

---

# 5. Dependency Guardrails

Dependencies must remain **minimal and justified**.

Prefer:

- standard libraries
- existing project dependencies
- simple local implementations when practical

Do not introduce a new dependency unless it:

- significantly simplifies implementation
- reduces long-term maintenance risk
- improves reliability or correctness

Evaluate dependencies for:

- maintenance cost
- ecosystem stability
- lock-in risk
- reversibility

If a dependency affects architecture or pipeline behavior, record the decision in `docs/DECISIONS.md`.

---

# 6. State and Data Flow Rules

State must remain **explicit and traceable**.

Prefer:

- explicit inputs and outputs
- local state
- clearly defined configuration boundaries

Avoid:

- hidden global state
- implicit cross-module mutation
- hidden caching that alters behavior
- stage behavior depending on ambient runtime state
- shared mutable objects across pipeline stages

Any stateful behavior affecting pipeline correctness must be documented.

---

# 7. Determinism and Reproducibility

Unfolda should prefer **deterministic behavior wherever practical**.

This is especially important for:

- segmentation
- formatting
- export
- validation
- pipeline orchestration

For LLM-related components:

- deterministic or low-temperature settings should be used for non-creative stages
- prompt templates must live in `prompts/`
- model names must not be hardcoded in implementation logic
- prompt changes affecting pipeline behavior should be treated as architectural decisions
- retries or fallback logic must remain explicit and bounded

LLM-specific logic must not leak into unrelated pipeline stages.

---

# 8. Infrastructure Constraints

Unfolda is a **SaaS web service**.

The following infrastructure components are part of the approved architecture:

- web frontend
- API backend
- job queue for async background processing
- object storage for uploaded and generated EPUB files
- database for users, jobs, limits, and metadata
- LLM provider for translation and explanation generation

Infrastructure components must remain **isolated from domain logic**.

Pipeline stages must not depend directly on infrastructure concerns.

Side effects (storage writes, network calls, queue interactions) must remain at explicit boundaries.

External services must be introduced through explicit, well-defined integration points.

If a new external dependency is introduced, it must be recorded in `docs/DECISIONS.md`.

---

# 9. Change Approval Rules

The following changes require explicit approval before implementation:

- adding a pipeline stage
- changing pipeline stage order
- merging pipeline stages
- introducing a new architectural layer
- introducing a new external service or provider
- introducing a new core dependency
- introducing a new infrastructure component not listed in Rule 8
- changing prompt strategy affecting pipeline behavior
- modifying stage contracts

When approved, the change must be documented in:

- `docs/ARCHITECTURE.md`
- `docs/DECISIONS.md`

If a change requires escalation, follow Rule 13.

---

# 10. No Silent Architectural Drift

Agents must not silently change architectural direction during implementation.

Examples include:

- introducing abstraction layers not defined in the architecture
- shifting responsibilities across pipeline stages
- embedding infrastructure logic inside domain modules
- making temporary workarounds permanent
- introducing hidden architectural dependencies

If implementation pressure suggests architectural change:

→ stop and escalate instead of adapting the design silently.

---

# 11. Experimental Code

Experimental implementations are allowed only if they remain **clearly isolated and removable**.

Experimental code must not:

- become a hidden dependency of the main pipeline
- redefine architectural boundaries
- bypass documented constraints

If an experiment becomes permanent, it must be formalized in:

- `docs/ARCHITECTURE.md`
- `docs/DECISIONS.md`

---

# 12. Anti-Patterns

The following are considered architectural anti-patterns:

- skipping pipeline stages
- hidden cross-stage coupling
- hidden mutable global state
- mixing domain and infrastructure logic in large modules
- dependency-driven design instead of requirement-driven design
- speculative abstractions added prematurely
- duplicate implementations of the same responsibility
- non-deterministic behavior in deterministic stages
- silently swallowing exceptions at stage boundaries
- leaking sensitive input content in error messages
- embedding prompt templates directly inside implementation code
- introducing infrastructure dependencies inside domain modules

If a proposed solution relies on one of these patterns, escalate before implementation.

---

# 13. Escalation Rule

If a task cannot be completed without violating these guardrails:

- do not improvise around the problem
- do not silently weaken the architecture
- explicitly report the conflict
- propose the **smallest architectural change** required

Any approved architectural change must be documented in `docs/ARCHITECTURE.md` and `docs/DECISIONS.md`.