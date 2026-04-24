#!/usr/bin/env python3
"""
Phase 2 metrics: workflow telemetry extracted from Claude Code session transcripts.

Reads ~/.claude/projects/-Users-dm-projects-*/*.jsonl, finds:
  - Handoff blocks (the JSON our agents emit at end of every output)
  - Token usage metadata per message

Computes per-project and aggregate:
  - Workflow completion rate (% of tasks reaching status=completed)
  - Avg quality_loop_iterations per workflow
  - Avg builder_cycle_count per workflow
  - Token cost per workflow (input + output + cache)

Privacy: extracts only handoff JSON and usage metadata. Does not read or store
user/assistant message content.

Usage:
    python3 metrics_workflow.py                    # JSON to stdout
    python3 metrics_workflow.py --project NAME     # filter to one project name
    python3 metrics_workflow.py --since-days 30    # only sessions modified in last N days
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

CLAUDE_PROJECTS = Path.home() / ".claude" / "projects"
PROJECT_PREFIX = "-Users-dm-projects-"  # encoded path prefix Claude Code uses

# Approximate per-token pricing (Claude Sonnet 4 — adjust if model changes)
# $3/M input, $15/M output, $0.30/M cache read, $3.75/M cache write (5min)
PRICING = {
    "input": 3.00,
    "output": 15.00,
    "cache_read": 0.30,
    "cache_write_5m": 3.75,
    "cache_write_1h": 6.00,
}


def project_name_from_dir(d: Path) -> str:
    """Decode Claude Code's project directory name back to a project name."""
    name = d.name
    if name.startswith(PROJECT_PREFIX):
        name = name[len(PROJECT_PREFIX):]
    # Replace --claude-worktrees-X with @worktree:X for clarity
    name = re.sub(r"--claude-worktrees-(.+)$", r" (worktree:\1)", name)
    return name.replace("-", " ").strip()


def find_session_files(since_days: int | None = None) -> list[tuple[str, Path]]:
    """Yield (project_name, jsonl_path) for all relevant sessions."""
    if not CLAUDE_PROJECTS.exists():
        return []
    cutoff = None
    if since_days is not None:
        cutoff = dt.datetime.now().timestamp() - (since_days * 86400)
    files = []
    for d in CLAUDE_PROJECTS.iterdir():
        if not d.name.startswith(PROJECT_PREFIX):
            continue
        for jsonl in d.glob("*.jsonl"):
            if cutoff and jsonl.stat().st_mtime < cutoff:
                continue
            files.append((project_name_from_dir(d), jsonl))
    return files


