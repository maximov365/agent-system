"""Shared ownership manifest for sync, render, audit, and framework hooks."""

from pathlib import Path

FRAMEWORK_GLOBS = [
    "agents/**/*.md", "AGENTS.md", "CLAUDE.md", ".cursor/rules.md",
    "docs/AGENT_HANDOFF_CONTRACT.md", "docs/AGENT_EXECUTION_MODEL.md",
    "docs/CODING_RULES.md", "docs/CODEX.md", "docs/VISUAL_QUALITY.md",
    "docs/GAME_DEVELOPMENT.md", "docs/MODEL_POLICY.md",
    "docs/MODEL_GATEWAY_SETUP.md", "docs/EXTERNAL_REVIEW_CONTRACT.md",
    "docs/SANDBOX_POLICY.md", "docs/PULL_REQUEST_CONTRACT.md",
    "docs/TASK_BACKLOG_AUTOMATION.md", "docs/ARCHITECTURE_CHECKLIST.md",
    "docs/TASK_TEMPLATE.md", "docs/ONBOARDING.md", "docs/MCP_TOOLS.md",
    "docs/CLAUDE_SKILLS.md", "docs/MAST_MAPPING.md", "docs/FRAMEWORK_UPGRADE.md", "docs/VISUAL_RUNNER.md", "docs/ASSET_LIBRARY.md", "docs/QUALITY_PROFILES.md", "docs/WORK_METHODS.md",
    "evals/README.md", "evals/tasks/*.md", "evals/expected/*.yaml",
    "templates/codex/config.toml",
]

# Project-owned once created. Never include these in FRAMEWORK_GLOBS.
SEED_GLOBS = [
    "docs/PRD.md", "docs/ARCHITECTURE.md", "docs/ARCHITECTURE_GUARDRAILS.md",
    "docs/PIPELINE_CONTRACTS.md", "docs/DEPLOY_CONTRACTS.md",
    "docs/TASKS.md", "docs/DECISIONS.md", "docs/LESSONS_LEARNED.md",
    "docs/KNOWN_PATTERNS.md", "docs/FEATURE_MAP.md", "docs/BRAND.md",
    ".github/pull_request_template.md",
]

# Framework code lives in its own namespace downstream, avoiding app setup.py.
TOOL_DESTINATIONS = {
    "tools/profiles/profile.py": ".agent-system/profile.py",
    "setup.py": ".agent-system/setup.py",
    "framework_manifest.py": ".agent-system/framework_manifest.py",
    "requirements-framework.txt": ".agent-system/requirements.txt",
    "tools/visual/run.mjs": ".agent-system/visual/run.mjs",
    "tools/visual/package.json": ".agent-system/visual/package.json",
    "tools/visual/package-lock.json": ".agent-system/visual/package-lock.json",
    "tools/assets/assetlib.py": ".agent-system/assets/assetlib.py",
    "tools/assets/requirements.txt": ".agent-system/assets/requirements.txt",
}

# Only framework-owned files can be re-rendered. Project-owned seeds are
# rendered once by sync, then edited normally by the downstream project.
TEMPLATE_GLOBS = ["agents/*.md", "agents/**/*.md", "AGENTS.md", "CLAUDE.md",
                  "docs/AGENT_HANDOFF_CONTRACT.md", "docs/AGENT_EXECUTION_MODEL.md",
                  "docs/TASK_BACKLOG_AUTOMATION.md", "docs/TASK_TEMPLATE.md"]


def deployment_sources(root: Path) -> dict[Path, Path]:
    """Map destination paths to framework source files, excluding seeds."""
    files = {p.relative_to(root): p for pattern in FRAMEWORK_GLOBS
             for p in root.glob(pattern) if p.is_file()}
    # Keep missing explicit paths in the map so preflight/CI can detect them.
    files.update({Path(pattern): root / pattern for pattern in FRAMEWORK_GLOBS
                  if not any(char in pattern for char in "*?[")})
    files.update({Path(".agent-system/templates") / dst: src for dst, src in list(files.items())
                  if (dst.parts[0] == "agents" and dst.suffix == ".md")
                  or any(dst.match(pattern) for pattern in TEMPLATE_GLOBS)})
    files.update({Path(dst): root / src for src, dst in TOOL_DESTINATIONS.items()})
    return dict(sorted(files.items()))


def seed_sources(root: Path) -> dict[Path, Path]:
    return {p.relative_to(root): p for pattern in SEED_GLOBS
            for p in root.glob(pattern) if p.is_file()}


def framework_change_paths(root: Path) -> set[str]:
    """Tracked source names including tooling and CI (for version hooks)."""
    files = set(deployment_sources(root).values()) | set(seed_sources(root).values())
    files.update(root / name for name in ["sync.py", "audit.py", "init-downstream.py",
                                        "init-downstream.sh", "framework_manifest.py", "sync_transaction.py",
                                        "migrations/legacy-files.json", "templates/migrations/legacy-setup.py", "requirements-dev.txt",
                                        ".github/workflows/agent-quality.yml"])
    files.update(root.glob("tests/*.py"))
    return {str(p.relative_to(root)) for p in files}


def is_framework_change(name: str) -> bool:
    """Match deployed changes, excluding project history replaced by fixed seeds."""
    if name in {"docs/TASKS.md", "docs/DECISIONS.md", "docs/LESSONS_LEARNED.md", "docs/KNOWN_PATTERNS.md"}:
        return False
    path = Path(name)
    if path.parts and path.parts[0] == "agents" and path.suffix == ".md":
        return True
    patterns = FRAMEWORK_GLOBS + SEED_GLOBS + ["agents/*.md", "tests/*.py", "tools/**/*.py", "tools/**/*.mjs", "evals/*.py", "evals/fixtures/**/*", "evals/graders/*.py"]
    return (any(path.match(pattern) for pattern in patterns)
            or name in TOOL_DESTINATIONS
            or name in {"sync.py", "audit.py", "init-downstream.py", "init-downstream.sh",
                        "sync_transaction.py", "migrations/legacy-files.json", "templates/migrations/legacy-setup.py", "requirements-dev.txt",
                        ".github/workflows/agent-quality.yml"})
