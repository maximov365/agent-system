# Task backlog and continuity

This contract governs task records in {{ project.name }}. Follow `AGENTS.md` for authority, authorization, rigor, and completion.

## Ownership and scope

The current task owner creates and updates `docs/TASKS.md`, including when performing Product, Builder, Reviewer, or Iteration Manager methods locally. Delegated specialists propose updates to the owner unless their assignment explicitly includes editing task state. Task ownership does not authorize a Git commit, push, external message, or deployment by itself.

Record work requested by the user, necessary implementation steps, and verified defects within accepted scope. Search existing tasks and plans before creating a duplicate; resume or link related work. Keep speculative ideas in proposals, not the active backlog. Split tasks when outcomes can be implemented and verified independently. Task counts and role transitions are not approval gates.

Ask only for a material unresolved scope/priority decision or an action without authorization. Routine dependency and implementation choices remain within the accepted task. Preserve explicit project constraints and explain an unresolved conflict with its source.

## Records

The summary table keeps task ID, title, status, priority, and complexity. For substantial work, link a plan containing objective, acceptance criteria, dependencies, affected areas, evidence, and remaining decisions. Use `docs/TASK_TEMPLATE.md` when a separate task document helps; do not create empty documents for a small fix.

Reuse the project's existing ID convention. Otherwise use `TASK-<number>`, with optional `FEAT`, `FIX`, or `ATASK` prefixes where useful. Assign unique IDs after checking the existing backlog. Feature/capability IDs and analytics artifacts are optional links, not required boilerplate for every task.

## State and completion

Use `planned → in_progress → completed` for ordinary work. Existing `implemented`, `in_review`, and `approved` states remain available when a real review handoff needs them. Passing through every intermediate label is unnecessary.

- Start work: mark in_progress with the current objective and next verification.
- Finish: acceptance criteria satisfied, relevant correctness/security and visual checks performed, evidence recorded, and material limitations disclosed.
- Self-review: the owner may complete the task after reviewing; identify it as self-review. Never invent another reviewer or mark failed acceptance as complete.
- Blocked dependency: record the exact missing input/capability and the independent work still possible. Do not equate elapsed time or an iteration counter with a blocking decision.
- Changed request: incorporate steering, preserving completed work and accepted constraints. Reopen completed work when a demonstrated regression needs repair.
- Cancellation: preserve history and record the user's cancellation, superseding request, duplicate, or obsolete task and reason. Ask if cancelling would abandon an outcome the user still expects.

## Resumption

A checkpoint records objective, completed work, evidence paths, remaining work, and decisions. Reconcile it with the latest user instructions and actual repository state. Handoff JSON and `.agent/workflows/` are optional transport/cache formats; neither outranks current instructions or observable artifacts.

Update the durable record at meaningful milestones and before handing off a substantial task. Append lessons only for reusable findings; do not turn routine success into mandatory memory entries.
