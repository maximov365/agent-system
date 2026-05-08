# Discovery Mode: Import (existing-artifact onboarding)

Use this mode when the user has **already done discovery, brand, or architecture work externally** and that work is referenced in `project.config.yaml` under `output_docs.custom_docs` (typically as PDFs, HTMLs, or Markdown briefs). The right onboarding flow here is to **import and refine**, not to ask the user to redo what they already produced.

This mode is selected by Iteration Manager when entering Phase 1 of onboarding and `output_docs.custom_docs` is non-empty (see `agents/im-modes/onboarding.md` Phase 1 mode selection table).

---

## When to use vs `idea-intake` vs structured

| Situation | Use mode |
|---|---|
| User pasted external Discovery Brief / Brand Discovery PDF / Architecture Discovery / etc., listed in `output_docs.custom_docs` | **import-mode** (this file) |
| User typed a fresh idea (or `project.description` has rich text) and no external artifacts exist | `idea-intake` |
| User has neither artifacts nor a clear idea | structured `Onboarding intake mode` (13 questions) |

Mode selection is the IM's responsibility, not Discovery's. If you (Discovery) were invoked in `import-mode` and find that the artifacts are actually empty / placeholders, fall back to checking `project.description` (idea-intake) or escalate to user.

---

## Process

### 1. Inventory the artifacts

Read `project.config.yaml` `output_docs.custom_docs` list. For each entry:

- Check the file exists (use Bash `ls` or Read tool)
- Note its format: `.pdf`, `.html`, `.md`, `.txt`, image, directory
- For directories (e.g., `docs/assets/brand/`), list contents — visual assets typically don't need parsing but should be referenced in BRAND.md

Show the user a brief inventory:

```
## Existing artifacts I found

- docs/Discovery_Brief.pdf — discovery output
- docs/Brand_Discovery.pdf — brand exploration
- docs/Naming_Reevaluation.pdf — naming work
- docs/Architecture_Discovery.pdf — architecture exploration
- docs/BRAND.html — rendered brand guide
- docs/assets/brand/ — visual assets directory

I'll extract content from these and synthesize a Discovery Brief. I'll only ask you about gaps the artifacts don't cover.
```

### 2. Extract content from each artifact

Use the Read tool to extract content:

- **PDFs:** Read tool supports PDFs. For PDFs > 10 pages, read in chunks via `pages` parameter (e.g., `pages: "1-10"`).
- **HTML:** Read as text, ignore styling.
- **Markdown:** Direct read.
- **Images:** Note they exist; reference in BRAND.md but don't try to OCR.
- **Directories:** Bash `ls` to list contents; reference paths in handoff.

For each artifact, extract the structured content relevant to its domain:

| Artifact type (by name pattern) | Extract → maps to |
|---|---|
| `Discovery_Brief.*` | Vision, problem, target users, competitive landscape, MVP scope, success criteria |
| `Brand_Discovery.*` or `BRAND.*` | Brand essence, tone, colors, typography, design principles, anti-patterns |
| `Architecture_Discovery.*` | Tech stack, pipeline stages, data flow, key components, integration boundaries |
| `Naming.*` or `Naming_Reevaluation.*` | Final product name, naming rationale, alternatives considered |
| `Marketing.*` or `GTM.*` | Channels, positioning, pricing strategy |
| Generic `*.pdf`, `*.md` | Best-effort extraction; classify by content |

### 3. Synthesize into Discovery Brief

Build the Brief in the same format as `agents/discovery.md` Onboarding intake mode "Intake output", but:

- Mark every field with provenance: `imported from <file>` for content lifted from artifacts; `inferred from imports` for derived synthesis; `gap — needs user input` for fields the artifacts don't cover.
- Where multiple artifacts disagree (e.g., Discovery_Brief says "MVP is X" but Architecture_Discovery assumes "MVP is Y"), surface the conflict explicitly: `imported with conflict — Discovery says X, Architecture says Y; needs user resolution`.

Example field with provenance:

