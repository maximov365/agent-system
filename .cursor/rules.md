# Cursor Project Rules

This file defines **coding rules** for implementation and review.

Workflow rules, agent routing, escalation, and quality loops are in `AGENTS.md`.
Architectural constraints are in `docs/ARCHITECTURE_GUARDRAILS.md`.
Conflict resolution rules are in the Precedence section of `AGENTS.md`.

---

## Planning rules

Prefer plans that can be executed independently by Builder without requiring additional clarification.

**When to write a plan:**
- Task touches more than 2 files, OR
- Estimated complexity exceeds a trivial change, OR
- Task involves a new pipeline stage or module

**When to proceed directly (no plan required):**
- Single file change, fewer than 5 lines, isolated fix
- Must be a non-product change with no user-facing behavior

**Plan format for non-trivial tasks:**
- Write a 5–9 step implementation plan
- Define acceptance criteria
- Define non-goals
- State dependencies and risks
- List files to create or modify
- Estimate complexity of each step (small / medium / large)
- Include analytics instrumentation steps if Analytics Architect was used
- Prefer plans where individual steps can be implemented and verified independently

---

## Execution rules

- Implement only the requested scope unless instructed otherwise
- Read `docs/LESSONS_LEARNED.md` and `docs/KNOWN_PATTERNS.md` before non-trivial implementation (see `AGENTS.md`)
- Read relevant files before modifying them
- Follow existing code style in the file being modified
- Do not auto-format unrelated lines
- Use the same naming conventions as surrounding code
- Prefer minimal, local, reviewable changes
- Prefer direct fixes over broad refactors
- Avoid premature abstractions and unnecessary generalization
- Prefer standard libraries before introducing new dependencies
- Avoid adding new dependencies unless they significantly simplify implementation
- Default to changes affecting fewer than 5 files; changes affecting 6–10 files require a brief justification; avoid changes beyond 10 files unless explicitly approved
- Prefer extending existing modules over creating new ones when appropriate
- Avoid renaming files or moving modules unless strictly necessary

After each meaningful change:
- Run the smallest relevant verification step (test, script, or manual check)
- Ensure the repository remains in a working state

---

## Architecture rules

{% if pipeline.stages %}
Respect the processing pipeline:

```
{{ pipeline.stages | map(attribute='name') | join(' → ') }}
```
{% endif %}

Design principles:
- Keep domain logic pure where practical
- Isolate side effects in adapters/services
- Keep modules focused and cohesive
- Avoid large mixed-responsibility files
- Prefer readability and maintainability over cleverness
- Each pipeline stage must be independently testable
- New pipeline stages require explicit approval and an update to `docs/ARCHITECTURE.md`
- Do not violate the constraints defined in `docs/ARCHITECTURE_GUARDRAILS.md`

---

## Testing rules

- Place tests in `tests/` (when present) mirroring the source structure
- Mock external I/O (filesystem, network, APIs) in unit tests
- Add focused tests for non-trivial logic when feasible
- Run the smallest relevant test during iteration
- Before finishing, run broader validation for touched areas
- Do not introduce new failures in touched scope
- Prefer deterministic tests over tests relying on AI outputs

---

## Error handling rules

- Raise specific exceptions, not generic ones
- Log errors at the boundary where they are caught, not deeper
- Never silently swallow exceptions
- Validate inputs at the entry point of each pipeline stage
- Use structured error messages that include context (stage name, input type, reason)

---

## AI / LLM rules

- Do not change prompt templates without explicit instruction
- If prompt templates exist, keep them in `prompts/` (when present)
- Never hardcode model names — use config constants
- Log token usage at debug level for cost visibility
- Do not add new models or providers without explicit approval
- Prefer deterministic or low-temperature settings for non-creative pipeline stages

---

## Safety rules

- Do not modify unrelated files
- Do not delete files unless explicitly required
- Do not introduce new external services or infrastructure components without explicit approval
- Do not commit secrets, tokens, or `.env` files
- Validate external inputs at system boundaries
- Avoid destructive filesystem operations unless explicitly required

---

## Git rules

- Do not auto-commit unless explicitly asked
- When suggesting a commit message, use Conventional Commits format:
  `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`
- One logical change per commit
- Do not stage unrelated files

---

## Language rules

- Code, documentation, prompts, and comments must be written in English
- Conversational responses should match the user's language

---

## Documentation rules

When completing a task:
- Propose status changes in the handoff block — only Iteration Manager updates `docs/TASKS.md`
- Update `docs/DECISIONS.md` if architecture or approach changed
- Before introducing a new architectural approach or dependency, check whether a related decision already exists in `docs/DECISIONS.md`

Task creation rules are defined in `docs/TASK_BACKLOG_AUTOMATION.md`.

