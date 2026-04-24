#!/usr/bin/env python3
"""
Framework metrics: snapshot + append-only history.

Phase 1 — what we can compute now (no IM instrumentation needed):
- Portfolio: active downstreams, version drift, project maturity
- Knowledge: LESSONS_LEARNED and KNOWN_PATTERNS growth
- Framework velocity: commits per week, version bumps per month
- Health: audit.py findings summary

Phase 2 (planned) will add per-workflow telemetry from Iteration Manager:
- Workflow completion rate
- Quality loop iterations
- Builder cycles per task
- Token cost per workflow

Usage:
    python3 metrics.py                # snapshot to stdout + write docs/METRICS.md
    python3 metrics.py --json         # machine-readable JSON snapshot to stdout
    python3 metrics.py --append       # also append snapshot to docs/METRICS_HISTORY.jsonl
    python3 metrics.py --history 10   # show last N snapshots from history
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERSION_FILE = ROOT / "VERSION"
DOWNSTREAM_REGISTRY = ROOT / "downstream.projects"
METRICS_MD = ROOT / "docs" / "METRICS.md"
HISTORY_JSONL = ROOT / "docs" / "METRICS_HISTORY.jsonl"

# Thresholds for tier 1 alerts
THRESHOLDS = {
    "version_drift_minor": 1,    # 1 version behind = info
    "version_drift_major": 3,    # 3+ versions behind = warning
    "stub_doc_min_words": 50,    # < 50 words = considered stub
}


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_version() -> str:
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else "unknown"


def parse_semver(v: str) -> tuple[int, int, int]:
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)", v)
    return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)


def semver_distance(a: str, b: str) -> int:
    """Return how many patch versions a is behind b (positive = behind)."""
    pa, pb = parse_semver(a), parse_semver(b)
    if pa[0] != pb[0]:
        return (pb[0] - pa[0]) * 1000  # major version drift = huge
    if pa[1] != pb[1]:
        return (pb[1] - pa[1]) * 100   # minor drift = large
    return pb[2] - pa[2]


def read_downstream_registry() -> list[str]:
    if not DOWNSTREAM_REGISTRY.exists():
        return []
    paths = []
    for line in DOWNSTREAM_REGISTRY.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            paths.append(line)
    return paths


def compute_portfolio(framework_version: str) -> dict:
    """Active downstream projects + version drift."""
    paths = read_downstream_registry()
    projects = []
    for p in paths:
        proj = Path(p)
        info = {"path": str(p), "exists": proj.exists()}
        if not proj.exists():
            info["status"] = "missing"
            projects.append(info)
            continue

        ver_file = proj / ".agent-system-version"
        info["version"] = ver_file.read_text().strip() if ver_file.exists() else "unknown"
        info["drift"] = semver_distance(info["version"], framework_version) \
            if info["version"] != "unknown" else None

        # Project name from config
        cfg = proj / "project.config.yaml"
        if cfg.exists():
            m = re.search(r'name:\s*"([^"]+)"', cfg.read_text())
            info["name"] = m.group(1) if m else "unknown"

        # Maturity check — is PRD a stub or filled?
        prd = proj / "docs" / "PRD.md"
        if prd.exists():
            words = len(prd.read_text().split())
            info["maturity"] = (
                "stub" if words < THRESHOLDS["stub_doc_min_words"]
                else "filled"
            )
            info["prd_words"] = words
        else:
            info["maturity"] = "no_prd"

        projects.append(info)

    return {
        "registered_count": len(paths),
        "active_count": sum(1 for p in projects if p.get("exists")),
        "missing_count": sum(1 for p in projects if not p.get("exists")),
        "drift_summary": Counter(
            "current" if p.get("drift") == 0
            else "behind_minor" if p.get("drift", 0) <= THRESHOLDS["version_drift_minor"]
            else "behind_warning" if p.get("drift", 0) < THRESHOLDS["version_drift_major"]
            else "behind_major"
            for p in projects if p.get("exists") and p.get("drift") is not None
        ),
        "maturity_summary": Counter(p.get("maturity", "unknown") for p in projects if p.get("exists")),
        "projects": projects,
    }


def compute_knowledge() -> dict:
    """Count items in LESSONS_LEARNED + KNOWN_PATTERNS, plus recent growth."""
    lessons_file = ROOT / "docs" / "LESSONS_LEARNED.md"
    patterns_file = ROOT / "docs" / "KNOWN_PATTERNS.md"

    def count_entries(path: Path, marker: str) -> int:
        if not path.exists():
            return 0
        return sum(1 for line in path.read_text().splitlines() if line.startswith(marker))

    def recent_additions(path: Path, days: int) -> int:
        """Count lines added to file in last N days via git log."""
        if not path.exists():
            return 0
        try:
            since = (dt.datetime.now() - dt.timedelta(days=days)).strftime("%Y-%m-%d")
            r = subprocess.run(
                ["git", "log", f"--since={since}", "--numstat", "--pretty=tformat:", "--", str(path.relative_to(ROOT))],
                capture_output=True, text=True, cwd=str(ROOT), timeout=10,
            )
            total = 0
            for line in r.stdout.strip().splitlines():
                parts = line.split("\t")
                if len(parts) >= 1 and parts[0].isdigit():
                    total += int(parts[0])
            return total
        except Exception:
            return 0

    return {
        "lessons_total": count_entries(lessons_file, "## "),
        "patterns_total": count_entries(patterns_file, "## Pattern"),
        "lessons_added_lines_7d": recent_additions(lessons_file, 7),
        "lessons_added_lines_30d": recent_additions(lessons_file, 30),
        "patterns_added_lines_7d": recent_additions(patterns_file, 7),
        "patterns_added_lines_30d": recent_additions(patterns_file, 30),
    }


def compute_framework_velocity() -> dict:
    """Git log analysis: commits per week, version bumps per month."""
    try:
        # Commits in last 7 / 30 days
        def commit_count(days: int) -> int:
            since = (dt.datetime.now() - dt.timedelta(days=days)).strftime("%Y-%m-%d")
            r = subprocess.run(
                ["git", "log", f"--since={since}", "--oneline"],
                capture_output=True, text=True, cwd=str(ROOT), timeout=10,
            )
            return len([l for l in r.stdout.strip().splitlines() if l])

        # Version bumps in last 30 / 90 days (count VERSION file changes)
        def version_bumps(days: int) -> int:
            since = (dt.datetime.now() - dt.timedelta(days=days)).strftime("%Y-%m-%d")
            r = subprocess.run(
                ["git", "log", f"--since={since}", "--oneline", "--", "VERSION"],
                capture_output=True, text=True, cwd=str(ROOT), timeout=10,
            )
            return len([l for l in r.stdout.strip().splitlines() if l])

        return {
            "commits_7d": commit_count(7),
            "commits_30d": commit_count(30),
            "version_bumps_30d": version_bumps(30),
            "version_bumps_90d": version_bumps(90),
        }
    except Exception as e:
        return {"error": str(e)}


def compute_evolution_log_stats() -> dict:
    """AI Landscape Review activity from docs/EVOLUTION_LOG.md."""
    log = ROOT / "docs" / "EVOLUTION_LOG.md"
    if not log.exists():
        return {"reviews_total": 0, "exists": False}
    txt = log.read_text()
    review_count = len(re.findall(r"^## AI Landscape Review", txt, re.M))
    findings = len(re.findall(r"^#### F\d+:", txt, re.M))
    return {
        "exists": True,
        "reviews_total": review_count,
        "findings_logged": findings,
    }


def run_audit_summary() -> dict:
    """Invoke audit.py and store only counts/summary (not full payload)."""
    audit = ROOT / "audit.py"
    if not audit.exists():
        return {"available": False}
    try:
        r = subprocess.run(
            ["python3", str(audit), "--json"],
            capture_output=True, text=True, cwd=str(ROOT), timeout=30,
        )
        if r.returncode != 0:
            return {"available": True, "error": "audit.py failed", "stderr": r.stderr[:200]}
        try:
            data = json.loads(r.stdout)
        except json.JSONDecodeError:
            return {"available": True, "error": "audit.py output not JSON"}

        # Summarize: count findings by check, not the full payload
        summary = {"available": True, "checks_run": 0, "findings_total": 0}
        if isinstance(data, dict):
            for check_name, check_data in data.items():
                summary["checks_run"] += 1
                if isinstance(check_data, dict):
                    findings = check_data.get("findings") or check_data.get("issues") or []
                    if isinstance(findings, list):
                        summary["findings_total"] += len(findings)
                        summary[f"{check_name}_findings"] = len(findings)
                elif isinstance(check_data, list):
                    summary["findings_total"] += len(check_data)
                    summary[f"{check_name}_findings"] = len(check_data)
        return summary
    except Exception as e:
        return {"available": False, "error": str(e)}


def collect_snapshot() -> dict:
    framework_version = read_version()
    return {
        "ts": utc_now_iso(),
        "framework_version": framework_version,
        "portfolio": compute_portfolio(framework_version),
        "knowledge": compute_knowledge(),
        "velocity": compute_framework_velocity(),
        "evolution_log": compute_evolution_log_stats(),
        "health": run_audit_summary(),
        "phase2_pending": [
            "workflow_completion_rate",
            "avg_quality_loop_iterations",
            "avg_builder_cycles",
            "token_cost_per_workflow",
        ],
    }


def render_markdown(s: dict) -> str:
    pf = s["portfolio"]
    kn = s["knowledge"]
    vel = s["velocity"]
    ev = s["evolution_log"]

    def drift_indicator(d: int | None) -> str:
        if d is None:
            return "?"
        if d == 0:
            return "✓ current"
        if d <= THRESHOLDS["version_drift_minor"]:
            return f"↓{d} (minor)"
        if d < THRESHOLDS["version_drift_major"]:
            return f"⚠ ↓{d} (warning)"
        return f"🚨 ↓{d} (major)"

    project_rows = "\n".join(
        f"| {p.get('name', '?')} | `{p['path']}` | {p.get('version', '?')} | {drift_indicator(p.get('drift'))} | {p.get('maturity', '?')} |"
        for p in pf["projects"] if p.get("exists")
    )

    missing_section = ""
    if pf["missing_count"]:
        missing_rows = "\n".join(
            f"- `{p['path']}` — registered but folder missing"
            for p in pf["projects"] if not p.get("exists")
        )
        missing_section = f"\n### Missing projects ({pf['missing_count']})\n\n{missing_rows}\n"

    return f"""# Framework Metrics

