#!/usr/bin/env python3
"""
Unfolda instance test — verifies that rendering project.config.yaml
through agent templates produces correct output.

Three layers of verification:
  1. Content assertions      — key strings present in rendered output
  2. Template hygiene        — no unresolved {{ }} variables remain
  3. Idempotent re-render    — restore → render produces identical output

Usage:
    python test_setup.py
"""

import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AGENTS_DIR = ROOT / "agents"
TEMPLATES_DIR = ROOT / ".templates"
SETUP_PY = ROOT / "setup.py"

JINJA_VAR_RE = re.compile(r"\{\{.+?\}\}")

RENDERED_GLOBS = [
    "agents/*.md",
    "CLAUDE.md",
    "AGENTS.md",
    ".cursor/rules.md",
    "docs/AGENT_HANDOFF_CONTRACT.md",
    "docs/AGENT_EXECUTION_MODEL.md",
    "docs/TASK_BACKLOG_AUTOMATION.md",
    "docs/ARCHITECTURE_GUARDRAILS.md",
    "docs/TASK_TEMPLATE.md",
]

# ─── Content assertions ─────────────────────────────────────────────────
# Strings that MUST appear in each rendered file to confirm correct
# variable resolution. Maps relative path → list of expected substrings.

CONTENT_ASSERTIONS = {
    "agents/discovery.md": [
        "You are the Discovery agent for Unfolda.",
        "why this matters for Unfolda",
    ],
    "agents/product.md": [
        "You are the Product agent for Unfolda.",
        "ingestion → segmentation → translation → formatting → export",
        "Unfolda's core value",
    ],
    "agents/analytics-architect.md": [
        "You are the Analytics Architect agent for Unfolda.",
        "ingestion | segmentation | translation | formatting | export",
    ],
    "agents/architect.md": [
        "You are the Architect agent for Unfolda.",
        "ingestion → segmentation → translation → formatting → export",
    ],
    "agents/builder.md": [
        "You are the Builder agent for Unfolda.",
        "ingestion → segmentation → translation → formatting → export",
    ],
    "agents/analytics-validator.md": [
        "You are the Analytics Validator agent for Unfolda.",
        "ingestion | segmentation | translation | formatting | export",
    ],
    "agents/reviewer.md": [
        "You are the Reviewer agent for Unfolda.",
        "ingestion → segmentation → translation → formatting → export",
    ],
    "agents/spec-reviewer.md": [
        "You are the Spec Reviewer agent for Unfolda.",
    ],
    "agents/reviser.md": [
        "You are the Reviser agent for Unfolda.",
    ],
    "agents/gatekeeper.md": [
        "You are the Gatekeeper agent for Unfolda.",
    ],
    "agents/iteration-manager.md": [
        "You are the Iteration Manager for Unfolda.",
    ],
    "agents/security-reviewer.md": [
        "You are the Security Reviewer agent for Unfolda.",
    ],
    "agents/test-strategist.md": [
        "You are the Test Strategist agent for Unfolda.",
    ],
    "agents/designer.md": [
        "You are the Designer agent for Unfolda.",
    ],
    "agents/README.md": [
        "Unfolda",
        "ingestion → segmentation → translation → formatting → export",
    ],
    "CLAUDE.md": [
        "Unfolda",
    ],
    "AGENTS.md": [
        "Unfolda",
        "ingestion → segmentation → translation → formatting → export",
    ],
    "docs/ARCHITECTURE_GUARDRAILS.md": [
        "Unfolda",
    ],
    "docs/TASK_BACKLOG_AUTOMATION.md": [
        "Unfolda",
    ],
}

