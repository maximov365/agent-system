#!/usr/bin/env python3
"""
Install git hooks for the agent-system repository.

Usage:
    python hooks/install.py
"""

import os
import stat
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOKS_SRC = ROOT / "hooks"
GIT_HOOKS_DIR = ROOT / ".git" / "hooks"

HOOKS = ["pre-commit", "post-commit"]


def install(hooks_dir: Path = None) -> None:
    if hooks_dir is None:
        result = subprocess.run(["git", "rev-parse", "--git-path", "hooks"], cwd=ROOT,
                                capture_output=True, text=True, check=True)
        hooks_dir = Path(result.stdout.strip())
        if not hooks_dir.is_absolute():
            hooks_dir = ROOT / hooks_dir

    # Check all destinations before changing any hook. Existing unrelated hooks
    # belong to the user; installation must never silently unlink them.
    pending = []

    for hook_name in HOOKS:
        src = HOOKS_SRC / hook_name
        if not src.exists():
            continue

        dst = hooks_dir / hook_name
        if dst.exists() or dst.is_symlink():
            if dst.is_symlink() and dst.resolve() == src.resolve():
                continue
            raise ValueError(f"Existing hook preserved: {dst}. Integrate or back it up before installing.")
        pending.append((src, dst, hook_name))

    hooks_dir.mkdir(parents=True, exist_ok=True)
    for src, dst, hook_name in pending:
        os.symlink(src, dst)
        src.chmod(src.stat().st_mode | stat.S_IEXEC)
        print(f"  Installed: {hook_name} → {src.relative_to(ROOT)}")

    print("Done.")


if __name__ == "__main__":
    try:
        install()
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        sys.exit(str(exc))
