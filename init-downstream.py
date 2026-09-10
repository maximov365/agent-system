#!/usr/bin/env python3
"""Initialize a portable downstream, safely serializing names and paths."""

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

from setup import load_config
from sync import ROOT, DOWNSTREAM_REGISTRY, atomic_write, cmd_sync, safe_path


def initialize(name: str, target: Path, register: bool = True) -> bool:
    if not name.strip():
        raise ValueError("Project name must be nonempty")
    target = target.expanduser().resolve()
    if "\n" in str(target) or "\r" in str(target):
        raise ValueError("Project path cannot contain a newline")
    if target == ROOT or ((target / "sync.py").exists() and (target / "framework_manifest.py").exists()):
        raise ValueError("Choose a downstream folder, not the framework checkout")
    if (target / ".git").exists():
        remote = subprocess.run(["git", "-C", str(target), "remote", "get-url", "origin"],
                                capture_output=True, text=True)
        if remote.returncode == 0 and remote.stdout.strip().rstrip("/").removesuffix(".git").endswith("/agent-system"):
            raise ValueError("Target is a framework clone/worktree")
    target.mkdir(parents=True, exist_ok=True)
    config_path = safe_path(target, Path("project.config.yaml"))
    if config_path.exists():
        config = load_config(config_path)
        if config["project"]["name"] != name:
            raise ValueError(f"Target already belongs to {config['project']['name']!r}")
    else:
        config = {
            "project": {"name": name, "description": "Describe the intended product and audience."},
            "pipeline": {"stages": []},
            "analytics_by_default": False,
            "domain_rules": {},
            "output_docs": {"has_brand_guide": False, "custom_docs": []},
        }
        atomic_write(config_path, yaml.safe_dump(config, sort_keys=False, allow_unicode=True).encode())
    if not cmd_sync(target, render=True):
        return False
    if register:
        current = DOWNSTREAM_REGISTRY.read_text() if DOWNSTREAM_REGISTRY.exists() else ""
        if str(target) not in current.splitlines():
            current += ("\n" if current and not current.endswith("\n") else "") + str(target) + "\n"
            atomic_write(DOWNSTREAM_REGISTRY, current.encode())
    print(f"Ready: {name} at {target}")
    print("Open this folder in Codex (or another supported client) and describe your idea.")
    print("Reconfigure with: python3 .agent-system/setup.py")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name")
    parser.add_argument("target", type=Path, nargs="?", default=Path.cwd())
    parser.add_argument("--no-register", action="store_true", help="Useful for isolated trials")
    args = parser.parse_args()
    try:
        if not initialize(args.name, args.target, not args.no_register):
            sys.exit(1)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        sys.exit(f"Initialization failed: {exc}")


if __name__ == "__main__":
    main()
