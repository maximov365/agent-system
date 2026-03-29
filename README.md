# Agent System

A structured multi-agent workflow framework for AI-assisted software development.

The system enables predictable, safe, and increasingly autonomous product development while preserving architectural discipline.

## How it works

All work flows through a controlled pipeline of specialized agents:

```
Discovery → Product → [Designer] → Analytics Architect → Architect → [Test Strategist] → Builder → Analytics Validator → Security Reviewer → Reviewer
```

Every request is routed by the **Iteration Manager**, which selects the correct agent, manages transitions, and enforces quality gates.

Non-code artifacts (specs, plans) go through a quality iteration loop before implementation:

```
Generator → Spec Reviewer → Gatekeeper → Reviser → (repeat until accepted)
```

## Quick start

Full onboarding guide: [`docs/ONBOARDING.md`](docs/ONBOARDING.md)

1. Edit `project.config.yaml` with your project details
2. Run `python setup.py` to render all templates
3. Start working — Claude/Cursor will follow the agent workflow automatically

```bash
pip install jinja2 pyyaml
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
requirements.txt             # Python dependencies for setup.py
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
  FEATURES.md                # Feature specs (managed by agents)
  FEATURE_MAP.md             # Capability index (you fill this)
  BRAND.md                   # Brand guide (optional)
  FEATURE_TEMPLATE.md        # Template for new features
  TASK_TEMPLATE.md           # Template for new tasks
  AGENT_HANDOFF_CONTRACT.md  # Agent communication format
  AGENT_EXECUTION_MODEL.md   # Execution mechanics
  TASK_BACKLOG_AUTOMATION.md # Backlog management rules
  features/                  # Individual feature spec files
  plans/                     # Implementation plan files
  reviews/                   # Review output files

.cursor/
  rules.md                   # Coding rules (execution, testing, safety, git)

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
pip install jinja2 pyyaml
python setup.py            # render templates with your config
```

6. Add your project-specific docs: `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/PIPELINE_CONTRACTS.md`, etc.
7. Commit and start working

## Upgrading a downstream project

When `agent-system` improves, use `sync.py` to safely update any downstream project:

```bash
# 1. Preview changes
python sync.py --target /path/to/project --diff

# 2. Apply framework files (project-specific files are never touched)
python sync.py --target /path/to/project

# 3. In the target project: re-render templates with local config
cd /path/to/project
python setup.py --check    # verify rendering
python setup.py            # render with local config

# 4. Review and commit
git diff
git add -A && git commit -m "chore: upgrade agent framework to vX.Y.Z"
```

**Safety guarantees:**
- `sync.py` only overwrites framework files (agent definitions, workflow rules, tooling)
- Project-specific files (`docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/TASKS.md`, etc.) are never touched
- `project.config.yaml` is never overwritten — your project identity is preserved
- Use `--diff` to preview every change before applying
- Every step is explicit and reversible (`git checkout` to undo)

The framework version is tracked in `.agent-system-version` in each downstream project.

## Language

- Repository artifacts (code, docs, prompts): English
- Conversational responses: follow the user's language
