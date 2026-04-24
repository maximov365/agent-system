# Designer Mode: Handoff Spec

Use this mode when Designer is re-invoked **after** a design has been approved by the user, to produce a structured developer specification that UI Builder consumes alongside the mockups.

This mode does **not** create new mockups. It reads the previously approved design and translates it into precise specifications.

This mode exists to prevent interpretation drift between Designer and UI Builder on features with complex UI. It is **opt-in** — most features do not need it.

---

## When this mode runs

Iteration Manager (or the user) invokes this mode when **any** of the following is true:

- The feature has 3+ distinct screens or states
- The feature uses 5+ unique custom UI components
- Multiple breakpoints with non-trivial responsive behavior
- Animation or motion specifications need precise timing/easing
- Edge cases (empty/loading/error/long-text) materially change layout
- The user explicitly requests a structured handoff spec

Skip this mode for simple features (single screen, standard components, trivial responsive behavior). The standard Design output is sufficient — over-specification wastes time and creates maintenance burden.

---

## Process

1. Read the approved design artifact from the prior Designer invocation
2. Read `docs/BRAND.md` for design tokens (colors, typography, spacing)
3. Inventory every screen, component, state, and breakpoint in the design
4. For each, record exact specifications using design tokens (not raw values)
5. Document edge cases, responsive behavior, animation timing
6. Produce the handoff-spec document in the format below

---

## Specification principles

- **Reference tokens, not values.** Use `color-primary` not `#0066ff`. If the token doesn't exist in `BRAND.md`, propose adding it.
- **Specify all states.** Default, hover, active, disabled, loading, error, empty.
- **Describe the why for non-obvious choices.** "This collapses on mobile because users primarily use one-handed" helps UI Builder make consistent judgment calls on related decisions.
- **Don't over-specify obvious things.** Standard button hover (10% darken) doesn't need a paragraph.
- **Explicit edge cases.** Long text, empty states, slow connections, missing data — write them down.

---

## Optional skill augmentation

If the Claude skill `design:design-handoff` is available in the current environment, invoke it as a methodological reference and to augment the spec with additional structural patterns. Pass the approved design as the argument.

If the skill is not available (Cursor, API, or no plugin installed), use the built-in handoff-spec format below — it covers the same essential ground.

Skill availability is detected via the available-skills list in the conversation context. If unsure, do not invoke the skill — proceed with the built-in format.

The handoff-spec output structure is agent-defined; skill output is supplementary depth, never an output dependency.

---

## Output format

```text
## Handoff Spec — <feature name>

**Approved design:** <reference to original Designer artifact>
**Scope:** <what this spec covers>

### Layout & Grid
- Grid system: <columns, gutter, max-width>
- Breakpoints: <list with px values>
- Container behavior: <fluid / fixed / hybrid>

### Design Tokens Used

| Token | Value | Usage in this feature |
|---|---|---|
| `color-primary` | <hex> | Primary CTAs, active states |
| `spacing-md` | <X>px | Between sections |
| `font-heading-lg` | <size/weight/family> | Screen titles |

If a needed token does not exist in `BRAND.md`, list it under "Proposed Tokens" with a recommendation.

### Components

| Component | Variant | Props / Configuration | Notes |
|---|---|---|---|
| <component> | <variant> | <key props> | <special behavior> |

### States & Interactions

| Element | State | Visual change | Behavior |
|---|---|---|---|
| <element> | hover | <change> | <interaction> |
| <element> | loading | <change> | <interaction> |
| <element> | disabled | <change> | <interaction> |
| <element> | error | <change> | <interaction> |

### Responsive Behavior

| Breakpoint | Layout changes | Component changes |
|---|---|---|
| Desktop (>=1024px) | <default layout> | — |
| Tablet (768–1023px) | <what changes> | <what changes> |
| Mobile (<768px) | <what changes> | <what changes> |

### Edge Cases

| Case | Expected behavior |
|---|---|
| Empty state | <what to show when no data> |
| Loading | <skeleton / spinner / placeholder> |
| Error | <error state appearance + recovery action> |
| Long text | <truncation rules with character limits> |
| Slow network | <progressive disclosure / fallback> |

### Animation & Motion

| Element | Trigger | Animation | Duration | Easing |
|---|---|---|---|---|
| <element> | <trigger> | <description> | <ms> | <easing> |

### Accessibility Notes
- Focus order: <sequence>
- ARIA labels needed: <list>
- Keyboard interactions: <Tab / Enter / Esc / Arrow behavior>
- Touch target sizes: <min 44×44 verified>

### Proposed Tokens (if any)

| Token | Value | Reason needed |
|---|---|---|
| <new token> | <value> | <why this should be added to BRAND.md> |

### Implementation Notes for UI Builder
<any non-obvious implementation hints; references to existing components in the codebase if known>
```

---

## Handoff

Append a handoff block per `docs/AGENT_HANDOFF_CONTRACT.md` with `artifact_type: "design"` and `status: "produced"`. Set `next_recommended_agent` to `UI Builder`.
