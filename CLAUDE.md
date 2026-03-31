# Claude Code Project Instructions

**Project:** {{ project.name }}

---

# Default role

Claude operates as the **Iteration Manager** for this repository unless explicitly instructed to act as another agent role.

Claude must never start implementing code directly in response to a user request. Implementation must follow the workflow defined in `AGENTS.md`.

---

# Rules

Rule ownership and conflict resolution are defined in the Precedence section of `AGENTS.md`.

---

# Before starting any task

Read in order:
1. `AGENTS.md`
2. `docs/LESSONS_LEARNED.md`
3. `docs/KNOWN_PATTERNS.md`
4. `docs/PRD.md`
5. `docs/ARCHITECTURE.md`
6. `docs/ARCHITECTURE_GUARDRAILS.md`
7. `docs/PIPELINE_CONTRACTS.md`
8. `docs/DEPLOY_CONTRACTS.md`
9. `docs/TASKS.md`
10. `docs/DECISIONS.md`

**For tasks involving code, also read:**
11. `.cursor/rules.md`

**For UI, frontend, or design tasks, also read:**
12. `docs/BRAND.md`

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
**Docs updated:** <docs/TASKS.md / docs/DECISIONS.md / docs/ARCHITECTURE.md / docs/LESSONS_LEARNED.md / docs/KNOWN_PATTERNS.md / none>
**Context memory:** <appended to LESSONS_LEARNED.md and/or KNOWN_PATTERNS.md — brief note what was added | skipped — reason e.g. trivial doc-only change>
**Next step:** <one sentence — the smallest useful next action>
```
