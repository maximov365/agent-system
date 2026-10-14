# Audit implementation — 2026-10-14

Scope: agent-system 1.0.46 (`5f5299a`) to 1.0.48 and 18 registered local
downstreams. Implements the confirmed findings from the
[October 9 audit](RE-AUDIT-2026-10-09.md). Owner self-review; no delegated or
independent reviewer. Existing application sources and unrelated staged work were
preserved. Examples remain isolated verification fixtures, outside deployment.

## Changes

1. **Browser correctness:** `tap` now emits actual touch input, including locator
   targets, and rejects incompatible contexts or coordinates. Text/count assertions
   retry within a bounded timeout. Initial navigation waits for DOM readiness;
   explicit actions/assertions establish application readiness.
2. **Motion evidence:** verified Playwright 1.64.0 with matching Chromium. Optional
   requested recording FPS, normal/reduced-motion settings, hashed videos and
   embedded report playback. Screenshot animation behavior is recorded. Requested
   recording FPS is never reported as measured app FPS or reviewed motion.
3. **Reference integrity:** local Markdown links and native skill entry points are
   checked alongside literal paths. Findings identify projects and combine repeated
   occurrences. Fresh deployment no longer references missing framework history.
   Removed unsupported CoVe improvement claims and outdated mandatory-agent MAST
   coverage claims. Historical logs remain history.
4. **Readiness adoption:** all 18 project-owned profiles declare prerequisites and
   launch applicability. Eight have frontend/mockup HTTP contracts; ten explain
   why HTTP launch is unavailable. The framework audit now detects missing
   declarations/prerequisites without starting commands or making HTTP requests.
   A project-owned tracker documentation link was also repaired.
5. **CI stability:** explicit Ubuntu 24.04 baseline, optional workflow dispatch on
   26.04, bounded jobs, Python 3.10/3.14 and real Chromium checks. Python CI creates
   the environment declared by the root profile; local audit fails on warnings.
   CI exposed deprecated Node 20 action runtimes. Release 1.0.48 updates checkout
   to 7.0.1, setup-python to 7.0.0 and setup-node to 7.1.0, pinned to verified
   upstream commit SHAs. The application test runtime remains Node 22; automatic
   package-manager caching stays disabled.
6. **Codex/evaluation:** refreshed optional Sol/Astra speed guidance; retained Astra
   and no automatic paid tier/provider switch. Documented project-scoped skill
   discovery. Paired evaluation freezes grader sources as well as task inputs and
   records their hash, available skill files and unknown observed tier/invocations.

## Evidence

| Check | Observed result |
|---|---|
| Final Python suite, Python 3.14 | 67 passed |
| Node/browser checks | 6 runner + 1 UI grader + 5 example logic tests passed, none skipped |
| Isolated UI grader execution | Broken fixtures rejected; repaired fixture passed from frozen grader/runner copy |
| Template validation | Passed |
| Root audit | 0 critical, 0 warnings, 3 informational |
| Downstream audit | 18 projects; 0 critical, 1 warning, 43 informational |
| Local deployment | All 18 at 1.0.48, no framework integrity drift reported |
| Readiness adoption | 18 valid profiles with explicit launch applicability |
| Native skill discovery | Four framework skills enabled in root and each downstream, zero errors |
| HTTP launch identity | Seven passed; Iris skipped for missing prerequisites |
| Tracker representative interaction | Project doctor verification passed with actual deployed visual runner |
| Isolated game example | Six journeys passed: desktop normal, mobile normal and mobile reduced motion |
| Game artifacts | 15 captures, 6 indexed and hashed videos |

The installed Codex CLI was 0.162.0-alpha.17.2. Skill discovery did not start model
tasks; discovery is not evidence of invocation. The parent projects directory has
none of these repository-scoped skills.

The seven HTTP checks cover Unfolda, X5 Club's static mockup, Probey, Real-estate,
Synthetic_resp, Tracker and OKR/KPI. They establish expected frontend identity,
not backend/authentication/integration correctness. Only Tracker additionally ran
its existing representative interaction contract in this rollout.

