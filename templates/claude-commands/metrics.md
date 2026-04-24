---
description: Compute and display framework metrics (Phase 1 — portfolio, knowledge, velocity, AI landscape activity)
argument-hint: "[history N]"
---

# /metrics

Run the framework metrics snapshot and display key indicators. Optionally show recent history.

## What you must do

### 1. Resolve

- `AGENT_SYSTEM_ROOT` = `{{AGENT_SYSTEM_ROOT}}`
- `ARGS` = `$ARGUMENTS` (free-form; supports `history N` to view last N snapshots)

### 2. Verify location

If the current working directory is **not** `AGENT_SYSTEM_ROOT`, this command should still work — it operates on the framework repo specifically. Just be explicit in the report that metrics describe the framework, not the user's current project.

### 3. Run the appropriate command

**Default — fresh snapshot + append to history:**

```bash
cd {{AGENT_SYSTEM_ROOT}}
python3 metrics.py --append
```

**If user passed `history` (e.g. `/metrics history` or `/metrics history 10`):**

Parse N from `ARGS` (default 5 if not specified):

```bash
cd {{AGENT_SYSTEM_ROOT}}
python3 metrics.py --history N
```

### 4. Read the rendered snapshot

After `metrics.py` completes, read `{{AGENT_SYSTEM_ROOT}}/docs/METRICS.md` (the rendered Markdown snapshot) and present it to the user.

### 5. Highlight alerts

Scan the snapshot for any of these conditions and call them out at the top of your response:

- Any project with `Behind major` drift (≥3 versions behind framework)
- Any project listed under "Missing projects" (registered but folder gone)
- Knowledge growth = 0 lines added in last 30 days for both LESSONS_LEARNED and KNOWN_PATTERNS (system not learning)
- AI Landscape Review activity = 0 reviews logged AND framework is older than 30 days (cadence broken)

If no alerts: say "All Tier 1 indicators within thresholds."

### 6. Suggest next actions only if alerts exist

For each alert, propose one concrete action. Examples:
- "Project X is 5 versions behind — run `python3 sync.py --target /path/to/X --render` to update"
- "No AI landscape reviews in 30+ days — recommend running `/ai-landscape-review`"

Do **not** suggest actions when everything is healthy. Just report the snapshot.

### 7. Defer instrumentation reminder

If the report shows "Phase 2 pending" metrics as unavailable, mention this once at the bottom:

> Tier 1 workflow metrics (completion rate, quality loop iterations, builder cycles) require IM instrumentation. Status: planned for next iteration.

Do not propose implementing Phase 2 unless the user asks.

## Constraints

- **Never modify metrics.py output** — present what was generated
- **Never edit framework files** — this is a read-only command except for `docs/METRICS.md` and `docs/METRICS_HISTORY.jsonl`, which `metrics.py` itself manages
- **Never trigger the audit if it's slow** — `metrics.py` already calls audit.py with a 30s timeout
- **Always run from `AGENT_SYSTEM_ROOT`** — even if user invoked from a downstream project
