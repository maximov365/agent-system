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
- Read `docs/LESSONS_LEARNED.md` and `docs/KNOWN_PATTERNS.md` before implementation (per `AGENTS.md`)
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

## Irreversible-action protocol (cross-agent rule)

For **irreversible operations**, documenting an assumption in the handoff is **not sufficient**. If the plan or instruction is ambiguous about an irreversible step, **STOP and ask the user before proceeding**. Documenting assumptions is acceptable only for additive or reversible operations.

Irreversible operations include (non-exhaustive — apply judgment liberally; when in doubt, treat as irreversible and ask):

- **Destructive file ops:** `rm -rf`, `git rm` of un-backed files, deleting non-gitignored generated artifacts
- **Git history rewrite:** `git push --force`, `git rebase` on shared branches, `git reset --hard` past pushed commits, remote branch deletion
- **External API mutations:** payment processor calls (Stripe charge/refund), notification sends (Twilio SMS, email), posts to social/messaging APIs, webhook fires to third parties
- **Database schema/data:** `DROP TABLE`/`DROP COLUMN`/`TRUNCATE`/`DELETE` without `WHERE`, migrations losing data on rollback, production DB writes outside the planned scope
- **Deployment & infrastructure:** production deploys, secret rotation, Terraform `destroy`, revoking API keys, cloud-resource deletion
- **Mass notifications:** email/SMS/push to >10 users
- **Cost-incurring:** spinning up paid infra, LLM/API calls with >$1 estimated cost, without explicit budget approval

When you encounter an irreversible step:

1. Halt before executing
2. Restate what you're about to do in plain language with concrete numbers ("I'm about to: DELETE the `users_archive_2023` table — 14,000 rows — per plan step 4")
3. Confirm intent: "Plan says X but I want to confirm: proceed, modify, or skip?"
4. Wait for explicit go-ahead — do NOT proceed on silence or non-answers
5. Document confirmation in the handoff: `"user_confirmed_irreversible": [<step>]`

Builder and UI Builder agents have agent-specific elaborations of this rule (see their `Irreversible-action protocol` sections).

This rule applies to **all coding agents** invoked via the framework. Defense-in-depth measure derived from MAST taxonomy Mode 2.1 (Communication Breakdown) — see `docs/MAST_MAPPING.md`.

**Note on harness-level git protection (Claude Code, June 2026+):** Recent Claude Code versions natively block destructive git commands (`git reset --hard`, `git checkout -- .`, `git clean -fd`, `git stash drop`, and `git commit --amend` on commits not made by the agent this session) when you did not explicitly ask to discard work. This is a second safety layer beneath this rule — but it only covers git. This framework rule remains the primary defense for the broader set (DB migrations, external API mutations, deployments, mass notifications, cost-incurring ops), and it applies in all environments including Cursor and direct API where the Claude Code harness is not present. Do not rely on the harness alone.

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

