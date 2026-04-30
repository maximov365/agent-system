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
  "workflow_mode": "standard",
  "quality_loop_iteration": 0,
  "builder_cycle_count": 0,
  "analytics_used": false,
  "product_spec_accepted": false
}
```

Use `"current_stage": "product"` instead if the request skips Discovery and goes directly to Product.

Iteration Manager must persist the initial state to `.agent/workflows/<task_id>.json` before invoking the selected specialist agent. If the request has no stable task ID yet, use `.agent/workflows/new.json` until a stable `task_id` is assigned.

Set `workflow_mode` during initial routing:

- `lite` for small, low-risk tasks where Architect can define an implementation-ready plan without Product or Discovery.
- `standard` for normal feature, bugfix, refactor, and configuration work.
- `strict` for high-risk work requiring maximal evidence, such as security boundaries, migrations, billing, customer data, production infrastructure, analytics correctness, or broad architectural change.

---

## Implementation workflow transitions

After each agent completes, determine the next step based on the agent's output and current workflow state.

| Previous agent | Result | Next action |
|---|---|---|
| `Discovery` | Recommendation produced | → `Product` (if feature scope needed) or → `Architect` (if task already exists) |
| `Product` | Feature spec produced | → Quality loop (invoke `Spec Reviewer`); load `im-modes/quality-loop.md` |
| `Product` → Quality loop | Gatekeeper `accept`; feature has user-facing UI | → `Designer` |
| `Product` → Quality loop | Gatekeeper `accept`; no UI but has user-facing text | → `UX Writer` (copy creation) |
| `Product` → Quality loop | Gatekeeper `accept`; no UI; no user-facing text; feature has measurable outcomes | → `Analytics Architect` |
| `Product` → Quality loop | Gatekeeper `accept`; no UI; no user-facing text; no analytics needed | → `Architect` |
| `Designer` | Design output includes visual briefs for illustration | → `Illustrator` (generate images; return to Designer for review) |
| `Designer` | Design output includes video briefs for generation | → `Video Producer` (generate videos; return to Designer for review) |
| `Designer` | Design approved by user; feature is complex (3+ screens / 5+ custom components / non-trivial responsive or motion) | → `Designer` (handoff-spec mode) |
| `Designer` | Design approved by user; feature has motion/animation | → `Animator` |
| `Designer` | Design approved by user; no animation; feature has user-facing text | → `UX Writer` (copy creation) |
| `Designer` | Design approved by user; no animation; no text copy needed | → `Analytics Architect` (if measurable outcomes) or → `Architect` |
| `Designer` (handoff-spec mode) | Handoff spec produced; feature has motion/animation | → `Animator` |
| `Designer` (handoff-spec mode) | Handoff spec produced; no animation; feature has user-facing text | → `UX Writer` (copy creation) |
| `Designer` (handoff-spec mode) | Handoff spec produced; no animation; no text copy needed | → `Analytics Architect` (if measurable outcomes) or → `Architect` |
| `Animator` | Animation spec approved by user; complex (3+ animations / critical perf / a11y-sensitive motion / tooling affects bundle) | → Quality loop (invoke `Spec Reviewer`); load `im-modes/quality-loop.md` |
| `Animator` → Quality loop | Gatekeeper `accept`; feature has user-facing text | → `UX Writer` (copy creation) |
| `Animator` → Quality loop | Gatekeeper `accept`; no text copy needed | → `Analytics Architect` (if measurable outcomes) or → `Architect` |
| `Animator` | Animation spec approved by user; simple; feature has user-facing text | → `UX Writer` (copy creation) |
| `Animator` | Animation spec approved by user; simple; no text copy needed | → `Analytics Architect` (if measurable outcomes) or → `Architect` |
| `Illustrator` | Images generated successfully | → Return to requesting agent (`Designer` or `Marketing`) for review |
| `Illustrator` | MCP tool unavailable or generation failed | → Escalate to user (suggest MCP setup or alternative approach) |
| `Video Producer` | Videos generated successfully | → Return to requesting agent (`Designer`, `Animator`, or `Marketing`) for review |
| `Video Producer` | Video tool unavailable or generation failed | → Escalate to user (suggest video tool setup or alternative approach) |
| `UX Writer` | Copy document produced; complex (multiple screens or high brand risk) | → Quality loop (invoke `Spec Reviewer`); load `im-modes/quality-loop.md` |
| `UX Writer` | Copy document produced; simple (single screen or low risk) | → `Analytics Architect` (if measurable outcomes) or → `Architect` |
| `UX Writer` → Quality loop | Gatekeeper `accept` | → `Analytics Architect` (if measurable outcomes) or → `Architect` |
| `Analytics Architect` | Analytics spec produced; complex (multiple events or high risk) | → Quality loop (invoke `Spec Reviewer`); load `im-modes/quality-loop.md` |
| `Analytics Architect` | Analytics spec produced; simple | → `Architect` |
| `Analytics Architect` → Quality loop | Gatekeeper `accept` | → `Architect` |
| `Architect` | Implementation plan produced | → Quality loop (invoke `Spec Reviewer`); load `im-modes/quality-loop.md` |
| `Architect` → Quality loop | Gatekeeper `accept`; task has non-trivial testable logic | → `Test Strategist` |
| `Architect` → Quality loop | Gatekeeper `accept`; trivial change or no testable logic; task has user-facing UI | → `UI Builder` |
| `Architect` → Quality loop | Gatekeeper `accept`; trivial change or no testable logic; no user-facing UI | → `Builder` |
| `Test Strategist` | Test plan produced; task has user-facing UI | → `UI Builder` |
| `Test Strategist` | Test plan produced; no user-facing UI | → `Builder` |
| `UI Builder` | Implementation complete | → `Design Reviewer` |
| `Design Reviewer` | `APPROVED` or `APPROVED WITH MINOR NOTES`; feature has user-facing strings | → `UX Writer` (copy review) |
| `Design Reviewer` | `APPROVED` or `APPROVED WITH MINOR NOTES`; no user-facing strings; instrumentation changed | → `Analytics Validator` |
| `Design Reviewer` | `APPROVED` or `APPROVED WITH MINOR NOTES`; no user-facing strings; no instrumentation changes | → `Security Reviewer` |
| `Design Reviewer` | `CHANGES REQUIRED` | → `UI Builder` (design fixes required) |
| `Builder` | Implementation complete; feature has user-facing strings | → `UX Writer` (copy review) |
| `Builder` | Implementation complete; no user-facing strings; instrumentation changed | → `Analytics Validator` |
| `Builder` | Implementation complete; no user-facing strings; no instrumentation changes | → `Security Reviewer` |
| `UX Writer` (copy review) | `approved` or `changes_suggested` (minor) | → `Analytics Validator` (if instrumentation changed) or → `Security Reviewer` |
| `UX Writer` (copy review) | `changes_suggested` (significant) | → `Builder` or `UI Builder` (copy fixes required; route to whichever built the feature) |
| `Analytics Validator` | `accept` | → `Security Reviewer` |
| `Analytics Validator` | `revise` | → `Builder` or `UI Builder` (instrumentation fixes required; route to whichever built the feature) |
| `Analytics Validator` | `escalate` | → Escalate to user |
| `Security Reviewer` | `security_passed` | → `Reviewer` |
| `Security Reviewer` | `security_failed` | → `Builder` or `UI Builder` (security fixes required; route to whichever built the feature) |
| `Security Reviewer` | `escalate` | → Escalate to user |
| `Reviewer` | `APPROVED` or `APPROVED WITH MINOR CHANGES` | → Confirm workflow completion |
| `Reviewer` | `CHANGES REQUIRED` | → `Builder` or `UI Builder` (corrections required; route to whichever built the feature) |
| `Marketing` | Strategy produced | → Quality loop (invoke `Spec Reviewer`) if complex; otherwise → present to user |
| `Marketing` | Campaign / launch kit produced | → `UX Writer` (tone review) if brand consistency needed; otherwise → present to user |
| `Marketing` → Quality loop | Gatekeeper `accept` | → Present to user; proceed to campaign creation if requested |
| `System Auditor` | Audit report produced | → Present to user; user approves proposals → route to appropriate agents |
