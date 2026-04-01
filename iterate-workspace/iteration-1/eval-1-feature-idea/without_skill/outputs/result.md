# Iteration Manager — Initial Routing

## User Request

"Хочу добавить уведомления пользователям когда их задача переходит в статус in_review"

(Translation: "I want to add notifications to users when their task transitions to in_review status")

## Classification

This is a **rough feature idea** with unclear scope. The request describes a desired behavior (notifications on task status change) but lacks:

- Definition of "users" in this project's context (the project is a multi-agent development framework — it has no end-user accounts or notification infrastructure)
- Notification channel (email, in-app, push, CLI output, etc.)
- Whether this applies to the agent-system framework itself or to a downstream project
- Acceptance criteria
- Scope boundaries

**Assumption:** This feature is intended for a downstream application (not the agent-system framework itself), since the framework manages agent workflow tasks in `docs/TASKS.md` via Iteration Manager and has no user-facing notification system. If this is about framework-level task transitions, the scope would be very different (e.g., adding a hook to `TASK_BACKLOG_AUTOMATION.md`). Proceeding with the assumption that this needs Product agent to clarify scope and produce a feature specification.

## Routing Decision

```json
{
  "mode": "initial_routing",
  "request_type": "feature_idea",
  "selected_agent": "Product",
  "quality_loop_required": true,
  "analytics_required": true,
  "next_action": "invoke_product",
  "reason": "Rough feature idea with unclear scope — notifications on task status change needs Product to define users, channels, triggers, and acceptance criteria before any implementation planning.",
  "assumption": "Feature is intended for a downstream application, not the agent-system framework itself. If this is about framework-level task lifecycle hooks, the user should clarify.",
  "workflow_state": {
    "task_id": "new",
    "artifact_id": null,
    "current_stage": "product",
    "quality_loop_iteration": 0,
    "builder_cycle_count": 0,
    "analytics_used": false,
    "product_spec_accepted": false
  }
}
```

## Next Step

Invoke **Product** agent to turn this feature idea into a structured feature specification. Product will:

1. Clarify who the "users" are and how they are identified
2. Define the notification trigger (specifically: task status transition to `in_review`)
3. Define the notification channel(s) (email, in-app, push, webhook, etc.)
4. Determine whether other status transitions should also trigger notifications (scope boundary)
5. Write acceptance criteria
6. Produce a feature specification artifact for quality loop review

## Questions for the User (before invoking Product)

Before proceeding to Product, the following clarification would significantly improve routing efficiency:

1. **Which project is this for?** The agent-system framework itself, or a downstream project (e.g., Unfolda, Voxema)?
2. **What kind of notification?** Email, in-app notification, push notification, Slack/webhook, or CLI/terminal output?
3. **Who are the "users"?** Application end-users who own tasks, or developers/team members using the agent workflow?

If you would like to proceed without answering these questions, Product agent will make explicit assumptions and include them in the specification for your review.

---

**Handoff block:**

```json
{
  "from_agent": "Iteration Manager",
  "to_agent": "Product",
  "artifact_type": null,
  "artifact_id": null,
  "verdict": "routed",
  "workflow_state": {
    "task_id": "new",
    "artifact_id": null,
    "current_stage": "product",
    "quality_loop_iteration": 0,
    "builder_cycle_count": 0,
    "analytics_used": false,
    "product_spec_accepted": false,
    "onboarding_phase": null
  },
  "next_action": "invoke_product",
  "notes": "User request is a rough feature idea (notifications on task status change to in_review). Needs Product to define scope, users, channels, and acceptance criteria. Analytics likely required — notification delivery is a measurable outcome."
}
```