**Snapshot:** {s['ts']}
**Framework version:** {s['framework_version']}

This file is regenerated on every `python3 metrics.py` run. Append-only history is in `docs/METRICS_HISTORY.jsonl`. See `metrics.py` for the schema.

---

## Tier 1 — Portfolio

| Metric | Value |
|---|---|
| Registered downstreams | {pf['registered_count']} |
| Active (folder exists) | {pf['active_count']} |
| Missing | {pf['missing_count']} |
| Version-current projects | {pf['drift_summary'].get('current', 0)} |
| Behind minor (≤{THRESHOLDS['version_drift_minor']} ver) | {pf['drift_summary'].get('behind_minor', 0)} |
| Behind warning (<{THRESHOLDS['version_drift_major']} ver) | {pf['drift_summary'].get('behind_warning', 0)} |
| Behind major (≥{THRESHOLDS['version_drift_major']} ver) | {pf['drift_summary'].get('behind_major', 0)} |
| Maturity: filled | {pf['maturity_summary'].get('filled', 0)} |
| Maturity: stub | {pf['maturity_summary'].get('stub', 0)} |
| Maturity: no PRD | {pf['maturity_summary'].get('no_prd', 0)} |

### Active projects

| Name | Path | Version | Drift | PRD maturity |
|---|---|---|---|---|
{project_rows or "| _(none active)_ |  |  |  |  |"}
{missing_section}
---

