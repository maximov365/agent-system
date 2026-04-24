# Framework Metrics

**Snapshot:** 2026-04-24T11:20:14Z
**Framework version:** 1.0.23

This file is regenerated on every `python3 metrics.py` run. Append-only history is in `docs/METRICS_HISTORY.jsonl`. See `metrics.py` for the schema.

---

## Tier 1 — Portfolio

| Metric | Value |
|---|---|
| Registered downstreams | 6 |
| Active (folder exists) | 6 |
| Missing | 0 |
| Version-current projects | 6 |
| Behind minor (≤1 ver) | 0 |
| Behind warning (<3 ver) | 0 |
| Behind major (≥3 ver) | 0 |
| Maturity: filled | 5 |
| Maturity: stub | 0 |
| Maturity: no PRD | 1 |

### Active projects

| Name | Path | Version | Drift | PRD maturity |
|---|---|---|---|---|
| Voxema | `/Users/dm/projects/voxema` | 1.0.23 | ✓ current | filled |
| Unfolda | `/Users/dm/projects/unfolda` | 1.0.23 | ✓ current | filled |
| X5 Club | `/Users/dm/projects/x5club` | 1.0.23 | ✓ current | filled |
| Ecom Scout | `/Users/dm/projects/ecom-scout` | 1.0.23 | ✓ current | filled |
| Пробей! | `/Users/dm/projects/probey` | 1.0.23 | ✓ current | no_prd |
| Real Estate | `/Users/dm/projects/real-estate` | 1.0.23 | ✓ current | filled |

---

## Tier 2 — Knowledge

| Metric | Value |
|---|---|
| LESSONS_LEARNED entries | 13 |
| KNOWN_PATTERNS entries | 14 |
| Lines added to LESSONS_LEARNED (7d) | 0 |
| Lines added to LESSONS_LEARNED (30d) | 230 |
| Lines added to KNOWN_PATTERNS (7d) | 14 |
| Lines added to KNOWN_PATTERNS (30d) | 113 |

---

## Tier 3 — Framework velocity

| Metric | Value |
|---|---|
| Commits (7d) | 9 |
| Commits (30d) | 42 |
| Version bumps (30d) | 24 |
| Version bumps (90d) | 24 |

---

## AI Landscape Review activity

| Metric | Value |
|---|---|
| Total reviews logged | 0 |
| Findings logged | 0 |

---

## Pending (Phase 2 — needs IM instrumentation)

These metrics require Iteration Manager to log per-workflow telemetry. Not available yet:

- `workflow_completion_rate`
- `avg_quality_loop_iterations`
- `avg_builder_cycles`
- `token_cost_per_workflow`

---

## Schema & methodology

- Active downstreams: registered in `downstream.projects` AND folder exists on disk
- Version drift: `<project>/.agent-system-version` vs framework `VERSION`
- Maturity: `filled` if `docs/PRD.md` has ≥50 words
- Velocity: `git log` analysis on this repository
- Knowledge growth: lines added per file via `git log --numstat`
- AI Landscape: count of `## AI Landscape Review` headings in `docs/EVOLUTION_LOG.md`

Run `python3 metrics.py --json` for raw machine-readable output.
