# Pull Request Contract

This document defines the PR-based execution mode for agent-system workflows.

The default interactive workflow remains Iteration Manager → specialist agent → handoff. PR-based mode adds a GitHub pull request as the evidence and approval boundary before changes are merged.

---

## Purpose

PR-based mode is for mature workflows where implementation must be tied to objective checks, review evidence, and human approval.

Use PR-based mode when:

- The task changes production code.
- The task affects architecture, security, deployment, analytics, or data handling.
- External reviewers are used.
- CI/CD gates are required before merge.
- The work should be reviewed asynchronously.

---

## Lifecycle

```text
Task → branch → implementation → tests → PR → AI reviews → human approval → merge
```

Iteration Manager still controls agent routing. The PR is the delivery artifact for code changes, not a replacement for workflow state.

---

## Required PR Fields

Every agent-produced PR must include:

- Task ID.
- Link to task spec or user request.
- Link to implementation plan when one exists.
- Implementation summary.
- Test evidence.
- Known risks and limitations.
- AI review reports, including external review reports when used.
- Security review status.
- Human decision field.

The PR template in `.github/pull_request_template.md` encodes these fields.

---

## Branch Rules

- Work must happen on a feature branch.
- Agents must not push directly to `main` or `master`.
- Agents must not force-push unless the user explicitly authorizes the exact operation.
- Agents must not merge their own PRs.
- Human approval is required before merge.

---

## Evidence Requirements

Minimum evidence:

- Relevant test command and result.
- Lint/format result when available.
- Typecheck result when available.
- Security scan result when configured.
- Review verdicts from `Security Reviewer` and `Reviewer`.

For strict mode:

- External review report if requested by policy.
- Coverage report when configured.
- Architecture constraints checked.
- Known residual risks explicitly listed.

---

## CI/CD Requirements

CI is the objective enforcement layer. A PR is not merge-ready until required checks pass or the user explicitly accepts the risk.

Recommended checks:

- Framework audit for agent-system changes.
- Unit tests.
- Lint or format check.
- Typecheck.
- Security scan.
- Eval suite checks for workflow contract changes.

The reference workflow is `.github/workflows/agent-quality.yml`.

---

## Relationship To Other Contracts

- `docs/AGENT_EXECUTION_MODEL.md` defines workflow state and routing.
- `docs/AGENT_HANDOFF_CONTRACT.md` defines agent-to-agent handoff.
- `docs/MODEL_POLICY.md` defines model authority.
- `docs/EXTERNAL_REVIEW_CONTRACT.md` defines external review reports.
- `docs/SANDBOX_POLICY.md` defines command and runtime safety.

When contracts conflict, use the Precedence section in `AGENTS.md` and escalate if the conflict changes scope, safety, architecture, or merge authority.
