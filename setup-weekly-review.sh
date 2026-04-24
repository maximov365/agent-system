#!/usr/bin/env bash
# Install macOS launchd job for weekly framework review reminder.
# Fires every Monday at 10:08 local time, sends a desktop notification.
# When the user sees the notification, they open Claude Code and run:
#   /metrics
#   /ai-landscape-review
#
# Usage:
#   bash setup-weekly-review.sh         # install
#   bash setup-weekly-review.sh --check # check if installed and next fire time
#   bash setup-weekly-review.sh --remove

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/templates/launchd/com.agent-system.weekly-review.plist"
TARGET="$HOME/Library/LaunchAgents/com.agent-system.weekly-review.plist"
LABEL="com.agent-system.weekly-review"

if [ "$(uname)" != "Darwin" ]; then
  echo "✗ This setup uses macOS launchd. For Linux use cron with similar schedule:"
  echo "    8 10 * * 1 osascript -e 'display notification ...' OR your preferred notifier"
  exit 1
fi

cmd="${1:-install}"

case "$cmd" in
  --check|check)
    if [ -f "$TARGET" ]; then
      echo "✓ Installed at $TARGET"
      launchctl list | grep "$LABEL" || echo "  (not currently loaded — try: launchctl load $TARGET)"
    else
      echo "✗ Not installed"
    fi
    log="$SCRIPT_DIR/docs/.weekly-review.log"
    if [ -f "$log" ]; then
      echo "Recent firings:"
      tail -5 "$log"
    fi
    ;;

  --remove|remove)
    if [ -f "$TARGET" ]; then
      launchctl unload "$TARGET" 2>/dev/null || true
      rm -f "$TARGET"
      echo "✓ Removed $TARGET"
    else
      echo "  Already not installed."
    fi
    ;;

  install|"")
    if [ ! -f "$TEMPLATE" ]; then
      echo "✗ Template missing: $TEMPLATE" >&2
      exit 1
    fi

    mkdir -p "$(dirname "$TARGET")"
    sed "s|{{AGENT_SYSTEM_ROOT}}|$SCRIPT_DIR|g" "$TEMPLATE" > "$TARGET"

    # Reload to pick up changes
    launchctl unload "$TARGET" 2>/dev/null || true
    launchctl load "$TARGET"

    echo "✓ Installed: $TARGET"
    echo "✓ Loaded into launchd"
    echo
    echo "Next fire: every Monday at 10:08 local time"
    echo "  Sends a macOS notification reminding you to run /metrics + /ai-landscape-review"
    echo
    echo "Manage:"
    echo "  bash $0 --check"
    echo "  bash $0 --remove"
    ;;

  *)
    echo "Usage: $0 [install|--check|--remove]"
    exit 1
    ;;
esac
