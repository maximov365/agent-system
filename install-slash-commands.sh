#!/usr/bin/env bash
# Install user-level Claude Code slash commands from this framework's templates.
#
# Run once after cloning agent-system, and re-run after every framework update
# (or `git pull`) to pick up new/updated commands.
#
# Usage:
#   bash install-slash-commands.sh          # install/update all commands
#   bash install-slash-commands.sh --check  # show what's installed vs available

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/templates/claude-commands"
TARGET_DIR="$HOME/.claude/commands"

if [ ! -d "$SOURCE_DIR" ]; then
  echo "✗ Source directory not found: $SOURCE_DIR" >&2
  exit 1
fi

mkdir -p "$TARGET_DIR"

if [ "${1:-}" = "--check" ]; then
  echo "Available commands in $SOURCE_DIR:"
  ls "$SOURCE_DIR" 2>/dev/null | sed 's/^/  /'
  echo
  echo "Installed commands in $TARGET_DIR:"
  ls "$TARGET_DIR" 2>/dev/null | sed 's/^/  /' || echo "  (none)"
  exit 0
fi

count=0
for src in "$SOURCE_DIR"/*.md; do
  [ -f "$src" ] || continue
  name="$(basename "$src")"
  target="$TARGET_DIR/$name"

  if [ -f "$target" ] && cmp -s "$src" "$target"; then
    echo "  = $name (unchanged)"
  else
    cp "$src" "$target"
    echo "  ✓ $name (installed)"
    count=$((count + 1))
  fi
done

echo
echo "Done. $count command(s) installed/updated to $TARGET_DIR"
echo "Restart Claude Code session to pick up new commands."