def extract_handoff_blocks(line: str) -> list[dict]:
    """
    Find handoff JSON blocks in a JSONL event line.

    Handoff blocks look like:
        ```json
        { "handoff": { "agent": "...", ... } }
        ```
    Embedded in assistant message content as a code block.
    """
    blocks = []
    # Quick filter
    if '"handoff"' not in line and "handoff" not in line:
        return blocks
    # Find all `{...}` JSON-ish substrings that look like handoff
    # Use a simple state machine: brace counter starting at "handoff" key
    # First convert escaped JSON-in-JSON (the message content itself is JSON-stringified)
    # Try the cheap route: find `\"handoff\": {` and extract through balanced braces
    for match in re.finditer(r'\\"handoff\\":\s*\\?{', line):
        start = match.start()
        # Find balanced braces from the opening { after "handoff":
        depth = 0
        i = match.end() - 1  # position of opening {
        while i < len(line):
            c = line[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    # Extract substring, unescape
                    raw = line[match.end() - 1:i + 1]
                    try:
                        unescaped = raw.replace('\\"', '"').replace("\\\\", "\\")
                        blocks.append(json.loads(unescaped))
                    except json.JSONDecodeError:
                        pass
                    break
            i += 1
    return blocks


def extract_usage(line: str) -> dict | None:
    """Find usage metadata (token counts) in a JSONL event."""
    if '"usage":' not in line:
        return None
    try:
        # Find first usage object
        m = re.search(r'"usage":\s*({[^{}]*(?:{[^{}]*}[^{}]*)*})', line)
        if not m:
            return None
        return json.loads(m.group(1))
    except (json.JSONDecodeError, AttributeError):
        return None


def usage_to_cost_usd(usage: dict) -> float:
    """Compute USD cost from a usage block."""
    cost = 0.0
    cost += usage.get("input_tokens", 0) * PRICING["input"] / 1_000_000
    cost += usage.get("output_tokens", 0) * PRICING["output"] / 1_000_000
    cost += usage.get("cache_read_input_tokens", 0) * PRICING["cache_read"] / 1_000_000
    cc = usage.get("cache_creation", {}) or {}
    cost += cc.get("ephemeral_5m_input_tokens", 0) * PRICING["cache_write_5m"] / 1_000_000
    cost += cc.get("ephemeral_1h_input_tokens", 0) * PRICING["cache_write_1h"] / 1_000_000
    return cost


def analyze_session(jsonl: Path) -> dict:
    """
    Single-pass analysis of one session JSONL.
    Returns aggregate stats + per-workflow stats grouped by task_id.
    """
    total_tokens = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}
    total_cost = 0.0
    message_count = 0
    handoffs_by_task: dict[str, list[dict]] = defaultdict(list)
    last_activity = None

    try:
        with jsonl.open("rb") as f:
            for raw in f:
                # Use bytes → str with errors='replace' to be safe
                try:
                    line = raw.decode("utf-8")
                except UnicodeDecodeError:
                    continue

                usage = extract_usage(line)
                if usage:
                    message_count += 1
                    total_tokens["input"] += usage.get("input_tokens", 0)
                    total_tokens["output"] += usage.get("output_tokens", 0)
                    total_tokens["cache_read"] += usage.get("cache_read_input_tokens", 0)
                    cc = usage.get("cache_creation", {}) or {}
                    total_tokens["cache_write"] += (
                        cc.get("ephemeral_5m_input_tokens", 0)
                        + cc.get("ephemeral_1h_input_tokens", 0)
                    )
                    total_cost += usage_to_cost_usd(usage)

                handoffs = extract_handoff_blocks(line)
                for h in handoffs:
                    state = h.get("workflow_state", {}) or {}
                    task_id = state.get("task_id") or h.get("task_id") or "unknown"
                    handoffs_by_task[task_id].append({
                        "agent": h.get("agent"),
                        "status": h.get("status"),
                        "stage": state.get("current_stage"),
                        "ql_iter": state.get("quality_loop_iteration", 0),
                        "builder_cycles": state.get("builder_cycle_count", 0),
                    })
    except FileNotFoundError:
        pass

    last_activity = dt.datetime.fromtimestamp(jsonl.stat().st_mtime).isoformat() if jsonl.exists() else None

    return {
        "session_file": jsonl.name,
        "last_activity": last_activity,
        "message_count": message_count,
        "tokens": total_tokens,
        "cost_usd": round(total_cost, 4),
        "workflows": dict(handoffs_by_task),
    }


def aggregate_workflows(per_project: dict) -> dict:
    """
    From per-project session data, compute aggregate workflow metrics.
    """
    all_workflows = []  # list of (task_id, list[handoff])
    for proj, sessions in per_project.items():
        for sess in sessions:
            for task_id, handoffs in sess["workflows"].items():
                if task_id != "unknown":
                    all_workflows.append((task_id, handoffs, proj))

    if not all_workflows:
        return {
            "workflow_count": 0,
            "completion_rate": None,
            "avg_quality_loop_iterations": None,
            "avg_builder_cycles": None,
            "note": "No handoff blocks found in any session yet — workflows haven't run or weren't routed through the agent system.",
        }

    completed = sum(
        1 for _, hs, _ in all_workflows
        if hs and hs[-1].get("status") == "completed"
    )
    max_ql = [max((h.get("ql_iter", 0) for h in hs), default=0) for _, hs, _ in all_workflows]
    max_bc = [max((h.get("builder_cycles", 0) for h in hs), default=0) for _, hs, _ in all_workflows]

    return {
        "workflow_count": len(all_workflows),
        "completed_count": completed,
        "completion_rate": round(completed / len(all_workflows), 3) if all_workflows else None,
        "avg_quality_loop_iterations": round(sum(max_ql) / len(max_ql), 2) if max_ql else None,
        "avg_builder_cycles": round(sum(max_bc) / len(max_bc), 2) if max_bc else None,
    }


