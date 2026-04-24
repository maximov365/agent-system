# Designer Mode: Onboarding Intake

Use this mode when invoked during the **Onboarding Workflow** (Phase 3). The goal is to produce `docs/BRAND.md` — the brand guide that all future UI work in this project will follow.

---

## Intake behavior

1. Read the approved `docs/PRD.md` from Phase 2
2. Read the Discovery Brief from Phase 1
3. Read `project.config.yaml` for any pre-filled brand context
4. Do **not** assume existing brand assets — this is a new project
5. Present the intake questions below to the user
6. After receiving answers, produce a complete `docs/BRAND.md`

---

## Intake questions

**Product personality:**
1. If the product were a person, how would you describe their personality? (e.g., "calm and professional", "energetic and playful", "technical and precise")
2. What 3–4 adjectives define the product's tone? (e.g., calm, clear, literate, honest)
3. Are there brands or products whose visual style you admire? (reference examples help)

**Visual identity:**
4. Do you have existing brand colors, or should I propose a palette?
5. Any color constraints? (e.g., "must feel professional, no bright neon")
6. Typography preference? (modern sans-serif, classic serif, monospace, system fonts)
7. Dark mode, light mode, or both?

**UI character:**
8. What are the key screens or views in the product? (from the PRD capabilities)
9. What UI metaphors feel right? (dashboard, timeline, chat, document, canvas)
10. Density preference: spacious and minimal, or compact and information-dense?
11. Any design anti-patterns to avoid? ("no dark patterns", "no gamification", "no modals")

---

## Output: `docs/BRAND.md`

Produce a complete `docs/BRAND.md`:

```text
# Brand Guide — <product name>

## Brand Essence
<one paragraph: what the brand stands for>

## Tone
- ...
- ...

## Design Principles
- ...
- ...

## Colors
| Name | Hex | Usage |
|---|---|---|
| Primary | #... | ... |
| Accent | #... | ... |
| Background | #... | ... |
| Error | #... | ... |

## Color Story
<why these colors; what they communicate>

## Typography
| Role | Family | Weight |
|---|---|---|
| Headings | ... | ... |
| Body | ... | ... |
| Code / mono | ... | ... |

## Spacing
- Base unit: ...
- Component padding: ...
- Page margin: ...

## Components
### Buttons
- Primary: ...
- Secondary: ...
- Destructive: ...

### States
- Active: ...
- Hover: ...
- Disabled: ...

## UI Patterns
- Key metaphor: ...
- Layout approach: ...
- Information density: ...

## Anti-patterns
- ...
```

---

## Handoff

Append a handoff block per `docs/AGENT_HANDOFF_CONTRACT.md` with `artifact_type: "design"` and `status: "produced"`. The document will go through the quality loop.
