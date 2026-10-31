# Code review method

Review the implementation for {{ project.name }} under `AGENTS.md`. The current
owner may implement and review; disclose self-review. A review-only assignment
returns findings. If fixes are authorized, apply focused corrections and verify
them in the same task. Do not introduce unrelated features or require a separate
Builder invocation. The owner maintains task state and significant decisions.

## Inputs

Read the actual change, affected source/tests and acceptance or plan if present.
Consult applicable architecture/guardrails and relevant decisions; pipeline
contracts apply only to real processing stages. Read deploy contracts for release,
infrastructure, configuration or migration changes. Reuse relevant test/analytics
findings without treating them as independent proof. No complete document
inventory is required for a small fix.

## Review criteria

Check in this order, at depth proportional to risk:

1. Scope and completeness: accepted behavior is implemented, important plan steps
   are not omitted, and refactors, renames or dependencies have concrete reasons.
2. Architecture: actual boundaries remain coherent; no hidden coupling or side
   effects; domain logic and external I/O have understandable ownership. For a
   declared pipeline, respect its boundaries: {{ pipeline.stages | map(attribute='name') | join(' → ') }}.
3. Security/data: inputs are validated at boundaries; authorization is enforced;
   secrets and private content are not exposed in output/logs; filesystem and
   destructive operations preserve user data and current authority.
4. Correctness: inspect normal, edge, error and cancellation behavior. Prefer
   concrete reproductions over speculative warnings or naming-based inference.
5. Tests/evidence: meaningful non-trivial behavior and security regressions are
   covered; external I/O is controlled where appropriate; failures are explained.
   UI/game acceptance needs running interaction and visual/performance evidence.
6. Maintainability: identify needless complexity, duplicated behavior, fragile
   assumptions and unclear interfaces. Prefer small corrections; style alone is
   not a defect.

## Affected specialized surfaces

- Prompts/model calls: check intentional prompt changes and the project's actual
  prompt location, configured model/provider selection, supported request settings,
  bounded retries and meaningful validation. Follow `docs/MODEL_POLICY.md`; do
  not impose temperature settings or claim deterministic model output. Record
  usage when exposed without logging sensitive content.
- Dependencies: use an existing capability or standard library when suitable;
  verify necessity, compatibility and applicable advisories before adoption.
- Deployment: check required environment changes, migration order/recovery, API
  compatibility, CI and the concrete deployment impact. No universal deployment
  section is needed when the change has no deployment effect.
- Documentation: significant decisions, changed behavior and task state should
  reflect actual results. Avoid routine memory entries and duplicate specs.

## Result

Use APPROVED when no issues remain, APPROVED WITH MINOR CHANGES for nonblocking
findings, and CHANGES REQUIRED for blockers. Lead with concrete findings and
locations, impact and evidence, then checks performed and limitations. Report
missing evidence honestly. Empty checklist sections and handoff JSON add no value
to ordinary review. Preserve scope and separate optional follow-ups from blockers.

When an integration explicitly requests the old sectioned report, load
[its adapter](review-modes/structured-code.md). Handoffs are optional data exchange,
not a reason to stop authorized work. Follow the active model/effort policy.
