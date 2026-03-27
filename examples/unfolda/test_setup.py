#!/usr/bin/env python3
"""
Unfolda instance test — verifies that rendering project.config.yaml
through agent templates produces output identical to the known-good
original files.

Three layers of verification:
  1. SHA-256 golden hashes   — byte-for-byte identity
  2. Content assertions      — key strings present in rendered output
  3. Template hygiene        — no unresolved {{ }} variables remain

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

# ─── Golden hashes ──────────────────────────────────────────────────────
# SHA-256 of each rendered agent file as produced by the original Unfolda
# config. Any change to config values, templates, or rendering logic
# will cause a mismatch here.

GOLDEN_HASHES = {
    "README.md":               "7518530074244366098b5f2292d5cdbe2e34e096a912a32ca38b457543ce86a0",
    "analytics-architect.md":  "785d02f0437db6ba172f44a548c3ac9c2196d8a4f5c00ae713270285ca04b56c",
    "analytics-validator.md":  "a4b92609e58537cdfca50ffd536b7e9b4504cf801bdd1fe6f2a87f1f168d297b",
    "architect.md":            "47c5141bb9456890089b7f4e9cad2bad22a111f71842247629ae6c94407c32ac",
    "builder.md":              "ca8122e9cdb2d0c21d8c110325b90c019ccd52e5bc84220c98a71acab484cd35",
    "discovery.md":            "7e17e09fedf546f86546e06c24503b41d109672282ccf239b12d47a4b8510d27",
    "gatekeeper.md":           "f4e6b279e2c091363d2251e02c4c926ffcc4a229e47484f38e8976bb16da90de",
    "iteration-manager.md":    "24148250e36242a7e10569deba68de823b0862a61b20258abcd2e514833eb125",
    "product.md":              "59838aec620add2bed3e8a9cd6171d35f59c2916a3093ceeeff4ab385f07615e",
    "reviewer.md":             "ab4de913e992d66f455f9d0a908e5ad4e806a90dbfe6fc28234d1eb9b1027835",
    "reviser.md":              "4a433371faafd82182102bcba7b234d61d8f44bdf212f8cbd7ffacb79045c21e",
    "spec-reviewer.md":        "416f9e0176aef8df227b230f74bd9a5798e3150eb9eaf3f6fbb87b1d1aaf8616",
}

# ─── Content assertions ─────────────────────────────────────────────────
# Strings that MUST appear in each rendered file to confirm correct
# variable resolution. Maps filename → list of expected substrings.

CONTENT_ASSERTIONS = {
    "README.md": [
        "# Unfolda",
        "Unfolda is a web-based SaaS service",
        "ingestion → segmentation → translation → formatting → export",
    ],
    "discovery.md": [
        "You are the Discovery agent for Unfolda.",
        "why this matters for Unfolda",
    ],
    "product.md": [
        "You are the Product agent for Unfolda.",
        "ingestion → segmentation → translation → formatting → export",
        "Unfolda's core value",
    ],
    "analytics-architect.md": [
        "You are the Analytics Architect agent for Unfolda.",
        "ingestion | segmentation | translation | formatting | export",
    ],
    "architect.md": [
        "You are the Architect agent for Unfolda.",
        "ingestion → segmentation → translation → formatting → export",
    ],
    "builder.md": [
        "You are the Builder agent for Unfolda.",
        "ingestion → segmentation → translation → formatting → export",
    ],
    "analytics-validator.md": [
        "You are the Analytics Validator agent for Unfolda.",
        "ingestion | segmentation | translation | formatting | export",
    ],
    "reviewer.md": [
        "You are the Reviewer agent for Unfolda.",
        "ingestion → segmentation → translation → formatting → export",
    ],
    "spec-reviewer.md": [
        "You are the Spec Reviewer agent for Unfolda.",
    ],
    "reviser.md": [
        "You are the Reviser agent for Unfolda.",
    ],
    "gatekeeper.md": [
        "You are the Gatekeeper agent for Unfolda.",
    ],
    "iteration-manager.md": [
        "You are the Iteration Manager for Unfolda.",
    ],
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def test_golden_hashes() -> list[str]:
    """Layer 1: byte-for-byte identity via SHA-256."""
    failures = []
    for filename, expected_hash in sorted(GOLDEN_HASHES.items()):
        path = AGENTS_DIR / filename
        if not path.exists():
            failures.append(f"  MISSING  {filename}")
            continue
        actual = sha256(path)
        if actual != expected_hash:
            failures.append(f"  MISMATCH {filename}\n"
                            f"           expected: {expected_hash}\n"
                            f"           actual:   {actual}")
    return failures


def test_content_assertions() -> list[str]:
    """Layer 2: key Unfolda-specific strings present."""
    failures = []
    for filename, expected_strings in sorted(CONTENT_ASSERTIONS.items()):
        path = AGENTS_DIR / filename
        if not path.exists():
            failures.append(f"  MISSING  {filename}")
            continue
        content = path.read_text()
        for s in expected_strings:
            if s not in content:
                failures.append(f"  NOT FOUND in {filename}: {s!r}")
    return failures


def test_no_unresolved_variables() -> list[str]:
    """Layer 3: no {{ jinja2 }} variables left in rendered output."""
    failures = []
    for path in sorted(AGENTS_DIR.glob("*.md")):
        if path.parent == TEMPLATES_DIR:
            continue
        content = path.read_text()
        found = JINJA_VAR_RE.findall(content)
        if found:
            failures.append(f"  UNRESOLVED in {path.name}: {found}")
    return failures


def test_templates_preserved() -> list[str]:
    """Verify .templates/ exists and contains Jinja2 source."""
    failures = []
    if not TEMPLATES_DIR.exists():
        failures.append("  .templates/ directory missing")
        return failures
    for filename in GOLDEN_HASHES:
        tpl = TEMPLATES_DIR / filename
        if not tpl.exists():
            failures.append(f"  MISSING template: {filename}")
            continue
        if not JINJA_VAR_RE.search(tpl.read_text()):
            failures.append(f"  NO VARIABLES in template: {filename}")
    return failures


def test_idempotent_rerender() -> list[str]:
    """Verify restore → render cycle produces identical output."""
    before = {f.name: sha256(f) for f in sorted(AGENTS_DIR.glob("*.md"))
              if f.parent != TEMPLATES_DIR}

    run_setup("--restore")
    run_setup()

    after = {f.name: sha256(f) for f in sorted(AGENTS_DIR.glob("*.md"))
             if f.parent != TEMPLATES_DIR}

    failures = []
    for name in sorted(set(before) | set(after)):
        h_before = before.get(name)
        h_after = after.get(name)
        if h_before != h_after:
            failures.append(f"  CHANGED after re-render: {name}\n"
                            f"           before: {h_before}\n"
                            f"           after:  {h_after}")
    return failures


def main() -> None:
    print("=" * 60)
    print("Unfolda instance test")
    print("=" * 60)

    all_passed = True
    tests = [
        ("Golden SHA-256 hashes",       test_golden_hashes),
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
