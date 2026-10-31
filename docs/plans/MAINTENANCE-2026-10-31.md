# Maintenance implementation — 2026-10-31

Baseline: 1.0.48, ef4b5b7. Owner self-review; no delegated agents. Preserve
unrelated files, project-owned application code, profiles, CI and Git staging.
The user authorized implementation of the dated news audit; earlier root
publication/downstream update authorization remains applicable.

## Sequence and acceptance

1. Upgrade Pillow to 13.0.0, document Python 3.11+, fail closed on vulnerable
   installed Pillow, and restrict raster decoders/content before loading pixels.
   Verify real PNG/JPEG/WebP/alpha/sprite acceptance and negative format/version/
   frame/size cases. Keep raster dependencies optional for sync-only users.
2. Make ordinary reviewer/spec/analytics methods concise and model-neutral;
   retain structured schemas only for explicitly selected adapters. Preserve
   domain/security criteria and run a bounded synthetic review comparison.
3. Refresh main CI and reference templates with verified action pins, supported
   defaults and scoped permissions. Add offline CI-policy coverage and an explicit
   release dependency-advisory check; never run network research on every task.
4. Upgrade Playwright patch and verify actual touch, async, negative, recorded
   video and allowed-origin behavior. Document native host versus project doctor.
5. Run isolated pixelmatch 7/8 and Astra/Terra visual-review comparisons on frozen
   synthetic inputs. Keep defaults/baselines unchanged unless results justify a
   specific change. Record failed/unavailable runs and self-review limitations.
6. Run focused/full release checks, inspect the final diff, safely propagate
   framework-owned files with transaction backups, publish root and verify CI
   (Python 3.11/3.14 plus opt-in 3.15, Ubuntu 24.04/26.04).

## Recovery and evidence

Evidence: ignored .agent/audit/2026-10-31/implementation. Freeze baseline bytes and
downstream staging before writes. Use verified sync recovery, never reset a dirty
project. Dependency installation is distinct from copying requirement files;
record which environments actually changed. If the secure raster upgrade fails,
disable raster processing rather than silently reinstalling vulnerable Pillow.
Revert workflow/instruction changes independently of the security fix if needed.

## Checkpoint

- Baseline inspected; implementation in progress.
