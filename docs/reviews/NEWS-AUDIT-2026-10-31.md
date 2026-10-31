# News and simplification audit — 2026-10-31

Scope: framework 1.0.48 at `ef4b5b7`, 18 registered local downstreams, and
developments since October 14. Owner research/self-review, no delegated agents.
This is an assessment: no runtime, dependency, model or downstream changes were
applied. Findings below distinguish upstream reports, local observations and
experiments still needed.

## Decision

Prioritize the image-processing dependency and supported Python baseline, then
finish removing legacy workflow restrictions and refresh the CI reference
templates. Keep Astra and the existing small native skill set. Use native Codex
diagnostics for host health; do not build another orchestration or diagnostic
subsystem. Evaluate Terra and changed visual-diff metrics separately before
claiming better design or speed.

## Fresh local evidence

| Check | Observed result |
|---|---|
| Root structural/contract audit | 0 critical, 0 warnings, 3 informational |
| Downstream audit | 18 projects; 0 critical, 1 warning, 43 informational |
| Render validation | Passed |
| Exact deployment plans | All 18 at 1.0.48; no pending framework changes |
| npm audit, installed visual dependencies | Zero reported advisories |
| Installed Python dependencies | Pillow 12.2.0, Jinja2 3.1.6, PyYAML 6.0.3 |
| Installed application | 26.1023.51421, build 22530, production channel |
| Bundled Codex CLI | 0.165.0-alpha.1.2 |
| Eligible desktop update check | Busy; availability remains unknown |
| Existing HEAD CI | Success, run 38552113524; not a new CI run |
| Benign image-format check | BMP content named .png accepted by asset inspector |

These audits do not inspect dependency advisories, lifecycle dates or every
instruction's meaning. Their clean root result does not invalidate the findings
below. The Iris warning still concerns absent frontend dependencies and lockfile.
No complete regression suite, real-device test, model run or aesthetic comparison
was performed in this research pass. Prior October 14 test counts are not fresh
evidence for this date.

## 1. First priority: Pillow security and Python support

