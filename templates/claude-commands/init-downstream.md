---
description: Bootstrap an agent-system downstream project in the current directory and offer to start onboarding
argument-hint: "\"<Project Name>\""
---

# /init-downstream

Initialize the **current working directory** as a downstream project of the `agent-system` framework. The project name passed as the argument will be used in `project.config.yaml` and rendered into all framework agent files.

## What you must do

Execute the following steps in order. Stop and report any error.

### 1. Resolve paths

- `TARGET_DIR` = current working directory (use `pwd` via Bash)
- `PROJECT_NAME` = the user-supplied argument (`$ARGUMENTS`); strip surrounding quotes if present
- `AGENT_SYSTEM_ROOT` = `{{AGENT_SYSTEM_ROOT}}`

If `PROJECT_NAME` is empty or only whitespace, stop and ask the user for a name.

If `AGENT_SYSTEM_ROOT` does not exist, stop and report. Suggest the user clone it first: `git clone https://github.com/maximov365/agent-system.git {{AGENT_SYSTEM_ROOT}}`.

### 2. Refuse to overwrite an existing downstream

Check if `TARGET_DIR/project.config.yaml` already exists. If yes:
- Read the existing `project.name` value
- If it differs from `PROJECT_NAME`, stop and ask the user whether to proceed (refuse to silently overwrite a different project)
- If it matches, skip step 3 (config already in place) and proceed to step 4

If `TARGET_DIR` contains a `.git/` folder pointing to `agent-system` repo (`git -C "$TARGET_DIR" remote get-url origin` returns the agent-system repo URL), stop and report — this folder is a clone of the framework, not a downstream. Suggest the user pick a different empty folder.

### 3. Create `project.config.yaml`

Write `TARGET_DIR/project.config.yaml` with the standard template, substituting the project name:

```yaml
# ============================================================================
# Project Configuration — <PROJECT_NAME>
# Edit this file, then run: python3 setup.py
# ============================================================================

project:
  name: "<PROJECT_NAME>"
  description: |-
    <One-paragraph description — TODO: edit after onboarding>

pipeline:
  stages:
    - name: ingest
      description: "Parse and normalize input"
    - name: process
      description: "Core processing logic"
    - name: export
      description: "Produce final output"

analytics_by_default: false

domain_rules:
  llm_rules: |
    - Never hardcode model names — use config constants
    - Prompts must live in prompts/ directory
  pipeline_principles: |
    - Each stage has explicit inputs and outputs
    - Stages must remain independently testable

output_docs:
  has_brand_guide: false
  custom_docs: []
```

### 4. Register in downstream registry

Append `TARGET_DIR` (absolute path) to `AGENT_SYSTEM_ROOT/downstream.projects` if not already present. Use idempotent check:

```bash
TARGET_ABS="$(cd "$TARGET_DIR" && pwd)"
if ! grep -qxF "$TARGET_ABS" "$AGENT_SYSTEM_ROOT/downstream.projects"; then
  echo "$TARGET_ABS" >> "$AGENT_SYSTEM_ROOT/downstream.projects"
fi
```

### 5. Sync framework + render templates

Run from `AGENT_SYSTEM_ROOT`:

```bash
cd "$AGENT_SYSTEM_ROOT"
python3 sync.py --target "$TARGET_ABS" --render
```

Report the version copied (e.g. "Synced framework version X.Y.Z").

### 6. Verify deployment

Run quick checks:
- `head -3 "$TARGET_DIR/CLAUDE.md"` — should show `**Project:** <PROJECT_NAME>` (not `{{ project.name }}`)
- `ls "$TARGET_DIR/agents/"` — should contain at least 20 agent .md files
- `cat "$TARGET_DIR/.agent-system-version"` — should match `AGENT_SYSTEM_ROOT/VERSION`

If any check fails, stop and report.

### 7. Report success and offer onboarding

Print this exact summary:

```
✓ <PROJECT_NAME> deployed at <TARGET_DIR>
  • Framework version: <X.Y.Z>
  • Agent files rendered: 30
  • Registered in downstream.projects: ✓

Next: Edit project.config.yaml description and pipeline.stages to match the project, then run `python3 setup.py` to re-render.

Ready to start onboarding (Discovery intake mode)? This walks through 13 structured questions to populate docs/PRD.md, docs/ARCHITECTURE.md, and docs/BRAND.md.

Reply "yes" to begin onboarding, or "later" to defer.
```

### 8. If user replies "yes"

Re-read this project's `CLAUDE.md`, `AGENTS.md`, and `agents/iteration-manager.md` (now rendered with the project name) to load the local agent context. Then act as Iteration Manager and start the onboarding workflow per `agents/im-modes/onboarding.md` Phase 1: invoke Discovery agent in onboarding intake mode.

If user replies "later" or anything else, just acknowledge and stop.

## Important rules

- **Never `cd` away from `TARGET_DIR`** for anything user-visible. The session must end in the target project's directory so the user can continue working there.
- **Never modify** `AGENT_SYSTEM_ROOT` files except for `downstream.projects`.
- **Never overwrite** an existing project without explicit user confirmation.
- **Never start** real Discovery work (interviews, file creation beyond config) without the user's "yes" in step 8.
