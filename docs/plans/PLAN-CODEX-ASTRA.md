# Codex / GPT-6 Astra adaptation

Date: 2026-09-10. User requested a complete framework audit, adaptation to Codex / GPT-6 Astra, and improvements for high-quality games, applications, and graphics.

## Scope and acceptance

1. Audit entry instructions, role transitions, model/tool assumptions, graphics, sync/render/bootstrap, CI, evals, and metrics. Record findings with evidence and distinguish verified bugs from recommendations.
2. Make AGENTS.md the portable entry point. Preserve specialist knowledge through selective reading. Continue authorized work within one task; use proportionate review and honest evidence.
3. Document verified Astra configuration and native Codex capabilities without changing the user's global settings, starting services, installing providers, or inventing model access.
4. Add visual and game production contracts covering art direction, reusable assets, runtime inspection, playtesting, accessibility, and measured performance.
5. Fix demonstrated sync/render/bootstrap hazards and add focused regression tests. Preview must never mutate, project CI/config must survive, invalid render must fail before copies, and application setup.py must not be replaced.
6. Make local audit work without a downstream registry and make CI detect real failures. Retain legacy adapters with explicit scope and limitations.
7. Review the final diff for correctness/security, run regression tests and isolated deployment checks, and report remaining limitations.

This is a cross-cutting framework migration, so more than ten files are necessary: bootstraps, shared policy, specialized graphics rules, deployment tooling, and verification must agree. No third-party dependencies are needed beyond existing Jinja2/PyYAML.

## Boundaries

- Only agent-system is changed. Registered downstream projects are not synchronized during this task.
- Existing untracked worktrees and weekly-review logs are preserved.
- No commit, push, model API run, paid asset generation, or background automation is required.
- A framework process cannot guarantee commercial-quality art or gameplay by itself; runtime/device evidence and independent user evaluation remain necessary.

## Validation

Use standard-library unittest with temporary repositories, both current and legacy project configurations, repeated render/sync, invalid configuration, dry-run/diff plus render, CI seed preservation, template-to-static upgrades, and path/symlink cases. Run audit independently of local downstream configuration. Model behavior evals are specified separately from deterministic tool tests; do not report unrun model evals as passed.

## Outcome

Completed locally on 2026-09-10. Audit and recommendations: `docs/AUDIT-CODEX-ASTRA-2026-09-10.md`. Implementation and owner security/correctness review completed. All 22 regression tests, the 5-check Unfolda fixture, template preflight, syntax checks, and local audit passed their required gates; one optional prompt-size advisory remains. Full evidence and unrun behavioral/model checks are recorded in `docs/reviews/CODEX-ASTRA-VALIDATION.md`.
