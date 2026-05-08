# Iteration Manager Mode: Onboarding Workflow

Load this mode when `workflow_state.task_id` is `"onboarding"` or the request is classified as `project_onboarding`.

---

## State initialisation

When a `project_onboarding` request is detected, initialise `workflow_state` as:

```json
{
  "task_id": "onboarding",
  "artifact_id": null,
  "current_stage": "discovery",
  "quality_loop_iteration": 0,
  "builder_cycle_count": 0,
  "analytics_used": false,
  "product_spec_accepted": false,
  "onboarding_phase": 1
}
```

`onboarding_phase` tracks progress: 1 (Discovery intake), 2 (Product intake), 3 (Designer intake), 4 (Architect intake), 5 (Assembly). Advance this value after each phase completes successfully.

---

## Phase 1 mode selection — structured intake vs idea-intake

When entering Phase 1, decide which Discovery intake mode to use:

| Trigger | Mode | Why |
|---|---|---|
| User's first onboarding message contains substantial product context (≥ ~30 words describing what to build, for whom, where) | `idea-intake` (default for new projects) | Inference-first onboarding — skips ~50 questions across phases by reading the idea and asking only about genuine forks with options |
| User's first message is short / lacks product context (e.g., "Help me set up a project", "I want to use this framework") | structured `Onboarding intake mode` in `agents/discovery.md` | The 13-question structured intake is the right tool when there's nothing to infer from |
| User explicitly asks for the structured questionnaire ("just ask me the questions one by one") | structured | Respect explicit preference |

After Discovery completes Phase 1, **Product, Designer, and Architect should also use cascading inference** (per `agents/discovery-modes/idea-intake.md` "Cascading inference" section) — read the Discovery Brief first, ask only about gaps that affect their domain, present options with rationale, cap at 3–5 disambiguation questions per phase.

If a downstream agent finds the Brief insufficient, it can fall back to its standard onboarding intake mode for its phase only.

## Onboarding transitions

| Previous agent | Phase | Result | Next action |
|---|---|---|---|
| `Discovery` (idea-intake or structured intake) | 1 | Discovery brief produced | → `Product` (onboarding intake mode, applying cascading inference); set `onboarding_phase: 2` |
| `Product` (intake) | 2 | PRD.md draft produced | → Quality loop (invoke `Spec Reviewer`); load `im-modes/quality-loop.md` |
| `Product` → Quality loop | 2 | Gatekeeper `accept` | → `Designer` (onboarding intake mode) if UI product, set `onboarding_phase: 3`; else → `Architect` (onboarding intake mode), set `onboarding_phase: 4` |
| `Designer` (intake) | 3 | BRAND.md draft produced | → Quality loop (invoke `Spec Reviewer`); load `im-modes/quality-loop.md` |
| `Designer` → Quality loop | 3 | Gatekeeper `accept` | → `Architect` (onboarding intake mode); set `onboarding_phase: 4` |
| `Architect` (intake) | 4 | Architecture docs drafts produced | → Quality loop (invoke `Spec Reviewer`); load `im-modes/quality-loop.md` |
| `Architect` → Quality loop | 4 | Gatekeeper `accept` | → Assembly phase; set `onboarding_phase: 5` |

---

## Assembly phase (phase 5)

When `onboarding_phase` reaches 5, Iteration Manager performs assembly:

1. Generate `project.config.yaml` from approved documents
2. Run `python setup.py` to re-render templates
3. Create any missing stub docs (`docs/TASKS.md`, `docs/DECISIONS.md`, `docs/LESSONS_LEARNED.md`, `docs/KNOWN_PATTERNS.md`, `docs/DEPLOY_CONTRACTS.md`)
4. Commit the initial project
5. Produce the closing summary defined in `CLAUDE.md`

After assembly, set `current_stage: "complete"` and `onboarding_phase: 5`.
