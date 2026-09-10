# Coding rules

Workflow and authorization are governed by `AGENTS.md`. These rules apply across Codex, Claude Code, Cursor, and API runtimes.

## Planning and implementation

- Read the affected source and relevant existing decisions before editing.
- Use the smallest approach that fulfills the task; preserve surrounding style and unrelated work.
- Plan non-trivial work around acceptance criteria, affected components, verification, dependencies, and risks. Small fixes need only a brief approach.
- Prefer existing modules and dependencies. Justify additions by concrete benefit; document significant architecture changes.
- File count is not an approval boundary. Keep each change coherent and reviewable.
- Search with `rg` when available; batch independent reads and run dependent mutations sequentially.
- Keep side effects at explicit boundaries; validate external inputs and make failures actionable without leaking secrets.
- Follow the project's actual architecture. Do not impose a processing pipeline on a UI, game loop, or service that has none.

## Verification

- Test meaningful behavior and negative cases, not a restatement of the implementation.
- Reproduce a bug before fixing it where feasible; use focused regression tests for non-trivial defects.
- Run relevant existing checks once the change is ready. Expand coverage only for new failures, changed risk, or unresolved concerns.
- Inspect the running UI for visual changes using `docs/VISUAL_QUALITY.md`; inspect timing and gameplay using `docs/GAME_DEVELOPMENT.md`.
- Report checks actually run and any blocked checks. A passing build is not evidence of visual fidelity or gameplay quality.
- Prefer deterministic fixtures; control clock, random seed, viewport, and motion for reproducible visual tests where appropriate.

## Model-backed code

Keep model selection and supported parameters in configuration. Preserve existing workload tiers and explicitly requested targets. Verify provider documentation when changing models or request schemas. Do not assume temperature support or deterministic LLM output. For Astra, follow `docs/MODEL_POLICY.md`; deterministic validation and structured contracts provide reliability.

## Permissions and git

Work within the current task's authorization and runtime sandbox. Prepare a concrete, reviewable result before asking for permission for an unauthorized external/destructive step. Existing approval is sufficient for that scope; silence is not approval. Reversible source edits (including UI component refactors) are ordinary implementation work.

Do not expose secrets or inspect credential stores without a task-relevant authorization. Do not send private content to an additional provider merely because its tool exists. Do not bypass sandbox denials or disable required checks.

Preserve the user's changes; do not reset or clean a workspace to simplify work. Prefer a feature branch/worktree for concurrent work when permitted. Do not commit, push, merge, deploy, send messages, or start persistent services unless requested or otherwise clearly authorized.

## Records

The task owner updates task state and significant decisions. Append reusable lessons only when something was learned; do not fill memory with routine success entries. Use English in code/docs/prompts and the user's language in conversation.
