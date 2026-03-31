# Iteration Manager Mode: Standard Workflow

Load this mode for any non-onboarding implementation workflow — feature development, technical changes, refactoring, bug fixes.

---

## State initialisation

When a new feature request is detected (no existing `task_id` in `docs/TASKS.md`), initialise `workflow_state` as:

```json
{
  "task_id": "new",
  "artifact_id": null,
  "current_stage": "discovery",
  "quality_loop_iteration": 0,
  "builder_cycle_count": 0,
  "analytics_used": false,
  "product_spec_accepted": false
}
```

Use `"current_stage": "product"` instead if the request skips Discovery and goes directly to Product.

---

## Implementation workflow transitions

After each agent completes, determine the next step based on the agent's output and current workflow state.

| Previous agent | Result | Next action |
|---|---|---|
| `Discovery` | Recommendation produced | → `Product` (if feature scope needed) or → `Architect` (if task already exists) |
| `Product` | Feature spec produced | → Quality loop (invoke `Spec Reviewer`); load `im-modes/quality-loop.md` |
| `Product` → Quality loop | Gatekeeper `accept`; feature has user-facing UI | → `Designer` |
| `Product` → Quality loop | Gatekeeper `accept`; no UI; feature has measurable outcomes | → `Analytics Architect` |
| `Product` → Quality loop | Gatekeeper `accept`; no UI; no analytics needed | → `Architect` |
| `Designer` | Design approved by user | → `Analytics Architect` (if feature has measurable outcomes) or → `Architect` |
| `Analytics Architect` | Analytics spec produced; complex (multiple events or high risk) | → Quality loop (invoke `Spec Reviewer`); load `im-modes/quality-loop.md` |
| `Analytics Architect` | Analytics spec produced; simple | → `Architect` |
| `Analytics Architect` → Quality loop | Gatekeeper `accept` | → `Architect` |
| `Architect` | Implementation plan produced | → Quality loop (invoke `Spec Reviewer`); load `im-modes/quality-loop.md` |
| `Architect` → Quality loop | Gatekeeper `accept`; task has non-trivial testable logic | → `Test Strategist` |
| `Architect` → Quality loop | Gatekeeper `accept`; trivial change or no testable logic | → `Builder` |
| `Test Strategist` | Test plan produced | → `Builder` |
| `Builder` | Implementation complete; instrumentation changed | → `Analytics Validator` |
| `Builder` | Implementation complete; no instrumentation changes | → `Security Reviewer` |
| `Analytics Validator` | `accept` | → `Security Reviewer` |
| `Analytics Validator` | `revise` | → `Builder` (instrumentation fixes required) |
| `Analytics Validator` | `escalate` | → Escalate to user |
| `Security Reviewer` | `security_passed` | → `Reviewer` |
| `Security Reviewer` | `security_failed` | → `Builder` (security fixes required) |
| `Security Reviewer` | `escalate` | → Escalate to user |
| `Reviewer` | `APPROVED` or `APPROVED WITH MINOR CHANGES` | → Confirm workflow completion |
| `Reviewer` | `CHANGES REQUIRED` | → `Builder` (corrections required) |
| `System Auditor` | Audit report produced | → Present to user; user approves proposals → route to appropriate agents |
