# Discovery Mode: Idea Intake (inference-first onboarding)

Use this mode when the user **provides an initial product idea** (free-form description, anywhere from one sentence to several paragraphs) instead of expecting to answer a structured questionnaire.

This mode is the **default** entry point for onboarding when the user's first message contains enough product context to infer most of the Discovery Brief. It replaces the 13-question structured intake with: parse idea → infer everything you can → ask only about genuine forks → present options with recommendations.

When the user's first message is too thin to infer from (e.g. "I want to build something with AI" with no further context), fall back to the structured 13-question intake in `agents/discovery.md` Onboarding intake mode section.

---

## Process

### 1. Parse the user's idea

Read the user's message line by line. Extract every signal you can about:

- **Product / what it does** — vertical, core capability, named function
- **Target users / market** — segments, geography, language, demographics
- **Differentiation** — explicit "X but with Y" or implicit positioning vs competitors
- **Tech approach** — explicit stack mentions or implicit constraints (mobile, WebView, serverless, edge)
- **Business model** — monetization hints, B2B vs B2C, free vs paid
- **Scope** — MVP-vs-future hints, "first" / "phase 0" / "starter" markers
- **Constraints** — solo founder, weeks-to-MVP, regulatory, geographic restrictions

Also extract from `project.config.yaml` if pre-filled (some users edit the config before invoking onboarding).

### 2. Build the inference summary

Present what you understood — short, scannable, structured. This lets the user catch misreadings immediately.

```
## What I understood from your idea

- **Product:** <inferred 1-line summary>
- **Vertical:** <category>
- **Target users:** <primary segment(s)>
- **Geography / language:** <regions, languages>
- **Differentiation:** <what makes it different>
- **Tech approach:** <implied stack or "not specified yet">
- **Business model:** <monetization hints or "not specified yet">
- **Scope hint:** <MVP vs full vision>
- **Constraints:** <hard limits inferred>

If anything above is wrong, tell me before answering the questions below.
```

### 3. Identify genuine forks

For every gap, classify:

- **Inferable from market norms?** → Don't ask. State the assumption with a "(default for [vertical])" tag in the Brief, user can override later.
- **Trivial / can be answered later?** → Don't ask in onboarding. Defer to first relevant feature spec.
- **Critical AND genuinely ambiguous?** → ASK with options.

A fork is genuinely ambiguous when **multiple equally-valid choices exist** and the choice **changes the product or roadmap meaningfully**. If one choice is obviously dominant, just default to it and tell the user.

### 4. Cap to 5–8 questions

If you found more than 8 ambiguous forks, prioritize by:

1. Forks that affect the entire product (data model, monetization model, target geography)
2. Forks that affect first 4 weeks of work
3. Forks where wrong choice is expensive to reverse

Defer the rest. Note them in the Brief under "Open Questions" so the user (or later agents) can address them as they come up.

### 5. Always present options with rationale

**Never ask open-ended questions in onboarding.** Even when the question feels open ("what colors do you want?"), reframe as multiple-choice with a recommendation:

```
### N. <Decision name>

- **A)** <Option name> — <one-line rationale, including trade-off>
- **B)** <Option name> — <one-line rationale>
- **C)** <Option name> — <one-line rationale>
- **Recommended: A** — <one sentence why this fits the user's idea>
```

Each option must be:

- **Concrete** — not "good design" but "calm minimalism with cool grays"
- **Differentiated** — A and B should produce visibly different products
- **Honest about trade-offs** — name the cost of each choice

Always include a recommendation. Users want guidance, not raw choice.

### 6. Make answering trivial

End with a one-line pick template:

> "Reply with picks like `1A 2C 3B 4A 5B`, or expand any with edits like `1A 2C-but-also-D 3B 4: actually, X 5B`."

Accept short-form picks (`1A 2C`), expanded picks (`1A — but I want to also do X`), and partial picks ("only the recommended ones for now"). Do not ask for confirmation on each — process the batch and proceed.

### 7. Produce the Discovery Brief

After the user answers, write the Discovery Brief using the same format as the standard intake mode (see `agents/discovery.md` "Intake output" section), but:

- Mark every field with one of: `inferred from idea`, `user-confirmed`, `default for vertical`, `open question`
- This makes provenance explicit so later agents (Product, Designer, Architect) know which fields are firm vs assumed

Example Brief field:

```
### Target Users
| Segment | Core need | Provenance |
|---|---|---|
| Belgrade rental seekers (international) | English-language listings, smart filtering | inferred from idea |
| Belgrade rental seekers (local) | Aggregated coverage across portals | inferred from idea |
| Long-term renters (3-12 months) | <added by user pick 2C> | user-confirmed |
```

### 8. Hand off

After producing the Brief, append a handoff block per `docs/AGENT_HANDOFF_CONTRACT.md` with:
- `artifact_type: "design_note"`
- `status: "produced"`
- `next_recommended_agent: "Product"` (in onboarding intake mode — Phase 2)
- `next_recommended_reason: "Discovery brief ready; Product can build PRD with most context already inferred"`

If `next_recommended_agent` is `Product`, **note that Product should also use the idea-intake-style inference**: read the Brief, infer most of the PRD, ask only the remaining forks. (Same applies to Designer and Architect downstream — see "Cascading inference" below.)

---

## Cascading inference (downstream agents)

The idea-intake principle propagates through the whole onboarding workflow. When Product, Designer, or Architect run after Discovery completed in idea-intake mode, they should:

1. **Read the Discovery Brief first** — most of their typical questions are already answered there
2. **Identify only the gaps that genuinely affect their domain** (e.g., Designer asks about brand only if Brief didn't lock visual direction)
3. **Apply the same options-with-rationale rule** when they do need to ask
4. **Cap themselves to 3–5 disambiguation questions** instead of the full 11-14 from structured intake

If a downstream agent finds the Brief insufficient (too thin, too many "open question" tags), it can fall back to its standard onboarding intake mode for its specific phase only.

---

## When NOT to use this mode

- The user's first message is short and lacks product context (e.g., "Help me start a project", "I want to use this framework") — fall back to the structured 13-question intake
- The user explicitly asks for the structured questionnaire ("just ask me the questions one by one")
- The project config already has substantial PRD content (this is post-onboarding, not onboarding)

---

## Output format (the user-facing turn)

```text
## What I understood from your idea

- **Product:** <one-line summary>
- **Vertical:** <category>
- **Target users:** <segments>
- **Geography / language:** <regions, languages>
- **Differentiation:** <what makes it different>
- **Tech approach:** <stack or "not specified">
- **Business model:** <monetization or "not specified">
- **Scope hint:** <MVP vs full vision>
- **Constraints:** <hard limits>

If anything above is wrong, tell me before answering the questions below.

---

## Decisions I need from you

These are genuine forks — multiple choices are reasonable and the answer changes the product. Everything else I'll infer or default. You can override defaults later.

### 1. <Decision>
- **A)** <Option> — <rationale>
- **B)** <Option> — <rationale>
- **C)** <Option> — <rationale>
- **Recommended: <X>** — <why>

### 2. <Decision>
... (up to 5–8 total)

---

Reply with picks like `1A 2C 3B 4A 5B`, or expand any with edits.
```

After receiving the user's picks, produce the Discovery Brief in the format defined in `agents/discovery.md` (Intake output section), with provenance tags as specified above.

Append a handoff block per `docs/AGENT_HANDOFF_CONTRACT.md`.
