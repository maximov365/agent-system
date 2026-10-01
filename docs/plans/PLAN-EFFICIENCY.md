# Faster execution with preserved acceptance

Owner: current task owner. Started 2026-09-10, baseline 1.0.43 / 850af3e.
The user authorized research and implementation following the efficiency proposal;
prior commit, sync and publication authorization persists. Keep the framework
clean: project maps are project-owned, fixtures optional, raw evidence ignored.
No model/effort downgrade, new provider, automatic delegation or reduced acceptance.

| Task | Acceptance | Status |
|---|---|---|
| TASK-020 Research and lightweight entry | Primary sources + measured local observations; compact entry retains authority, security, review, completion and visual requirements | completed |
| TASK-021 Project navigation and check evidence | Source-verified maps, concise summary, opt-in same-session evidence reuse, invalidate inputs/config/environment/runtime/time/corruption, fresh checks by default | completed |
| TASK-022 Compare and verify | Frozen before/after Astra runs, unchanged graders/model/effort, meaningful cache negative tests, real project timing and existing UI evidence; no unsupported quality claim | completed |
| TASK-023 Release and propagate | Verified source release, safe downstream update, isolated commits preserving other work, existing GitHub destinations and Unfolda PR updated | completed |

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

Completion: source release 1.0.44 (`87b3699`) and its CI passed; 54 Python tests,
four actual browser tests, five existing example logic tests and all 16 native
Astra runs passed. Final frozen-candidate mean wall time was 76.470s to 63.855s
(−16.5%); pagination was +2.5%, authorization −25.5%. The shipped entry restored
explicit security/release strict-mode triggers after the snapshot (434 to 438 words).
No general speed/visual-quality claim is made. Full results and limitations:
`docs/reviews/EFFICIENCY-RESULTS.md`.

All 16 projects now validate on 1.0.44, including navigation. Ten isolated local
Git commits preserved other work/index entries. Seven existing main branches and
the existing Unfolda draft PR were updated; two repositories have no remote and
six projects have no Git. No new repositories, providers, assets or game behavior.
