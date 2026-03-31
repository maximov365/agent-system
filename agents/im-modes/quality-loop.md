# Iteration Manager Mode: Quality Loop

Load this mode **additionally** (alongside onboarding or standard-workflow) when a quality loop is active (`quality_loop_iteration > 0`) or when the current transition requires starting one.

---

## Quality loop transitions

| Previous agent | Result | Next action |
|---|---|---|
| `Spec Reviewer` | Review complete | → `Gatekeeper` |
| `Gatekeeper` | `iterate` | → `Reviser` |
| `Gatekeeper` | `accept` | → Resume parent workflow (see onboarding or standard-workflow transitions) |
| `Gatekeeper` | `escalate` | → Escalate to user |
| `Reviser` | Revision complete | → `Spec Reviewer` (next iteration) |

---

## When to start the quality loop

Start the quality loop (invoke `Spec Reviewer`) when:

- A new feature specification was produced by `Product`
- An implementation plan was produced by `Architect` and affects multiple modules
- Architectural risk is detected in an artifact
- Artifact clarity is insufficient for Builder to proceed without clarification

Applicable artifact types:

- feature specifications
- task breakdowns
- implementation plans
- design notes
- decision notes
- analytics specifications
- UX copy documents
- onboarding documents (PRD, Architecture, Brand — during the Onboarding Workflow)

Do not start the quality loop for:

- Code, tests, or configuration — those go through Builder → Security Reviewer → Reviewer (mandatory code review is separate)
- Trivial non-product changes (dependency upgrades, single-line fixes)
- Artifacts that have already been accepted by Gatekeeper in this workflow cycle

---

## Loop lifecycle

```
Spec Reviewer
      ↓
  Gatekeeper
      ↓ iterate
   Reviser
      ↓
Spec Reviewer (next iteration)
```

1. Invoke `Spec Reviewer` with the artifact and current iteration number (start at 1)
2. Pass `Spec Reviewer` JSON output to `Gatekeeper`
3. If Gatekeeper returns `iterate`: invoke `Reviser` with the artifact and Gatekeeper `notes_for_reviser`, then return to step 1 with incremented iteration
4. If Gatekeeper returns `accept`: exit loop and resume parent workflow
5. If Gatekeeper returns `escalate`: stop loop and escalate to user

---

## Loop termination conditions

- Maximum iterations: **3**
- Stop immediately if Gatekeeper returns `accept`
- Stop immediately if Gatekeeper returns `escalate`
- Do not restart the loop after Gatekeeper `accept`
- Do not trigger a new loop for the same artifact unless the artifact meaningfully changes. Meaningful change means structural modification of the artifact — new sections, major scope change, or significant updates to acceptance criteria. Wording improvements or minor clarifications do not qualify.
- If the artifact changes substantially (e.g. Product rewrote the spec), reset iteration counter to 1
