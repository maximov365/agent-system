# Astra paired workflow evaluation — 2026-09-10

Eight real ephemeral Codex CLI 0.153.4 runs requested `gpt-6-astra`, medium effort:
2 synthetic Python tasks × 2 conditions × 2 repeats. Order was plain/framework
then framework/plain. A no-tool capability probe succeeded before the comparison.
The same task prompt, source fixture, public tests and external held-out grader
were used in each pair. Framework condition included a frozen deployment snapshot;
plain condition had no framework files. Temporary roots did not inherit the
framework checkout's AGENTS.md. User config was disabled for both; built-in host
instructions/tools remained available. No user intervention during the eight runs.

| Run | Seconds | Input tokens | Output tokens | Grading |
|---|---:|---:|---:|---|
| pagination-plain-1 | 42.2 | 63,223 | 959 | pass |
| pagination-framework-1 | 46.2 | 96,534 | 1,044 | pass |
| authorization-plain-1 | 59.2 | 80,379 | 1,441 | pass |
| authorization-framework-1 | 92.0 | 142,995 | 1,872 | pass |
| pagination-framework-2 | 48.4 | 95,419 | 1,072 | pass |
| pagination-plain-2 | 45.3 | 80,034 | 917 | pass |
| authorization-framework-2 | 58.1 | 107,030 | 1,378 | pass |
| authorization-plain-2 | 70.5 | 80,245 | 1,343 | pass |

All eight passed public tests and the held-out grader: 144 pagination boundary
cases and 22 authorization cases plus immutability. No escaped defects were found
by these graders; this is not proof of general correctness. Owner inspected the
resulting synthetic implementation and test evidence; no independent review.

Mean time: plain 54.3s, framework 61.2s.
Mean cumulative input tokens: plain 75,970, framework
110,494. Cached tokens are included in input counts.
CLI JSON reported token usage; dollar cost is unknown. The CLI accepted the exact
requested model, but did not expose a separate resolved-model field.

This small sample shows extra workflow/context overhead on tiny tasks and no
correctness advantage. Do not market the framework as faster or cheaper from
this result. Keep specialist methods lazy and avoid separate role calls for
small tasks. Medium effort was sufficient here; effort alternatives were not
compared. Complex app, visual, image-tool and game comparisons remain future
experiments, so no measured improvement in artistic quality is claimed.

The machine-readable record preserves fixture/grader/snapshot hashes and exact
observations. Later clone-safe template persistence and malformed-input hardening
are outside that frozen snapshot. Synthetic model outputs/logs stay in ignored
`.agent/evals/paired-astra-v1/`; private session history was never read or copied.
The initial execution request was rejected pending payload verification, then
allowed after PUBLIC repository visibility and the exact generic payload were
verified. No model failure or intervention is hidden by that pre-run approval.
