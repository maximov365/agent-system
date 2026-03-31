# Lessons learned

Project-specific log of what went wrong in completed workflows, what review feedback repeated, and what worked. **Append-only** by default — do not delete history; Iteration Manager may add a short “superseded by” note if a lesson no longer applies.

**Maintainer:** Iteration Manager appends a new section after each workflow that reached completion (Reviewer approved) or was explicitly closed with a documented outcome.

**Audience:** Every agent reads this file (with `KNOWN_PATTERNS.md`) before starting work, per `AGENTS.md`.

---

## How to write an entry

Use one block per closed workflow. Keep it factual and short.

```markdown
## YYYY-MM-DD — <task id or short title>

**Workflow outcome:** completed | closed (other)

### What went wrong
- ...

### Repeated must_fix / review / security themes
- ... (quote or paraphrase recurring themes from Spec Reviewer, Reviewer, Security Reviewer)

### What worked well
- ... (optional; durable wins also belong in `KNOWN_PATTERNS.md`)

### Follow-ups
- ... (optional — links to `docs/TASKS.md` entries if any)
```

---

## Entries

*(Iteration Manager appends below this line.)*

## 2026-03-29 — requirements.txt collision breaks production

**Workflow outcome:** hotfix

### What went wrong
- `sync.py` included `requirements.txt` in `FRAMEWORK_GLOBS`, overwriting the application's own `requirements.txt` with the framework's 2-line file (`jinja2`, `pyyaml`)
- This caused production deployment failure for Unfolda (missing all app dependencies)
- The same issue had already been manually fixed **twice before** (commits `17869bd`, `35a2162`) without a permanent solution

### Repeated must_fix / review / security themes
- Framework files must never collide with common application filenames
- The audit process missed this because `requirements.txt` was treated as "just another framework file"

### What worked well
- The permanent fix (renaming to `requirements-framework.txt`) prevents recurrence
- Git history immediately showed the pattern of repeated fixes

### Follow-ups
- When adding any file to `FRAMEWORK_GLOBS`, verify the filename doesn't collide with common app conventions (`requirements.txt`, `Makefile`, `Dockerfile`, `.env`, etc.)

## 2026-03-29 — TASK-001 Guided conversational onboarding

**Workflow outcome:** completed

### What went wrong
- none — clean implementation

### Repeated must_fix / review / security themes
- none

### What worked well
- Reusing existing agent roles (Discovery, Product, Designer, Architect) in "intake mode" rather than creating new onboarding-specific agents
- Onboarding documents go through the same quality loops as feature specs, ensuring consistent quality
- Each agent's intake questions are self-contained — no complex cross-agent dependency during the conversation phase

### Follow-ups
- Consider adding a `--guided` flag to `sync.py` that automatically creates stub docs and prints onboarding instructions

## 2026-03-29 — TASK-002 Consistency audit and prompt optimization

**Workflow outcome:** completed

### What went wrong
- `onboarding_phase` was added to `AGENTS.md` and `agents/iteration-manager.md` but not to `docs/AGENT_HANDOFF_CONTRACT.md` workflow_state schema — agents had no guidance on how to include it in handoffs
- `design` and `test_plan` artifact types existed in the Allowed artifact types table but were missing from the handoff JSON template example — agents would use the template and omit valid types
- `Security Reviewer` `security_failed` was documented as incrementing `builder_cycle_count` in `iteration-manager.md` but the AGENT_HANDOFF_CONTRACT.md field update rules table only listed Reviewer — inconsistency between the two sources
- Feature status lifecycle used `done` in FEATURE_TEMPLATE while task lifecycle used `completed` — inconsistent terminal status names
- Quality loop was declared to apply to "analytics specifications" but no routing path existed for it

### Repeated must_fix / review / security themes
- Cross-file consistency breaks when a concept (artifact type, workflow state field, lifecycle status) is added to one file but not propagated to all files that reference it
- Terminology drift: "quality iteration loop" / "quality loop" / "iteration loop" appeared interchangeably

### What worked well
- Single-source compression reduced the four most-loaded files by ~735 lines (~45%) without losing any normative content
- Table format for Agent Roles and per-agent handoff requirements is more scannable and harder to drift

### Follow-ups
- none

## 2026-03-29 — TASK-003 Re-audit, FEATURES.md removal, checklist compression

**Workflow outcome:** completed

### What went wrong
- `onboarding_phase` was added to handoff template and IM init block but missed in the IM state fields table — the primary reference table that agents consult
- `builder_cycle_count` prose described only Reviewer CHANGES REQUIRED but the counter also covers Security Reviewer security_failed — misleading parenthetical
- Iteration Manager itself was missing from the per-agent handoff requirements table despite being required to append handoff blocks
- `docs/FEATURES.md` was a dead file: referenced in TASK_BACKLOG_AUTOMATION.md escalation rules and ONBOARDING.md, but no agent was instructed to write to it — the escalation rule was silently broken

### Repeated must_fix / review / security themes
- Same pattern as TASK-002: adding a concept to one file without propagating to all files that reference it
- Dead references create false safety: an escalation rule that references an empty file provides no protection

### What worked well
- Systematic re-audit caught 6 warnings that the first batch of fixes introduced or left behind
- ARCHITECTURE_CHECKLIST.md compression (252 → 97 lines) by referencing GUARDRAILS rule numbers instead of restating rationale

### Follow-ups
- ~~Run `sync.py` to propagate framework changes to Voxema and other downstream projects~~ Superseded by TASK-004: post-commit hook now auto-syncs downstream.

## 2026-03-29 — TASK-004 Auto-sync downstream projects on framework commit

**Workflow outcome:** completed

### What went wrong
- First `sync.py --all --render` test failed because `sys.executable` was system python (no pyyaml) — `run_check` and `run_setup` did not discover project venvs

### Repeated must_fix / review / security themes
- Tools that invoke subprocess with `sys.executable` must account for venv discovery when the calling python may differ from the project python

### What worked well
- `find_python` fallback chain (project venv → agent-system venv → sys.executable) resolved the dependency issue cleanly
- Plain-text `downstream.projects` format avoids adding yaml as a dependency to sync.py

### Follow-ups
- none