## Tier 2 — Knowledge

| Metric | Value |
|---|---|
| LESSONS_LEARNED entries | {kn['lessons_total']} |
| KNOWN_PATTERNS entries | {kn['patterns_total']} |
| Lines added to LESSONS_LEARNED (7d) | {kn['lessons_added_lines_7d']} |
| Lines added to LESSONS_LEARNED (30d) | {kn['lessons_added_lines_30d']} |
| Lines added to KNOWN_PATTERNS (7d) | {kn['patterns_added_lines_7d']} |
| Lines added to KNOWN_PATTERNS (30d) | {kn['patterns_added_lines_30d']} |

---

## Tier 3 — Framework velocity

| Metric | Value |
|---|---|
| Commits (7d) | {vel.get('commits_7d', '?')} |
| Commits (30d) | {vel.get('commits_30d', '?')} |
| Version bumps (30d) | {vel.get('version_bumps_30d', '?')} |
| Version bumps (90d) | {vel.get('version_bumps_90d', '?')} |

---

## AI Landscape Review activity

| Metric | Value |
|---|---|
| Total reviews logged | {ev.get('reviews_total', 0)} |
| Findings logged | {ev.get('findings_logged', 0)} |

---

## Pending (Phase 2 — needs IM instrumentation)

These metrics require Iteration Manager to log per-workflow telemetry. Not available yet:

