#!/usr/bin/env python3
"""
Sync agent-system framework files to downstream projects.

Usage:
    python sync.py --target /path/to/project              # sync one project
    python sync.py --target /path/to/project --render      # sync + render templates
    python sync.py --target /path/to/project --dry-run     # preview without writing
    python sync.py --target /path/to/project --diff        # show unified diff
    python sync.py --all                                   # sync all registered projects
    python sync.py --all --render                          # sync + render all projects

Downstream projects are registered in downstream.projects (one path per line).
Framework files are overwritten; project-specific files are never touched.
"""

import argparse
import difflib
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERSION_FILE = ROOT / "VERSION"
DOWNSTREAM_REGISTRY = ROOT / "downstream.projects"

FRAMEWORK_GLOBS = [
    "agents/*.md",
    "agents/discovery-modes/*.md",
    "agents/im-modes/*.md",
    "AGENTS.md",
    "CLAUDE.md",
    ".cursor/rules.md",
    "docs/AGENT_HANDOFF_CONTRACT.md",
    "docs/AGENT_EXECUTION_MODEL.md",
    "docs/TASK_BACKLOG_AUTOMATION.md",
    "docs/ARCHITECTURE_GUARDRAILS.md",
    "docs/ARCHITECTURE_CHECKLIST.md",
    "docs/TASK_TEMPLATE.md",
    "docs/ONBOARDING.md",
    "docs/MCP_TOOLS.md",
    "setup.py",
    "requirements-framework.txt",
]

# Seed files: copied only when they do NOT exist in the target project.
# These are scaffolds that projects fill in with project-specific content.
# Once created, they are never overwritten by sync.
SEED_GLOBS = [
    "docs/PIPELINE_CONTRACTS.md",
    "docs/DEPLOY_CONTRACTS.md",
]

GITIGNORE_MARKER_START = "# >>> agent-system framework (managed by sync.py) >>>"
GITIGNORE_MARKER_END = "# <<< agent-system framework <<<"

