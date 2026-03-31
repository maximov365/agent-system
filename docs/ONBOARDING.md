# Onboarding Guide — Agent System

This guide covers everything needed to adopt the agent system in a new or existing project.

---

## What the agent system gives you

A structured workflow where every development task is handled by a specialized AI agent — not a single general-purpose LLM doing everything at once.

**Without the system:** You send a feature request, the AI thinks about it and writes code immediately. There is no verification that the plan is sound, no review that the code is correct, no tracking of decisions.

**With the system:** Requests are routed through a controlled pipeline. Discovery clarifies unknowns (including market research), Product defines scope, Designer creates UI mockups for user feedback, Analytics Architect defines measurement, Architect plans, Test Strategist defines what to test, Builder implements, Analytics Validator verifies instrumentation, Security Reviewer checks for vulnerabilities, Reviewer validates. Each step is explicit and the output of one step is the input to the next.

The key benefits:
- Architectural discipline — code stays inside defined boundaries
- Traceability — decisions, tasks, and plans are recorded in docs
- Predictability — agents follow a defined workflow, not improvise
- Autonomy with guardrails — agents can chain without user input on every step

---

## Concepts

### project.config.yaml

The single source of truth for everything project-specific:

- Project name and description (injected into all agent files at render time)
- Pipeline stage names and descriptions (agents reference these when discussing the system)
- Domain rules (LLM guidelines, pipeline principles — read by agents at runtime)
- Analytics settings
- Optional: brand guide flag, custom docs list

Agents read this file directly at runtime for context. Some fields are also rendered into Jinja2 templates via `setup.py`.

### Framework files vs project files

The agent system is split into two categories:

| Category | Managed by | Examples |
|---|---|---|
| **Framework files** | `agent-system` repo, via `sync.py` | `agents/*.md`, `AGENTS.md`, `CLAUDE.md`, `.cursor/rules.md`, `setup.py` |
| **Project files** | You, in your project repo | `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/TASKS.md`, `project.config.yaml` |

Framework files are templates rendered with your project config. Project files are written by you (or by agents operating within your project) and are never overwritten by `sync.py`.

### Rendering

`setup.py` takes the framework file templates (stored in `.templates/`) and renders them with values from `project.config.yaml`. The result is agent definitions that say "You are the Builder agent for **YourProject**" instead of `{{ project.name }}`.

### Organizational memory (`LESSONS_LEARNED.md`, `KNOWN_PATTERNS.md`)

Two **project-owned** files accumulate experience across workflows:

- **`docs/LESSONS_LEARNED.md`** — after each completed workflow, Iteration Manager appends what went wrong, which review or `must_fix` themes repeated, and what worked.
- **`docs/KNOWN_PATTERNS.md`** — durable approaches that proved correct in practice (complements `docs/DECISIONS.md`).

Every agent reads both files before work (see `CLAUDE.md` and `AGENTS.md`). They are **not** on the `sync.py` copy list so that framework upgrades do not overwrite your project’s accumulated history. Seed empty files from the `agent-system` repo’s `docs/` templates when adopting the system, then keep them in version control.

### Development workflow

All code changes follow a structured pipeline. The full workflow for features with measurable outcomes:

```
Discovery → Product → [Designer] → Analytics Architect → Architect → [Test Strategist] → Builder → Analytics Validator → Security Reviewer → Reviewer
```

Internal technical changes (refactors, config, dependencies):

```
Discovery → Architect → [Test Strategist] → Builder → Security Reviewer → Reviewer
```

Brackets indicate optional steps. Designer runs for features with user-facing UI that need visual design. Test Strategist is invoked when the task has non-trivial testable logic. Security Reviewer runs for all code changes. Analytics Architect and Analytics Validator are paired: if one runs, the other must too.

Non-code artifacts go through a quality loop:

```
Generator → Spec Reviewer → Gatekeeper → Reviser → Spec Reviewer (repeat until accepted)
```

---

## Scenario A — Guided onboarding (recommended)

The fastest way to start. You create a minimal project, sync framework files, and then the agent system guides you through creating all project documents via conversation.

### 1. Create a repository and bootstrap

```bash
mkdir my-project && cd my-project
git init
cp /path/to/agent-system/project.config.yaml ./project.config.yaml
```

You do **not** need to fill in `project.config.yaml` — the agents will populate it during onboarding.

### 2. Sync framework files and render

```bash
# From agent-system directory:
python sync.py --target /path/to/my-project

# In your project:
cd my-project
pip install -r requirements-framework.txt
python setup.py
```

### 3. Create empty doc stubs and commit

```bash
mkdir -p docs
for f in PRD.md ARCHITECTURE.md PIPELINE_CONTRACTS.md FEATURE_MAP.md TASKS.md DECISIONS.md LESSONS_LEARNED.md KNOWN_PATTERNS.md; do
  [ ! -f "docs/$f" ] && echo "<!-- placeholder -->" > "docs/$f"
done
git add -A
git commit -m "chore: bootstrap agent system v$(cat .agent-system-version)"
```

### 4. Start the guided onboarding

Open the project in Cursor and say:

