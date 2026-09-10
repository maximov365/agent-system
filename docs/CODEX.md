# Codex / GPT-6 Astra

## Start here

Open the agent-system repository in Codex and select **GPT-6 Astra**. The root `AGENTS.md` provides the portable workflow. No Claude installation, slash-command installer, model gateway, or new API key is needed merely to work in an existing signed-in Codex session.

For a downstream project, preview first:

```bash
python3 /path/to/agent-system/sync.py --target /path/to/project --render --dry-run
python3 /path/to/agent-system/sync.py --target /path/to/project --render
```

For a new project:

```bash
bash /path/to/agent-system/init-downstream.sh "My Game" /path/to/my-game
```

Then open that folder in Codex, describe the intended result, and include target platform/device and visual references when available. The agent should make routine assumptions and continue; onboarding does not require completing a fixed questionnaire.

## Model configuration

`templates/codex/config.toml` is a minimal optional example. Merge its two settings into the intended Codex configuration layer only if needed; do not overwrite an existing config, permissions, MCP servers, or credentials. The framework does not install it automatically.

Codex reads project `.codex/config.toml` only for trusted projects; user defaults live in `~/.codex/config.toml`. Model and effort can be configured there. [Official configuration guide](https://learn.chatgpt.com/docs/config-file/config-basic).

Codex discovers AGENTS.md guidance along the project path, with closer files overriding earlier guidance. The default aggregate instruction cap is 32 KiB. Keep the root short and load references selectively. [Official instruction guide](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

## Capabilities

Use the actual tools exposed by the host. Native image generation is preferred when available; an MCP server is optional. Use real screenshots and interactions for visual verification, and measure the running application for performance claims. Never report generated art or a viewed screenshot unless the tool actually produced or displayed it.

For reusable procedures, Codex supports skills with progressive loading and repository skills in `.agents/skills/`. Existing `agents/*.md` files are reference methods, not automatically registered native agents or skills. Package a few proven workflows later rather than converting every role into an always-on plugin. [Official skills guide](https://learn.chatgpt.com/docs/build-skills).

Use built-in task scheduling only when a user requests recurring work; do not install a launchd reminder as part of ordinary project initialization. Model-specific API features are distinct from Codex desktop capabilities; `docs/MODEL_POLICY.md` covers the boundary.

## Validation and rollout

In the framework repository, install `requirements-dev.txt` into an appropriate Python environment for the complete regression suite (`requirements-framework.txt` remains sufficient for sync/render only), then run:

```bash
python3 -m unittest discover -s tests -v
python3 audit.py --local --json --fail-on critical
```

Review the diff for one downstream before rolling out more widely. Existing project config, product docs, local CI, and application setup.py remain project-owned. Downstream framework instructions stay in version control so clones/worktrees can reproduce them; sync no longer edits the Git index. Review/stage changes normally.

Sync replaces its managed ignore block and installs rendering under `.agent-system/`. Known exact legacy root setup.py copies are migrated to a compatibility entry point with recovery backups; locally modified/application scripts remain untouched. See `docs/FRAMEWORK_UPGRADE.md` for preview, backup, lock, and restore behavior. Use the namespaced path for reconfiguration:

```bash
python3 .agent-system/setup.py --check
python3 .agent-system/setup.py
```
