#!/usr/bin/env python3
"""
Install git hooks for the agent-system repository.

Usage:
    python hooks/install.py
"""

import os
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOKS_SRC = ROOT / "hooks"
GIT_HOOKS_DIR = ROOT / ".git" / "hooks"

HOOKS = ["pre-commit", "post-commit"]


def install() -> None:
    if not GIT_HOOKS_DIR.exists():
        sys.exit(f"Error: {GIT_HOOKS_DIR} not found. Are you in a git repo?")

    for hook_name in HOOKS:
        src = HOOKS_SRC / hook_name
        if not src.exists():
            continue

        dst = GIT_HOOKS_DIR / hook_name
        if dst.exists() or dst.is_symlink():
            dst.unlink()

        os.symlink(src, dst)
        src.chmod(src.stat().st_mode | stat.S_IEXEC)
        print(f"  Installed: {hook_name} → {src.relative_to(ROOT)}")

    print("Done.")


if __name__ == "__main__":
    install()
