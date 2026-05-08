#!/usr/bin/env bash
# Bootstrap an agent-system downstream project.
# Works in any environment (Cursor, plain terminal, VSCode, vim, anywhere bash runs).
#
# Usage:
#   bash init-downstream.sh "Project Name" [target-path]
#   bash init-downstream.sh "Project Name"               # uses current directory
#
# Examples:
#   mkdir -p ~/projects/my-thing && cd ~/projects/my-thing
#   bash /path/to/agent-system/init-downstream.sh "My Thing"
#
# Or absolute target:
#   bash /path/to/agent-system/init-downstream.sh "My Thing" ~/projects/my-thing
#
# What it does (idempotent):
#   1. Validates target directory (creates if missing, refuses to overwrite a different project)
#   2. Refuses to deploy on top of a clone of agent-system itself
#   3. Creates project.config.yaml with the supplied name
#   4. Registers absolute path in agent-system/downstream.projects
#   5. Runs sync.py --target <abs-path> --render
#   6. Verifies the deployment
#   7. Prints next steps

set -euo pipefail

# Colors (only if stdout is a terminal)
if [ -t 1 ]; then
  GREEN=$'\033[0;32m'
  YELLOW=$'\033[0;33m'
  RED=$'\033[0;31m'
  BOLD=$'\033[1m'
  NC=$'\033[0m'
else
  GREEN=""; YELLOW=""; RED=""; BOLD=""; NC=""
fi

err() { printf "${RED}✗ %s${NC}\n" "$*" >&2; }
ok()  { printf "${GREEN}✓ %s${NC}\n" "$*"; }
warn() { printf "${YELLOW}⚠ %s${NC}\n" "$*"; }
info() { printf "  %s\n" "$*"; }

# --- Resolve paths ------------------------------------------------------------

AGENT_SYSTEM_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="${1:-}"
TARGET_DIR="${2:-$(pwd)}"

if [ -z "$PROJECT_NAME" ]; then
  err "Project name required."
  echo "Usage: bash $0 \"Project Name\" [target-path]"
  exit 1
fi

# Strip surrounding quotes if accidentally double-quoted
PROJECT_NAME="${PROJECT_NAME%\"}"
PROJECT_NAME="${PROJECT_NAME#\"}"

# Resolve target to absolute path (create if missing)
if [ ! -d "$TARGET_DIR" ]; then
  mkdir -p "$TARGET_DIR"
  info "Created directory: $TARGET_DIR"
fi
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

# --- Sanity checks ------------------------------------------------------------

# Refuse to deploy on top of agent-system root itself
if [ "$TARGET_DIR" = "$AGENT_SYSTEM_ROOT" ]; then
  err "Target is agent-system root itself — refusing to deploy framework on itself."
  exit 1
fi

# Refuse to deploy on top of a clone of agent-system (has .git pointing to that repo)
if [ -d "$TARGET_DIR/.git" ]; then
  origin="$(git -C "$TARGET_DIR" remote get-url origin 2>/dev/null || echo "")"
  if echo "$origin" | grep -qi "agent-system"; then
    err "Target is a clone of agent-system itself ($origin)."
    err "A downstream project should not be a clone of the framework repo."
    err "Pick a different empty folder, or remove the .git/ here first."
    exit 1
  fi
fi

# Check for existing project.config.yaml with a different name (Python YAML parser for reliability across shells)
EXISTING_NAME=""
if [ -f "$TARGET_DIR/project.config.yaml" ]; then
  EXISTING_NAME="$(python3 -c "
import yaml, sys
try:
    with open('$TARGET_DIR/project.config.yaml') as f:
        d = yaml.safe_load(f) or {}
    print(d.get('project', {}).get('name', '') or '')
except Exception:
    pass
" 2>/dev/null)"
fi
if [ -n "$EXISTING_NAME" ] && [ "$EXISTING_NAME" != "$PROJECT_NAME" ]; then
  err "Target already configured for a DIFFERENT project: \"$EXISTING_NAME\""
  err "You asked to deploy: \"$PROJECT_NAME\""
  err "Refusing to overwrite. Either use the existing name or pick a different folder."
  exit 1
