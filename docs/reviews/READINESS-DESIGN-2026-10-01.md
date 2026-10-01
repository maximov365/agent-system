# Readiness and design release — 2026-10-01

Version 1.0.46, based on 84ec177 / 1.0.44. The main implementation is 240ef86;
5c86c7f keeps the per-check result consistent after explicit verification. Implementation and review by the same
current task owner; no independent agent or user preference study is claimed.

## Delivered

- Removed active Claude-first/gateway-required contradictions and compressed the
  landscape review into relevant primary-source research. Preserved compatibility
  entry names and historical decisions. Optional speed tiers do not change the
  selected Astra model/effort or enable a paid tier.
- Added optional project readiness and four focused native skills. Plain doctor
  performs no command/network call; explicit probe only uses loopback HTTP, while
  explicit launch verification executes the project's existing check fresh.
- Added shared design craft and an expanded project-owned brand seed. Existing
  brand documents, tokens, skills and application code remain project-owned.
  No external skill installer, binary, hook or automatic delegation was imported.
- Added multi-file query/service/API and browser UI evaluation fixtures, held-out
  graders, nested fixture support and a visual comparison protocol. Developer
  fixtures and game assets remain outside downstream deployment.
- CI now covers Python 3.10 and 3.14 and an actual browser grader regression.

## Fresh local evidence

Python 3.14.3: **62 tests passed**, including readonly diagnostics, malformed
contracts, missing dependencies, HTTP identity/redirect handling, actual check
success/failure, deployed imports/skill links, project ownership, and sync recovery.
The existing recovery suite exercises rollback, restore, corrupted backup and
concurrent-edit refusal. Template validation passed. Local audit: **0 critical,
0 warnings**. All four native skills passed the skill validator.

Node 22.22.3 / Playwright 1.62.1 / Chromium 151.0.7922.34: **5 browser/grader tests
passed**, including deliberately broken and repaired UI fixtures; **5 example
logic tests passed**. These are tooling checks, not model-performance runs.

The new doctor launch path ran an isolated copy of the existing game at a free
loopback port, preserving the user's existing server. Four viewport/journey
combinations passed: full cycle and mistake feedback at 1440×1000 and 390×844.
Assertions cover start, order/score, pause, resume, finish, retry and sound state.
Ten captures were saved with traces. The owner viewed desktop welcome, mobile
playing and mobile paused captures: controls/text are visible and the pause
layout fits. This limited self-review is not a new aesthetic comparison, complete
accessibility audit or device playtest. Automated reports retain their pending
visual-review status; this paragraph records the actual viewed subset separately.

Local detailed evidence: `.agent/validation/readiness-final-unit.log`,
`readiness-browser.log`, `readiness-final-audit.json`,
`readiness-example-report.json`, and the isolated example's `.agent/evidence/`.
These generated artifacts remain ignored. Public CI and rollout outcomes are
recorded after publication below.

## Measurement boundary and remaining evaluation

No new actual-model paired runs were made in this release. Multi-file/UI graders
were tested against known broken/repaired implementations, and the runner's
selected-task preflight passed without model calls. Actual Astra comparisons and
independent A/B design review remain future evaluation, using frozen briefs and
representative devices. No general speed or visual-quality percentage is asserted.
The editorial and game rows in the visual protocol require exact fixtures before
execution. Desktop/account tools and skill discovery still depend on the host;
readiness deliberately leaves unobserved model/effort/tier null.

Sources and the reasoning behind adaptation are linked from `docs/MODEL_POLICY.md`,
`docs/DESIGN_CRAFT.md` and `evals/VISUAL_COMPARISON.md`.

## Verified rollout

All **17 registered projects** received 1.0.46. Rendered framework bytes and
version markers match; project-owned files and unrelated staged/worktree content
were preserved. Recovery records remain outside projects. All 17 template checks
passed, and all **16 existing quality profiles** validated. The newly registered
`fallout2-remaster` has no project-owned profile; this is recorded as not configured,
not as a passing application check. No application code or game asset was shipped.

Ten Git projects received isolated local framework commits. Seven existing main
branches and Unfolda's existing draft PR branch were published. X5Club and Iris
have no remote; seven projects have no Git repository. No repository or remote
was invented. Ecom Scout used its verified `ecom-scout` remote because its `origin`
points at a different project. Unfolda's unpublished local application history
remains outside the PR. Its local checkout was also updated.

| Project | Final local commit / storage |
|---|---|
| voxema | `18a9236d` |
| unfolda | `78d5f55e` |
| x5club | `cc2e73d7` |
| ecom-scout | `19f7bf74` |
| probey | `50a4942d` |
| real-estate | `618c63e5` |
| collective-purch | Files updated; no Git |
| synthetic_resp | `8c35a994` |
| beautyrs | Files updated; no Git |
| tracker_fiz | Files updated; no Git |
| Iris | `14c0fe63` |
| game_tsx | Files updated; no Git |
| disco-system | Files updated; no Git |
| okr&kpi | `ebc9782b` |
| astrology | `992af1c7` |
| xslides | Files updated; no Git |
| fallout2-remaster | Files updated; no Git |

The main implementation's [GitHub CI](https://github.com/maximov365/agent-system/actions/runs/36840221532)
passed both Python 3.10/3.14 jobs and the visual runner/grader job. The small report
consistency fix passed a fresh 62-test local suite and its own
[GitHub CI](https://github.com/maximov365/agent-system/actions/runs/36840567346). The
[existing Unfolda PR](https://github.com/maximov365/unfolda/pull/1) remains draft;
its final framework branch commit is `82a4dd9`. Publication and preservation
receipts remain in ignored `.agent/validation/readiness-*.json` files.
