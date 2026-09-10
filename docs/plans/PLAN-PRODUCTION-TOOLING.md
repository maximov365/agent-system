# Production tooling follow-through

Date: 2026-09-10. Owner: current task owner. User approved implementing the eight remaining improvements in order, including downstream commits and GitHub publication. Existing unrelated application changes, worktrees, and logs must survive. No public product deployment or new paid external service is included.

## Ordered work and acceptance

| Task | Work | Acceptance | Status |
|---|---|---|---|
| TASK-012 | Consistent task ownership and specialist instructions | No role-only task authority, automatic three-pass stop, compulsory MCP, or implicit commit in current workflow methods; templates render | completed |
| TASK-013 | Safe legacy migration and recoverable sync | Recognize exact legacy files; preview without writes; backups, conflict-aware restore, exclusive writer lock, failure rollback; negative regression tests | completed |
| TASK-014 | Executable visual verification | Configured local app start, journeys/states/viewports, captures, browser errors, evidence report; exercise a real app and inspect captures | completed |
| TASK-015 | Asset library and validators | Versioned source/export manifest, lineage and provenance; useful image/sprite/audio validation; passing and failing fixtures | completed |
| TASK-016 | Optional integration example | A polished representative game slice with input, feedback, animation, audio, pause/retry; scripted and exploratory play; measured desktop performance with device limitations | completed |
| TASK-017 | Project quality profiles | Typed web/mobile/desktop/game/service profiles, explicit runnable checks and budgets; review placeholder pipelines against project evidence; preserve product configuration | completed |
| TASK-018 | Astra workflow evaluation | Frozen paired fixtures, real model runs when host permits, observed correctness/interventions/time and honest unavailable usage; reusable runner and report | completed |
| TASK-019 | Downstream release | Verified framework release; 16 downstreams migrated and validated; isolated framework commits in repositories with Git/remotes, preserve application work; publish where an existing remote permits | completed |

## Verification and boundaries

Use focused deterministic tests for migration/security and tooling behavior. Visual acceptance requires viewed captures and interactions; model effectiveness requires actual model runs. A desktop playtest cannot establish mobile performance or player enjoyment. Run each stage's checks before moving to the next. Durable reports retain any external/device limitations rather than claiming fabricated evidence.

For downstream publication stage only the known framework path set and explicitly reviewed profile/migration changes. Do not initialize or publish new repositories for folders without Git/remotes without a concrete user choice. Evaluate models with sanitized fixtures and existing account capabilities; do not inspect private transcripts or credentials.

## Checkpoint

Starting revision: `10f5488` / version `1.0.41`. GitHub Agent Quality succeeded for that revision. Existing untracked `.claude/worktrees/` and `docs/.weekly-review.log` are unrelated. Prior rollout backups: `/Users/dm/projects/.agent-system-backups/20260910T092257Z/`.

TASK-012: current workflow/backlog/restore/onboarding and external-review authority reconciled; 27 dynamic templates validate, local audit has 0 critical and the existing optional landscape size advisory.

TASK-013: 32 regression tests passed, including disk-failure rollback, restore conflicts, corrupted backups, writer locks, exact legacy migration, and preservation of custom setup.py. No actual downstream update yet; rollout remains TASK-019.

TASK-014: optional Playwright runner, fixtures, trace/capture/baseline failures, local process cleanup, four passing tests, and ten actually viewed tracker_fiz captures. Manual app polish findings preserved in docs/reviews/PRODUCTION-TOOLS-VISUAL.md.

TASK-015: asset CLI register/validate/inspect/catalog implemented; seven tests passed for provenance/hashes, sprite grids/padding/ground lines, graph cycles, paths/SVG safety, audio peaks/loops, and budgets/alpha. Sample library validates and produces a catalog.

User clarification: agent-system remains a clean development framework. Examples and tests are allowed, but application code/assets stay exclusively in examples/ and never enter deployment or framework runtime dependencies. A sync regression test enforces this boundary.

TASK-016: isolated example completed. Five model tests, four browser journeys/ten viewed captures, and an adaptive normal-duration playthrough: 40 orders, wrong input, pause/resume, persisted score after reload; 3,448 frames, p95 17.7 ms, no browser errors. No human enjoyment study, physical mobile test, or listening review claimed. See docs/reviews/GAME-EXAMPLE.md.

TASK-017: 16 project-owned profiles source-validated; four exact unused pipeline placeholders removed with transaction backups. Three profile-runner tests passed, plus actual tracker_fiz type-check and probey build. Missing native/device/app capabilities remain explicit unavailable checks. See docs/reviews/PROJECT-PROFILES.md.

TASK-018: eight actual paired synthetic Codex/Astra runs completed. Both conditions passed; framework overhead increased on these small tasks. Results, exact snapshot hashes, usage and limitations are recorded in docs/reviews/ASTRA-PAIRED-EVAL.md and evals/results/astra-paired-2026-09-10.json. No general speed/artistic quality claim.

TASK-019: release 1.0.43 published with passing GitHub CI. All 16 downstreams pass version/content/profile/render validation, ten have isolated framework commits, seven existing main branches are published, and Unfolda has isolated draft PR #1 to avoid publishing an unrelated predecessor. Two repositories have no remote; six folders have no Git. All unrelated index/worktree content checked preserved. Full delivery table: docs/reviews/RELEASE-1.0.43.md.
