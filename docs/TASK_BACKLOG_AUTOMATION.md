# Task Backlog Automation

This document defines the rules for automated task creation and backlog management in {{ project.name }}.

Agents may propose tasks. Only Iteration Manager may commit tasks to `docs/TASKS.md`. Tasks must not be created speculatively — the backlog grows only from accepted artifacts and verified workflow outcomes.

---

## Task creation authority

| Agent | May propose tasks | May commit to TASKS.md |
|---|---|---|
| Product | Yes — feature-level tasks and task breakdowns | No |
| Architect | Yes — implementation subtasks | No |
| Reviewer | Yes — non-blocking follow-up tasks only | No |
| Analytics Architect | Yes — instrumentation subtasks when instrumentation is explicitly separate work | No |
| Iteration Manager | No — receives and validates proposals only | **Yes — sole authority; commits only from valid proposals** |
| Builder | No | No |
| Spec Reviewer | No | No |
| Reviser | No | No |
| Gatekeeper | No | No |
| Analytics Validator | No | No |

**Commit rule:** Iteration Manager commits a proposed task to `docs/TASKS.md` only after:
1. Running deduplication checks (see below)
2. Confirming the task falls within an accepted feature scope
3. Confirming no escalation is required

If any check fails, Iteration Manager escalates to the user instead of committing.

---

## When tasks may be created automatically

Tasks may be proposed and committed only in the following four cases.

### Case A — Product spec accepted

When Gatekeeper accepts a Product feature specification:

- Iteration Manager may commit the feature-level task and associated task breakdown proposed by Product
- Maximum 6 implementation tasks per feature at this stage
- All tasks must be within the accepted feature scope — no expansion

### Case B — Architect decomposition

When Architect's implementation plan is accepted by Gatekeeper:

- Iteration Manager may commit implementation subtasks proposed by Architect
- Each subtask must map to a specific step in the approved plan
- Subtasks must not introduce new scope not present in the accepted feature specification

### Case C — Reviewer approved with minor changes

When Reviewer returns `APPROVED WITH MINOR CHANGES`:

- Iteration Manager may commit one follow-up task for the minor changes
- The follow-up task must be non-blocking (the current task is still approved)
- The follow-up task must not require a new Architect plan or new feature scope

### Case D — Analytics instrumentation is separate work

When Analytics Architect defines instrumentation that cannot be implemented within the current Builder step:

- Iteration Manager may commit one analytics subtask
- The subtask must reference the Analytics Specification as its source artifact
- The subtask must not expand the feature scope

---

## When tasks must NOT be created automatically

Iteration Manager must not commit a task if the proposal is:

- A stylistic or code quality suggestion without a functional impact
- A speculative improvement ("could be improved later", "might be useful")
- A change of scope beyond the accepted feature specification
- A conflict with `docs/PRD.md` or `docs/DECISIONS.md`
- A new feature or product direction requiring user approval
- A dependency on a new external provider, infrastructure component, or library not already approved
- A duplicate of an existing open or completed task (see Deduplication rules)

---

## Task schema

Every task committed to `docs/TASKS.md` must include the following fields. `docs/TASK_TEMPLATE.md` provides a long-form prose template for task proposals; the schema below defines the structured fields that Iteration Manager extracts when committing to the backlog. `docs/TASKS.md` uses a summary table; the full schema is the source of truth for required fields.

```
task_id:              <prefix>-<number>       # Assigned by Iteration Manager at commit time
title:                <short imperative title> # e.g. "Implement pipeline retry logic"
type:                 feature | implementation | analytics | fix | follow_up
status:               planned                  # Always starts as planned
priority:             high | medium | low
capability_id:        <capability ID from docs/FEATURE_MAP.md> | null  # e.g. "INGEST", "EXPORT"
parent_feature:       FEAT-<number> | null    # Feature this task belongs to
source_agent:         <agent name>            # Agent that proposed the task
source_artifact:      <artifact_id>           # Artifact that triggered the task
description:          <one paragraph>
acceptance_criteria:
  - <testable criterion>
  - ...
dependencies:
  - <task_id> | none
estimated_complexity: small | medium | large
```

All fields are required except `capability_id` and `parent_feature`, which may be `null` for standalone tasks. A task proposal missing any required field must be returned to the proposing agent before commitment.

`capability_id` links a task to a product capability defined in `docs/FEATURE_MAP.md` (see Capability Index). Valid values are the capability IDs listed there. This enables coverage tracking and prevents duplicate work on the same capability across different features.

---

## Task ID convention

Task IDs use the same prefixes as artifact IDs defined in `docs/AGENT_HANDOFF_CONTRACT.md`. A `FEAT-42` task ID and a `FEAT-42` artifact ID refer to the same feature — the task tracks the work, the artifact ID tracks the specification document. The only namespace split is for analytics: `AN-*` is reserved for specification artifacts, while `ATASK-*` is used for analytics implementation tasks.

| Task type | ID format | Example |
|---|---|---|
| Feature task | `FEAT-<number>` | `FEAT-42` |
| Implementation subtask | `TASK-<number>` | `TASK-42` |
| Analytics subtask | `ATASK-<number>` | `ATASK-42` |
| Fix or follow-up | `FIX-<number>` | `FIX-42` |

