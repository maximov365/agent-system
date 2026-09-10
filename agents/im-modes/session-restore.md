# Restore task context

Use after context loss, interruption, or a real handoff. Preserve the user's original outcome and incorporate the latest steering. Follow `AGENTS.md` and `docs/AGENT_EXECUTION_MODEL.md`.

1. Read the latest user instructions and the concise durable task/plan checkpoint.
2. Inspect actual files, Git state, and evidence for the work being resumed. Reconcile claimed completion with observable results; do not rerun successful checks without a reason.
3. Use earlier handoff JSON or `.agent/workflows/<task_id>.json` as supplementary context. Stale state never wins over current instructions or verified repository state.
4. Record completed work, remaining work, and any unresolved dependency. Continue the next useful step; do not restart intake or ask the user to restate available context.

The current task owner may read/write optional workflow cache files. Delegated specialists use only the state their assignment needs and report changes to the owner. Cache files contain no credentials or private transcripts, remain disposable, and do not replace durable plans for substantial work.

If records conflict, inspect relevant artifacts and resolve routine drift. Ask only when an unresolved decision materially changes the expected outcome. A missing task ID or handoff JSON alone does not block recovery.
