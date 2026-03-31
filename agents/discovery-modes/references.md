# Discovery Mode: Visual & UX References

Use this mode when the question is about **visual references, UI/UX benchmarks, or design inspiration** for a feature or product direction.

This mode feeds into the Designer agent — its output is used as design context.

---

## Additional responsibilities

- Search for 5–10 visual or UX references relevant to the question
- Include direct competitors AND analogous products from adjacent domains
- For each reference, capture: what the UI looks like, how the interaction works, what makes it effective
- Identify UI patterns (layout, navigation, onboarding, empty states, data display)
- Note accessibility and platform convention adherence
- Use web search tools to find current screenshots and product pages
- Prefer references the user can visit and evaluate themselves

---

## Output format

```text
## Discovery Question
<what visual or UX question is being explored>

## Context
<why this matters; what feature or screen this informs>

## References

### Reference 1 — <product name>
- Category: competitor / analogous product / design benchmark
- What it looks like: <layout, visual style, key UI elements>
- Interaction pattern: <how the user interacts; key flows>
- What works well: <specific UX strengths>
- What doesn't work: <friction, confusion, gaps>
- URL: <link to product or screenshot>

### Reference 2 — <product name>
- (same structure)

## UI/UX Patterns Identified
| Pattern | Used by | Recommendation |
|---|---|---|
| <pattern name> | <which references> | adopt / adapt / avoid |

## Visual Direction Recommendation
<suggested visual direction based on references; which patterns to combine>

## Assumptions Made
- ...

## Recommended Next Step
<one concrete action for Designer>
```
