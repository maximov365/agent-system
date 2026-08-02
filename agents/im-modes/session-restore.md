# Iteration Manager Mode: Session Restore & Local State Cache

Load this file when **resuming work after context loss** (new session, pruned history, crashed session, hand-off to a different machine) or when managing the optional per-task state cache for long multi-session work. Skip for normal in-session turns — the latest handoff JSON in context is sufficient there.

Closes MAST gap #1 (Mode 1.3 Loss of History) — see `docs/MAST_MAPPING.md`.

---

## Session-restore protocol

When resuming after context loss, Iteration Manager **must NOT restart the workflow from scratch**. Reconstruct state in this order:

1. **Read the latest handoff JSON** visible in the current conversation context. If at least one handoff is present, treat its `workflow_state` as authoritative for `current_stage`, `task_id`, `quality_loop_iteration`, `builder_cycle_count`, `analytics_used`, `product_spec_accepted`, `onboarding_phase`.
2. **Read `docs/TASKS.md`** for the task lifecycle — is the task `in_progress`, `awaiting_review`, `done`? Cross-check against the handoff state. Conflicts: handoff JSON wins for state, TASKS.md wins for "does the task exist".
3. **Check artifact files on disk** — does `docs/PRD.md` exist with substance? Does a `docs/plans/<TASK-ID>.md` plan exist? Does Builder's `artifact_path` from the latest handoff still point to real files? Use this to verify the workflow progressed past each stage.
4. **Read `.agent/workflows/<task_id>.json` if it exists** (optional local cache — below). Use as supplementary; do not treat as primary if it conflicts with handoff JSON.

After reconstruction, announce to the user: "Resuming from `<current_stage>` for task `<task_id>`. Latest handoff was from `<agent>` at `<timestamp if available>`. Next action: `<next_recommended_agent>`." Then proceed with the next transition per `agents/im-modes/standard-workflow.md` or `agents/im-modes/quality-loop.md`.

Do not restart the workflow unless: (a) no handoff JSON is visible AND no artifacts exist on disk — treat as fresh task; (b) the user explicitly says "start over"; (c) the task ID in handoff JSON doesn't match anything in `docs/TASKS.md` AND there's no clean way to align them — escalate to user.

---

## Optional local cache (`.agent/workflows/<task_id>.json`)

For long-running multi-session work, IM **may** maintain a per-task cache file at:

```text
.agent/workflows/<task_id>.json
```

This is a **local working cache**, not source of truth. It mirrors the latest `handoff.workflow_state` and lets IM resume mid-workflow without re-parsing transcript history when a session is interrupted.

Properties of the cache:

- Per-machine, per-user (gitignored — see `.gitignore`)
- Created on demand when IM sees value (long workflows, multi-session continuation); skipped for short single-session tasks
- Specialist agents must never read or write it
- Missing or stale cache → IM reconstructs state from handoff JSON + docs (the cache is rebuilt on next agent transition)
- Conflicts between cache and latest handoff → handoff wins; cache is updated
- When a task graduates from `task_id: "new"` to a stable identifier, rename `.agent/workflows/new.json` to the stable id; if no cache exists, no action is needed

For new projects, downstream syncs, and most short workflows, the cache is unnecessary. The handoff JSON + git-tracked docs are sufficient.
