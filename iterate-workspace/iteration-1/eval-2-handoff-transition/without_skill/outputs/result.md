# Iteration Manager: Handoff Processing

## Incoming Handoff Analysis

**Source agent:** Architect
**Artifact type:** implementation_plan
**Artifact path:** `docs/plans/ARCH-15.md`
**Status:** produced
**Recommended next:** Builder (reason: "Plan is straightforward, no complex testable logic")
**Task ID:** TASK-15
**Current stage:** architecture

---

## Validation Issues

The handoff block has two problems that prevent normal routing:

1. **Missing artifact file.** `docs/plans/ARCH-15.md` does not exist in the repository. The `docs/plans/` directory contains only `.gitkeep`. Per the handoff contract, `artifact_path` must not be `null` for `implementation_plan` and must point to a locatable output. The file is referenced but was never written.

2. **Unknown task ID.** `TASK-15` does not exist in `docs/TASKS.md`. The backlog ends at TASK-009. Either the task was not committed before Architect started, or the ID is incorrect.

---

## Routing Decision

Even if the artifact existed, the standard-workflow transition table requires:

> `Architect` | Implementation plan produced | -> Quality loop (invoke `Spec Reviewer`); load `im-modes/quality-loop.md`

Architect plans **always** enter the quality loop. The `next_recommended_agent: Builder` is a suggestion that Iteration Manager overrides per workflow rules. Builder would be invoked only after Gatekeeper accepts the plan.

However, because the artifact file is missing, routing cannot proceed at all.

---

## Stage Transition Output

```json
{
  "mode": "stage_transition",
  "previous_agent": "Architect",
  "previous_result": "produced",
  "current_stage": "Architect plan produced, but artifact file is missing — cannot route",
  "selected_agent": null,
  "quality_loop_active": false,
  "quality_loop_iteration": null,
  "next_action": "escalate_to_user",
  "analytics_required": false,
  "reason": "Artifact file docs/plans/ARCH-15.md does not exist; TASK-15 is not in docs/TASKS.md. Cannot route to Spec Reviewer without a reviewable artifact.",
  "escalation_reason": "Two blocking issues: (1) ARCH-15.md was not written to disk — the plan artifact is missing; (2) TASK-15 does not exist in the task backlog. Architect must re-run and produce the artifact file, or the user must provide the missing plan.",
  "workflow_state": {
    "task_id": "TASK-15",
    "artifact_id": "ARCH-15",
    "current_stage": "architecture",
    "quality_loop_iteration": 0,
    "builder_cycle_count": 0,
    "analytics_used": false,
    "product_spec_accepted": true,
    "onboarding_phase": null
  }
}
```

---

## What Needs to Happen

1. **Architect must produce the actual artifact file** at `docs/plans/ARCH-15.md`. The handoff claims it was produced, but the file does not exist.
2. **TASK-15 must be added to `docs/TASKS.md`** with proper fields (title, status, priority, complexity) before the workflow can proceed.
3. Once both issues are resolved, the correct next step is **Spec Reviewer** (quality loop for the implementation plan), not Builder. After Gatekeeper accepts the plan, Iteration Manager will route to Builder (since the Architect noted no complex testable logic, Test Strategist would be skipped).

---

```json
{
  "handoff": {
    "agent": "Iteration Manager",
    "artifact_type": "none",
    "artifact_path": null,
    "status": "escalate",
    "next_recommended_agent": null,
    "next_recommended_reason": "Artifact file and task entry are missing; Architect must re-run or user must provide the plan",
    "blocking_issues": [
      {
        "type": "missing_field",
        "source": "docs/plans/ARCH-15.md",
        "message": "Architect handoff references docs/plans/ARCH-15.md but the file does not exist in the repository"
      },
      {
        "type": "missing_field",
        "source": "docs/TASKS.md",
        "message": "TASK-15 is not present in the task backlog; task must be committed before workflow can proceed"
      }
    ],
    "workflow_state": {
      "task_id": "TASK-15",
      "artifact_id": "ARCH-15",
      "current_stage": "architecture",
      "quality_loop_iteration": 0,
      "builder_cycle_count": 0,
      "analytics_used": false,
      "product_spec_accepted": true,
      "onboarding_phase": null
    }
  }
}
```
