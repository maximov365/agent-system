# Iteration Manager — Request Handling

## Request

"Нужно переписать весь pipeline на новую архитектуру"
(Need to rewrite the entire pipeline to a new architecture)

## Classification and Routing

```json
{
  "mode": "initial_routing",
  "request_type": "ambiguous",
  "selected_agent": null,
  "quality_loop_required": false,
  "analytics_required": false,
  "next_action": "escalate_to_user",
  "reason": "Request is ambiguous and large-scope: no specifics on which pipeline, what the target architecture is, or why the rewrite is needed. Additionally, a full pipeline rewrite would change pipeline boundaries, which is an escalation trigger per Iteration Manager rules.",
  "assumption": null,
  "escalation_reason": "Multiple escalation triggers: (1) request is ambiguous — does not specify which pipeline, what 'new architecture' means, or what problems the current architecture has; (2) implementation would change pipeline boundaries, requiring user decision; (3) contradicts key principle of preferring small changes; (4) repository context is insufficient to determine the correct next step.",
  "workflow_state": {
    "task_id": "new",
    "artifact_id": null,
    "current_stage": "discovery",
    "quality_loop_iteration": 0,
    "builder_cycle_count": 0,
    "analytics_used": false,
    "product_spec_accepted": false,
    "onboarding_phase": null
  }
}
```

## Escalation to User

I am escalating this request rather than routing it to an agent. The request needs clarification before any workflow can begin. Here is what I need from you:

1. **Which pipeline?** This project has a multi-agent workflow pipeline (Discovery -> Product -> Architect -> Builder -> Reviewer) and may have application-level data pipelines. Which one are you referring to?

2. **What is the "new architecture"?** Please describe the target state — what should the pipeline look like after the rewrite? Is there a reference, RFC, or design document?

3. **What problem does this solve?** What is wrong with the current architecture that motivates a full rewrite? Understanding the pain points will help determine whether a full rewrite is actually needed or whether targeted changes would be more appropriate.

4. **Scope boundaries.** A full pipeline rewrite is a large undertaking. Can we break this into smaller, independently deliverable tasks? The project principles strongly prefer small, verifiable changes over large rewrites.

5. **Constraints.** Are there backward compatibility requirements, migration needs, or deadlines that should inform the approach?

Once these questions are answered, I can route to the appropriate starting agent:
- If there is technical uncertainty about approaches -> **Discovery**
- If the scope needs to be defined as a feature spec -> **Product**
- If the target architecture is already clear and documented -> **Architect**

---

**Handoff block:**

```json
{
  "agent": "iteration-manager",
  "status": "escalated",
  "next_action": "escalate_to_user",
  "reason": "Ambiguous large-scope request requires user clarification before routing. Multiple escalation triggers: ambiguous request type, pipeline boundary changes, insufficient context.",
  "artifact_type": null,
  "artifact_id": null,
  "workflow_state": {
    "task_id": "new",
    "artifact_id": null,
    "current_stage": "discovery",
    "quality_loop_iteration": 0,
    "builder_cycle_count": 0,
    "analytics_used": false,
    "product_spec_accepted": false,
    "onboarding_phase": null
  }
}
```