def _cache_ratios(tokens: dict) -> dict:
    """
    Compute cache efficiency signals from token counts.

    - cache_hit_ratio = cache_read / (cache_read + cache_write)
      How much of our caching activity is productive vs wasted writes.
      >70% = efficient. 30-70% = mixed. <30% = bad (likely TTL or prompt instability).
    - cache_coverage = cache_read / (input + cache_read)
      What fraction of ALL input tokens are served from cache.
      Higher = better cost optimization.
    - cache_waste_usd_est = theoretical USD saved if all cache_write had also been cache_read
      This estimates money "left on the table" — writes that expired before being read.
    """
    cr = tokens.get("cache_read", 0)
    cw = tokens.get("cache_write", 0)
    inp = tokens.get("input", 0)

    cached_activity = cr + cw
    hit_ratio = round(cr / cached_activity, 3) if cached_activity else None
    coverage = round(cr / (inp + cr), 3) if (inp + cr) else None

    # Estimate wasted cost: a write at $3.75/M that isn't read back is ~pure overhead
    # vs if it had been a read at $0.30/M. Conservative estimate — real waste depends on TTL behavior.
    avg_write_cost_per_m = 4.88  # midpoint of 5m ($3.75) and 1h ($6.00) cache writes
    waste_usd_est = round(cw * avg_write_cost_per_m / 1_000_000, 2) if cw else 0.0

    # Health assessment
    health = "unknown"
    if hit_ratio is not None:
        if hit_ratio >= 0.70:
            health = "efficient"
        elif hit_ratio >= 0.30:
            health = "mixed"
        else:
            health = "poor"

    return {
        "cache_hit_ratio": hit_ratio,
        "cache_coverage": coverage,
        "cache_write_cost_estimate_usd": waste_usd_est,
        "health": health,
    }


def aggregate_costs(per_project: dict, since_days: int) -> dict:
    """Total tokens + USD cost across all projects, filtered by recency."""
    cutoff = dt.datetime.now() - dt.timedelta(days=since_days)
    totals = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}
    total_cost = 0.0
    sessions_counted = 0
    by_project = {}

    for proj, sessions in per_project.items():
        proj_tokens = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}
        proj_cost = 0.0
        for sess in sessions:
            if sess["last_activity"]:
                try:
                    last = dt.datetime.fromisoformat(sess["last_activity"])
                    if last < cutoff:
                        continue
                except ValueError:
                    pass
            for k, v in sess["tokens"].items():
                totals[k] += v
                proj_tokens[k] += v
            total_cost += sess["cost_usd"]
            proj_cost += sess["cost_usd"]
            sessions_counted += 1

        if proj_cost > 0:
            by_project[proj] = {
                "tokens": proj_tokens,
                "cost_usd": round(proj_cost, 2),
                "cache": _cache_ratios(proj_tokens),
            }

    return {
        "since_days": since_days,
        "sessions_counted": sessions_counted,
        "total_tokens": totals,
        "total_cost_usd": round(total_cost, 2),
        "cache": _cache_ratios(totals),
        "by_project": by_project,
    }


def collect(filter_project: str | None = None, since_days: int | None = None) -> dict:
    files = find_session_files(since_days=since_days)
    per_project: dict[str, list] = defaultdict(list)

    def _norm(s: str) -> str:
        return s.lower().replace("-", " ").replace("_", " ").strip()

    for proj, path in files:
        if filter_project and _norm(filter_project) not in _norm(proj):
            continue
        per_project[proj].append(analyze_session(path))

    workflows = aggregate_workflows(per_project)
    cost_30d = aggregate_costs(per_project, since_days=30)
    cost_7d = aggregate_costs(per_project, since_days=7)

    return {
        "ts": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sessions_scanned": sum(len(v) for v in per_project.values()),
        "projects_with_activity": list(per_project.keys()),
        "workflows": workflows,
        "cost_7d": cost_7d,
        "cost_30d": cost_30d,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", help="Filter to one project name (substring match)")
    ap.add_argument("--since-days", type=int, default=None, help="Only sessions modified in last N days")
    ap.add_argument("--summary", action="store_true", help="Brief human-readable summary instead of JSON")
    args = ap.parse_args()

    data = collect(filter_project=args.project, since_days=args.since_days)

    if args.summary:
        print(f"=== Workflow telemetry — {data['ts']} ===")
        print(f"Sessions scanned: {data['sessions_scanned']}")
        print(f"Projects with activity: {len(data['projects_with_activity'])}")
        wf = data["workflows"]
        print(f"\nWorkflows:")
        if wf["workflow_count"] == 0:
            print(f"  (none yet — {wf.get('note', '')})")
        else:
            print(f"  total:           {wf['workflow_count']}")
            print(f"  completion rate: {wf['completion_rate']:.0%}")
            print(f"  avg QL iter:     {wf['avg_quality_loop_iterations']}")
            print(f"  avg builder cyc: {wf['avg_builder_cycles']}")
        for label, cost in [("Cost (7d)", data["cost_7d"]), ("Cost (30d)", data["cost_30d"])]:
            print(f"\n{label}: ${cost['total_cost_usd']:.2f} across {cost['sessions_counted']} session(s)")
            for proj, info in sorted(cost["by_project"].items(), key=lambda x: -x[1]["cost_usd"])[:5]:
                print(f"  {proj:50s} ${info['cost_usd']:.2f}")
    else:
        print(json.dumps(data, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