```
### Target Users
| Segment | Core need | Provenance |
|---|---|---|
| Belgrade rental seekers (international) | English listings, smart filtering | imported from Discovery_Brief.pdf p.4 |
| Belgrade rental seekers (local) | Aggregated coverage | imported from Discovery_Brief.pdf p.4 |
| Long-term renters | Verified listings | gap — needs user input |
```

### 4. Identify gaps and conflicts

Two categories of items the user must address:

- **Gaps** — fields the artifacts don't cover that downstream phases need (e.g., explicit MVP timeline, monetization tier specifics)
- **Conflicts** — places where artifacts disagree

For each gap or conflict, present **options with rationale + recommendation**, exactly as in `idea-intake` mode. Cap at **5–8 total** (gaps + conflicts combined). Same format:

```
### N. <Gap or conflict description>

- **A)** <Option> — <one-line rationale>
- **B)** <Option> — <one-line rationale>
- **Recommended: A** — <why>
```

If there are zero gaps/conflicts, skip this step and proceed directly to producing the Brief — the user has done complete discovery work and just needs framework integration.

### 5. Show summary + ask only the disambiguation questions

```
## Discovery Brief — extracted from your existing artifacts

[full Brief with provenance tags]

## Gaps and conflicts I need you to resolve

[5–8 questions max, each with options + recommendation]

If everything looks right, reply with picks like `1A 2C 3B`. If something in
the imported content is wrong, point it out — I'll re-extract from the source.
```

### 6. Apply user picks

Update the Brief with user's decisions, changing provenance on those fields from `gap — needs user input` to `user-confirmed`.

### 7. Hand off

Append a handoff block per `docs/AGENT_HANDOFF_CONTRACT.md`:
- `artifact_type: "design_note"`
- `status: "produced"`
- `next_recommended_agent: "Product"` (Phase 2, applying cascading inference — Product reads the imported Brief and asks only about gaps that affect PRD specifically)
- `next_recommended_reason: "Brief produced from imported artifacts ([list]) + user disambiguation"`

---

## Cascading inference for downstream agents

When Product, Designer, or Architect run after Discovery completed in `import-mode`, they should:

1. **Read the Discovery Brief AND the original imported artifacts** (Designer reads `Brand_Discovery.pdf` directly; Architect reads `Architecture_Discovery.pdf` directly) — the Brief is a synthesis but the source artifacts may have details the Brief omitted
2. **Identify gaps specific to their phase** (Product asks PRD-specific gaps; Designer asks BRAND.md-specific gaps; Architect asks ARCHITECTURE.md-specific gaps)
3. **Apply options-with-rationale** when asking — same rule as idea-intake mode
4. **Cap at 3–5 disambiguation questions per phase**

When a downstream agent's domain is fully covered by an imported artifact (e.g., `BRAND.html` has every field BRAND.md would need), produce the framework doc by direct conversion from the artifact and ask zero disambiguation questions. Just confirm with user: "BRAND.md generated from BRAND.html — review and let me know if anything needs adjustment."

---

## Anti-patterns

- ❌ Asking the structured 13 questions when artifacts already cover them — ignores the user's prior work
- ❌ Importing artifacts but treating their content as "draft" requiring full review by the user — they already approved this work; only ask about gaps
- ❌ Failing to surface conflicts between artifacts — silently picking one source loses information
- ❌ Treating directories of assets (e.g., `docs/assets/brand/`) as if they need parsing — just reference them; the visual assets are the source of truth for designers, not framework docs

---

## Output format (the user-facing turn)

```text
## Existing artifacts I found

- <file 1> — <inferred role>
- <file 2> — <inferred role>
...

I'll extract content and synthesize a Discovery Brief. Reading now...

[Brief in standard format with provenance tags]

## Gaps and conflicts I need you to resolve

### 1. <gap or conflict>
- **A)** <option>
- **B)** <option>
- **Recommended: A** — <why>

[up to 5–8 total]

If everything looks right, reply with picks like `1A 2C 3B`. If something
imported is wrong, point it out and I'll re-extract from the source.
```

After receiving picks, produce the final Discovery Brief in the format defined in `agents/discovery.md`, with provenance tags, and append a handoff block per `docs/AGENT_HANDOFF_CONTRACT.md`.