> **"Запускаем новый проект"** (or "Start a new project")

The Iteration Manager detects that project docs are empty stubs and starts the **Onboarding Workflow** (defined in `AGENTS.md`):

| Phase | Agent | What happens | Output |
|---|---|---|---|
| 1 | Discovery | Asks about product identity, users, competitors, technical constraints | Discovery Brief |
| 2 | Product | Asks follow-ups, produces PRD → Quality Loop (up to 3 iterations) | `docs/PRD.md` |
| 3 | Designer | Asks about brand, colors, typography, UI patterns → Quality Loop | `docs/BRAND.md` |
| 4 | Architect | Asks about tech stack, pipeline, domain rules → Quality Loop | `docs/ARCHITECTURE.md`, `docs/PIPELINE_CONTRACTS.md`, `docs/FEATURE_MAP.md` |
| 5 | IM | Generates `project.config.yaml`, re-renders templates, creates stubs, commits | Ready for development |

Phase 3 (Designer) is optional — skipped for backend-only or API-only products.

### What you need to know before starting

The agents will ask you everything they need, but it helps to have thought about:

- **What the product does** — a clear 2–3 sentence description
- **Who it's for** — 2–4 user segments
- **What makes it different** — competitive context
- **Technical constraints** — platform, language, privacy rules
- **What's in MVP** — and what's explicitly not

You don't need polished answers. The agents refine through iteration.

---

## Scenario B — Manual setup

For teams that prefer to write project documents directly, or when adopting the agent system into an existing project with established docs.

### 1. Create a repository

```bash
mkdir my-project && cd my-project
git init
```

### 2. Create project.config.yaml

Copy the template from agent-system and fill in your project details:

```bash
cp /path/to/agent-system/project.config.yaml ./project.config.yaml
```

Or use the Unfolda example as a reference for a richer config:

```bash
cp /path/to/agent-system/examples/unfolda/project.config.yaml ./project.config.yaml
```

**Minimum required fields:**

```yaml
project:
  name: "Your Project Name"
  description: |-
    One paragraph describing what the product does and for whom.

pipeline:
  stages:
    - name: stage_one
      description: "What this stage does"
    - name: stage_two
      description: "What this stage does"

analytics_by_default: false  # set true if the project requires analytics specs

domain_rules:
  llm_rules: |
    - Project-specific rules for LLM behavior
  pipeline_principles: |
    - Key principles agents should follow

output_docs:
  has_brand_guide: false
```

### 3. Sync framework files

From the `agent-system` directory:

```bash
python sync.py --target /path/to/my-project --diff    # preview
python sync.py --target /path/to/my-project            # apply
```

### 4. Render templates

In your project:

```bash
cd my-project
pip install -r requirements-framework.txt
python setup.py
```

### 5. Create project-specific docs

These are not created by the agent system — you write them. Agents will read them at runtime:

| File | What to put in it |
|---|---|
| `docs/PRD.md` | Product requirements — what you're building and why |
| `docs/ARCHITECTURE.md` | System architecture — components, boundaries, data flow |
| `docs/PIPELINE_CONTRACTS.md` | Input/output contracts for each pipeline stage |
| `docs/FEATURE_MAP.md` | Capability blocks and their dependencies |
| `docs/TASKS.md` | Start empty — agents will add tasks here |
| `docs/DECISIONS.md` | Start empty — agents will record decisions here |
| `docs/LESSONS_LEARNED.md` | Start empty — Iteration Manager appends after completed workflows |
| `docs/KNOWN_PATTERNS.md` | Start empty — Iteration Manager appends validated patterns |

Create these files manually (they are project-owned and not included in `sync.py`). Fill PRD, ARCHITECTURE, and PIPELINE_CONTRACTS with your project content; the rest can start empty.

### 6. Commit and start working

```bash
git add -A
git commit -m "chore: bootstrap agent system v$(cat .agent-system-version)"
```

Open Cursor in your project directory. The agent workflow is active immediately.

---

## Scenario C — Existing project

### 1. Check prerequisites

The only requirement is that `project.config.yaml` exists at the project root. If the project already used a previous version of the agent system with hardcoded agent files, this is still the right path — the sync will overwrite the old files cleanly.

If `project.config.yaml` does not exist yet:

```bash
cp /path/to/agent-system/examples/unfolda/project.config.yaml /path/to/my-project/project.config.yaml
# Edit it with your project's actual details
```

### 2. Preview changes

```bash
cd /path/to/agent-system
python sync.py --target /path/to/my-project --diff
```

The diff will show:
- Which framework files are new (not in the project yet)
- Which framework files differ from the current version
- Exact line-by-line changes for each file

Review the diff. Framework files should only include agent definitions, workflow rules, and tooling — never application code or product docs.

### 3. Apply

```bash
python sync.py --target /path/to/my-project
```

This copies framework files and writes `.agent-system-version`. It also runs `setup.py --check` automatically to verify templates will render correctly.

### 4. Render

```bash
cd /path/to/my-project
pip install -r requirements-framework.txt   # if not already installed
python setup.py
```

### 5. Review and commit