fi

# --- Step 1: project.config.yaml ----------------------------------------------

if [ -n "$EXISTING_NAME" ] && [ "$EXISTING_NAME" = "$PROJECT_NAME" ]; then
  info "project.config.yaml already configured for \"$PROJECT_NAME\" — skipping write"
else
  cat > "$TARGET_DIR/project.config.yaml" <<EOF
# ============================================================================
# Project Configuration — $PROJECT_NAME
# Edit this file, then run: python3 setup.py
# ============================================================================

project:
  name: "$PROJECT_NAME"
  description: |-
    <Edit this description — TODO: fill after onboarding>

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
EOF
  ok "Wrote $TARGET_DIR/project.config.yaml"
fi

# --- Step 2: Register in downstream.projects ----------------------------------

REGISTRY="$AGENT_SYSTEM_ROOT/downstream.projects"
if [ -f "$REGISTRY" ] && grep -qxF "$TARGET_DIR" "$REGISTRY"; then
  info "Already registered in downstream.projects"
else
  echo "$TARGET_DIR" >> "$REGISTRY"
  ok "Registered in $REGISTRY"
fi

# --- Step 3: Sync framework files + render templates --------------------------

cd "$AGENT_SYSTEM_ROOT"
if ! command -v python3 >/dev/null 2>&1; then
  err "python3 not found — install Python 3.9+ before running sync."
  exit 1
fi

info "Running sync.py..."
python3 sync.py --target "$TARGET_DIR" --render | sed 's/^/  /'

# --- Step 4: Verify deployment ------------------------------------------------

VERSION_FILE="$TARGET_DIR/.agent-system-version"
CLAUDE_MD="$TARGET_DIR/CLAUDE.md"
AGENTS_DIR="$TARGET_DIR/agents"

errors=0
[ -f "$VERSION_FILE" ] || { err "Missing $VERSION_FILE"; errors=$((errors+1)); }
[ -f "$CLAUDE_MD" ]    || { err "Missing $CLAUDE_MD"; errors=$((errors+1)); }
[ -d "$AGENTS_DIR" ]   || { err "Missing $AGENTS_DIR"; errors=$((errors+1)); }

# Check that {{ project.name }} got rendered (no Jinja remnants for the project.name var)
if [ -f "$CLAUDE_MD" ] && grep -qE '\{\{\s*project\.name\s*\}\}' "$CLAUDE_MD"; then
  err "CLAUDE.md still contains unrendered {{ project.name }} — render failed"
  errors=$((errors+1))
fi

if [ "$errors" -gt 0 ]; then
  err "Deployment verification failed with $errors issue(s)."
  exit 2
fi

VERSION="$(cat "$VERSION_FILE")"
AGENT_COUNT="$(find "$AGENTS_DIR" -maxdepth 2 -name '*.md' | wc -l | tr -d ' ')"

# --- Step 5: Print summary ----------------------------------------------------

echo
echo "${BOLD}${GREEN}✓ $PROJECT_NAME deployed${NC}"
echo "  Path: $TARGET_DIR"
echo "  Framework version: $VERSION"
echo "  Agent files rendered: $AGENT_COUNT"
echo "  Registered in downstream.projects: ✓"
echo
echo "${BOLD}Next steps:${NC}"
echo "  1. cd \"$TARGET_DIR\""
echo "  2. Edit project.config.yaml (description, pipeline.stages, domain_rules)"
echo "  3. Re-render after edits: python3 setup.py"
echo
echo "${BOLD}Start onboarding:${NC}"
echo "  • In Cursor:  open the folder, then in chat say \"Start onboarding\""
echo "  • In Claude Code:  cd \"$TARGET_DIR\" && claude, then say \"Start onboarding\""
echo "  • Discovery → Product → Designer → Architect intake fills docs/PRD.md, ARCHITECTURE.md, BRAND.md"
echo
