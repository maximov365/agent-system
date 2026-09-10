# Onboarding and upgrades

## New project

Install the framework dependencies in a Python 3.10+ environment. Run the common initializer from the framework:

```bash
bash init-downstream.sh "Project Name" /path/to/project
```

It preserves an existing matching project config, safely serializes a new one when absent, deploys the framework, renders templates, seeds missing project docs, and registers the project after success. `--no-register` creates an isolated trial. Conflicting identity, invalid YAML, framework self-targets, and unsafe destinations fail explicitly.

Open the folder in Codex or another supported client and describe the idea. The agent infers product context and asks only about important unresolved forks. Reuse existing project documents and completed work. Do not force a fixed questionnaire or a separate approval after each role.

For an application, establish the primary user journey and representative screen. For a game, establish controls, core loop, target device, art direction, and a playable vertical slice. See `docs/VISUAL_QUALITY.md` and `docs/GAME_DEVELOPMENT.md`.

## Existing project

Inventory current product/config/architecture and outstanding work before onboarding. Preview the upgrade:

```bash
python3 /path/to/agent-system/sync.py --target /path/to/project --render --diff
```

Inspect framework file changes and any newly seeded files. Then apply the same command without `--diff`. `--dry-run` is another non-mutating preview and works with `--render`. `--all` applies to the registry, so first validate a single project.

## Ownership

- Project-owned: `project.config.yaml`, PRD, architecture and guardrails, deployment/stage contracts, tasks, decisions, memory, brand, application source/dependencies, Codex configuration, and CI.
- Framework-owned: root entry pointers, specialist methods, portable process/tool/model contracts, eval definitions, and `.agent-system/` renderer tools. See `framework_manifest.py` in the framework checkout for the exact mapping.
- Missing project docs are seeded once. Framework task/decision history is not copied as a downstream backlog.
- Sync does not edit Git tracking. Instructions and tooling should be committed when the project needs reproducible clones/worktrees.

The old managed ignore block is replaced with ignores for disposable caches only. Other ignore rules are preserved. Review/stage the resulting changes normally. An existing application `setup.py`, old framework root setup.py, custom PR template, and CI are not overwritten or executed by sync. Existing project-specific guardrails stay intact; reconcile them with new workflow guidance during review.

## Reconfigure

After editing project configuration, run in the downstream:

```bash
python3 .agent-system/setup.py --check
python3 .agent-system/setup.py
```

This re-renders only framework-owned templates. Project docs remain normal editable documents. Original templates are kept in `.templates/`; restore is available through `.agent-system/setup.py --restore` for framework-owned current paths only.

In the framework source checkout, `setup.py --check` verifies source templates without rendering the repository in place. Prefer deployment into a temporary folder for integration checks.

## Codex and legacy clients

`docs/CODEX.md` covers model/configuration and actual tool discovery. `CLAUDE.md` and `.cursor/rules.md` are compatibility pointers. Claude slash commands are optional and not recognized as custom commands by Codex merely because they exist in the repository.

Do not install hooks, services, model gateways, or global settings during normal onboarding unless requested. The post-commit hook now previews upgrades rather than synchronizing live projects automatically.
