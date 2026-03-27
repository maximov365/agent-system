#!/usr/bin/env python3
"""
Sync agent-system framework files to a downstream project.

Usage:
    python sync.py --target /path/to/project              # copy framework files
    python sync.py --target /path/to/project --dry-run     # preview without writing
    python sync.py --target /path/to/project --diff        # show unified diff

The target project must have a project.config.yaml file.
Framework files are overwritten; project-specific files are never touched.
After syncing, run `python setup.py` in the target to render templates.
"""

import argparse
import difflib
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERSION_FILE = ROOT / "VERSION"

FRAMEWORK_GLOBS = [
    "agents/*.md",
    "AGENTS.md",
    "CLAUDE.md",
    ".cursor/rules.md",
    "docs/AGENT_HANDOFF_CONTRACT.md",
    "docs/AGENT_EXECUTION_MODEL.md",
    "docs/TASK_BACKLOG_AUTOMATION.md",
    "docs/ARCHITECTURE_GUARDRAILS.md",
    "docs/ARCHITECTURE_CHECKLIST.md",
    "docs/FEATURE_TEMPLATE.md",
    "docs/TASK_TEMPLATE.md",
    "docs/ONBOARDING.md",
    "setup.py",
    "requirements.txt",
]


def get_version() -> str:
    if VERSION_FILE.exists():
        return VERSION_FILE.read_text().strip()
    return "unknown"


def collect_framework_files() -> list[Path]:
    paths = []
    for pattern in FRAMEWORK_GLOBS:
        paths.extend(ROOT.glob(pattern))
    return sorted(set(paths))


def classify_changes(source_root: Path, target_root: Path, files: list[Path]):
    new, updated, unchanged = [], [], []
    for src in files:
        rel = src.relative_to(source_root)
        tgt = target_root / rel
        if not tgt.exists():
            new.append(rel)
        elif tgt.read_bytes() != src.read_bytes():
            updated.append(rel)
        else:
            unchanged.append(rel)
    return new, updated, unchanged


def show_diff(source_root: Path, target_root: Path, rel_path: Path) -> str:
    src = source_root / rel_path
    tgt = target_root / rel_path

    src_lines = src.read_text().splitlines(keepends=True)
    if tgt.exists():
        tgt_lines = tgt.read_text().splitlines(keepends=True)
    else:
        tgt_lines = []

    diff = difflib.unified_diff(
        tgt_lines, src_lines,
        fromfile=f"old/{rel_path}",
        tofile=f"new/{rel_path}",
        n=3,
    )
    return "".join(diff)


def copy_file(source_root: Path, target_root: Path, rel_path: Path) -> None:
    src = source_root / rel_path
    tgt = target_root / rel_path
    tgt.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, tgt)


def write_version(target_root: Path, version: str) -> None:
    version_file = target_root / ".agent-system-version"
    version_file.write_text(version + "\n")


def run_check(target_root: Path) -> bool:
    setup_py = target_root / "setup.py"
    if not setup_py.exists():
        print("  Warning: setup.py not found in target; skipping render check.")
        return True

    result = subprocess.run(
        [sys.executable, str(setup_py), "--check"],
        capture_output=True, text=True, cwd=str(target_root),
    )
    if result.returncode == 0:
        print("\n  Render check passed (setup.py --check).")
        return True

    print(f"\n  Render check FAILED:\n{result.stderr}", file=sys.stderr)
    return False


def cmd_sync(target: Path, dry_run: bool = False, show_diffs: bool = False) -> bool:
    if not (target / "project.config.yaml").exists():
        print(
            f"Error: {target / 'project.config.yaml'} not found.\n"
            "The target must be an agent-system project with a project.config.yaml.",
            file=sys.stderr,
        )
        return False

    version = get_version()
    files = collect_framework_files()
    new, updated, unchanged = classify_changes(ROOT, target, files)

    old_version_file = target / ".agent-system-version"
    old_version = old_version_file.read_text().strip() if old_version_file.exists() else "none"

    print(f"Agent System Sync")
    print(f"  Source:  {ROOT}")
    print(f"  Target:  {target}")
    print(f"  Version: {old_version} -> {version}")
    print(f"\n  {len(new)} new, {len(updated)} updated, {len(unchanged)} unchanged")

    if not new and not updated:
        print("\n  Already up to date.")
        return True

    if new:
        print(f"\n  New files:")
        for rel in new:
            print(f"    + {rel}")

    if updated:
        print(f"\n  Updated files:")
        for rel in updated:
            print(f"    ~ {rel}")

    if show_diffs:
        for rel in new + updated:
            diff_text = show_diff(ROOT, target, rel)
            if diff_text:
                print(f"\n{'=' * 60}")
                print(diff_text, end="")

    if dry_run or show_diffs:
        print(f"\n  Dry run — no files written.")
        return True

    for rel in new + updated:
        copy_file(ROOT, target, rel)

    write_version(target, version)

    print(f"\n  Copied {len(new) + len(updated)} file(s).")
    print(f"  Version file: .agent-system-version -> {version}")

    print(f"\n  Running render check...")
    ok = run_check(target)

    if ok:
        print(f"\n  Done. Next steps:")
        print(f"    cd {target}")
        print(f"    python setup.py          # render templates")
        print(f"    git diff                  # review changes")
        print(f"    git add -A && git commit  # commit")

    return ok


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync agent-system framework files to a downstream project.",
    )
    parser.add_argument(
        "--target", type=Path, required=True,
        help="Path to the downstream project root",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Preview without writing")
    mode.add_argument("--diff", action="store_true", help="Show unified diff of changes")
    args = parser.parse_args()

    target = args.target.resolve()
    if not target.is_dir():
        sys.exit(f"Error: {target} is not a directory.")

    ok = cmd_sync(target, dry_run=args.dry_run, show_diffs=args.diff)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
