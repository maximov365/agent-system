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
