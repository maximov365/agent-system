# Known patterns

Durable approaches and architectural choices that **proved correct** in this project (after implementation, review, or production validation). This is not a duplicate of `docs/DECISIONS.md` — decisions record *what we chose*; patterns record *what kept working in practice*.

**Maintainer:** Iteration Manager appends new patterns when a completed workflow confirms an approach (often aligned with an entry in `docs/DECISIONS.md` or `docs/ARCHITECTURE.md`).

**Audience:** Every agent reads this file (with `LESSONS_LEARNED.md`) before starting work, per `AGENTS.md`.

---

## How to write a pattern

```markdown
## Pattern: <short name>

- **Context:** When to apply this.
- **Approach:** What to do (concrete).
- **Why it worked:** Evidence from reviews, metrics, or incidents avoided.
- **Related:** `docs/DECISIONS.md` / `docs/ARCHITECTURE.md` links or section names if applicable.
```

Avoid one-off bugfixes here — those belong in `LESSONS_LEARNED.md` unless they generalize to a reusable pattern.

---

## Patterns

*(Iteration Manager appends below this line.)*

## Pattern: Framework files must not collide with app-level filenames

- **Context:** When adding files to `sync.py` `FRAMEWORK_GLOBS` for distribution to downstream projects.
- **Approach:** Use unique prefixes or suffixes for framework-owned files that share common names with application files. Example: `requirements-framework.txt` instead of `requirements.txt`.
- **Why it worked:** `requirements.txt` collision broke production three times before the rename permanently fixed it.
- **Related:** `docs/LESSONS_LEARNED.md` entry 2026-03-29.

## Pattern: Agent intake mode for document generation

- **Context:** When a new project needs foundational documents (PRD, Architecture, Brand) and the agents can't operate normally because those documents don't exist yet.
- **Approach:** Add an "onboarding intake mode" to existing agents rather than creating new onboarding-specific agents. Each agent presents structured questions, waits for answers, and produces the document as its artifact. The document then goes through the standard quality loop.
- **Why it worked:** Reuses existing agent definitions, quality loops, and handoff contracts. No new infrastructure or agent types needed. Documents get the same iterative refinement as any other artifact.
- **Related:** `AGENTS.md` Onboarding Workflow section; `docs/DECISIONS.md` DEC-001.

## Pattern: Single-source with cross-references for workflow rules

- **Context:** When the same rule (agent roles, routing logic, coding policy, quality loop details) appears in multiple framework files.
- **Approach:** Keep the normative definition in one authoritative file. Other files use a compact summary (table or one-liner) with an explicit cross-reference. Authoritative sources: `AGENTS.md` for workflow rules, `.cursor/rules.md` for coding rules, `agents/iteration-manager.md` for detailed routing and transition tables, `docs/AGENT_HANDOFF_CONTRACT.md` for handoff format.
- **Why it worked:** Reduced token count by ~45% in the four heaviest files. Eliminated the class of bugs where a rule is updated in one file but not propagated to others (five such bugs found in the first audit).
- **Related:** `docs/DECISIONS.md` DEC-002.

## Pattern: Remove dead framework files rather than wiring them up

- **Context:** When an audit reveals a framework file that no agent reads, writes, or routes to, and existing documents already cover its intended purpose.
- **Approach:** Delete the file and all references. Inline any essential format guidance into the agent that would use it. Update escalation rules to reference the file that actually serves the function.
- **Why it worked:** `docs/FEATURES.md` was referenced in an escalation rule but never populated across 36+ completed tasks. Removing it (and redirecting the rule to `docs/FEATURE_MAP.md`) eliminated a false safety guarantee. Three existing docs (PRD, FEATURE_MAP, TASKS) already covered feature tracking.
- **Related:** `docs/DECISIONS.md` DEC-003.
