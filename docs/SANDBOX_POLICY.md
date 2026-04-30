# Sandbox Policy

This document defines safety constraints for agent command execution and optional automated runtimes.

It applies to Cursor, Claude Code, OpenHands, OpenAI Agents SDK, LangGraph, local scripts, CI jobs, and any other runtime that executes agent-selected commands.

---

## Goals

- Let agents inspect code, run tests, and produce review evidence.
- Prevent accidental damage to the main branch, secrets, production data, or user machines.
- Make sandbox assumptions explicit when moving from an interactive IDE session to automated runtimes.

---

## Baseline Rules

- Agents work on feature branches, not directly on `main` or `master`.
- Destructive commands require explicit user confirmation.
- Secrets, tokens, credentials, private keys, and `.env` files must not be read unless the user explicitly authorizes that operation.
- Network access should be limited to required package managers, VCS remotes, and approved services.
- Database migrations must run in dry-run or preview mode first when the tooling supports it.
- Push, merge, release, production deploy, and force-push remain manual unless the user explicitly delegates a specific operation.
- Agents must not disable CI, lint, tests, typecheck, security scans, branch protection, or review gates.

---

## Forbidden Without Explicit Approval

- `rm -rf` or equivalent recursive deletion outside generated build artifacts.
- `git reset --hard`, `git clean`, force-push, history rewrite, or branch deletion.
- Reading `.env`, credential stores, SSH keys, API keys, production dumps, or customer data.
- Writing to production databases or production object stores.
- Running migrations against production.
- Installing or starting persistent system services.
- Opening broad network access for unreviewed tools.

If a task appears to require one of these actions, stop and ask the user for confirmation with the exact command or access requested.

---

## Recommended Runtime Profile

Interactive IDE runtimes should provide:

- Repository-scoped write access.
- Read access to framework documents and relevant source files.
- Explicit confirmation for destructive git and filesystem operations.
- Tool output capture for test evidence.
- Clear indication when commands ran outside a sandbox.

Automated runtimes should additionally provide:

- Disposable workspace per task.
- Clean checkout of the target branch.
- No mounted user secrets by default.
- Network allowlist.
- CPU, memory, and wall-clock limits.
- Persistent workflow state under `.agent/workflows/`.
- Artifact collection for logs, reports, diffs, and review outputs.

---

## Docker / Devcontainer Target

Projects that want stronger isolation may add a devcontainer or Docker Compose profile.

Recommended files:

```text
.devcontainer/devcontainer.json
.devcontainer/docker-compose.agent.yml
```

Minimum container requirements:

- Mount only the repository workspace.
- Use a non-root user where practical.
- Mount dependency caches explicitly, not the full home directory.
- Do not mount host SSH keys or credential stores by default.
- Provide package-manager network access only when needed.
- Keep production credentials out of the container.

The devcontainer is optional for the framework, but recommended for autonomous runtimes that execute long command sequences.

---

## CI/CD Boundary

CI is the objective enforcement layer. Agents may generate evidence for CI, but CI decides whether objective checks pass.

Minimum PR gates:

- Lint or formatting check when available.
- Unit tests or the smallest relevant test suite.
- Typecheck when the project has typed code.
- Security scan when configured.
- Coverage reporting when configured.
- Required human approval before merge.

See `docs/PULL_REQUEST_CONTRACT.md` for PR evidence requirements.

---

## Runtime Escalation

Escalate to the user when:

- The runtime cannot guarantee sandbox constraints.
- Required tests need credentials or network access beyond the approved profile.
- A command would modify data outside the repository.
- A migration cannot be dry-run.
- The current branch or workspace is ambiguous.
- The agent detects secrets in files proposed for commit or external review.
