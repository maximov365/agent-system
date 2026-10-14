# Repeatable browser evidence

The optional runner captures actual UI states, interaction results, browser errors, trace archives, optional videos, and approved-baseline comparisons. It never marks captures as visually reviewed. It supports local web apps and browser games; native/engine adapters remain project-specific.

## Install once

In a downstream's `.agent-system/visual/` (or framework `tools/visual/`):

```bash
npm ci
npx playwright install chromium --only-shell
```

An existing host-provided package installation can be selected with `AGENT_NODE_MODULES`; an explicit compatible browser binary can be selected with `AGENT_BROWSER_EXECUTABLE`. The evidence report records runtime/browser versions. Installation or launching a browser may require runtime permission.

## Configure and run

Create project-owned `quality/visual.config.json`; `examples/quality/tracker-visual.config.json` is an exercised example in the framework. The schema has `schema_version: 1`, a local `baseURL`, `server.command` as an argv array (no shell), optional project-relative server cwd/env, viewports, and journeys. Each journey has a stable ID, relative route, ordered steps, and at least one named capture.

```bash
node .agent-system/visual/run.mjs --check
node .agent-system/visual/run.mjs
```

`--project` selects another project; `--config` and `--output` remain relative to that project. Default output is a new directory in `.agent/evidence/visual/`. Existing runs are never overwritten. `--check` validates without launching commands, browser, or network requests. Review config commands before running: project configuration is executable task configuration, not a sandbox.

Steps: `click`, `fill`, `press`, `keyDown`, `keyUp`, `waitFor`, `expectText`, `expectCount`, `tap`, bounded `delay`, `capture`, and `probe`. Prefer role/name locators or stable selectors. A probe reads the optional project-owned `window.__agentEvidence.snapshot()` and can assert scalar `equals` fields; it does not execute arbitrary strings from configuration.

`tap` sends actual touch input. Prefer a role/name or selector; alternatively pass
`x` and `y` coordinates, which must fit every selected viewport;
each must have `mobile: true` or explicit `touch: true`. Use separate configs for
mouse-only and touch journeys rather than silently substituting a mouse click.
Text/count assertions retry until `timeoutMs` (default 5000, maximum 60000), so
ordinary asynchronous state changes need no arbitrary sleeps. Navigation waits
for DOM content, then actions/assertions establish readiness; persistent network
activity does not block the entire journey.

Journeys use fresh browser contexts, a fixed locale/timezone, optional fixed wall clock/seed, and reduced motion. For deterministic frontend fixtures, list exact API path/method/body responses in the journey. `responses` can supply an ordered series. Unexpected API requests fail when fixtures are active. Fixtures validate the real frontend against controlled service responses; they do not validate backend integration.

External resource requests fail by default. `allowedOrigins` accepts explicit HTTPS origins for required assets and records external dependencies in the report. Prefer project-local fonts/assets for durable baseline comparisons. Credentials, real customer data, and authenticated browser sessions should not be used as fixture inputs.

## Evidence and acceptance

Open `index.html` and actually view the relevant screenshots/recordings. `report.json` contains assertions, runtime errors, capture hashes, viewport, environment, revision, timings, and optional game probes. `checks_passed` covers the automated checks only; `visual_review` remains `pending` until a separate reviewer records which captures they viewed and their findings. Keep a task-scoped review document with those filenames/hashes, reviewer identity, observations, and limitations.

To compare approved images, set a project-relative `baselineDir` and `maxDiffRatio` (default 0.001). The runner fails on missing baselines, size mismatch, or an excessive pixel difference; it writes a diff image and never updates baselines automatically. Review intended changes before copying final captures into the baseline directory. Keep fonts, browser/runtime, device scale, fixtures, and image dimensions consistent; pixel similarity does not establish usability or taste.

Browser API details: [local server lifecycle](https://playwright.dev/docs/test-webserver), [trace capture](https://playwright.dev/docs/api/class-tracing), and [visual comparison constraints](https://playwright.dev/docs/test-snapshots). Traces from this library runner capture browser operations; step assertions are recorded separately in report.json.

Motion defaults to `reducedMotion: "reduce"` for repeatable screenshots. Use `"no-preference"` explicitly to exercise normal animation; record that setting with evidence. Static captures alone do not validate timing.

Set `video: true` to record each journey, optionally `videoFps: 1..60` with
Playwright 1.64+. The HTML report embeds the recordings; JSON records filenames,
hashes, motion/touch settings and requested fps. Observed fps remains unknown;
recording rate is not a measurement of the application's frame performance.
Videos from failed journeys are retained too. Captures default to disabled
animations in reduced-motion mode and allow them in normal-motion mode; a capture
can explicitly override `animations: "allow" | "disabled"`. Disabling animations
can fast-forward transitions and affect the recording, so use normal-motion runs
for motion review and separate stable captures for approved pixel baselines.

The optional browser tooling is tested with Node.js 22 and its locked Playwright version. Install the matching browser with Playwright; an older cached browser is not sufficient. Core framework sync/render remains Python-only.
