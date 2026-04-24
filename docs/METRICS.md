# Framework Metrics

**Snapshot:** 2026-04-24T11:40:48Z
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
| Commits (7d) | 10 |
| Commits (30d) | 43 |
| Version bumps (30d) | 24 |
| Version bumps (90d) | 24 |

---

## AI Landscape Review activity

| Metric | Value |
|---|---|
| Total reviews logged | 0 |
| Findings logged | 0 |

---

## Tier 1 — Workflow telemetry (from Claude Code transcripts)

| Metric | Value |
|---|---|
| Sessions scanned | 10 |
| Projects with activity | 9 |
| Workflows tracked (with task_id) | 0 |
| Workflow tracking | _no handoff blocks yet — agents haven't emitted them in recorded sessions_ |
| Cost (last 7 days) | $80.73 |
| Cost (last 30 days) | $295.94 |

**Cost breakdown (30d, top 5 projects):**

| Project | Input tok | Output tok | Cache read | Cost USD |
|---|---|---|---|---|
| probey | 14,923 | 320,829 | 409,974,029 | $138.41 |
| Voxema (worktree:inspiring chaum) | 5,607 | 433,870 | 114,591,683 | $68.89 |
| ecom scout | 18,258 | 239,273 | 72,725,661 | $42.57 |
| agent system (worktree:brave bouman) | 29,121 | 151,001 | 53,959,737 | $38.16 |
| x5club (worktree:jolly raman) | 298 | 114,573 | 13,013,442 | $7.91 |

---

## Schema & methodology

- Active downstreams: registered in `downstream.projects` AND folder exists on disk
- Version drift: `<project>/.agent-system-version` vs framework `VERSION`
- Maturity: `filled` if `docs/PRD.md` has ≥50 words
- Velocity: `git log` analysis on this repository
- Knowledge growth: lines added per file via `git log --numstat`
- AI Landscape: count of `## AI Landscape Review` headings in `docs/EVOLUTION_LOG.md`

Run `python3 metrics.py --json` for raw machine-readable output.
