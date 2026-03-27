# Architecture Checklist

Use this checklist when reviewing any **non-trivial change**.

This checklist helps ensure that implementation remains aligned with:

- `docs/ARCHITECTURE.md`
- `docs/ARCHITECTURE_GUARDRAILS.md`
- `docs/DECISIONS.md`

It should be used primarily by:

- Architect
- Reviewer

Builder may also use it before finalizing a non-trivial implementation step.

---

# Quick Review Rule

If any checklist section raises a concern:

→ stop  
→ report the issue  
→ propose the smallest architectural correction  

Do not continue implementation while violating architectural constraints.

---

# When to Use This Checklist

This checklist must be used for any **non-trivial implementation or architectural change**, including:

- changes affecting pipeline stages
- changes affecting stage interfaces
- new dependencies
- modifications involving LLM usage
- changes affecting data flow or state
- changes touching multiple modules

Minor changes that affect only a small isolated function may skip this checklist.

If uncertain whether the change is trivial:

→ assume the checklist should be used.

---

# Checklist Usage Rule

Architect and Reviewer should explicitly confirm checklist usage when reviewing non-trivial changes.

Typical confirmation format:

> Architecture Checklist reviewed — no violations detected.

or

> Architecture Checklist reviewed — issue detected in section <X>.

This ensures the checklist is actively applied during implementation and review.

---

# 1. Pipeline Integrity

- Does the change preserve the pipeline structure?
- Are pipeline stages still conceptually distinct?
- Has any stage been bypassed or collapsed?
- Has a later stage been called directly without going through earlier required stages?
- Has any stage contract changed?

If any answer indicates pipeline drift, stop and escalate.

---

# 2. Stage Boundaries

- Are inputs and outputs for the affected stage still explicit?
- Are stage boundaries still clear?
- Has hidden coupling been introduced between stages?
- Has any stage begun depending on ambient runtime state?
- Are errors raised at stage boundaries rather than silently swallowed?
- Do error messages avoid leaking sensitive input content?

If stage boundaries are no longer explicit, the change is not acceptable.

---

# 3. Domain Logic vs Infrastructure

- Is domain logic still separate from I/O and infrastructure concerns?
- Has filesystem, network, model, or persistence logic leaked into domain modules?
- Are side effects still located at explicit boundaries?

If domain logic and infrastructure are mixed without strong justification, stop and escalate.

---

# 4. Module Design

- Are modules still focused and cohesive?
- Has the change introduced a mixed-responsibility file?
- Has duplicate logic been introduced?
- Has a new module been added unnecessarily?

Prefer extending existing modules over parallel implementations unless separation clearly improves maintainability.

---

# 5. Dependency Safety

- Were any new dependencies introduced?
- If yes, are they justified?
- Do they fit the project's architectural constraints?
- Do they create lock-in or broad project impact?
- Was a related architectural decision recorded if needed?

If a dependency significantly affects architecture, pipeline behavior, or LLM integration, it must be recorded in `docs/DECISIONS.md`.

---

# 6. State and Data Flow

- Is state still explicit and traceable?
- Has hidden global state been introduced?
- Has hidden caching been introduced?
- Are shared mutable objects crossing pipeline stages?

If state is implicit or cross-stage mutation exists, the change is architecturally unsafe.

---

# 7. Determinism

- Does the change preserve deterministic behavior where required?
- Has non-deterministic behavior appeared in any pipeline stage, validation, or orchestration?

If LLM logic is involved:

- are prompts externalized in `prompts/`
- are model settings controlled and configurable
- are retries explicit and bounded
- are outputs stable where determinism is required

If deterministic stages become non-deterministic without approval, stop and escalate.

---

# 8. External Dependencies and Services

- Has a new external API or cloud dependency been introduced?
- If yes, is it explicitly approved and isolated?
- Has experimentation been clearly separated from core behavior?

If new external dependencies are introduced without approval, the change must not proceed.

---

# 9. Prompt / LLM Architecture

- Are prompt templates stored in `prompts/`?
- Has prompt logic been embedded directly into implementation code?
- Are model names externalized through configuration or constants?
- Is retry/fallback behavior explicit and bounded?
- Has LLM-specific logic leaked into unrelated parts of the pipeline?

If prompt or model behavior changes affect pipeline correctness, the change may require a decision entry in `docs/DECISIONS.md`.

---

# 10. Architectural Drift Check

- Does the change silently alter the architectural direction?
- Has a temporary workaround become a de facto architectural decision?
- Has an abstraction been added without architectural approval?
- Has responsibility shifted across modules or stages without being documented?

If the implementation changes architecture implicitly, stop and escalate.

---

# 11. Test Coverage

- Does the change preserve independent testability of affected stages?
- Has existing test coverage been broken?
- Has new non-trivial logic been added without tests?
- Are new tests deterministic and free of external I/O?

If test coverage for affected stages has been reduced, the change is not acceptable without justification.

---

# 12. Documentation Check

- Does `docs/ARCHITECTURE.md` still describe the system correctly?
- Does `docs/ARCHITECTURE_GUARDRAILS.md` still match the intended constraints?
- Should this change be recorded in `docs/DECISIONS.md`?
- Should task or feature documentation be updated?

If architecture-relevant behavior changed, documentation must be updated before completion.

---

# 13. Final Review Decision

A non-trivial change should be approved only if:

- pipeline integrity is preserved
- stage contracts remain explicit
- no hidden coupling or hidden state was introduced
- dependencies remain justified
- deterministic behavior remains intact where required
- no unapproved external dependencies were introduced
- error handling is correct at stage boundaries
- test coverage for affected stages is preserved
- relevant architecture decisions are documented

If any of these fail, the correct action is:

- stop
- report the conflict
- propose the smallest acceptable architectural correction

Use the verdict defined in `agents/reviewer.md`:

- `APPROVED`
- `APPROVED WITH MINOR CHANGES`
- `CHANGES REQUIRED`