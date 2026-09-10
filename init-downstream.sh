#!/usr/bin/env bash
# Portable entry point; names and paths are passed as data, never embedded code.
set -euo pipefail
AGENT_SYSTEM_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -x "$AGENT_SYSTEM_ROOT/.venv/bin/python3" ] && "$AGENT_SYSTEM_ROOT/.venv/bin/python3" -c 'import yaml,jinja2' >/dev/null 2>&1; then
  exec "$AGENT_SYSTEM_ROOT/.venv/bin/python3" "$AGENT_SYSTEM_ROOT/init-downstream.py" "$@"
fi
exec python3 "$AGENT_SYSTEM_ROOT/init-downstream.py" "$@"
