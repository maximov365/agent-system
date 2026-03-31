# Agent System

A structured multi-agent workflow framework for AI-assisted software development.

The system enables predictable, safe, and increasingly autonomous product development while preserving architectural discipline.

## How it works

All work flows through a controlled pipeline of specialized agents:

```
Discovery → Product → [Designer] → Analytics Architect → Architect → [Test Strategist] → Builder → Analytics Validator → Security Reviewer → Reviewer
```

Every request is routed by the **Iteration Manager**, which selects the correct agent, manages transitions, and enforces quality gates.

Non-code artifacts (specs, plans) go through a quality loop before implementation:

```
Generator → Spec Reviewer → Gatekeeper → Reviser → Spec Reviewer (repeat until accepted)
```

## Quick start

Full onboarding guide: [`docs/ONBOARDING.md`](docs/ONBOARDING.md)

1. Edit `project.config.yaml` with your project details
2. Run `python setup.py` to render all templates
3. Start working — Claude/Cursor will follow the agent workflow automatically

```bash
pip install -r requirements-framework.txt
python setup.py --check    # preview what will be rendered
python setup.py            # render templates
```

To re-configure after changing the config:

```bash
python setup.py --restore  # restore Jinja2 templates
python setup.py            # render with new values
```

## Project structure

```
project.config.yaml          # Your project configuration (name, pipeline, domain rules)
setup.py                     # Renders Jinja2 templates from config
sync.py                      # Syncs framework files to downstream projects
requirements-framework.txt   # Python deps for setup.py (won't overwrite app's requirements.txt)
VERSION                      # Framework version (auto-bumped by pre-commit hook)
CLAUDE.md                    # Entry point for Claude Code (bootstrap only)
AGENTS.md                    # Workflow rules, agent roles, routing

agents/
  README.md                  # Agent directory overview
  discovery.md               # Explore technical options
  product.md                 # Define features and tasks
  designer.md                # UI mockups and visual prototypes
  analytics-architect.md     # Design observability
  architect.md               # Plan implementation
  test-strategist.md         # Define test strategy
  builder.md                 # Implement code
  analytics-validator.md     # Verify instrumentation
  security-reviewer.md       # Security validation
  reviewer.md                # Review implementation
  spec-reviewer.md           # Evaluate non-code artifacts
  reviser.md                 # Fix non-code artifacts
  gatekeeper.md              # Accept/iterate/escalate decisions
  iteration-manager.md       # Workflow orchestration

docs/
  PRD.md                     # Product requirements (you fill this)
  ARCHITECTURE.md            # System architecture (you fill this)
  ARCHITECTURE_GUARDRAILS.md # Architectural constraints
  ARCHITECTURE_CHECKLIST.md  # Review checklist
  PIPELINE_CONTRACTS.md      # Stage I/O contracts (you fill this)
  TASKS.md                   # Task backlog (managed by agents)
  DECISIONS.md               # Technical decisions (managed by agents)
  LESSONS_LEARNED.md         # Workflow lessons (IM appends; all agents read)
  KNOWN_PATTERNS.md          # Validated patterns (IM appends; all agents read)
  FEATURE_MAP.md             # Capability index (you fill this)
  BRAND.md                   # Brand guide (optional)
  TASK_TEMPLATE.md           # Template for new tasks
  AGENT_HANDOFF_CONTRACT.md  # Agent communication format
  AGENT_EXECUTION_MODEL.md   # Execution mechanics
  TASK_BACKLOG_AUTOMATION.md # Backlog management rules
  ONBOARDING.md              # Guide for new and existing projects
  features/                  # Individual feature spec files
  plans/                     # Implementation plan files
  reviews/                   # Review output files

.cursor/
  rules.md                   # Coding rules (execution, testing, safety, git)

hooks/
  pre-commit                 # Auto-bump VERSION on framework changes
  post-commit                # Auto-sync downstream projects on framework changes
  install.py                 # Install hooks into .git/hooks/

downstream.projects            # Local registry of downstream projects (gitignored)

examples/
  unfolda/                   # Reference project configuration
```

## Agent roles

