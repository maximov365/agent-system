#!/usr/bin/env python3
"""Preview or sync framework files without altering downstream Git tracking."""

import argparse
import difflib
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from framework_manifest import (FRAMEWORK_GLOBS, SEED_GLOBS, TEMPLATE_GLOBS,
                                deployment_sources, seed_sources)
from setup import has_variables, load_config, render_text
from sync_transaction import (atomic_write, safe_path, backup_root, project_lock,
                              apply_batch, restore_plan)

ROOT = Path(__file__).resolve().parent
VERSION_FILE = ROOT / "VERSION"
DOWNSTREAM_REGISTRY = ROOT / "downstream.projects"
GITIGNORE_MARKER_START = "# >>> agent-system framework (managed by sync.py) >>>"
GITIGNORE_MARKER_END = "# <<< agent-system framework <<<"
# Instructions and framework code should survive clone/worktree/CI.
GITIGNORE_ENTRIES = ["/.templates/", "/.agent/", "/.agent-system/**/node_modules/",
                     "/.agent-system/**/__pycache__/", "/.agent-system/**/.venv/"]

SEED_CONTENT = {
    "docs/TASKS.md": "# Tasks\n\n| Task ID | Title | Status | Priority | Complexity |\n|---|---|---|---|---|\n",
    "docs/DECISIONS.md": "# Decisions\n\nRecord significant project decisions here.\n",
    "docs/LESSONS_LEARNED.md": "# Lessons learned\n\nAppend useful lessons from this project's work.\n",
    "docs/KNOWN_PATTERNS.md": "# Known patterns\n\nRecord patterns validated in this project.\n",
}


def get_version() -> str:
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else "unknown"


def collect_framework_files() -> list[Path]:
    return sorted(deployment_sources(ROOT).values())


def collect_seed_files() -> list[Path]:
    return sorted(seed_sources(ROOT).values())


def is_template(rel: Path) -> bool:
    if rel.parts and rel.parts[0] == ".agent-system":
        return False
    if rel.parts and rel.parts[0] == "agents" and rel.suffix == ".md":
        return True
    return any(rel.match(pattern) for pattern in TEMPLATE_GLOBS)


def build_gitignore_block() -> str:
    return "\n".join([GITIGNORE_MARKER_START, *GITIGNORE_ENTRIES, GITIGNORE_MARKER_END])


def gitignore_content(target: Path) -> bytes:
    path = safe_path(target, Path(".gitignore"))
    content = path.read_text() if path.exists() else ""
    start_count, end_count = content.count(GITIGNORE_MARKER_START), content.count(GITIGNORE_MARKER_END)
    if (start_count, end_count) not in ((0, 0), (1, 1)):
        raise ValueError("Malformed or duplicate managed .gitignore block; repair before sync")
    block = build_gitignore_block()
    if start_count:
        start = content.index(GITIGNORE_MARKER_START)
        end = content.index(GITIGNORE_MARKER_END)
        if end < start:
            raise ValueError("Reversed managed .gitignore markers")
        content = content[:start] + block + content[end + len(GITIGNORE_MARKER_END):]
    else:
        content += ("\n" if content and not content.endswith("\n") else "") + block + "\n"
    return content.encode()


def plan_sync(target: Path, render: bool) -> dict[Path, bytes]:
    """Compute/validate every destination before any mutation, including previews."""
    target = target.resolve()
    if target == ROOT.resolve():
        raise ValueError("Refusing to sync the framework onto itself")
    # A framework clone/worktree is not a downstream target.
    if (target / "sync.py").exists() and (target / "framework_manifest.py").exists():
        raise ValueError("Target appears to be a framework checkout")
    config = load_config(safe_path(target, Path("project.config.yaml")))
    pending = {}
    sources = deployment_sources(ROOT)
    seeds = seed_sources(ROOT)
    overlap = sources.keys() & seeds.keys()
    if overlap:
        raise ValueError(f"Framework/seed ownership overlap: {sorted(map(str, overlap))}")
    for rel, src in sources.items():
        raw = src.read_bytes()
        if is_template(rel):
            text = raw.decode()
            rendered = render_text(text, config) if has_variables(text) else text
            pending[rel] = rendered.encode() if render else raw
            # Canonical source survives clone and supersedes any previous version.
            pending[Path(".agent-system/templates") / rel] = raw
        else:
            pending[rel] = raw
    for rel, src in seeds.items():
        if not (target / rel).exists():
            content = SEED_CONTENT.get(str(rel), src.read_text())
            pending[rel] = (render_text(content, config) if has_variables(content) else content).encode()
    # Only exact known framework copies are migrated; app/custom scripts survive.
    migrations = json.loads((ROOT / "migrations/legacy-files.json").read_text())
    for name, rule in migrations["files"].items():
        rel = Path(name)
        legacy = safe_path(target, rel)
        if legacy.exists() and hashlib.sha256(legacy.read_bytes()).hexdigest() in rule["sha256"]:
            pending[rel] = safe_path(ROOT, Path(rule["replacement"])).read_bytes()
    pending[Path(".gitignore")] = gitignore_content(target)
    pending[Path(".agent-system-version")] = (get_version() + "\n").encode()
    for rel in pending:
        safe_path(target, rel)
    return pending


