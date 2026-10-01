# Readiness and design release — 2026-10-01

Version 1.0.45, based on 84ec177 / 1.0.44. Implementation and review by the same
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
