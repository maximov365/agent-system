# Agent System

A portable development workflow for Codex / **GPT-6 Astra**, with compatibility references for Claude Code and Cursor. The active agent owns a task from intent through implementation, visual/runtime verification, and review. Specialist prompts are loaded only when useful.

The September 2026 adaptation replaces mandatory routing ceremony with risk-based execution and fixes unsafe downstream updates. Read the [audit and roadmap](docs/AUDIT-CODEX-ASTRA-2026-09-10.md) and [Codex guide](docs/CODEX.md).

## Quick start

Prerequisites: Python 3.10+, Git, and an available coding-agent client. In the framework repository:

```bash
python3 -m venv .venv
.venv/bin/python3 -m pip install -r requirements-framework.txt
bash init-downstream.sh "My Project" /path/to/my-project
```

Open the new folder in Codex, select GPT-6 Astra, and describe your product or task. A Claude installation, gateway, and slash commands are optional. Use `templates/codex/config.toml` as a minimal model/effort example; merge intentionally into your existing configuration rather than overwriting it.

For an existing downstream:

```bash
.venv/bin/python3 sync.py --target /path/to/project --render --diff
.venv/bin/python3 sync.py --target /path/to/project --render
```

For a temporary trial, use `init-downstream.sh "Trial" /path/to/trial --no-register`.

## How work proceeds

`AGENTS.md` defines the core agreement. `lite` tasks get a brief approach and focused verification; `standard` tasks get acceptance criteria and a short plan; `strict` tasks get durable risk, review, and rollback evidence. All code changes receive proportionate correctness/security review. Visual work is inspected in a running product. Role changes do not force a new user turn or approval.

The existing roles cover research, product, design, motion, copy, analytics, architecture, implementation, and review. They are reference methods, not automatically registered Codex subagents. Delegation is used only when requested/allowed by the task and runtime. A review performed by the same agent is identified as self-review.

The compact entry points to [task-scoped methods](docs/WORK_METHODS.md) and a
project-owned [quality profile](docs/QUALITY_PROFILES.md): source/test navigation,
verified commands and concise check evidence. Independent reads/checks can run
together. Passing checks are repeated for changed inputs or unresolved concerns;
explicit short-lived evidence reuse is available only for reviewed deterministic
checks, with fresh execution required for release/security approval. Model and
reasoning effort stay as requested. See the [research](docs/reviews/EFFICIENCY-RESEARCH.md)
for assumptions and measurement limits.

## High-quality applications and games

- [Design craft](docs/DESIGN_CRAFT.md): composition, typography, semantic color, purposeful motion and specific critique, adapted to the project's own identity.
- [Visual production](docs/VISUAL_QUALITY.md): art direction, references, asset briefs/provenance, runtime screenshots, interaction checks, accessibility, and performance evidence.
- [Game production](docs/GAME_DEVELOPMENT.md): playable vertical slice, simulation/presentation boundaries, animation/audio, frame-time budgets, state/save flows, and real playtesting.
- [Model policy](docs/MODEL_POLICY.md): Astra defaults, API boundaries, model tiers, and honest cost/quality measurement.
- [Tool capabilities](docs/MCP_TOOLS.md): native tools first; optional verified provider integrations.

The framework provides a process and acceptance contracts. Final artistic quality, game feel, and commercial readiness still need product-specific iteration and player/user evidence.

Four narrow native skills are shipped in `.agents/skills/`: readiness, design,
design review and framework upgrade. They route to shared methods; they do not
install providers or change model settings. Discoverability depends on the host's
loaded skill catalog. See the [Codex guide](docs/CODEX.md).

[Project readiness](docs/PROJECT_READINESS.md) separates prerequisites, an HTTP
response, an executed journey and visual review. Run `python3 .agent-system/profile.py doctor`
inside a configured child project for read-only diagnostics. Launch verification
is explicit and reuses the project's own check command.

## Configuration and ownership

`project.config.yaml` contains project identity, optional processing stages, analytics preference, and domain context. Apps and games default to an empty stage list. Existing pipeline configurations remain supported.

`framework_manifest.py` is the common ownership registry for sync, rendering, audit, and hooks. Project docs (including architecture guardrails), project configuration, CI, and application files are preserved. Framework tooling is installed under `.agent-system/`, leaving an application's root `setup.py` alone.

Downstream reconfiguration:

```bash
python3 .agent-system/setup.py --check
python3 .agent-system/setup.py
```

Framework instructions and tooling can be committed in downstream repositories so clones, CI, and worktrees receive the same guidance. Sync updates its old managed ignore block, but does not stage/untrack files, delete obsolete files, or change global tool configuration. Additional user-authored ignore rules remain intact.

## Updates and verification

```bash
.venv/bin/python3 sync.py --all --render --dry-run
.venv/bin/python3 -m unittest discover -s tests -v
.venv/bin/python3 audit.py --local --json
```

Preview flags never apply the update, including when combined with `--render`. Rendering is validated before the first copied file; each file is replaced atomically. The operation is not a full filesystem transaction against disk failure or concurrent writers: use a quiet workspace and inspect failures before retrying.

Hooks are optional. `hooks/pre-commit` can bump VERSION; `hooks/post-commit` previews
downstream changes, which must be applied explicitly. Installed scheduler jobs
remain untouched. Known legacy framework `setup.py` files migrate to a wrapper
only after an exact-hash match; customized/application scripts are preserved.

CI runs deterministic regression tests, template validation, and local audit without needing a machine-specific downstream registry. [Evals](evals/README.md) define model/process comparisons; writing an eval prompt is not a completed benchmark.

## Legacy and limitations

Claude command templates and launchd reminder scripts remain optional compatibility utilities. `/init-downstream` now delegates to the common initializer. The historical transcript metric adapter is explicit opt-in and cannot estimate Astra cost: default metrics report unavailable usage instead of fabricated zero cost. No Codex private transcript format is assumed.

[Full onboarding](docs/ONBOARDING.md), [execution model](docs/AGENT_EXECUTION_MODEL.md), and [decisions](docs/DECISIONS.md) explain the remaining contracts. This repository is MIT licensed; see [LICENSE](LICENSE).

Optional [project quality profiles](docs/QUALITY_PROFILES.md), [visual runner](docs/VISUAL_RUNNER.md), and [asset tooling](docs/ASSET_LIBRARY.md) make acceptance executable. [Examples](examples/README.md) are isolated development fixtures and are never installed in downstream projects.
