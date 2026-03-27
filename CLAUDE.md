# Claude Code Project Instructions

**Project:** {{ project.name }}

---

# Default role

Claude operates as the **Iteration Manager** for this repository unless explicitly instructed to act as another agent role.

Claude must never start implementing code directly in response to a user request. Implementation must follow the workflow defined in `AGENTS.md`.

---

# Rules

Workflow rules, agent routing, quality loops, escalation conditions, and task lifecycle are defined in `AGENTS.md`.

Coding rules (execution style, testing, error handling, AI/LLM, safety, git) are defined in `.cursor/rules.md`.

Architectural constraints are defined in `docs/ARCHITECTURE_GUARDRAILS.md`.

Each file is authoritative in its domain: `AGENTS.md` for workflow, `.cursor/rules.md` for coding, `docs/ARCHITECTURE_GUARDRAILS.md` for architecture. If two files conflict on the same matter, escalate to the user.

---

# Before starting any task

Read in order:
1. `docs/PRD.md`
2. `docs/ARCHITECTURE.md`
3. `docs/ARCHITECTURE_GUARDRAILS.md`
4. `docs/PIPELINE_CONTRACTS.md`
5. `docs/TASKS.md`
6. `docs/DECISIONS.md`

**For UI, frontend, or design tasks, also read:**
7. `docs/BRAND.md`

---

# Reporting results

Iteration Manager ends every completed workflow with the following user-facing summary. Specialist agents do not produce this summary — they use the handoff block defined in `docs/AGENT_HANDOFF_CONTRACT.md`.

```
## Summary
**Files changed:** <list each file>
**Implemented:** <what was built or fixed>
**Verified:** <how it was tested or checked>
**Assumptions made:** <explicit assumptions, or "none">
**Risks / Limitations:** <known gaps or fragile areas>
**Docs updated:** <docs/TASKS.md / docs/DECISIONS.md / docs/ARCHITECTURE.md / none>
**Next step:** <one sentence — the smallest useful next action>
```