Pillow 13.0.0 was released October 16 with critical/high security fixes and drops
Python 3.10. The upstream multi-frame advisory lists 11.0.0–12.3.0 as affected;
13.0.0 is patched. Our exact installed/pinned 12.2.0 is in that range.
[Release notes](https://pillow.readthedocs.io/en/stable/releasenotes/13.0.0.html),
[upstream advisory](https://github.com/python-pillow/Pillow/security/advisories/GHSA-v9pv-5gc8-w2m6).

Affected source: `tools/assets/requirements.txt`, `tools/assets/assetlib.py`,
`requirements-dev.txt`, root quality profile, onboarding and CI. The asset tool
opens, loads and converts image files. Its extension allowlist does not restrict
Pillow's content-detected decoders: a harmless BMP stored as .png was accepted.
Restrict both image-opening sites to the intended decoder formats, and verify
content/extension consistency before declaring an export valid.

This is confirmed dependency exposure and a format-validation gap, not a claim
of demonstrated exploitation here. The separate upstream FlashPix issue needs
optional `olefile`, absent in our inspected root environment; downstream Python
environments were not inventoried. No malicious fixture was used.
[FlashPix conditions](https://github.com/python-pillow/Pillow/security/advisories/GHSA-5x8w-8jj5-q52h).

Python 3.10 is now officially unsupported. This predates the last audit and was
missed there; it is not a new October 31 retirement. Recommend a documented
Python 3.11 minimum, a 3.11/3.14 default test matrix, and separate 3.15 compatibility
validation. Sync-only tooling need not acquire Pillow as a mandatory dependency.
[Python lifecycle](https://devguide.python.org/versions/).

Acceptance: asset and full Python regressions on the supported baseline; valid
PNG/JPEG/WebP/alpha/sprite fixtures pass and mismatched/unsupported content fails;
confirm installed versions after dependency installation, not just synced pins.
Effort: medium. Risk: changed decoding/export behavior; compare representative
assets without silently rewriting their approved files. Recovery must not quietly
restore a vulnerable decoder; disable optional raster inspection if necessary.

## 2. Finish the workflow simplification

Two active role files still contradict the current portable execution model:

- `agents/analytics-validator.md:80` recommends a Claude 5 reviewer and a minimum
  high effort despite the active model/effort preservation policy.
- `agents/spec-reviewer.md:5–12,148` requires Gatekeeper ownership and JSON-only
  output; later sections require Reviser cycles and a handoff. `agents/reviewer.md`
  also unconditionally appends a handoff. These methods are reachable references,
  unlike deliberately preserved historical decision logs.

Keep domain-specific review criteria. Move the structured output/transition
contract behind explicit adapter selection; ordinary review should yield concise
findings with evidence, and authorized fixes should continue under the current
owner. Do not remove security checks, useful specialist methods or compatibility
entry points merely to reduce file count.

The official skills guidance favors narrow descriptions and loading supporting
instructions only when needed. Our four short native skills already follow this;
another bundle is not justified. The newer maintenance article recommends replaying
one task with one instruction changed, measuring quality and work performed.
[Skills guidance, September 11](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra),
[maintenance method, October 14](https://developers.openai.com/blog/maintaining-software-with-the-gpt-6-family).

Acceptance: paired representative review with preserved findings and fewer
unnecessary format/handoff steps; explicit structured adapter still works. Effort:
small to medium. Risk: downstream parsers; preserve their opt-in schema and verify
actual consumers before deleting any adapter.

## 3. Refresh CI templates and cover this audit blind spot

The main workflow has pinned modern Actions and Ubuntu 24.04. However,
`templates/ci/web-api.yml` still defaults to Node 20, ubuntu-latest and old
checkout/setup Actions; `templates/ci/macos-app.yml` also uses old checkout.
These reference templates are not auto-synced, so the previous main-workflow
upgrade did not repair them. Node 20 is EOL; Node 22 remains supported. Prefer
Node 24 for new template defaults after validation; no urgent forced migration
of existing Node 22 apps is implied.
[Node release status](https://nodejs.org/en/about/previous-releases).

Refresh template Actions with verified commit pins and intentional runner/runtime
versions. Keep application CI project-owned. Add lightweight template checks and
release-time dependency advisory/lifecycle review; do not put network research in
every ordinary task. The current `check_contracts` validates ownership/rendering
and evaluation prompts, not these CI defaults or dependency lifecycle.

setup-python 7.1.0 (October 22) is available with dependency/diagnostic changes;
checkout 7.0.1 and setup-node 7.1.0 still match the observed latest releases.
Upgrade setup-python during this maintenance batch rather than creating a new
system solely to track it. [Release](https://github.com/actions/setup-python/releases/tag/v7.1.0).

Acceptance: templates parse, no unsupported default runtimes/deprecated Actions,
least required permissions, and actual selected-stack CI passes. Effort: small
for templates, medium for validation. Rollback: versioned workflow changes; never
overwrite a child's customized CI automatically.

## 4. Browser patch: useful, bounded update

Playwright 1.64.1 shipped October 14 after our release work and fixes an Electron
first-window problem and a Chromium cross-origin redirect regression when routes
are registered. The runner installs `context.route('**/*', ...)`, so the latter is
relevant to allowed cross-origin fixtures. This relevance is an inference from
our code; that exact upstream regression has not been reproduced in our harness.
[Patch release](https://github.com/microsoft/playwright/releases/tag/v1.64.1).

Update 1.64.0 to 1.64.1 with the lockfile/browser, retaining touch/negative/video
regressions. Add a targeted permitted-origin redirect case if representative.
Effort: small; risk: browser/render changes. Retain approved screenshot baselines
and compare differences instead of regenerating approvals.

## 5. Native host diagnostics instead of another detector

Codex CLI 0.166.0 (October 29) adds focused network diagnostics and fixes resumed
permissions, image restoration and reasoning-token accounting. The installed
bundled CLI already exposes `doctor --json`/`--summary`; its help does not yet
expose `--network-only`. Use supported native diagnostics for Codex installation
and connections, retaining our project doctor for app dependencies and launch.
[Official changelog](https://learn.chatgpt.com/docs/changelog).

Document the two responsibilities and capability-check optional flags. Do not
replace the app-bundled executable with a global npm installation; the app updater
returned busy and an eligible app update is unknown. Existing evaluator CLI
flags remain present in local help. Effort: small; no new daemon/plugin needed.
CLI presets are optional user convenience, not a replacement for versioned skills.

## 6. Graphics experiments worth doing, without automatic adoption

**Terra:** GPT-6.1 Terra launched October 26 for image reasoning and computer use.
It is a reasonable candidate for screenshot critique and interactive checks.
Preserve Astra as requested and compare the same screen/state/tool budget before
changing workflow defaults. Image input is supported; image generation and video
understanding should not be inferred from this model description. No Terra
evaluation or independent design review was performed here.
[Model specification](https://developers.openai.com/api/docs/models/gpt-6.1-terra).

**pixelmatch 8:** changes color comparison to OKLab/HyAB and adds localized noise
handling/masks. It may improve regression usefulness, but difference counts change
even with the same threshold. Keep 7.2.0 until a frozen set of true regressions
and harmless rendering noise establishes acceptable behavior. Never blanket-mask
important controls or automatically approve new screenshots.
[Release and migration note](https://github.com/mapbox/pixelmatch/releases/tag/v8.0.0).

These are different experiments: a pixel difference is not aesthetic judgment.
Our existing workspace/editorial/game comparison protocol still needs execution.
Compare one change at a time, include failures/ties and record review independence.
Effort: medium; no new model router or extra always-on reviewer required.

## Keep out of the framework core

The October 22 Decisions API GA (typed batch classification), October 20 12-hour
API caching, and new voice/hosted-artifact capabilities have potential downstream
uses. They do not justify turning this development framework into an API harness.
Long-lived cache writes have a premium, so enable them only for measured reuse.
The new life-sciences model has no relevant task here.
[API updates](https://developers.openai.com/api/docs/changelog).

Fast/Ultrafast remain opt-in usage tradeoffs, not a default speed optimization.
Current guidance still lists 2.5x included usage for Fast and 8x for Ultrafast;
token-generation speed is not measured task completion speed.
[Current speed policy](https://learn.chatgpt.com/docs/agent-configuration/speed).

## Evidence and next sequence

Ignored evidence lives under `.agent/audit/2026-10-31/`: `local.json`,
`downstreams.json`, `templates.log`, `deployment.json`, `versions.json`,
`python-versions.json`, `npm-audit.json`, `asset-format.json`, and CLI help.
The existing successful HEAD run is
[38552113524](https://github.com/maximov365/agent-system/actions/runs/38552113524).

Proposed implementation order: (1) Pillow/Python/format validation, (2) review
instruction simplification, (3) CI templates and audit coverage, (4) Playwright
patch/native diagnostics guidance, (5) separate visual-method/model comparisons.
No commit, push, dependency installation or downstream modification was performed
for this review. Only this report, its research-log entry and ignored evidence
were added. Existing unrelated files remain untouched.
