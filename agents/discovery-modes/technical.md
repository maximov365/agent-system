# Discovery Mode: Technical

Use this mode when the question is about **how to build** something: libraries, architectures, protocols, infrastructure choices, implementation approaches.

This is the default mode when no other mode clearly fits.

---

## Additional responsibilities

- Identify the most relevant technical options (2–4 candidates)
- Compare options using practical trade-offs
- Discard any option that clearly violates the architecture before comparing
- Only compare options that could realistically be implemented within the current architecture
- Consider deterministic behavior for pipeline stages
- Consider external dependency constraints

---

## Comparison criteria

For each option, evaluate:

- **Pros / cons**
- **Dependency friendliness:** does it add new deps? Are they well-maintained?
- **Implementation simplicity:** how much code and how complex?
- **Operational simplicity:** low / medium / high ongoing burden
- **Value-to-complexity ratio:** high / medium / low
- **Reversibility:** easy / hard / irreversible — how easy to replace later?
- **Pipeline fit:** fits cleanly / requires adaptation / conflicts
- **MVP fit:** good for first version?
- **Long-term fit:** good beyond MVP?

Limit options to 2–4 meaningful candidates. If one is clearly the simplest viable choice, say so directly.

---

## Decision quality score

For major decisions, score each option (1 = poor, 3 = acceptable, 5 = strong):

- MVP fit
- Architecture fit
- Implementation simplicity
- Reversibility
- Dependency friendliness
- Operational simplicity
- Testability
- Long-term fit

Scores support reasoning but do not determine the decision automatically. Architectural constraints override scoring — if an option violates the architecture, do not recommend it even if its score is higher.

---

## Output format

```text
## Discovery Question
<what decision or uncertainty is being explored>

## Prior Decisions
<any relevant prior decisions from docs/DECISIONS.md, or "none found">

## Context
<why this matters for the project>

## Options Considered
1. <option>
2. <option>
3. <option> (optional)

## Comparison

### Option 1 — <name>
- pros:
- cons:
- dependency friendliness:
- implementation simplicity:
- operational simplicity: low / medium / high
- value-to-complexity: high / medium / low
- reversibility: easy / hard / irreversible
- pipeline fit: fits cleanly / requires adaptation / conflicts
- MVP fit:
- long-term fit:

### Option 2 — <name>
- (same structure)

## Decision Quality Score (for major decisions)

### Option 1 — <name>
- MVP fit: 1–5
- architecture fit: 1–5
- implementation simplicity: 1–5
- reversibility: 1–5
- dependency friendliness: 1–5
- operational simplicity: 1–5
- testability: 1–5
- long-term fit: 1–5

### Option 2 — <name>
- (same structure)

## Decision Stability
temporary / stable / revisit after MVP

## Recommendation
<the recommended option and why>

## Why This Is the Simplest Viable Choice
<short explanation>

## Risks / Trade-offs
- ...

## Follow-up Implications
- ...

## Should This Go Into DECISIONS.md?
- yes — record now
- yes — record after implementation confirms the choice
- no

## Assumptions Made
- ...

## Recommended Next Step
<one concrete action for Product or Architect>
```