def cmd_sync(target: Path, dry_run: bool = False, show_diffs: bool = False,
             render: bool = False, backup_dir: Path | None = None) -> bool:
    target = target.resolve()
    try:
        if not target.is_dir():
            raise ValueError(f"Not a project directory: {target}")
        pending = plan_sync(target, render)
        changes = {rel: data for rel, data in pending.items()
                   if not (target / rel).exists() or (target / rel).read_bytes() != data}
        print(f"Agent System Sync: {target}")
        print(f"  Version: {get_version()}; {len(changes)} changed file(s)")
        for rel, data in changes.items():
            if rel.parts[0] == ".templates":
                continue
            print(f"  {'~' if (target / rel).exists() else '+'} {rel}")
            if show_diffs:
                old = (target / rel).read_text() if (target / rel).exists() else ""
                print("".join(difflib.unified_diff(old.splitlines(True), data.decode().splitlines(True),
                                                   fromfile=f"old/{rel}", tofile=f"new/{rel}")), end="")
        if dry_run or show_diffs:
            print("  Preview only; no files or Git index entries changed.")
            return True
        root = backup_root(target, backup_dir)
        with project_lock(target, root):
            current = plan_sync(target, render)
            if current != pending:
                raise ValueError("Project/configuration changed during sync preflight; retry preview")
            backup = apply_batch(target, current, root=root, writer=atomic_write, version=get_version())
        print("  Sync complete. Review and stage changes normally; Git index was not modified.")
        if backup:
            print(f"  Recovery backup: {backup}")
        return True
    except (OSError, ValueError) as exc:
        print(f"Sync failed: {exc}", file=sys.stderr)
        return False
    except Exception as exc:
        # Jinja/YAML exceptions are reported without executing downstream code.
        print(f"Sync validation failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return False


def cmd_restore(target: Path, backup: Path, dry_run: bool = False) -> bool:
    target = target.resolve()
    try:
        if target == ROOT.resolve() or not target.is_dir():
            raise ValueError("Choose an existing downstream target")
        if dry_run:
            pending, _ = restore_plan(target, backup)
            print(f"Restore preview: {target}; {len(pending)} recorded paths; no writes")
            return True
        root = backup_root(target)
        with project_lock(target, root):
            pending, modes = restore_plan(target, backup)
            reverse = apply_batch(target, pending, root=root, modes=modes, version="restore")
        print(f"Restore complete. Reverse-operation backup: {reverse or 'no changes'}")
        return True
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Restore failed: {exc}", file=sys.stderr)
        return False


def find_python(project_root: Path) -> str:
    """Compatibility helper; rendering itself uses this process's dependencies."""
    for candidate in [project_root / ".venv/bin/python3", ROOT / ".venv/bin/python3"]:
        if candidate.exists():
            try:
                result = subprocess.run([str(candidate), "-c", "import jinja2,yaml"],
                                        capture_output=True, timeout=15)
                if result.returncode == 0:
                    return str(candidate)
            except (OSError, subprocess.TimeoutExpired):
                pass
    return sys.executable


def load_downstream_projects() -> list[Path]:
    if not DOWNSTREAM_REGISTRY.exists():
        return []
    return list(dict.fromkeys(Path(line.strip()).expanduser().resolve()
                              for line in DOWNSTREAM_REGISTRY.read_text().splitlines()
                              if line.strip() and not line.strip().startswith("#")))


def cmd_sync_all(render: bool = False, dry_run: bool = False, show_diffs: bool = False) -> bool:
    projects = load_downstream_projects()
    if not projects:
        print("No downstream projects registered.")
        return True
    results = [cmd_sync(p, dry_run=dry_run, show_diffs=show_diffs, render=render) for p in projects]
    return all(results)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--target", type=Path)
    target.add_argument("--all", action="store_true", dest="sync_all")
    parser.add_argument("--restore", type=Path, help="Restore a recovery record for --target; refuses newer edits")
    parser.add_argument("--backup-dir", type=Path, help="Store recovery records outside the target")
    parser.add_argument("--render", action="store_true", help="Render in memory before copying")
    preview = parser.add_mutually_exclusive_group()
    preview.add_argument("--dry-run", action="store_true")
    preview.add_argument("--diff", action="store_true")
    args = parser.parse_args()
    if args.restore:
        if args.sync_all or args.render or args.diff or args.backup_dir:
            parser.error("--restore requires --target and supports only --dry-run")
        ok = cmd_restore(args.target, args.restore, args.dry_run)
    elif args.sync_all:
        if args.backup_dir:
            parser.error("--backup-dir requires a single --target")
        ok = cmd_sync_all(args.render, args.dry_run, args.diff)
    else:
        ok = cmd_sync(args.target, args.dry_run, args.diff, args.render, args.backup_dir)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
