---
description: Compute and display framework or project metrics (auto-detects scope from current directory)
argument-hint: "[history N]"
---

# /metrics

Run the metrics snapshot. Auto-detects whether you want framework-level (portfolio, velocity, aggregate workflows) or project-level (single project's status, knowledge, costs) view based on the current working directory.

## What you must do

### 1. Resolve

- `AGENT_SYSTEM_ROOT` = `{{AGENT_SYSTEM_ROOT}}`
- `CWD` = current working directory (use `pwd`)
- `ARGS` = `$ARGUMENTS`

### 2. Detect scope

Run this check:

```bash
ABS_CWD="$(cd "$CWD" && pwd)"
if [ "$ABS_CWD" = "{{AGENT_SYSTEM_ROOT}}" ]; then
  SCOPE="framework"
elif grep -qxF "$ABS_CWD" "{{AGENT_SYSTEM_ROOT}}/downstream.projects" 2>/dev/null; then
  SCOPE="project"
  PROJECT_PATH="$ABS_CWD"
else
  SCOPE="unknown"
fi
```

If `SCOPE = unknown`:
- If `$CWD` contains a `project.config.yaml` AND `.agent-system-version`, treat as project (offer to register it later) and proceed
- Otherwise, ask the user: "Run framework metrics or specify a project path?"

### 3. Run the appropriate command

**For `history` argument** (`/metrics history` or `/metrics history N`):

Parse N from `ARGS` (default 5):

```bash
cd {{AGENT_SYSTEM_ROOT}}
python3 metrics.py --history N
```

**For framework scope:**

```bash
cd {{AGENT_SYSTEM_ROOT}}
python3 metrics.py --append
```

**For project scope:**

```bash
cd {{AGENT_SYSTEM_ROOT}}
python3 metrics.py --project "$PROJECT_PATH"
```

(Project scope does not append to history — only the framework scope's history is tracked.)

### 4. Read the rendered snapshot

After `metrics.py` completes, read the appropriate Markdown:

- Framework scope: `{{AGENT_SYSTEM_ROOT}}/docs/METRICS.md`
- Project scope: `$PROJECT_PATH/docs/METRICS.md`

Present it to the user, focusing on key indicators.

### 5. Highlight alerts

Scan the snapshot for these conditions:

**Framework scope:**
- Any project with `Behind major` drift (≥3 versions behind framework)
- Any project under "Missing projects" (registered but folder gone)
- 0 lines added to LESSONS_LEARNED + KNOWN_PATTERNS in last 30 days
- 0 AI Landscape reviews in last 30 days
- Aggregate cost (30d) significantly higher than previous snapshots — possible runaway spend

**Project scope:**
- `PRD maturity: no_prd` or `stub` (project hasn't started or onboarding incomplete)
- Drift `≥3 versions` behind framework
- 0 workflows tracked AND project is older than 7 days (system not being used)
- Cost (30d) significantly higher than expected for this project size

If no alerts: say "All Tier 1 indicators within thresholds."

### 6. Suggest next actions only if alerts exist

Concrete actions per alert. Examples:
- "Project X is 5 versions behind — `python3 sync.py --target /path/to/X --render`"
- "PRD is empty for project Y — start onboarding: open Y in Claude Code and say 'start onboarding'"
- "No AI landscape reviews in 30+ days — run `/ai-landscape-review`"

Do **not** suggest actions when everything is healthy. Just report.

### 7. Workflow telemetry note

If "Workflows tracked" = 0 but the project has been around for >7 days, mention:

> Workflow telemetry counts handoff blocks emitted by agents in Claude Code transcripts. If you've been working in Claude Code without invoking agents (e.g., direct manual edits), no workflows will be tracked. Use the agent system (`@discovery`, `@product`, etc.) for tracked workflows.

## Constraints

- **Never modify metrics.py output** — present what was generated
- **Never write to project files outside `<project>/docs/METRICS.md`**
- **Always run `metrics.py` from `AGENT_SYSTEM_ROOT`** — even when computing project scope (the script lives only there)
- **Project scope reads from `<project>/docs/METRICS.md`** after generation
