Routing to Product agent -- this is a feature idea that needs scope definition before implementation.

```json
{
  "mode": "initial_routing",
  "request_type": "feature_idea",
  "selected_agent": "Product",
  "quality_loop_required": false,
  "analytics_required": false,
  "next_action": "invoke_product",
  "reason": "User requests task status change notifications (in_review) — this is a new feature idea with unclear scope that needs a Product spec before any implementation planning.",
  "assumption": "The user is referring to the task lifecycle defined in docs/TASKS.md (planned → in_progress → implemented → in_review → approved → completed), and wants an in-app or system-level notification when a task moves to in_review status.",
  "workflow_state": {
    "task_id": "new",
    "artifact_id": null,
    "current_stage": "product",
    "quality_loop_iteration": 0,
    "builder_cycle_count": 0,
    "analytics_used": false,
    "product_spec_accepted": false,
    "onboarding_phase": null
  }
}
```

```json
{
  "handoff": {
    "agent": "Iteration Manager",
    "artifact_type": "none",
    "artifact_path": null,
    "status": "completed",
    "next_recommended_agent": "Product",
    "next_recommended_reason": "Feature idea needs scope definition: what triggers the notification, who receives it, what channel (email, in-app, webhook), and what content it includes.",
    "blocking_issues": [],
    "workflow_state": {
      "task_id": "new",
      "artifact_id": null,
      "current_stage": "product",
      "quality_loop_iteration": 0,
      "builder_cycle_count": 0,
      "analytics_used": false,
      "product_spec_accepted": false,
      "onboarding_phase": null
    }
  }
}
```

**Next step:** Product agent will define the feature spec for task status notifications -- scoping the trigger condition (transition to `in_review`), notification channel (email, in-app push, webhook, etc.), recipient logic (task assignee, task creator, or both), and message content. The assumption is that this refers to the task lifecycle in `docs/TASKS.md`. If the user means something different by "task" or "in_review", please clarify before Product begins.
