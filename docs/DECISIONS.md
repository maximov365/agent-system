# Decisions

<!-- Record significant technical decisions here. -->
<!-- Each decision should include: context, options considered, decision, and rationale. -->

| ID | Title | Status | Date |
|----|-------|--------|------|
| DEC-001 | Guided conversational onboarding for new projects | accepted | 2026-03-29 |
| DEC-002 | Single-source principle for workflow rules | accepted | 2026-03-29 |
| DEC-003 | Remove FEATURES.md and FEATURE_TEMPLATE.md from framework | accepted | 2026-03-29 |

---

## DEC-001 — Guided conversational onboarding for new projects

**Status:** accepted
**Date:** 2026-03-29

### Context

New project setup required users to manually write `project.config.yaml`, `docs/PRD.md`, `docs/ARCHITECTURE.md`, and other project-specific documents before agents could function. This created a high barrier to entry and meant the most critical documents were written without agent assistance.

### Options Considered

1. **Manual setup only** — user writes all docs by hand (status quo)
2. **Guided conversational onboarding** — agents ask structured questions and produce documents iteratively through quality loops
3. **Template wizard** — a CLI script that asks questions and generates files from templates

### Decision

Option 2 — Guided conversational onboarding.

### Rationale

- Leverages existing agents (Discovery, Product, Designer, Architect) and quality loops
- Documents benefit from the same iterative refinement as feature specs
- No new tooling required — works within the existing Cursor/Claude Code execution model
- Reduces barrier to entry dramatically: user only needs to answer questions
- Template wizard (option 3) would produce lower-quality one-shot output without the benefit of quality iteration

### Implications

- New `onboarding_phase` field added to `workflow_state`
- Each participating agent has an "onboarding intake mode" with structured questions
- `AGENTS.md` has a new Onboarding Workflow section
- `docs/ONBOARDING.md` updated with guided flow as the recommended approach
- Manual setup preserved as Scenario B for teams that prefer it

---

## DEC-002 — Single-source principle for workflow rules

**Status:** accepted
**Date:** 2026-03-29

### Context

Consistency audit revealed ~8,000 tokens of duplicated content across framework files. Agent Roles were described verbosely in `AGENTS.md` (~190 lines) and repeated in each agent file. Routing rules were duplicated between `AGENTS.md` and `agents/iteration-manager.md`. Coding rules in `agents/builder.md` duplicated `.cursor/rules.md`. Per-agent handoff examples in `AGENT_HANDOFF_CONTRACT.md` (~230 lines) repeated the same JSON structure 14 times.

### Options Considered

1. **Keep duplication for self-contained reading** — each file remains standalone but context window pressure grows
2. **Single-source with cross-references** — detailed definitions live in one place; other files reference them

### Decision

Option 2 — Single-source with cross-references.

### Rationale

- Reduces base prompt token count by ~45% for the four most-loaded files
- Eliminates inconsistency risk when rules change (update one place, not five)
- Agent role files remain authoritative for their own behavior; `AGENTS.md` provides the index
- `.cursor/rules.md` remains authoritative for coding rules; `agents/builder.md` references it

### Implications

- `AGENTS.md` Agent Roles section compressed from ~190 lines to a table + sequencing notes
- `AGENTS.md` Routing Rules section compressed from ~130 lines to a table + hard rules
- `AGENTS.md` Repository Structure replaced with a reference to `README.md`
- `AGENT_HANDOFF_CONTRACT.md` per-agent examples compressed from ~230 lines to a table + notes
- `AGENT_EXECUTION_MODEL.md` quality loop and analytics loop sections replaced with references
- `agents/builder.md` coding rules section replaced with a reference to `.cursor/rules.md`

---

## DEC-003 — Remove FEATURES.md and FEATURE_TEMPLATE.md from framework

**Status:** accepted
**Date:** 2026-03-29

### Context

Audit of the Voxema project (36 completed tasks, detailed PRD and FEATURE_MAP) revealed `docs/FEATURES.md` was never populated. Investigation showed no agent was wired to write to it: `agents/product.md` did not mention it, `agents/iteration-manager.md` did not route to it, `CLAUDE.md` did not include it in mandatory reads. An escalation rule in `docs/TASK_BACKLOG_AUTOMATION.md` referencing it was dead code.

### Options Considered

1. **Remove both files** — accept that PRD + FEATURE_MAP + TASKS covers the need
2. **Wire them up** — add explicit write instructions to Product agent and IM routing

### Decision

Option 1 — Remove both files from the framework.

### Rationale

- Three existing documents (PRD.md, FEATURE_MAP.md, TASKS.md) already cover feature definition, capability tracking, and task tracking
- Adding a middle layer increases maintenance overhead without clear benefit at current project scale
- The dead escalation rule was silently broken — removing the file makes the gap explicit rather than hidden
- FEATURE_TEMPLATE.md format guidance was inlined into `agents/product.md`

### Implications

- `docs/FEATURES.md` and `docs/FEATURE_TEMPLATE.md` deleted from framework, Voxema, and unfolda example
- Escalation rule in TASK_BACKLOG_AUTOMATION.md now references `docs/FEATURE_MAP.md` instead
- If a future project needs per-feature spec files, the concept can be reintroduced as an optional extension
