#!/usr/bin/env python3
"""Compatibility entry point for the former Agent System renderer."""

import runpy
import sys
from pathlib import Path

sys.dont_write_bytecode = True
renderer = Path(__file__).resolve().parent / ".agent-system" / "setup.py"
if not renderer.is_file():
    raise SystemExit("Framework renderer missing. Update Agent System before reconfiguring.")
sys.path.insert(0, str(renderer.parent))
print("Agent System: using .agent-system/setup.py (legacy entry point).")
runpy.run_path(str(renderer), run_name="__main__")
