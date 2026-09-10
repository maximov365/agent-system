# Agent System Evals

Deterministic tooling tests live in `tests/` and run in CI. This directory defines **behavioral evaluation tasks** for actual model sessions; their existence is not evidence that a model passed them.

## Compare the same work

Use a frozen downstream fixture and the same acceptance criteria for a plain Codex baseline and agent-system + GPT-6 Astra. Record exact client/model/effort, revision, tools, task, wall time, tokens/cost when observable, interruptions, tests, meaningful defects, and evidence artifacts. Repeat representative tasks before attributing improvements to the workflow.

Include small fixes, API authorization, refactors, UI, analytics, native image tools, mid-task steering, and a playable game slice. Use `expected/acceptance_criteria.yaml` for acceptance. A role name is not evidence of a review; assess the result and the actual checks performed.

## Run record

Save a JSON record under `evals/results/` with:

- `run_id`, `runtime`, `model`, `reasoning_effort`, `framework_revision`, `fixture_revision`, `workflow_mode`.
- `tasks`: task ID, completion status, checks and outcomes, evidence paths, meaningful/escaped defects, independent-review status, manual interventions, and elapsed seconds.
- `usage` / `cost`: observed value with source or null. Codex subscription usage is not API dollar cost. Do not infer usage from handoff count or a historical Claude pricing table.
- For visuals: viewed captures, states/viewports, art/coherence/craft/interaction judgments with rubric and rationale, plus measured performance and accessibility defects.
- For games: playtest inputs/device/duration, state/save flows, frame-time measurements, and player evidence if collected.

Do not store private session transcripts as evaluation artifacts. Use task-scoped evidence with sensitive data removed.

## Promotion criteria

Require preserved correctness/security, fewer unnecessary interventions/ceremony on lite tasks, accurate capability handling, honest unavailable-evidence reporting, and better observed visual/game results on representative tasks. A small noisy sample is exploratory evidence, not a general quality claim. No Astra behavioral benchmark has been run as part of the framework migration; run these tasks before broad rollout claims.