| Agent | Role |
|---|---|
| **Iteration Manager** | Routes requests, manages transitions, controls quality loops |
| **Discovery** | Explores technical and market options before specification |
| **Product** | Turns ideas into feature specs and task breakdowns |
| **Designer** | Creates UI mockups and iterates with user feedback (optional) |
| **Analytics Architect** | Defines events, metrics, instrumentation |
| **Architect** | Plans implementation before coding |
| **Test Strategist** | Defines test strategy before implementation (optional) |
| **Builder** | Implements approved plans |
| **Analytics Validator** | Verifies instrumentation correctness |
| **Security Reviewer** | Validates code for security vulnerabilities and unsafe patterns |
| **Reviewer** | Reviews code for correctness and architecture compliance |
| **Spec Reviewer** | Evaluates non-code artifact quality |
| **Reviser** | Fixes non-code artifacts based on review feedback |
| **Gatekeeper** | Final accept/iterate/escalate decision |

## Configuration

All project-specific content lives in `project.config.yaml`. The file controls:

- **project** — name, description
- **pipeline** — processing stages
- **domain_rules** — LLM rules, pipeline principles
- **analytics_by_default** — whether features require analytics specs
- **output_docs** — optional brand guide and custom documentation

`setup.py` passes the entire YAML as the Jinja2 rendering context, so all top-level keys are available. Commonly used template variables: `project.name`, `project.description`, `pipeline.stages`, `analytics_by_default`. Conditional blocks (`{% if analytics_by_default %}`, `{% if pipeline.stages %}`) control optional sections. Keys like `domain_rules`, `output_docs`, and per-stage `description` are not expanded into template files by default — they serve as structured reference data that agents read directly from `project.config.yaml` at runtime.

See [`examples/unfolda/`](examples/unfolda/) for a complete real-world configuration.

## New project setup

1. Create a new repository for your project
2. Copy `project.config.yaml` from this repo (or use `examples/unfolda/project.config.yaml` as a reference)
3. Edit `project.config.yaml` with your project details — name, description, pipeline stages, domain rules
4. Run sync to copy the framework files:

```bash
# From agent-system repo:
python sync.py --target /path/to/your-project     # copy framework files
```

5. Install dependencies and render templates in the new project:

```bash
cd /path/to/your-project
pip install -r requirements-framework.txt
python setup.py            # render templates with your config
```

6. Add your project-specific docs: `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/PIPELINE_CONTRACTS.md`, etc.
7. Create empty organizational memory files: `docs/LESSONS_LEARNED.md`, `docs/KNOWN_PATTERNS.md`
8. Commit and start working

## Upgrading downstream projects

### Automatic (recommended)

Register downstream projects and let the post-commit hook handle sync + render automatically:

```bash
# 1. Register your projects (one path per line)
echo "/Users/you/projects/my-app" >> downstream.projects

# 2. Install hooks (once after cloning)
python3 hooks/install.py

# 3. Commit framework changes — downstream projects update automatically
git add -A && git commit -m "feat: improve architect agent"
# post-commit hook detects framework file changes → runs sync.py --all --render
```

### Manual

```bash
# Sync + render a single project
python sync.py --target /path/to/project --render

# Sync all registered projects
python sync.py --all --render

# Preview without writing
python sync.py --all --dry-run
python sync.py --target /path/to/project --diff
```

**Safety guarantees:**
- `sync.py` only overwrites framework files (agent definitions, workflow rules, tooling)
- Project-specific files (`docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/TASKS.md`, etc.) are never touched
- `project.config.yaml` is never overwritten — your project identity is preserved
- Framework files are automatically added to downstream `.gitignore` (managed block)
- Framework files are removed from downstream git tracking on first sync (`git rm --cached`)
- `find_python` auto-discovers project venvs for template rendering
- `downstream.projects` is gitignored (machine-specific paths)

After cloning a downstream project, run `sync.py --target <project> --render` to restore framework files.

## Versioning

`VERSION` is auto-bumped (patch increment) on every commit that changes framework files. A pre-commit hook detects staged framework file changes and increments `VERSION` automatically. A post-commit hook then syncs all registered downstream projects.

To install hooks after cloning:

```bash
python3 hooks/install.py
```

## Language

- Repository artifacts (code, docs, prompts): English
- Conversational responses: follow the user's language