GITIGNORE_ENTRIES = [
    "/agents/",
    "/AGENTS.md",
    "/CLAUDE.md",
    "/.cursor/rules.md",
    "/docs/AGENT_HANDOFF_CONTRACT.md",
    "/docs/AGENT_EXECUTION_MODEL.md",
    "/docs/TASK_BACKLOG_AUTOMATION.md",
    "/docs/ARCHITECTURE_GUARDRAILS.md",
    "/docs/ARCHITECTURE_CHECKLIST.md",
    "/docs/TASK_TEMPLATE.md",
    "/docs/ONBOARDING.md",
    "/docs/MCP_TOOLS.md",
    "/setup.py",
    "/requirements-framework.txt",
    "/.agent-system-version",
    "/.templates/",
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


def collect_seed_files() -> list[Path]:
    paths = []
    for pattern in SEED_GLOBS:
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


def find_python(project_root: Path) -> str:
    """Find a python with jinja2/pyyaml: project venv → agent-system venv → sys.executable."""
    candidates = [
        project_root / ".venv" / "bin" / "python3",
        ROOT / ".venv" / "bin" / "python3",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return sys.executable


def run_check(target_root: Path) -> bool:
    setup_py = target_root / "setup.py"
    if not setup_py.exists():
        print("  Warning: setup.py not found in target; skipping render check.")
        return True

    python = find_python(target_root)
    result = subprocess.run(
        [python, str(setup_py), "--check"],
        capture_output=True, text=True, cwd=str(target_root),
    )
    if result.returncode == 0:
        print("\n  Render check passed (setup.py --check).")
        return True

    print(f"\n  Render check FAILED:\n{result.stderr}", file=sys.stderr)
    return False


def load_downstream_projects() -> list[Path]:
    if not DOWNSTREAM_REGISTRY.exists():
        return []
    projects = []
    for line in DOWNSTREAM_REGISTRY.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        path = Path(stripped).expanduser().resolve()
        projects.append(path)
    return projects


def run_setup(target: Path) -> bool:
    setup_py = target / "setup.py"
    if not setup_py.exists():
        print(f"  Warning: setup.py not found in {target}; skipping render.")
        return True

    python = find_python(target)
    print(f"\n  Rendering templates...")
    result = subprocess.run(
        [python, str(setup_py)],
        capture_output=True, text=True, cwd=str(target),
    )
    if result.returncode == 0:
        print(result.stdout.rstrip())
        return True

    print(f"  Render FAILED:", file=sys.stderr)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return False


def build_gitignore_block() -> str:
    lines = [GITIGNORE_MARKER_START]
    for entry in GITIGNORE_ENTRIES:
        lines.append(entry)
    lines.append(GITIGNORE_MARKER_END)
    return "\n".join(lines)


def update_gitignore(target: Path, dry_run: bool = False) -> bool:
    """Add or update the managed framework block in downstream .gitignore."""
    gitignore = target / ".gitignore"
    block = build_gitignore_block()

    if gitignore.exists():
        content = gitignore.read_text()
        if GITIGNORE_MARKER_START in content and GITIGNORE_MARKER_END in content:
            start = content.index(GITIGNORE_MARKER_START)
            end = content.index(GITIGNORE_MARKER_END) + len(GITIGNORE_MARKER_END)
            old_block = content[start:end]
            if old_block == block:
                return False
            if not dry_run:
                new_content = content[:start] + block + content[end:]
                gitignore.write_text(new_content)
            return True
        else:
            if not dry_run:
                separator = "\n" if content.endswith("\n") else "\n\n"
                gitignore.write_text(content + separator + "\n" + block + "\n")
            return True
    else:
        if not dry_run:
            gitignore.write_text(block + "\n")
        return True


def untrack_framework_files(target: Path) -> list[str]:
    """Remove framework files from git index (keep on disk). Returns list of untracked files."""
    git_dir = target / ".git"
    if not git_dir.exists():
        return []

    result = subprocess.run(
        ["git", "ls-files", "--cached"] + [f":{e.lstrip('/')}" for e in GITIGNORE_ENTRIES if not e.endswith("/")],
        capture_output=True, text=True, cwd=str(target),
    )
    tracked_files = [f for f in result.stdout.strip().splitlines() if f]

    result_dirs = subprocess.run(
        ["git", "ls-files", "--cached", "agents/"],
        capture_output=True, text=True, cwd=str(target),
    )
    tracked_files += [f for f in result_dirs.stdout.strip().splitlines() if f]

    if not tracked_files:
        return []

    tracked_files = sorted(set(tracked_files))
    subprocess.run(
        ["git", "rm", "--cached", "-q"] + tracked_files,
        capture_output=True, text=True, cwd=str(target),
    )
    return tracked_files


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

    # Seed files: only copy if they don't exist in target
    seed_files = collect_seed_files()
    seeded = []
    for src in seed_files:
        rel = src.relative_to(ROOT)
        tgt = target / rel
        if not tgt.exists():
            seeded.append(rel)

    old_version_file = target / ".agent-system-version"
    old_version = old_version_file.read_text().strip() if old_version_file.exists() else "none"

    print(f"Agent System Sync")
    print(f"  Source:  {ROOT}")
    print(f"  Target:  {target}")
    print(f"  Version: {old_version} -> {version}")
    print(f"\n  {len(new)} new, {len(updated)} updated, {len(unchanged)} unchanged", end="")
    if seeded:
        print(f", {len(seeded)} seeded")
    else:
        print()

    if not new and not updated and not seeded:
        print("\n  Already up to date.")
        return True

    if new:
        print(f"\n  New files:")
        for rel in new:
            print(f"    + {rel}")

    if seeded:
        print(f"\n  Seeded files (first-time only):")
        for rel in seeded:
            print(f"    * {rel}")

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

    gitignore_updated = update_gitignore(target, dry_run=(dry_run or show_diffs))
    if gitignore_updated:
        action = "would update" if (dry_run or show_diffs) else "updated"
        print(f"\n  .gitignore: framework block {action}")

    if dry_run or show_diffs:
        print(f"\n  Dry run — no files written.")
        return True

    for rel in new + updated + seeded:
        copy_file(ROOT, target, rel)

    write_version(target, version)

    print(f"\n  Copied {len(new) + len(updated) + len(seeded)} file(s).")
    print(f"  Version file: .agent-system-version -> {version}")

    untracked = untrack_framework_files(target)
    if untracked:
        print(f"  Removed {len(untracked)} file(s) from git tracking (kept on disk)")

    print(f"\n  Running render check...")
    ok = run_check(target)
    return ok


def cmd_sync_all(render: bool = False, dry_run: bool = False) -> bool:
    projects = load_downstream_projects()
    if not projects:
        print("No downstream projects registered.")
        print(f"Add project paths to {DOWNSTREAM_REGISTRY} (one per line).")
        return True

    all_ok = True
    for target in projects:
        print(f"\n{'=' * 60}")
        if not target.is_dir():
            print(f"  SKIP: {target} (directory not found)")
            continue
        if not (target / "project.config.yaml").exists():
            print(f"  SKIP: {target} (no project.config.yaml)")
            continue

        ok = cmd_sync(target, dry_run=dry_run)
        if ok and render and not dry_run:
            ok = run_setup(target)
        all_ok = all_ok and ok

    print(f"\n{'=' * 60}")
    status = "All projects synced." if all_ok else "Some projects had errors."
    print(f"\n{status}")
    return all_ok


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync agent-system framework files to downstream projects.",
    )
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument(
        "--target", type=Path,
        help="Path to a single downstream project root",
    )
    target_group.add_argument(
        "--all", action="store_true", dest="sync_all",
        help="Sync all projects listed in downstream.projects",
    )
    parser.add_argument(
        "--render", action="store_true",
        help="Run setup.py in each project after syncing to render templates",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Preview without writing")
    mode.add_argument("--diff", action="store_true", help="Show unified diff of changes")
    args = parser.parse_args()

    if args.sync_all:
        ok = cmd_sync_all(render=args.render, dry_run=args.dry_run)
    else:
        target = args.target.resolve()
        if not target.is_dir():
            sys.exit(f"Error: {target} is not a directory.")
        ok = cmd_sync(target, dry_run=args.dry_run, show_diffs=args.diff)
        if ok and args.render:
            ok = run_setup(target)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