The game was copied into ignored temporary verification storage; no product
feature or asset was added. Mobile journeys used actual browser touch events.
At the completed full-cycle probes, 446–448 frame samples per mode had p95
16.7–16.8 ms and zero stalls over 50 ms. These are short headless Chromium runs on
this Mac, not real-phone performance guarantees. The owner inspected five
captures (mobile welcome/playing/paused/result; desktop playing): controls and
text fit their captured states. Continuous video playback was not reviewed;
normal-speed motion review remains pending. No new aesthetic comparison occurred.

An initial restricted-shell test attempt could not bind a local test server;
the authorized rerun passed. Earlier negative-fixture diagnostics and test-only
timeout sensitivity were corrected and rechecked; failures were not hidden.

## Release status

Local implementation and propagation are complete. Root publication and fresh
Ubuntu 24.04/26.04 CI verification are pending at this checkpoint; replace this
paragraph with observed run results after completion. Child workspaces remain
local modifications; this task does not publish unrelated application work.

## Remaining work

- **Iris application setup:** no frontend lockfile or installed node_modules.
  `npm ci` correctly refuses this state. Resolve/review the initial dependency set
  in Iris, commit its lockfile, then install and verify its frontend. Its profile
  now reports this prerequisite explicitly; readiness is not claimed.
- **Design effectiveness:** execute frozen workspace/editorial/game comparisons
  with matched content/tools/budgets and neutral A/B review. Existing design skills
  and craft guidance are present; their incremental aesthetic benefit remains
  unmeasured. More skill bundles are not a substitute for this experiment.
- **Application acceptance:** add project-owned representative journeys where
  absent, verify backends/native devices separately, and watch normal-motion
  recordings. HTTP success does not close these application tasks.
- **Model/tier comparison:** no new paid or model-backed experiment ran. Unknown
  resolved identity/tier/skill invocation stays null. No advertised token-speed
  gain is presented as our end-to-end productivity result.

## Evidence retention and recovery

Ignored local evidence: `.agent/audit/2026-10-14/`. Key records include
`unit-release.log`, `browser-touch-locators.log`, `browser-tests-final.log`,
`ui-grader-frozen.log`, `local-release.json`, `downstreams-release.json`,
`skills-observed.json`, `launch-verification.json`,
`launch-verification-x5club.json`, `tracker-verification.json`,
`game-verification.json`, `baseline-integrity.json` and `rollout.json`.

Before rollout, all downstream framework bytes were compared with the trusted
1.0.46 baseline. Each sync and profile edit used a recoverable transaction.
`rollout.json`, `readiness-adoption.json` and `profile-adjustments.json` record exact
backup directories under the sibling `.agent-system-backups` directory. Git
staged bytes were checked for preservation. Recovery must use the verified
transaction preview, respecting later edits; never reset a dirty child repository.

## Primary sources rechecked

- [Codex changelog](https://learn.chatgpt.com/docs/changelog) and
  [speed guide](https://learn.chatgpt.com/docs/agent-configuration/speed): optional
  Ultrafast eligibility, usage and regional distinctions; no automatic migration.
- [Playwright 1.64 release notes](https://playwright.dev/docs/release-notes#version-164)
  and [browser context/video lifecycle](https://playwright.dev/docs/api/class-browser):
  recording support and flushing on context close.
- [Ubuntu runner migration notice](https://github.com/actions/runner-images/issues/14748):
  explicit compatibility check before changing the pinned baseline.
- [CoVe paper](https://arxiv.org/abs/2309.11495) and
  [MAST paper](https://arxiv.org/abs/2503.13657): methodological references,
  not measured effectiveness of this framework.

- [GitHub Actions Node 20 deprecation](https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/)
  and verified releases: [checkout 7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1),
  [setup-python 7.0.0](https://github.com/actions/setup-python/releases/tag/v7.0.0),
  [setup-node 7.1.0](https://github.com/actions/setup-node/releases/tag/v7.1.0).