`ATASK` is used for analytics tasks (not `AN`) to avoid collision with analytics specification artifact IDs (`AN-42` in `AGENT_HANDOFF_CONTRACT.md`). `AN-<number>` always refers to an analytics specification; `ATASK-<number>` always refers to an analytics implementation task.

Numbers are assigned sequentially across all task types. Iteration Manager assigns the ID at commit time — agents propose tasks without IDs.

---

## Allowed status transitions

Task status follows a strict lifecycle. Not all agents may trigger every transition.

```
planned → in_progress → implemented → in_review → approved → completed
   ↓            ↓                                     ↓
cancelled    cancelled                          (with minor changes)
                                                  follow_up created
```

| Transition | Triggered by | Condition |
|---|---|---|
| `planned` → `in_progress` | Iteration Manager | Builder begins implementation |
| `in_progress` → `implemented` | Iteration Manager | Builder completes and handoff status is `produced` |
| `implemented` → `in_review` | Iteration Manager | Reviewer begins validation |
| `in_review` → `approved` | Iteration Manager | Reviewer handoff status is `approved` |
| `approved` → `completed` | Iteration Manager | All completion conditions are met (see `agents/iteration-manager.md`) |
| Any status → `in_progress` (correction) | Iteration Manager | Reviewer handoff status is `changes_required` |
| `planned` → `cancelled` | Iteration Manager (with user confirmation) | Task is obsolete, merged, or invalid |
| `in_progress` → `cancelled` | Iteration Manager (with user confirmation) | Task is abandoned mid-implementation |

**Rules:**
- Builder must not self-assign `approved` or `completed`
- Reviewer must not self-assign `completed`
- No status may be skipped in the forward direction
- Status may only regress to `in_progress` when Reviewer returns `changes_required`
- Tasks must not be deleted from `docs/TASKS.md` — use `cancelled` instead
- `cancelled` requires user confirmation before Iteration Manager commits the status change
- `approved` and `completed` tasks may not be cancelled without user confirmation and a documented reason

---

## Task explosion limits

The number of tasks per feature is bounded to prevent backlog inflation.

| Task type | Maximum per feature |
|---|---|
| Feature tasks (`FEAT`) | 1 |
| Implementation subtasks (`TASK`) | 8 |
| Analytics subtasks (`ATASK`) | 2 |
| Follow-up or fix tasks (`FIX`) | 2 |

If a proposed task would exceed any of these limits, Iteration Manager must escalate to the user rather than commit the task. The escalation must include the current task count for that feature and a summary of the proposed task.

Limits apply per `parent_feature`. Tasks with `parent_feature: null` are not subject to per-feature limits but must still pass all other validation rules.

---

## Deduplication rules

Before committing any proposed task, Iteration Manager must verify:

1. **No open duplicate** — `docs/TASKS.md` does not contain an open task with a semantically similar `title`, `description`, or `acceptance_criteria`. Two tasks are considered semantically similar if their core intent and scope overlap substantially even when phrasing differs — do not rely on exact string matching alone.
2. **Not a subtask of existing work** — the proposed task is not already covered by a step in an existing open implementation plan
3. **Not previously completed** — the task has not been completed and closed in a prior workflow cycle

If any check fails:
- Do not commit the task
- If the existing task is open: link the current work to the existing task instead
- If the task was completed: escalate to the user if the same work is being proposed again (potential scope regression)
- If the task is a subtask of existing work: flag it as redundant and discard

---

## Escalation rules for backlog changes

Iteration Manager must escalate to the user before committing when:

- The proposed task changes the priority of an existing open task
- The proposed task introduces a new major feature not present in `docs/FEATURES.md`
- The proposed task changes the order of planned roadmap items
- The proposed task introduces a scope boundary beyond the accepted feature specification
- The proposed task requires a new external dependency, provider, or infrastructure component
- The proposed task appears to conflict with `docs/PRD.md` or `docs/DECISIONS.md`

Escalation format: Iteration Manager produces a `stage_transition` output with `next_action: escalate_to_user` and a `blocking_issues` entry of type `scope_conflict` or `decision_conflict`.

---

## Integration with workflow state

When Iteration Manager commits a task to `docs/TASKS.md`, it must:

1. Assign the task ID and set `status: planned`
2. Update `workflow_state.task_id` to the new task ID in the next handoff
3. Update `workflow_state.artifact_id` to reference the source artifact
4. Update `workflow_state.current_stage` to `product` or `architecture` depending on the task type

When a task status transitions, Iteration Manager must update `docs/TASKS.md` immediately in the same execution cycle — not deferred to the next cycle.

---

## Relationship to other documents

| Document | Relationship |
|---|---|
| `docs/TASKS.md` | The backlog file this contract governs |
| `docs/FEATURE_MAP.md` | Source of truth for capability IDs used in `capability_id` field |
| `docs/FEATURES.md` | Feature tasks must have a corresponding entry here |
| `docs/AGENT_HANDOFF_CONTRACT.md` | Task ID conventions and `workflow_state.task_id` field |
| `agents/iteration-manager.md` | Workflow completion conditions and state lifecycle rules |
| `docs/AGENT_EXECUTION_MODEL.md` | Workflow persistence via `docs/TASKS.md` |
| `docs/TASK_TEMPLATE.md` | Template that all task proposals must follow |
| `docs/FEATURE_TEMPLATE.md` | Template that all feature proposals must follow |