# Agent System Evals

This directory contains framework-level evaluation tasks for comparing workflow quality across interactive IDE usage, external reviewers, model gateways, and optional automated runtimes.

These evals test the agent-system process layer, not a downstream product.

---

## Layout

```text
evals/
  tasks/                  # Task prompts used as inputs
  expected/               # Expected routing, criteria, and quality outcomes
  results/                # Per-run results and metrics
```

---

## Metrics

Each eval run should record:

- `task_completed`: yes / no
- `tests_passed`: yes / no / not_applicable
- `review_defects_found`: count
- `escaped_defects`: count
- `agent_cycles`: count
- `cost`: numeric value or unknown
- `wall_clock_time`: duration
- `manual_interventions`: count
- `architecture_violations`: count
- `workflow_mode`: lite / standard / strict
- `model_policy`: model map or gateway used
- `runtime`: Cursor / Claude Code / OpenHands / Agents SDK / LangGraph / other

---

## Run Record Format

Store run results under `evals/results/`:

```text
evals/results/<YYYYMMDD>-<runtime>-<model-policy>.json
```

Recommended JSON shape:

```json
{
  "run_id": "20260430-cursor-standard",
  "runtime": "Cursor",
  "model_policy": "single-primary",
  "workflow_mode": "standard",
  "tasks": [
    {
      "id": "small_bugfix",
      "task_completed": true,
      "tests_passed": true,
      "review_defects_found": 1,
      "escaped_defects": 0,
      "agent_cycles": 4,
      "cost": null,
      "wall_clock_time": "00:12:30",
      "manual_interventions": 0,
      "architecture_violations": 0
    }
  ]
}
```

---

## Comparison Targets

Use the same task set to compare:

- `agent-system + Claude`
- `agent-system + Claude + external GPT/Kimi reviewer`
- `agent-system + LiteLLM/OpenRouter gateway`
- `OpenHands`
- `OpenAI Agents SDK`
- `LangGraph`
- `SWE-agent` or other benchmark runtimes

The comparison should use objective evidence from tests, review reports, and workflow state files rather than impressions.
