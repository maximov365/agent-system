# Faster execution with preserved acceptance

Owner: current task owner. Started 2026-09-10, baseline 1.0.43 / 850af3e.
The user authorized research and implementation following the efficiency proposal;
prior commit, sync and publication authorization persists. Keep the framework
clean: project maps are project-owned, fixtures optional, raw evidence ignored.
No model/effort downgrade, new provider, automatic delegation or reduced acceptance.

| Task | Acceptance | Status |
|---|---|---|
| TASK-020 Research and lightweight entry | Primary sources + measured local observations; compact entry retains authority, security, review, completion and visual requirements | done |
| TASK-021 Project navigation and check evidence | Source-verified maps, concise summary, opt-in same-session evidence reuse, invalidate inputs/config/environment/runtime/time/corruption, fresh checks by default | done |
| TASK-022 Compare and verify | Frozen before/after Astra runs, unchanged graders/model/effort, meaningful cache negative tests, real project timing and existing UI evidence; no unsupported quality claim | in_progress |
| TASK-023 Release and propagate | Verified source release, safe downstream update, isolated commits preserving other work, existing GitHub destinations and Unfolda PR updated | planned |

Cache correctness is a design boundary: only declared deterministic, side-effect-free
local checks can reuse evidence. Missing dependency declarations or external state
require execution. Build outputs, security release checks, visual review and native
playtesting are not skipped by this facility. Report reuse as reuse, never as a new run.

Initial findings: eight earlier runs showed +12.6% mean wall time and +45.4% cumulative
input tokens, but only two tasks. Logs include broad framework searches, repeated
rule reads and large intentional failing-test output; red/green reproduction is
useful quality work and is retained. Reading/token costs are not a causal time breakdown.

Checkpoint: 16 project navigation maps applied with transaction backups; existing
checks preserved, none opted into reuse. tracker_fiz type check passed fresh in
0.568s. The existing optional five-test logic suite averaged 0.074s fresh, 0.163s
to record reusable evidence, 0.040s per reuse: three subsequent hits are needed
to recover recording overhead. Keep it disabled for these short checks.
Initial Astra candidate logs still show unnecessary method discovery. The final
entry explicitly batches known rules/source/tests and avoids a framework inventory
for a local fix. Preserve both candidate experiments and unchanged graders.