```bash
git diff        # verify only framework files changed
git add -A
git commit -m "chore: upgrade agent framework to v$(cat .agent-system-version)"
```

If anything looks wrong — `git checkout .` reverts everything.

---

## Upgrading an existing installation

When `agent-system` is updated with improvements, apply them to any downstream project with the same three-step process:

```bash
# From agent-system:
python sync.py --target /path/to/project --diff    # review
python sync.py --target /path/to/project            # apply

# In the project:
cd /path/to/project
python setup.py                                     # re-render
git diff && git add -A && git commit -m "chore: upgrade agent framework to vX.Y.Z"
```

The framework version before and after is shown in the sync summary.

---

## What agents need to work

After setup, agents expect to find these files in your project:

| File | Required | Purpose |
|---|---|---|
| `project.config.yaml` | **Yes** | Project identity, pipeline, domain rules |
| `docs/PRD.md` | **Yes** | Product requirements — read before any task |
| `docs/ARCHITECTURE.md` | **Yes** | System design — read before any task |
| `docs/ARCHITECTURE_GUARDRAILS.md` | auto (framework) | Constraints agents enforce |
| `docs/PIPELINE_CONTRACTS.md` | **Yes** | Stage I/O contracts |
| `docs/TASKS.md` | **Yes** | Task backlog (can start as stub) |
| `docs/DECISIONS.md` | **Yes** | Decision log (can start as stub) |
| `docs/FEATURE_MAP.md` | **Yes** | Capability index |
| `docs/LESSONS_LEARNED.md` | **Yes** | Workflow lessons — starts empty; IM appends |
| `docs/KNOWN_PATTERNS.md` | **Yes** | Validated patterns — starts empty; IM appends |
| `docs/BRAND.md` | optional | Required only for UI/design tasks |

Agents will ask you to fill in missing required docs before proceeding. They will not fabricate missing context.

---

## How to work with agents day-to-day

You don't invoke agents directly by name. You describe what you want and the Iteration Manager routes the request to the correct agent.

**Examples:**

> "I want to add support for multiple target languages in a single job"

→ Iteration Manager evaluates: feature idea, scope unclear → routes to Product.

> "We need to decide between Redis and PostgreSQL LISTEN/NOTIFY for the job queue"

→ Iteration Manager evaluates: technical uncertainty, multiple approaches → routes to Discovery.

> "Implement task TASK-042 from the backlog"

→ Iteration Manager evaluates: task exists, Architect plan approved → routes to Builder.

The system self-documents. After each workflow cycle:
- Tasks are updated in `docs/TASKS.md`
- Decisions are recorded in `docs/DECISIONS.md`
- Lessons and review themes are appended to `docs/LESSONS_LEARNED.md`
- Validated patterns are recorded in `docs/KNOWN_PATTERNS.md`

---

## File ownership reference

Quick reference for what to edit yourself vs what is managed by the framework:

| File | Who edits |
|---|---|
| `project.config.yaml` | You |
| `docs/PRD.md` | You |
| `docs/ARCHITECTURE.md` | You + agents (architecture updates) |
| `docs/PIPELINE_CONTRACTS.md` | You + agents |
| `docs/FEATURE_MAP.md` | You + agents |
| `docs/BRAND.md` | You |
| `docs/TASKS.md` | Iteration Manager (commits); Product, Architect (propose only) |
| `docs/DECISIONS.md` | Agents (Builder, Architect, Discovery — write; Iteration Manager — routes) |
| `docs/LESSONS_LEARNED.md` | Iteration Manager (append after completed workflows); all agents read |
| `docs/KNOWN_PATTERNS.md` | Iteration Manager (append when a pattern is validated); all agents read |
| `agents/*.md` | Framework (`sync.py` + `setup.py`) |
| `AGENTS.md` | Framework |
| `CLAUDE.md` | Framework |
| `.cursor/rules.md` | Framework |
| `setup.py` | Framework |
| `requirements-framework.txt` | Framework (will not overwrite app's `requirements.txt`) |
| `docs/AGENT_HANDOFF_CONTRACT.md` | Framework |
| `docs/AGENT_EXECUTION_MODEL.md` | Framework |
| `docs/TASK_BACKLOG_AUTOMATION.md` | Framework |
| `docs/ARCHITECTURE_GUARDRAILS.md` | Framework |
| `docs/ARCHITECTURE_CHECKLIST.md` | Framework |
| `docs/TASK_TEMPLATE.md` | Framework |
| `docs/ONBOARDING.md` | Framework |

---

## Reference: sync.py options

```
python sync.py --target PATH              Copy framework files to target
python sync.py --target PATH --dry-run   Preview: show what would change
python sync.py --target PATH --diff      Preview: show unified diff of changes
```

**Safety guarantees:**
- Refuses to run if target has no `project.config.yaml`
- Only touches files in the framework list — never application code
- `project.config.yaml` is never overwritten
- Every operation is reversible with `git checkout`

---

## Reference: setup.py options

Run inside the project directory (not agent-system):

```
python setup.py              Render all templates from project.config.yaml
python setup.py --check      Dry-run: preview what would be rendered
python setup.py --restore    Restore Jinja2 source templates from .templates/
```
