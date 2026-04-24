---
description: Scan the AI landscape (papers, frameworks, benchmarks, Anthropic ecosystem) and propose concrete framework improvements
argument-hint: "[optional focus, e.g. \"agent orchestration\" or \"MCP servers\"]"
---

# /ai-landscape-review

Run an AI landscape review and produce a structured report with prioritized proposals for framework improvements.

This command does **not** implement changes. It only scans, evaluates, and reports. The user reviews findings in `docs/EVOLUTION_LOG.md` and decides what to adopt.

## What you must do

### 1. Resolve scope

- `AGENT_SYSTEM_ROOT` = `{{AGENT_SYSTEM_ROOT}}`
- `OPTIONAL_FOCUS` = `$ARGUMENTS` (if empty, do a general review)

If the current working directory is `AGENT_SYSTEM_ROOT`, scope is **framework** (review for the agent system itself).

If the current working directory is a downstream project (has `project.config.yaml` and is registered in `AGENT_SYSTEM_ROOT/downstream.projects`), scope is **project** (review for that project's domain).

If neither, ask the user which scope they want.

### 2. Load context

Read in this order:

- `AGENT_SYSTEM_ROOT/agents/discovery-modes/ai-landscape.md` — full methodology
- The relevant `docs/EVOLUTION_LOG.md` (framework root for framework scope, project root for project scope) — prior reviews to avoid re-proposing rejected items
- `AGENT_SYSTEM_ROOT/docs/CLAUDE_SKILLS.md` and `AGENT_SYSTEM_ROOT/docs/MCP_TOOLS.md` — what's already integrated
- `AGENT_SYSTEM_ROOT/docs/KNOWN_PATTERNS.md` — patterns we already know work
- `AGENT_SYSTEM_ROOT/docs/LESSONS_LEARNED.md` — anti-patterns

If `docs/EVOLUTION_LOG.md` does not exist, create it with header:

```markdown
# Evolution Log

Append-only log of AI landscape reviews and framework evolution decisions.

Each entry is produced by Discovery in `ai-landscape` mode (typically via `/ai-landscape-review`). The user reviews and decides which proposals to adopt; adopted items get linked here from the implementing commit.

---
```

### 3. Run the review

Act as Discovery agent in `ai-landscape` mode. Follow the methodology in `agents/discovery-modes/ai-landscape.md`:

1. **Scan** — make ~5–10 targeted web queries across the 6 tiers (Anthropic, agent frameworks, research, benchmarks, community, tools). If `OPTIONAL_FOCUS` is set, weight queries toward that area.
2. **Filter** — discard duplicates of existing capabilities and previously-rejected items. Aim for 5–15 high-signal findings.
3. **Map** — for each, identify which component would be affected and check backward-compatibility.
4. **Score** — rank by Impact × Confidence ÷ Effort.
5. **Propose** — write concrete actions for top findings.
6. **Log** — append the full report to `docs/EVOLUTION_LOG.md` using the format defined in `ai-landscape.md`.

### 4. Defer implementation

Do **not** modify any file other than `docs/EVOLUTION_LOG.md`. Do not commit. Do not start implementing proposals.

### 5. Report to user

After appending to `EVOLUTION_LOG.md`, print to the user:

- Path to the appended report
- Summary: count of findings by priority (high/medium/monitor)
- The single most important proposal (one sentence)
- Number of decisions awaiting user input

Then ask: **"Which findings should I deep-dive on or implement first?"** — wait for the user's response. Do not proceed to implementation without explicit instruction.

## Constraints

- **Time-box scanning to ~30 minutes / 10 web queries total** — this is a survey, not a deep audit
- **Never propose changes that break backward compatibility** without flagging them clearly
- **Never propose adopting something pre-alpha** without explicit "speculative / monitor only" tag
- **Never edit framework agent files** during this command — only `EVOLUTION_LOG.md`
- **Always cross-check against prior reviews** to avoid re-proposing rejected items
