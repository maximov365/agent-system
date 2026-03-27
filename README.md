# Agent System

A structured multi-agent workflow framework for AI-assisted software development.

The system enables predictable, safe, and increasingly autonomous product development while preserving architectural discipline.

## How it works

All work flows through a controlled pipeline of specialized agents:

```
Discovery → Product → Analytics Architect → Architect → Builder → Analytics Validator → Reviewer
```

Every request is routed by the **Iteration Manager**, which selects the correct agent, manages transitions, and enforces quality gates.

Non-code artifacts (specs, plans) go through a quality iteration loop before implementation:

```
Generator → Spec Reviewer → Gatekeeper → Reviser → (repeat until accepted)
```

## Quick start

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
  analytics-architect.md     # Design observability
  architect.md               # Plan implementation
  builder.md                 # Implement code
  analytics-validator.md     # Verify instrumentation
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
| **Discovery** | Explores technical options before specification |
| **Product** | Turns ideas into feature specs and task breakdowns |
| **Analytics Architect** | Defines events, metrics, instrumentation |
| **Architect** | Plans implementation before coding |
| **Builder** | Implements approved plans |
| **Analytics Validator** | Verifies instrumentation correctness |
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

## Language

- Repository artifacts (code, docs, prompts): English
- Conversational responses: follow the user's language
