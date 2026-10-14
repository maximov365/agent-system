# Audit implementation — 2026-10-14

Owner: current Codex task; self-review, no delegated agents. Baseline: 1.0.46,
5f5299a. Preserve unrelated files and application code. The October 9 report is
the starting evidence; verify the final result against actual current files.

## Acceptance and sequence

1. Browser input/evidence: actual touch events with invalid-context rejection;
   bounded asynchronous assertions; recorded motion settings and discoverable,
   hashed videos. Verify positive and deliberately broken fixtures in Chromium.
   Upgrade Playwright only to an available verified release and matching browser.
2. Reference audit: repair missing history references without distributing root
   history; inspect local Markdown/skill links, deduplicate occurrences and retain
   project identity. Verify a fresh deployment and negative reference fixtures.
3. CI: pin a validated Ubuntu baseline and provide explicit opt-in Ubuntu 26.04
   validation; retain Python 3.10/3.14 and actual browser checks.
4. Readiness: inspect each downstream's own launch/check sources, then populate
   applicable prerequisites and launch contracts. Preserve absent-product status
   and project ownership. Validate profiles and record checks actually performed.
5. Codex/design: refresh current official guidance, improve comparison metadata,
   and audit existing design methods. Keep Astra, optional paid tiers, and no
   compulsory additional provider. Distinguish tooling evidence from unperformed
   model/design comparison.
6. Run full focused suites, template/local/downstream audits, review diff and
   safely propagate framework-owned changes with transaction backups. Record
   limitations, rollback locations and final evidence in a dated review.

## Risks and rollback

Browser updates can alter screenshots; never update approved baselines silently.
Project profiles are application-owned: make targeted additions with originals
saved outside deployed content. Sync must refuse unexpected framework edits and
preserve unrelated work/index state. Restore only this task's changes or use the
sync transaction's verified recovery; never reset a dirty project.

## Progress

- Browser/reference/readiness/evaluation changes implemented and self-reviewed.
- Local release checks: 67 Python tests; six browser-runner tests, one UI-grader
  test (including its frozen copy) and five example logic tests passed.
- All 18 downstreams safely updated to 1.0.48. Their project-owned readiness
  contracts were added separately with recovery backups; Git indexes preserved.
- Seven HTTP launch identities verified; tracker interaction verification and six
  isolated game journeys passed. Iris has no frontend lockfile/dependencies.
- Root audit: 0 critical/0 warnings. Downstream audit: 0 critical/1 warning (Iris).
- Published root implementation e61ba3d and CI follow-up 6d859f0. CI on both
  Ubuntu 24.04 (38551834997) and Ubuntu 26.04 (38551835392) passed all jobs.
  The observed Node 20 deprecation warning is fixed with verified, SHA-pinned
  upstream action releases. Version-only follow-up safely propagated to all 18.
- Final sync plans have zero changes. Root has only the pre-existing untracked
  worktree/log/archive artifacts; downstream application changes remain preserved.
- Implementation complete. The dated review records remaining application setup
  and experimental validation work separately from this framework release.
- Deferred experiments are not release failures: neutral design A/B comparisons,
  actual model/tier measurements and real-device/motion review remain unperformed.
