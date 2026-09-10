#!/usr/bin/env python3
"""
Render Jinja2 templates across the repository using project.config.yaml.

Usage:
    python setup.py              # render all templates
    python setup.py --check      # dry-run — preview without writing
    python setup.py --restore    # restore original Jinja2 templates

First run saves originals to .templates/ for safe re-rendering.
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from framework_manifest import TEMPLATE_GLOBS

try:
    import yaml
except ImportError:
    sys.exit("Missing dependency: pip install pyyaml")

try:
    from jinja2 import Environment, BaseLoader, StrictUndefined, TemplateSyntaxError, UndefinedError
except ImportError:
    sys.exit("Missing dependency: pip install jinja2")

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent if SCRIPT_DIR.name == ".agent-system" else SCRIPT_DIR
CONFIG_PATH = ROOT / "project.config.yaml"
TEMPLATES_DIR = (ROOT / ".agent-system/templates" if SCRIPT_DIR.name == ".agent-system"
                 else ROOT / ".templates")

JINJA_VAR_RE = re.compile(r"\{\{.+?\}\}|\{%.+?%\}")

def load_config(path: Path = None) -> dict:
    with open(path or CONFIG_PATH) as f:
        config = yaml.safe_load(f)
    if not isinstance(config, dict):
        raise ValueError("Project configuration must be a YAML mapping")
    project = config.get("project")
    if not isinstance(project, dict) or not isinstance(project.get("name"), str) or not project["name"].strip():
        raise ValueError("project.name must be a nonempty string")
    project.setdefault("description", "")
    if not isinstance(project["description"], str):
        raise ValueError("project.description must be a string")
    pipeline = config.setdefault("pipeline", {"stages": []})
    if not isinstance(pipeline, dict) or not isinstance(pipeline.get("stages", []), list):
        raise ValueError("pipeline.stages must be a list")
    pipeline.setdefault("stages", [])
    for stage in pipeline["stages"]:
        if not isinstance(stage, dict) or not isinstance(stage.get("name"), str) or not stage["name"].strip():
            raise ValueError("Each pipeline stage needs a nonempty name")
    config.setdefault("analytics_by_default", False)
    if not isinstance(config["analytics_by_default"], bool):
        raise ValueError("analytics_by_default must be a boolean")
    return config


def has_variables(text: str) -> bool:
    return bool(JINJA_VAR_RE.search(text))


def render_text(text: str, context: dict) -> str:
    env = Environment(
        loader=BaseLoader(),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )
    return env.from_string(text).render(**context)


def extract_variables(text: str) -> list[str]:
    return JINJA_VAR_RE.findall(text)


def collect_template_paths() -> list[Path]:
    """Resolve all glob patterns to actual files."""
    paths = []
    for pattern in TEMPLATE_GLOBS:
        paths.extend(ROOT.glob(pattern))
    for path in paths:
        assert_safe_path(path)
    return sorted(set(paths))


def assert_safe_path(path: Path) -> None:
    """Do not render through symlinks or outside the chosen project."""
    rel = path.relative_to(ROOT)
    cursor = ROOT
    for part in rel.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError(f"Refusing symlink in framework path: {cursor}")


def template_backup_path(source: Path) -> Path:
    """Map a source file to the canonical template location for this checkout."""
    return TEMPLATES_DIR / source.relative_to(ROOT)


def discover_templates() -> list[tuple[Path, Path]]:
    """Return (template_source, output_target) pairs.

    Priority: if the main file has Jinja2 variables (e.g. freshly synced),
    use it as source and update the canonical template. Otherwise fall back to
    tracked downstream templates (or the framework development cache).
    """
    pairs = []

    if TEMPLATES_DIR.exists():
        for target in collect_template_paths():
            backup = template_backup_path(target)
            assert_safe_path(backup)
            target_text = target.read_text()
            if has_variables(target_text):
                pairs.append((target, target))
            elif backup.exists():
                pairs.append((backup, target))
    else:
        for path in collect_template_paths():
            if has_variables(path.read_text()):
                pairs.append((path, path))

    return pairs


def save_template(source: Path) -> None:
    """Save source as the canonical template backup, always overwriting."""
    backup = template_backup_path(source)
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, backup)


def cmd_render(config: dict, dry_run: bool = False) -> list[dict]:
    results = []
    pairs = discover_templates()
    pending = []

    if not pairs:
        return results

    for source, target in pairs:
        source_text = source.read_text()
        variables = extract_variables(source_text)
        rel = target.relative_to(ROOT)
        entry = {"file": str(rel), "variables": len(variables), "status": "ok"}

        try:
            rendered = render_text(source_text, config)
        except UndefinedError as e:
            entry["status"] = "error"
            entry["error"] = f"Undefined variable: {e}"
            results.append(entry)
            continue
        except TemplateSyntaxError as e:
            entry["status"] = "error"
            entry["error"] = f"Syntax error: {e}"
            results.append(entry)
            continue

        pending.append((source, target, rendered))
        results.append(entry)

    # Validate the entire batch before the first write.
    if not dry_run and not any(r["status"] == "error" for r in results):
        for source, target, rendered in pending:
            assert_safe_path(target)
            assert_safe_path(template_backup_path(target))
        for source, target, rendered in pending:
            if source == target:
                save_template(source)
            target.write_text(rendered)
    return results


def cmd_restore() -> list[str]:
    if not TEMPLATES_DIR.exists():
        return []

    restored = []
    # Restore only current framework-owned templates, never arbitrary backups.
    pairs = [(template_backup_path(target), target) for target in collect_template_paths()
             if template_backup_path(target).exists()]
    for backup, target in pairs:
        assert_safe_path(backup)
        assert_safe_path(target)
    for backup, target in pairs:
        rel = target.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup, target)
        restored.append(str(rel))
    return restored


def print_results(results: list[dict], dry_run: bool) -> None:
    errors = [r for r in results if r["status"] == "error"]
    ok = [r for r in results if r["status"] == "ok"]

    action = "Would render" if dry_run else "Rendered"
    if errors and not dry_run:
        action = "Validated (batch not written)"

    if ok:
        print(f"\n{action} {len(ok)} file(s):\n")
        for r in ok:
            print(f"  {'~' if dry_run else '✓'} {r['file']}  ({r['variables']} variable(s))")

    if errors:
        print(f"\nFailed {len(errors)} file(s):\n", file=sys.stderr)
        for r in errors:
            print(f"  ✗ {r['file']}: {r['error']}", file=sys.stderr)

    if not dry_run and ok and not errors:
        print(f"\nTemplates preserved in .templates/")
        script = ".agent-system/setup.py" if SCRIPT_DIR.name == ".agent-system" else "setup.py"
        print(f"Run `python {script} --restore` to get Jinja2 templates back.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render project templates from project.config.yaml",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help="dry-run: preview without writing")
    group.add_argument("--restore", action="store_true", help="restore original Jinja2 templates")
    args = parser.parse_args()

    if args.restore:
        restored = cmd_restore()
        if restored:
            print(f"Restored {len(restored)} template(s):\n")
            for name in restored:
                print(f"  ✓ {name}")
        else:
            print("No saved templates found. Nothing to restore.")
        return

    if not CONFIG_PATH.exists():
        sys.exit(f"Config not found: {CONFIG_PATH}")

    try:
        config = load_config()
    except (ValueError, yaml.YAMLError) as exc:
        sys.exit(f"Invalid config: {exc}")
    project_name = config.get("project", {}).get("name", "?")
    print(f"Config:  {CONFIG_PATH.name}")
    print(f"Project: {project_name}")

    results = cmd_render(config, dry_run=args.check)
    print_results(results, dry_run=args.check)

    if any(r["status"] == "error" for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
