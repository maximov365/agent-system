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

## Phase 1 mode selection — invitation-first, never jump to structured

**Cardinal rule: never start Phase 1 with the 13-question structured form.** The structured intake is a last-resort fallback that runs only after the user explicitly opts in. The default behavior is to invite the user to share any product context they have, no matter how thin.

### Decision logic (in priority order)

| Priority | Trigger | Action |
|---|---|---|
| 1 (highest) | `project.config.yaml` has `output_docs.custom_docs` listing existing artifacts (PDFs, HTMLs, MD briefs) | Run **`import-mode`** immediately. The user already did discovery work externally; don't ask anything yet — read the artifacts first. |
| 2 | **Either** user's first onboarding message **OR** `project.config.yaml` `project.description` contains substantial product context (≥ ~30 words describing what / for whom / where) | Run **`idea-intake`** immediately. Parse the rich context; produce the inference summary + 5–8 disambiguation picks. |
| 3 | First message AND config description are both thin (placeholder, "Start onboarding", "Help me set up a project") | Send the **invitation message** (template below). Wait for user response. **Do NOT start the 13-question form.** |
| Always wins | User explicitly types `structured`, `walk me through`, `ask me one by one`, "questionnaire", or names a mode | Honour the request. If they say "structured", run `Onboarding intake mode` in `agents/discovery.md`. If they say a different mode, run that. |

### Invitation message (used only when Priority 3 triggers)

When the user's first message is thin AND config is placeholder, **send this exact invitation as your first turn**, then wait:

```
I'd like to start with your idea, however rough.

You can give me:

- A one-line summary ("Aggregator for X", "Internal tool for Y team")
- A paragraph or several — anything you have written down
- A reference to an existing product ("Like Linear but for design teams")
- Bullet points of features you imagine
- A problem you want solved (without a solution yet)

Even one sentence is enough — I'll infer everything I can and ask you only
5–8 sharp questions about genuine forks, with options and a recommendation.

If you genuinely have nothing yet — no idea, no problem statement, no
reference — reply with `walk me through` and I'll switch to a structured
13-question questionnaire that builds context from scratch.

What do you have?
```

After the user responds:

- **They share an idea (any length, any form)** → re-evaluate Priority 2 with the new context. The user's response itself is now "first message with substantial product context" — almost always enough to trigger `idea-intake`. Run `idea-intake` mode.
- **They reply `walk me through` / `structured` / equivalent** → run `Onboarding intake mode` in `agents/discovery.md` (the 13-question form).
- **They reply something ambiguous** ("just start", "let's go", a brief phrase that's neither an idea nor a structured request) → ask once more with sharper framing: "Sorry, was that an idea or a request to walk through structured questions? If it's an idea, expand it just a bit."

### Always read the config first

Before deciding mode, **always read `project.config.yaml` in full**, including `output_docs.custom_docs` and `project.description`. The most common error: ignoring rich context the user populated via `init-downstream.sh` or hand-edited, then jumping to structured because the user's chat message was just "Start onboarding".

### Cascading inference downstream

After Discovery completes Phase 1 (in any of the three modes), Product, Designer, and Architect apply cascading inference per `agents/discovery-modes/idea-intake.md` "Cascading inference" section — read the Brief first, ask only about gaps in their domain, present options with rationale, cap at 3–5 picks per phase. The Brief is the input contract for downstream phases regardless of which Phase 1 mode produced it.

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
