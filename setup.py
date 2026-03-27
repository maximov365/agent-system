#!/usr/bin/env python3
"""
Render agent Jinja2 templates using values from project.config.yaml.

Usage:
    python setup.py              # render all agent templates
    python setup.py --check      # dry-run — preview without writing
    python setup.py --restore    # restore original Jinja2 templates

First run saves originals to agents/.templates/ for safe re-rendering.
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Missing dependency: pip install pyyaml")

try:
    from jinja2 import Environment, BaseLoader, StrictUndefined, TemplateSyntaxError, UndefinedError
except ImportError:
    sys.exit("Missing dependency: pip install jinja2")

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "project.config.yaml"
AGENTS_DIR = ROOT / "agents"
TEMPLATES_DIR = AGENTS_DIR / ".templates"

JINJA_VAR_RE = re.compile(r"\{\{.+?\}\}")


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


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


def discover_templates() -> list[tuple[Path, Path]]:
    """Return (template_source, output_target) pairs."""
    pairs = []

    if TEMPLATES_DIR.exists():
        for tpl in sorted(TEMPLATES_DIR.glob("*.md")):
            pairs.append((tpl, AGENTS_DIR / tpl.name))
    else:
        for md in sorted(AGENTS_DIR.glob("*.md")):
            if has_variables(md.read_text()):
                pairs.append((md, md))

    return pairs


def save_template(source: Path) -> None:
    TEMPLATES_DIR.mkdir(exist_ok=True)
    dest = TEMPLATES_DIR / source.name
    if not dest.exists():
        shutil.copy2(source, dest)


def cmd_render(config: dict, dry_run: bool = False) -> list[dict]:
    results = []
    pairs = discover_templates()

    if not pairs:
        print("No templates found.")
        return results

    for source, target in pairs:
        source_text = source.read_text()
        variables = extract_variables(source_text)
        entry = {"file": target.name, "variables": len(variables), "status": "ok"}

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

        if not dry_run:
            if source.parent != TEMPLATES_DIR:
                save_template(source)
            target.write_text(rendered)

        results.append(entry)

    return results


def cmd_restore() -> list[str]:
    if not TEMPLATES_DIR.exists():
        return []

    restored = []
    for tpl in sorted(TEMPLATES_DIR.glob("*.md")):
        shutil.copy2(tpl, AGENTS_DIR / tpl.name)
        restored.append(tpl.name)
    return restored


def print_results(results: list[dict], dry_run: bool) -> None:
    errors = [r for r in results if r["status"] == "error"]
    ok = [r for r in results if r["status"] == "ok"]

    action = "Would render" if dry_run else "Rendered"

    if ok:
        print(f"\n{action} {len(ok)} file(s):\n")
        for r in ok:
            print(f"  {'~' if dry_run else '✓'} {r['file']}  ({r['variables']} variable(s))")

    if errors:
        print(f"\nFailed {len(errors)} file(s):\n", file=sys.stderr)
        for r in errors:
            print(f"  ✗ {r['file']}: {r['error']}", file=sys.stderr)

    if not dry_run and ok:
        print(f"\nTemplates preserved in {TEMPLATES_DIR.relative_to(ROOT)}/")
        print("Run `python setup.py --restore` to get Jinja2 templates back.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render agent templates from project.config.yaml",
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

    config = load_config()
    project_name = config.get("project", {}).get("name", "?")
    print(f"Config:  {CONFIG_PATH.name}")
    print(f"Project: {project_name}")

    results = cmd_render(config, dry_run=args.check)
    print_results(results, dry_run=args.check)

    if any(r["status"] == "error" for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
