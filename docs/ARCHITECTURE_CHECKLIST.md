# Architecture Checklist

Use this checklist when reviewing any **non-trivial change**. It verifies alignment with `docs/ARCHITECTURE_GUARDRAILS.md`, `docs/ARCHITECTURE.md`, and `docs/DECISIONS.md`.

Used primarily by Architect and Reviewer. Builder may also use it before finalizing a non-trivial step.

If any section raises a concern: **stop → report the issue → propose the smallest architectural correction.** Do not continue implementation while violating constraints.

---

## When to use

Any change affecting: pipeline stages, stage interfaces, new dependencies, LLM usage, data flow or state, multiple modules. Skip for small isolated fixes. When uncertain, use the checklist.

Confirm usage: `Architecture Checklist reviewed — no violations detected.` or `Architecture Checklist reviewed — issue detected in section <N>.`

---

## 1. Pipeline Integrity _(Guardrails Rule 1–2)_

- Does the change preserve the pipeline structure?
- Has any stage been bypassed, collapsed, or called out of order?
- Has any stage contract changed?

## 2. Stage Boundaries _(Guardrails Rule 2)_

- Are inputs/outputs for the affected stage still explicit?
- Has hidden coupling been introduced between stages?
- Are errors raised at boundaries (not silently swallowed)? Do error messages avoid leaking sensitive content?

## 3. Domain Logic vs Infrastructure _(Guardrails Rule 4)_

- Is domain logic still separate from I/O and infrastructure?
- Are side effects still at explicit boundaries?

## 4. Module Design _(Guardrails Rule 3)_

- Are modules still focused and cohesive?
- Has duplicate logic or a mixed-responsibility file been introduced?

## 5. Dependency Safety _(Guardrails Rule 5)_

- Were new dependencies introduced? If yes: justified, no lock-in, decision recorded?

## 6. State and Data Flow _(Guardrails Rule 6)_

- Is state still explicit and traceable?
- Has hidden global state, hidden caching, or cross-stage mutable objects been introduced?

## 7. Determinism _(Guardrails Rule 7)_

- Does the change preserve deterministic behavior where required?
- If LLM logic involved: prompts in `prompts/`, model names externalized, retries explicit and bounded?

## 8. External Dependencies _(Guardrails Rule 8)_

- Has a new external API or cloud dependency been introduced?
- If yes: explicitly approved and isolated?

## 9. Prompt / LLM Architecture _(Guardrails Rule 7, 9)_

- Are prompt templates in `prompts/`? Model names externalized?
- Has LLM-specific logic leaked into unrelated pipeline stages?

## 10. Architectural Drift _(Guardrails Rule 10)_

- Does the change silently alter architectural direction?
- Has a temporary workaround become a de facto decision?

## 11. Experimental Code _(Guardrails Rule 11)_

- Has experimental code been introduced? If yes: clearly isolated and removable?
- Has it become a hidden dependency or redefined boundaries?

## 12. Anti-Pattern Check _(Guardrails Rule 12)_

- Does the solution rely on a documented anti-pattern?
- Hidden cross-stage coupling? Speculative abstraction? Duplicate implementation?

## 13. Test Coverage

- Does the change preserve independent testability of affected stages?
- Has new non-trivial logic been added without tests?

## 14. Documentation

- Does `docs/ARCHITECTURE.md` still describe the system correctly?
- Should this change be recorded in `docs/DECISIONS.md`?

---

## Final Review Decision

Approve only if: pipeline integrity preserved, stage contracts explicit, no hidden coupling/state, dependencies justified, determinism intact, test coverage preserved, decisions documented.

If any fail: stop, report, propose the smallest correction.

Verdicts (per `agents/reviewer.md`): `APPROVED` | `APPROVED WITH MINOR CHANGES` | `CHANGES REQUIRED`