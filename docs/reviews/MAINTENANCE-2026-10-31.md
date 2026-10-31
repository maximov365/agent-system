# Maintenance implementation — 2026-10-31

Release: **1.0.49**, based on 1.0.48 / ef4b5b7. This implements the
[news audit](NEWS-AUDIT-2026-10-31.md) after user authorization. Framework-only
changes; synthetic fixtures remain under evals and are not deployed downstream.
Owner self-review, not an independent security or design audit.

## Changes

- **Raster safety:** Pillow 13.0.0, Python 3.11+ baseline. Both inspection and sprite
  validation reject older/unrecognized/prerelease Pillow before opening files.
  Decoder selection is limited to PNG/JPEG/WebP, with matching content, one frame
  and a pixel limit before pixel decoding. Animated formats need a project adapter
  or static sprite sheet. The secure version remains an optional asset dependency.
  [Pillow release](https://pillow.readthedocs.io/en/stable/releasenotes/13.0.0.html),
  [FPX advisory](https://github.com/python-pillow/Pillow/security/advisories/GHSA-5x8w-8jj5-q52h).
- **Review simplification:** normal code/spec/analytics reviews preserve active
  model/effort and use concise findings. No compulsory Gatekeeper/Reviser round,
  JSON, document inventory or fixed extra verification pass. Explicit structured
  adapters retain existing fields. Domain, privacy, correctness and acceptance
  checks remain; missing evidence cannot be a fabricated pass.
- **CI:** supported Python 3.11/3.14 and Node 24 defaults, verified action commit
  pins, opt-in Python 3.15/Ubuntu 26.04. Web/macOS templates have explicit runners,
  permissions and timeouts. macOS release waits for build/test and explicit
  configuration; no xcpretty dependency. An offline template policy check runs
  through the ordinary audit. Separate pip-audit/npm advisory checks run for
  published main changes and explicit dispatch, not ordinary task startup.
- **Browser evidence:** Playwright 1.64.1. Existing touch, async, video and negative
  tests pass. Added actual HTTPS allow/deny and CORS POST redirect coverage with a
  temporary local certificate trusted only by that test browser. This does not
  claim to reproduce every upstream regression.
  [Playwright release](https://github.com/microsoft/playwright/releases/tag/v1.64.1).
- **Host guidance:** native Codex doctor diagnoses the host when supported; project
  doctor remains about declared application prerequisites. Older bundled CLI flags
  are checked via help, not assumed. No custom host detector or global installation.

## Bounded comparisons

[Reproduction and limitations](../../evals/experiments/maintenance-2026-10-31/README.md)
and [machine-readable observations](../../evals/experiments/maintenance-2026-10-31/results.json).
Runtime: Codex 0.165.0-alpha.1.2, medium effort, ephemeral read-only calls, user
configuration disabled, no observed tool calls. All seven calls completed.
Resolved model identity/tier are not independently exposed. Token counts are
observed CLI usage, not API dollar cost. Built-in host instructions contribute
context; this is not a pure API model benchmark.

### Specification review

One synthetic plan deliberately contains five expectation groups: destructive
replacement, private-content transmission, cloud/account scope creep, untestable
acceptance, and omitted failure/verification behavior. Both old/new methods found
all five. The old method escalated and requested a Gatekeeper/Reviser handoff; the
new method gave actionable revision findings. A separate explicit adapter call
returned parseable JSON, retained all expected keys/ten dimensions and calculated
the mean correctly. This is compatibility evidence for the spec adapter only,
not an external integration certification.

| Method | Input tokens | Output tokens | Elapsed seconds | Seeded groups found |
|---|---:|---:|---:|---:|
| Old spec method | 18,147 | 1,032 | 27.43 | 5/5 |
| New spec method | 15,054 | 338 | 16.38 | 5/5 |
| Explicit structured adapter | 15,965 | 1,027 | 31.33 | 5/5 |

Each had 12,160 cached input tokens. One pair does not establish a general speed
or quality guarantee. Selected normal-method word counts fell from 4,298 to 1,762
(59%); this is not a reduction of the entire framework or every task's context.

### Visual review: Astra versus Terra

Both requested models found the three planted visible problems in both repeats:
clipped payment action, overlapping receipt/total labels and pale unreadable total.
The owner viewed the screenshot and read all responses. No interaction or precise
contrast measurement was claimed. Order was reversed on the second repeat.

| Requested model | Seconds, repeat 1 / 2 | Output tokens, repeat 1 / 2 | Findings |
|---|---:|---:|---:|
| gpt-6-astra | 8.81 / 8.39 | 97 / 106 | 3/3 in both |
| gpt-6.1-terra | 5.39 / 5.33 | 101 / 97 | 3/3 in both |

Both models received equal reported input tokens within each repeat (16,032 then
14,746; 12,160 cached). Host context varied between repeats. Requirements named
the defect classes, making this a simple visual-checking smoke test. **Keep Astra
as default.** Terra is an optional explicit comparison target; this sample does
not establish broad design, game-development or code-review superiority.

### Pixelmatch 7.2 versus 8.0

Same Chromium 156.0.8078.4 captures, 640×480, scale 1, threshold 0.1:

| Case | v7 total | v8 total | v8 maximum in 32×32 window |
|---|---:|---:|---:|
| Identical | 0 | 0 | 0 |
| Near-white tint | 0 | 0 | 0 |
| One-pixel shift | 2,852 | 2,874 | 164 |
| Missing action | 7,207 | 7,207 | 960 |
| Clipped action | 5,190 | 5,191 | 960 |
| Low-contrast total | 922 | 922 | 324 |
| Combined defects | 7,429 | 7,430 | 960 |

**Keep v7.2 and existing thresholds.** Version 8 changes the color-distance model;
its window metric is a local count and cannot replace a full-frame difference
ratio directly. These fixtures show no clear adoption advantage and do not cover
real-device variability, broad raster noise, alpha sprites or complex scenes.
[Upstream change](https://github.com/mapbox/pixelmatch/releases/tag/v8.0.0).

## Verification and rollout

Local verification: 76 Python tests; 13 actual browser/UI-grader/game-logic checks;
template rendering; offline audit with zero warnings/critical findings; actionlint
1.7.12 on all three workflows/templates; git whitespace check. Shellcheck/pyflakes
were disabled in actionlint; these are not claimed. pip-audit 2.10.1 found no known
advisories for resolved Pillow 13.0.0, Jinja2 3.1.6, PyYAML 6.0.3 and MarkupSafe
3.0.4; npm audit found none in the locked visual dependencies. Advisory results
are date-bound, not a guarantee of absence of vulnerabilities.

Root developer Pillow was actually upgraded. Copying downstream requirements does
not update app environments. A scoped inventory found two existing application
venvs with Pillow 11.3.0/12.3.0, and no dedicated framework asset/visual environments.
Those app environments were not silently altered; the new framework raster guard
refuses them. Their application dependency upgrades need project-specific checks.
No claim is made that every downstream dependency is patched.

The macOS/web templates received static validation; no real macOS app signing,
notarization or reference web/API deployment was performed. Desktop app update
availability was not established; bundled CLI was not replaced.

Publication, downstream transaction verification and remote CI results will be
recorded after completion. Recovery uses per-project sync backups; never restore
vulnerable raster processing as a workaround. Revert non-security guidance/CI
changes independently if needed.
