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

Require preserved correctness/security, fewer unnecessary interventions/ceremony on lite tasks, accurate capability handling, honest unavailable-evidence reporting, and better observed visual/game results on representative tasks. A small noisy sample is exploratory evidence, not a general quality claim. The first small paired evaluation is recorded in `results/astra-paired-2026-09-10.json` and `docs/reviews/ASTRA-PAIRED-EVAL.md`: eight real runs passed, with extra overhead on tiny tasks. It does not establish visual quality or general efficiency gains.


## Optional synthetic runner

`run_paired.py` is developer tooling in the framework checkout; it and its fixtures,
graders, outputs and dependencies are not installed into downstream projects.
Read the task text and payload before enabling actual model calls. Use the existing
Codex account; no credential discovery or additional provider is required.

```sh
.venv/bin/python3 evals/run_paired.py --codex /path/to/codex --output .agent/evals/new-run
.venv/bin/python3 evals/run_paired.py --codex /path/to/codex --output .agent/evals/new-run --run
```

The first command reports hashes without model calls. The second explicitly runs
at most eight calls by default, each bounded to 240 seconds. Each fresh fixture is
outside the framework tree, in a temporary Git repository. The runner freezes
framework bytes before starting, reverses pair order on the second repetition,
records available usage, and applies held-out checks. Existing output directories
are refused; runtime failure stops the remaining model calls. Synthetic transcripts
remain local ignored artifacts; publish only the reviewed numeric record.

Execution options were verified against local CLI help and the
[official non-interactive Codex documentation](https://learn.chatgpt.com/docs/non-interactive-mode).
