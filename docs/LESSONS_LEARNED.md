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
