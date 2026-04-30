#!/usr/bin/env python3
"""
Agent system audit: automated cross-project health checks.

Usage:
    python audit.py                       # full audit (all downstream projects)
    python audit.py --project /path       # audit a single project
    python audit.py --check version       # run a single check
    python audit.py --json                # machine-readable JSON output
    python audit.py --list-checks         # show available checks

Checks:
    version      Version drift across downstream projects
    integrity    Framework file integrity (detect manual edits)
    prompts      Prompt/file size analysis (token estimation)
    refs         Cross-reference validation (dead references)
    backlog      Task backlog health
    lessons      Cross-project lessons aggregation
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERSION_FILE = ROOT / "VERSION"
DOWNSTREAM_REGISTRY = ROOT / "downstream.projects"

FRAMEWORK_GLOBS = [
    "agents/*.md",
    "agents/discovery-modes/*.md",
    "agents/designer-modes/*.md",
    "agents/im-modes/*.md",
    "AGENTS.md",
    "CLAUDE.md",
    ".cursor/rules.md",
    "docs/AGENT_HANDOFF_CONTRACT.md",
    "docs/AGENT_EXECUTION_MODEL.md",
    "docs/MODEL_POLICY.md",
    "docs/MODEL_GATEWAY_SETUP.md",
    "docs/EXTERNAL_REVIEW_CONTRACT.md",
    "docs/SANDBOX_POLICY.md",
    "docs/PULL_REQUEST_CONTRACT.md",
    "docs/TASK_BACKLOG_AUTOMATION.md",
    "docs/ARCHITECTURE_GUARDRAILS.md",
    "docs/ARCHITECTURE_CHECKLIST.md",
    "docs/TASK_TEMPLATE.md",
    "docs/ONBOARDING.md",
    "docs/MCP_TOOLS.md",
    "docs/CLAUDE_SKILLS.md",
    "evals/README.md",
    "evals/tasks/*.md",
    "evals/expected/*.yaml",
    ".github/pull_request_template.md",
    ".github/workflows/agent-quality.yml",
    "setup.py",
    "requirements-framework.txt",
]

AVAILABLE_CHECKS = ["version", "integrity", "prompts", "refs", "backlog", "lessons"]

CHARS_PER_TOKEN = 4


def get_version() -> str:
    if VERSION_FILE.exists():
        return VERSION_FILE.read_text().strip()
    return "unknown"


def load_downstream_projects() -> list[Path]:
    if not DOWNSTREAM_REGISTRY.exists():
        return []
    projects = []
    for line in DOWNSTREAM_REGISTRY.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        path = Path(stripped).expanduser().resolve()
        if path.is_dir():
            projects.append(path)
    return projects


def collect_framework_files(root: Path) -> list[Path]:
    paths = []
    for pattern in FRAMEWORK_GLOBS:
        paths.extend(root.glob(pattern))
    return sorted(set(paths))


def estimate_tokens(text: str) -> int:
    return len(text) // CHARS_PER_TOKEN


def finding(fid: str, severity: str, category: str, title: str,
            description: str, files: list[str] = None, fix: str = None) -> dict:
    return {
        "id": fid,
        "severity": severity,
        "category": category,
        "title": title,
        "description": description,
        "files_affected": files or [],
        "proposed_fix": fix or "",
    }


# --- Checks ---

def check_version(projects: list[Path]) -> list[dict]:
    findings = []
    current = get_version()
    for project in projects:
        name = project.name
        ver_file = project / ".agent-system-version"
        if not ver_file.exists():
            findings.append(finding(
                f"V-{name}", "critical", "version_drift",
                f"{name}: no .agent-system-version",
                f"Project {project} has no .agent-system-version file. "
                "Framework may never have been synced.",
                [str(ver_file)],
                "Run: python sync.py --target " + str(project) + " --render",
            ))
            continue
        proj_ver = ver_file.read_text().strip()
        if proj_ver != current:
            findings.append(finding(
                f"V-{name}", "warning", "version_drift",
                f"{name}: version {proj_ver} (current: {current})",
                f"Project {project} is on framework version {proj_ver}, "
                f"but agent-system is at {current}.",
                [str(ver_file)],
                "Run: python sync.py --target " + str(project) + " --render",
            ))
    if not findings:
        findings.append(finding(
            "V-OK", "info", "version_drift",
            "All projects up to date",
            f"All {len(projects)} project(s) are on version {current}.",
        ))
    return findings


def check_integrity(projects: list[Path]) -> list[dict]:
    findings = []
    source_files = collect_framework_files(ROOT)

    for project in projects:
        name = project.name
        templates_dir = project / ".templates"

        for src in source_files:
            rel = src.relative_to(ROOT)
            tgt = project / rel
            if not tgt.exists():
                findings.append(finding(
                    f"I-{name}-{rel}", "warning", "integrity",
                    f"{name}: missing {rel}",
                    f"Framework file {rel} does not exist in {project}.",
                    [str(rel)],
                    f"Run: python sync.py --target {project} --render",
                ))
                continue

            backup = templates_dir / rel
            if backup.exists():
                src_text = src.read_text()
                backup_text = backup.read_text()
                if src_text != backup_text:
                    findings.append(finding(
                        f"I-{name}-{rel}", "info", "integrity",
                        f"{name}: template differs for {rel}",
                        f"Template backup for {rel} differs from source. "
                        "May indicate the project has an older template version.",
                        [str(rel)],
                        f"Run: python sync.py --target {project} --render",
                    ))

    if not findings:
        findings.append(finding(
            "I-OK", "info", "integrity",
            "Framework file integrity OK",
            f"All framework files present in {len(projects)} project(s).",
        ))
    return findings


def check_prompts(projects: list[Path]) -> tuple[list[dict], dict]:
    findings = []
    all_files = []

    scan_dirs = [ROOT] + projects
    for root_dir in scan_dirs:
        label = root_dir.name
        for pattern in ["agents/*.md", "agents/discovery-modes/*.md", "agents/im-modes/*.md", "AGENTS.md", "CLAUDE.md", ".cursor/rules.md"]:
            for f in root_dir.glob(pattern):
                text = f.read_text()
                tokens = estimate_tokens(text)
                lines = len(text.splitlines())
                all_files.append({
                    "project": label,
                    "file": str(f.relative_to(root_dir)),
                    "tokens_estimate": tokens,
                    "lines": lines,
                })

    all_files.sort(key=lambda x: x["tokens_estimate"], reverse=True)
    total = sum(f["tokens_estimate"] for f in all_files if f["project"] == ROOT.name)

    large = [f for f in all_files if f["tokens_estimate"] > 4000]
    for f in large:
        findings.append(finding(
            f"P-{f['project']}-{f['file']}", "warning", "prompt_size",
            f"{f['project']}/{f['file']}: ~{f['tokens_estimate']} tokens",
            f"File {f['file']} in {f['project']} is estimated at "
            f"~{f['tokens_estimate']} tokens ({f['lines']} lines). "
            "May cause context window pressure.",
            [f['file']],
            "Consider compressing or splitting this file.",
        ))

    prompt_health = {
        "total_framework_tokens": total,
        "largest_files": all_files[:10],
        "compression_opportunities": [
            f"{f['file']} ({f['project']}): ~{f['tokens_estimate']} tokens"
            for f in large
        ],
    }
    return findings, prompt_health


EXAMPLE_PATHS = {"docs/plans/ARCH-42.md", "docs/features/FEAT-42.md"}

HISTORICAL_FILES = {
    "docs/LESSONS_LEARNED.md",
    "docs/DECISIONS.md",
    "docs/KNOWN_PATTERNS.md",
}


def check_refs(root_dir: Path) -> list[dict]:
    """Check for dead file references in markdown files."""
    findings = []
    ref_pattern = re.compile(r"`((?:docs|agents|\.cursor)/[A-Za-z0-9_./\-]+\.(?:md|yaml|txt|py))`")

    md_files = list(root_dir.glob("agents/*.md")) + list(root_dir.glob("agents/discovery-modes/*.md")) + list(root_dir.glob("agents/im-modes/*.md")) + list(root_dir.glob("docs/*.md"))
    md_files += [root_dir / "AGENTS.md", root_dir / "CLAUDE.md"]
    md_files = [f for f in md_files if f.exists()]

    for md in md_files:
        text = md.read_text()
        refs = ref_pattern.findall(text)
        rel_md = str(md.relative_to(root_dir))
        for ref in refs:
            target = root_dir / ref
            if not target.exists():
                if ref in EXAMPLE_PATHS:
                    continue
                if rel_md in HISTORICAL_FILES:
                    continue
                findings.append(finding(
                    f"R-{rel_md}-{ref}", "warning", "dead_reference",
                    f"Dead reference: {ref} in {rel_md}",
                    f"File {rel_md} references `{ref}` but that file does not exist.",
                    [rel_md],
                    f"Update the reference in {rel_md} or create {ref}.",
                ))

    if not findings:
        findings.append(finding(
            "R-OK", "info", "dead_reference",
            "No dead references found",
            f"All file references in {root_dir.name} are valid.",
        ))
    return findings


def check_backlog(projects: list[Path]) -> list[dict]:
    findings = []
    task_line_re = re.compile(r"\|\s*(TASK-\d+)\s*\|([^|]*)\|([^|]*)\|")

    for project in projects:
        name = project.name
        tasks_file = project / "docs" / "TASKS.md"
        if not tasks_file.exists():
            findings.append(finding(
                f"B-{name}-missing", "warning", "backlog",
                f"{name}: no docs/TASKS.md",
                f"Project {project} has no TASKS.md file.",
                ["docs/TASKS.md"],
            ))
            continue

        text = tasks_file.read_text()
        tasks = task_line_re.findall(text)
        statuses = {}
        for task_id, title, status in tasks:
            statuses[task_id.strip()] = {
                "title": title.strip(),
                "status": status.strip().lower(),
            }

        stuck = [tid for tid, t in statuses.items()
                 if t["status"] in ("in_progress", "in_review")]
        if stuck:
            findings.append(finding(
                f"B-{name}-stuck", "warning", "backlog",
                f"{name}: {len(stuck)} task(s) stuck",
                f"Tasks {', '.join(stuck)} are in non-terminal status. "
                "May indicate stalled workflows.",
                ["docs/TASKS.md"],
                "Review these tasks and either complete or cancel them.",
            ))

        cancelled = [tid for tid, t in statuses.items() if t["status"] == "cancelled"]
        total = len(statuses)
        if total > 3 and len(cancelled) / total > 0.3:
            findings.append(finding(
                f"B-{name}-cancellation", "info", "backlog",
                f"{name}: high cancellation rate ({len(cancelled)}/{total})",
                f"{len(cancelled)} of {total} tasks are cancelled. "
                "May indicate scope definition issues.",
                ["docs/TASKS.md"],
            ))

    if not findings:
        findings.append(finding(
            "B-OK", "info", "backlog",
            "Task backlogs healthy",
            f"No stuck or problematic tasks across {len(projects)} project(s).",
        ))
    return findings


def check_lessons(projects: list[Path]) -> tuple[list[dict], list[dict]]:
    findings = []
    cross_patterns = []

    all_themes = {}
    for project in projects:
        name = project.name
        ll_file = project / "docs" / "LESSONS_LEARNED.md"
        if not ll_file.exists():
            continue
        text = ll_file.read_text()
        theme_lines = re.findall(r"^- (.+)$", text, re.MULTILINE)
        for theme in theme_lines:
            normalized = theme.strip().lower()
            if len(normalized) > 20:
                theme_projects = all_themes.setdefault(normalized, set())
                theme_projects.add(name)

    repeated = {theme: sorted(projs) for theme, projs in all_themes.items()
                if len(projs) > 1}
    for theme, projs in repeated.items():
        cross_patterns.append({
            "pattern": theme,
            "projects": list(projs),
            "recommendation": "This theme recurs across projects — consider a framework-level fix.",
        })

    if cross_patterns:
        findings.append(finding(
            "L-cross", "info", "lessons",
            f"{len(cross_patterns)} cross-project pattern(s) found",
            "Some lessons repeat across multiple projects, "
            "suggesting systemic issues that the framework should address.",
            fix="Review cross_project_patterns in the audit report.",
        ))

    return findings, cross_patterns


# --- Main ---

def run_audit(projects: list[Path], checks: list[str] = None) -> dict:
    if checks is None:
        checks = AVAILABLE_CHECKS

    all_findings = []
    prompt_health = {}
    cross_patterns = []

    if "version" in checks:
        all_findings.extend(check_version(projects))

    if "integrity" in checks:
        all_findings.extend(check_integrity(projects))

    if "prompts" in checks:
        pf, ph = check_prompts(projects)
        all_findings.extend(pf)
        prompt_health = ph

    if "refs" in checks:
        all_findings.extend(check_refs(ROOT))
        for project in projects:
            all_findings.extend(check_refs(project))

    if "backlog" in checks:
        all_findings.extend(check_backlog(projects))

    if "lessons" in checks:
        lf, cp = check_lessons(projects)
        all_findings.extend(lf)
        cross_patterns = cp

    critical = sum(1 for f in all_findings if f["severity"] == "critical")
    warnings = sum(1 for f in all_findings if f["severity"] == "warning")
    info = sum(1 for f in all_findings if f["severity"] == "info")

    return {
        "audit_date": __import__("datetime").date.today().isoformat(),
        "framework_version": get_version(),
        "projects_audited": [p.name for p in projects],
        "summary": {
            "critical": critical,
            "warnings": warnings,
            "info": info,
            "total": len(all_findings),
        },
        "findings": all_findings,
        "prompt_health": prompt_health,
        "cross_project_patterns": cross_patterns,
    }


def print_human(report: dict) -> None:
    s = report["summary"]
    print(f"\n{'=' * 60}")
    print(f"  Agent System Audit — {report['audit_date']}")
    print(f"  Framework version: {report['framework_version']}")
    print(f"  Projects: {', '.join(report['projects_audited']) or 'none'}")
    print(f"  Findings: {s['critical']} critical, {s['warnings']} warning, {s['info']} info")
    print(f"{'=' * 60}")

    for f in report["findings"]:
        icon = {"critical": "✗", "warning": "⚠", "info": "·"}.get(f["severity"], "?")
        print(f"\n  {icon} [{f['severity'].upper()}] {f['title']}")
        print(f"    {f['description']}")
        if f["proposed_fix"]:
            print(f"    Fix: {f['proposed_fix']}")

    ph = report.get("prompt_health", {})
    if ph:
        print(f"\n{'─' * 60}")
        print(f"  Prompt health")
        print(f"    Total framework tokens (estimate): {ph.get('total_framework_tokens', '?')}")
        top = ph.get("largest_files", [])[:5]
        if top:
            print(f"    Largest files:")
            for f in top:
                print(f"      {f['file']} ({f['project']}): ~{f['tokens_estimate']} tokens, {f['lines']} lines")
        opps = ph.get("compression_opportunities", [])
        if opps:
            print(f"    Compression opportunities: {len(opps)}")

    cps = report.get("cross_project_patterns", [])
    if cps:
        print(f"\n{'─' * 60}")
        print(f"  Cross-project patterns ({len(cps)}):")
        for cp in cps:
            print(f"    • {cp['pattern'][:80]}")
            print(f"      Projects: {', '.join(cp['projects'])}")

    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Agent system audit: automated cross-project health checks.",
    )
    parser.add_argument(
        "--project", type=Path,
        help="Audit a single project (instead of all downstream)",
    )
    parser.add_argument(
        "--check", choices=AVAILABLE_CHECKS,
        help="Run a single check only",
    )
    parser.add_argument(
        "--json", action="store_true", dest="json_output",
        help="Output as JSON",
    )
    parser.add_argument(
        "--list-checks", action="store_true",
        help="List available checks and exit",
    )
    args = parser.parse_args()

    if args.list_checks:
        print("Available checks:")
        for check in AVAILABLE_CHECKS:
            print(f"  {check}")
        return

    if args.project:
        projects = [args.project.resolve()]
    else:
        projects = load_downstream_projects()
        if not projects:
            print("No downstream projects registered in downstream.projects.")
            print("Use --project /path to audit a specific project.")
            return

    checks = [args.check] if args.check else None
    report = run_audit(projects, checks)

    if args.json_output:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_human(report)


if __name__ == "__main__":
    main()