{chr(10).join(f"- `{m}`" for m in s['phase2_pending'])}

---

## Schema & methodology

- Active downstreams: registered in `downstream.projects` AND folder exists on disk
- Version drift: `<project>/.agent-system-version` vs framework `VERSION`
- Maturity: `filled` if `docs/PRD.md` has ≥{THRESHOLDS['stub_doc_min_words']} words
- Velocity: `git log` analysis on this repository
- Knowledge growth: lines added per file via `git log --numstat`
- AI Landscape: count of `## AI Landscape Review` headings in `docs/EVOLUTION_LOG.md`

Run `python3 metrics.py --json` for raw machine-readable output.
"""


def append_history(snapshot: dict) -> None:
    HISTORY_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with HISTORY_JSONL.open("a") as f:
        f.write(json.dumps(snapshot, default=str) + "\n")


def show_history(n: int) -> None:
    if not HISTORY_JSONL.exists():
        print("No history yet. Run `python3 metrics.py --append` first.")
        return
    lines = HISTORY_JSONL.read_text().strip().splitlines()
    recent = lines[-n:] if n > 0 else lines
    for line in recent:
        try:
            s = json.loads(line)
            pf = s.get("portfolio", {})
            print(f"{s['ts']} | v{s['framework_version']} | "
                  f"active={pf.get('active_count', '?')} "
                  f"current={pf.get('drift_summary', {}).get('current', '?')} "
                  f"commits_7d={s.get('velocity', {}).get('commits_7d', '?')}")
        except json.JSONDecodeError:
            print(f"  (corrupt line: {line[:80]}...)")


def main() -> int:
    ap = argparse.ArgumentParser(description="Framework metrics snapshot + history")
    ap.add_argument("--json", action="store_true", help="Output snapshot as JSON to stdout")
    ap.add_argument("--append", action="store_true", help="Append snapshot to docs/METRICS_HISTORY.jsonl")
    ap.add_argument("--history", type=int, metavar="N", help="Show last N history entries instead of taking snapshot")
    args = ap.parse_args()

    if args.history is not None:
        show_history(args.history)
        return 0

    snapshot = collect_snapshot()

    # Always write the markdown snapshot
    METRICS_MD.parent.mkdir(parents=True, exist_ok=True)
    METRICS_MD.write_text(render_markdown(snapshot))

    if args.append:
        append_history(snapshot)

    if args.json:
        print(json.dumps(snapshot, indent=2, default=str))
    else:
        # Brief human summary
        pf = snapshot["portfolio"]
        kn = snapshot["knowledge"]
        vel = snapshot["velocity"]
        print(f"=== Framework Metrics — {snapshot['ts']} ===")
        print(f"  Framework: v{snapshot['framework_version']}")
        print(f"  Portfolio: {pf['active_count']} active / {pf['registered_count']} registered "
              f"({pf['missing_count']} missing)")
        print(f"    Current version: {pf['drift_summary'].get('current', 0)}")
        print(f"    Behind:          {pf['drift_summary'].get('behind_minor', 0)} minor / "
              f"{pf['drift_summary'].get('behind_warning', 0)} warning / "
              f"{pf['drift_summary'].get('behind_major', 0)} major")
        print(f"  Knowledge: {kn['lessons_total']} lessons, {kn['patterns_total']} patterns "
              f"(+{kn['lessons_added_lines_7d']}/{kn['patterns_added_lines_7d']} lines past 7d)")
        print(f"  Velocity:  {vel.get('commits_7d', '?')} commits / 7d, "
              f"{vel.get('version_bumps_30d', '?')} version bumps / 30d")
        print(f"  Snapshot:  {METRICS_MD.relative_to(ROOT)}")
        if args.append:
            print(f"  Appended:  {HISTORY_JSONL.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