# Files that must exist after rendering (relative to ROOT).
EXPECTED_FILES = [
    "agents/README.md",
    "agents/discovery.md",
    "agents/product.md",
    "agents/analytics-architect.md",
    "agents/analytics-validator.md",
    "agents/architect.md",
    "agents/builder.md",
    "agents/reviewer.md",
    "agents/spec-reviewer.md",
    "agents/reviser.md",
    "agents/gatekeeper.md",
    "agents/iteration-manager.md",
    "agents/security-reviewer.md",
    "agents/test-strategist.md",
    "agents/designer.md",
    "CLAUDE.md",
    "AGENTS.md",
    ".cursor/rules.md",
    "docs/AGENT_HANDOFF_CONTRACT.md",
    "docs/AGENT_EXECUTION_MODEL.md",
    "docs/TASK_BACKLOG_AUTOMATION.md",
    "docs/ARCHITECTURE_GUARDRAILS.md",
    "docs/TASK_TEMPLATE.md",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect_rendered_files() -> list[Path]:
    paths = []
    for pattern in RENDERED_GLOBS:
        paths.extend(ROOT.glob(pattern))
    return sorted(set(paths))


def run_setup(*args: str) -> None:
    result = subprocess.run(
        [sys.executable, str(SETUP_PY), *args],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    if result.returncode != 0:
        print(f"setup.py {' '.join(args)} failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(2)


def test_expected_files_exist() -> list[str]:
    """Verify all expected rendered files exist."""
    failures = []
    for rel in EXPECTED_FILES:
        path = ROOT / rel
        if not path.exists():
            failures.append(f"  MISSING  {rel}")
    return failures


def test_content_assertions() -> list[str]:
    """Key Unfolda-specific strings present in rendered output."""
    failures = []
    for rel_path, expected_strings in sorted(CONTENT_ASSERTIONS.items()):
        path = ROOT / rel_path
        if not path.exists():
            failures.append(f"  MISSING  {rel_path}")
            continue
        content = path.read_text()
        for s in expected_strings:
            if s not in content:
                failures.append(f"  NOT FOUND in {rel_path}: {s!r}")
    return failures


def test_no_unresolved_variables() -> list[str]:
    """No {{ jinja2 }} variables left in rendered output."""
    failures = []
    for path in collect_rendered_files():
        rel = path.relative_to(ROOT)
        content = path.read_text()
        found = JINJA_VAR_RE.findall(content)
        if found:
            failures.append(f"  UNRESOLVED in {rel}: {found}")
    return failures


def test_templates_preserved() -> list[str]:
    """Verify .templates/ exists and contains Jinja2 source."""
    failures = []
    if not TEMPLATES_DIR.exists():
        failures.append("  .templates/ directory missing")
        return failures
    for path in collect_rendered_files():
        rel = path.relative_to(ROOT)
        tpl = TEMPLATES_DIR / rel
        if not tpl.exists():
            continue
        if not JINJA_VAR_RE.search(tpl.read_text()):
            failures.append(f"  NO VARIABLES in template: {rel}")
    return failures


def test_idempotent_rerender() -> list[str]:
    """Verify restore → render cycle produces identical output."""
    before = {}
    for path in collect_rendered_files():
        rel = path.relative_to(ROOT)
        before[str(rel)] = sha256(path)

    run_setup("--restore")
    run_setup()

    after = {}
    for path in collect_rendered_files():
        rel = path.relative_to(ROOT)
        after[str(rel)] = sha256(path)

    failures = []
    for name in sorted(set(before) | set(after)):
        h_before = before.get(name)
        h_after = after.get(name)
        if h_before != h_after:
            failures.append(
                f"  CHANGED after re-render: {name}\n"
                f"           before: {h_before}\n"
                f"           after:  {h_after}"
            )
    return failures


def main() -> None:
    print("=" * 60)
    print("Unfolda instance test")
    print("=" * 60)

    all_passed = True
    tests = [
        ("Expected files exist",        test_expected_files_exist),
        ("Content assertions",          test_content_assertions),
        ("No unresolved variables",     test_no_unresolved_variables),
        ("Templates preserved",         test_templates_preserved),
        ("Idempotent re-render",        test_idempotent_rerender),
    ]

    for name, test_fn in tests:
        failures = test_fn()
        if failures:
            print(f"\nFAIL  {name}")
            for f in failures:
                print(f)
            all_passed = False
        else:
            print(f"\nPASS  {name}")

    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED")
        print("=" * 60)
    else:
        print("SOME TESTS FAILED")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
