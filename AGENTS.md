# AI Agent Workflow

This repository uses a structured multi-agent workflow for AI-assisted development.

The goal is to enable **predictable, safe, and increasingly autonomous product development** while preserving architectural discipline.

The system supports both:

1. **Deterministic implementation workflow**
2. **Quality-improvement loops for specifications and plans**

All production code implementation must follow the:

Architect → [Test Strategist] → Builder → Security Reviewer → Reviewer

cycle. Test Strategist is optional — Iteration Manager invokes it when the task has non-trivial testable logic.

Earlier steps (Discovery, Product, Designer, Analytics Architect) are used to clarify scope, product design, visual direction, and measurement before implementation.

---

# Project

**{{ project.name }}**

{{ project.description }}

{% if pipeline.stages %}
The system processes work through a pipeline: {{ pipeline.stages | map(attribute='name') | join(' → ') }}
{% endif %}
The project prioritizes:

- deterministic pipelines
- clear architecture boundaries
- minimal dependencies
- predictable AI behavior
- measurable product outcomes

---

# Agent Roles

The repository defines several agent roles.

## Discovery

Defined in: `agents/discovery.md`

Responsibilities:

- Explore technical options and market references
- Compare realistic approaches
- Research competitors and analogous products (when relevant)
- Identify trade-offs and risks
- Recommend the simplest viable direction
- Suggest whether the decision should be recorded in `docs/DECISIONS.md`

Discovery operates in two modes: **Technical Discovery** (how to build) and **Market & Competitive Discovery** (what others do, best practices). Both can be combined.

Discovery **does not write production code**.

---

## Product

Defined in: `agents/product.md`

Responsibilities:

- Turn rough ideas into clear feature specifications
- Define scope, non-goals, and acceptance criteria
- Break work into implementation-ready tasks
- Identify dependencies and risks
- Recommend the next smallest useful task

Product **does not write production code**.

---

## Designer

Defined in: `agents/designer.md`

Responsibilities:

- Create UI mockups and visual prototypes for features
- Present designs to the user for review
- Iterate based on user feedback
- Produce a finalized design artifact for Architect

Designer **does not write production code** and **does not define product scope**.

Designer is optional. It runs **after the Product specification is accepted and before Analytics Architect or Architect**, when the feature has a user-facing UI component that needs visual design.

---

## Analytics Architect

Defined in: `agents/analytics-architect.md`

Responsibilities:

- Ensure that every feature is **measurable**
- Define analytics events
- Define event properties
- Define product metrics
- Define operational metrics
- Link metrics to product goals
- Specify where instrumentation should occur

Analytics Architect **does not change product scope** and **does not implement code**.

Analytics definitions must exist **before Architect planning begins**.

Architect may add instrumentation if required by implementation constraints, but must not remove or weaken defined analytics events. When Analytics Architect has been used, Architect must include instrumentation in the implementation plan.

---

## Architect

Defined in: `agents/architect.md`

Responsibilities:

- Understand the task
- Align the task with PRD and architecture
- Propose a minimal implementation plan
- Identify risks and dependencies
- Define acceptance criteria
- Define which files will change
- Integrate analytics instrumentation if required

Architect **does not write production code**.

---

## Test Strategist

Defined in: `agents/test-strategist.md`

Responsibilities:

- Define test strategy for the approved Architect plan
- Identify test levels (unit, integration, end-to-end)
- Identify critical edge cases and failure modes
- Produce a test plan that Builder uses alongside the implementation plan

Test Strategist **does not write code** and **does not modify the implementation plan**.

Test Strategist is optional. It runs **after the Architect plan is accepted and before Builder**, when the task has non-trivial testable logic. Iteration Manager decides whether to invoke it.

---

## Builder

Defined in: `agents/builder.md`

Responsibilities:

- Implement the approved Architect plan
- Modify the smallest possible number of files
- Keep changes simple and reviewable
- Respect pipeline boundaries
- Run verification steps during implementation
- Respect file-change limits defined in `.cursor/rules.md`

Builder **does not expand scope beyond the approved plan**.

---

## Security Reviewer

Defined in: `agents/security-reviewer.md`

Responsibilities:

- Check for common vulnerability patterns (injection, exposure, unsafe operations)
- Verify input validation at system boundaries
- Verify secrets handling
- Verify authentication and authorization logic
- Verify data exposure and dependency safety
- Report all findings as structured output

Security Reviewer **does not implement fixes** and **does not review architecture compliance or scope**.

Security Reviewer runs **after Builder and before Reviewer** for all code changes.

---

## Analytics Validator

Defined in: `agents/analytics-validator.md`

Responsibilities:

- Verify that analytics events defined by Analytics Architect were implemented
- Check event naming consistency
- Check event property schemas
- Ensure metrics can be derived from instrumentation
- Ensure instrumentation does not break pipeline behavior

Analytics Validator **does not modify implementation logic**.

Analytics Validator runs **after Builder and before Security Reviewer** when Builder changed or introduced analytics instrumentation.

---

## Reviewer

Defined in: `agents/reviewer.md`

Responsibilities:

- Verify that implementation follows the approved plan
- Ensure architecture rules are respected
- Validate safety, tests, and dependencies
- Detect scope creep
- Approve or request changes

Reviewer **does not implement new features**.

Reviewer is the **final mandatory step** for all code changes, including those that went through Analytics Validator.

---

# Meta-Orchestration Roles

To support autonomous product iteration, the system introduces orchestration roles.

## Iteration Manager

Defined in: `agents/iteration-manager.md`

Coordinates the workflow.

Responsibilities:

- Determine the correct starting agent
- Decide whether a quality iteration loop is required
- Enforce iteration limits
- Move artifacts to the next workflow stage
- Decide when user input is required
- Escalate to the user when necessary

Iteration Manager **does not produce workflow artifacts** (specifications, plans, code). It produces routing JSON, handoff blocks, and the closing user-facing summary defined in `CLAUDE.md`.

---

## Spec Reviewer

Defined in: `agents/spec-reviewer.md`

Spec Reviewer **does not write code** and **does not rewrite artifacts**.

Used for reviewing **non-code artifacts** such as:

- feature specifications
- task breakdowns
- implementation plans
- design notes
- decision notes

Responsibilities:

- Evaluate artifact quality
- Score artifacts using a defined rubric
- Identify must-fix issues
- Identify architectural conflicts
- Produce structured feedback

---

## Reviser

Defined in: `agents/reviser.md`

Used within the quality iteration loop to improve non-code artifacts based on Spec Reviewer feedback.

Responsibilities:

- Apply all `must_fix` changes identified by Spec Reviewer
- Preserve intent and scope of the original artifact
- Avoid introducing new scope or architectural decisions
- Produce a revised artifact ready for Gatekeeper evaluation

Reviser **does not produce original artifacts** and **does not change product scope**.

---

## Gatekeeper

Defined in: `agents/gatekeeper.md`

Gatekeeper **does not rewrite artifacts** and **does not make architectural decisions**.

Final decision-maker for iteration loops.

Responsibilities:

- Determine whether artifact quality is sufficient
- Decide whether another iteration is required
- Escalate to the user if needed

---

# Agent Routing Rules

All requests are first interpreted by Iteration Manager, which determines the appropriate starting agent.

Choose the first agent based on the nature of the request.

## Use Discovery first when:

- the request is about choosing between technical options
- multiple implementation approaches are possible
- the right approach is unclear
- the decision may affect architecture or dependencies
- an existing decision in `docs/DECISIONS.md` may need to be revisited
- market research, competitive analysis, or reference gathering is needed
- the user wants to understand how others solve a similar problem

---

## Use Product first when:

- the request is a rough feature idea
- scope is unclear
- the feature must be turned into implementation-ready tasks
- acceptance criteria or non-goals are missing
- the task is not yet in `docs/TASKS.md`

---

## Use Designer when:

- the accepted Product specification includes a user-facing UI component
- visual design decisions need user input before implementation
- the user explicitly requests mockups or design review

Skip Designer when the feature is backend-only, API-only, has no visual component, or the UI change is trivial.

---

## Use Analytics Architect when:

- the feature changes user behavior
- the feature affects measurable outcomes
- the feature introduces new user interactions
- success metrics must be defined
- observability is required

Skip Analytics Architect only when the feature has no user-facing behavior, no measurable outcomes, and no pipeline observability requirements (for example: internal refactors, dependency upgrades, configuration changes), or when analytics definitions already exist for the feature.

---

## Use Architect when:

- implementation planning is needed
- the task may affect multiple modules
- the task may affect pipeline behavior
- Builder should not start yet

---

## Use Test Strategist when:

- the Architect plan has been accepted (quality loop complete)
- the task involves non-trivial testable logic
- the task introduces new modules, modifies behavior, or touches pipeline stages

Skip Test Strategist when the change is trivial (config, documentation, dependency bumps, single-line fixes) or has no testable logic.

---

## Use Builder when:

- an approved Architect plan exists
- Test Strategist has run (if applicable)
- a specific implementation step has been approved
- no further discovery or specification is required

---

## Use Analytics Validator when:

- Builder has completed implementation
- the feature went through Analytics Architect
- instrumentation must be verified before code review

---

## Use Security Reviewer when:

- Builder has completed implementation
- the change includes code (not purely documentation or non-code config)
- security validation is needed before general code review

Security Reviewer runs for all code changes. It is skipped only for non-code changes (documentation, configuration without secrets).

---

## Use Reviewer when:

- Builder completed implementation
- Security Reviewer has run (for code changes)
- Analytics Validator has run (if applicable)
- code must be validated

---

## Routing fallback rule

If the request is ambiguous:

- use Discovery if the uncertainty is technical or requires market research
- use Product if the uncertainty is about feature scope
- use Designer if the uncertainty is about visual design for an accepted spec
- use Architect if the task already exists

Never start with Builder unless an implementation step is approved.

Never skip Security Reviewer for code changes.

Never skip Reviewer for code changes.

---

# Development Workflow

Standard workflow for features with measurable outcomes:

Discovery → Product → [Designer] → Analytics Architect → Architect → [Test Strategist] → Builder → Analytics Validator → Security Reviewer → Reviewer

Standard workflow for internal technical changes (refactors, configuration, dependency upgrades):

Discovery → Architect → [Test Strategist] → Builder → Security Reviewer → Reviewer

Brackets indicate optional steps. Designer runs only for features with user-facing UI. Test Strategist runs only for tasks with non-trivial testable logic. Earlier stages (Discovery, Product) are optional depending on the request. Test Strategist is optional — invoked when the task has non-trivial testable logic. When Analytics Architect is used, Analytics Validator must run after Builder — unless Builder made no changes to analytics instrumentation, in which case Analytics Validator is skipped. Security Reviewer runs for all code changes; it is skipped only for non-code changes.

All code changes must go through **Security Reviewer** and **Reviewer**. Iteration Manager confirms workflow completion after Reviewer approval.

---

# Quality Iteration Workflow

The Iteration Manager decides when the Quality Iteration Workflow should be used:

- when a new feature spec is created
- when an implementation plan affects multiple modules
- when architectural risk is detected
- when artifact clarity is insufficient for implementation

Non-code artifacts may use a structured iteration loop:

Generator → Spec Reviewer → Gatekeeper → Reviser → Spec Reviewer (repeat)

Generator is typically the Product or Architect agent that created the artifact and remains responsible for its intent. The loop runs as follows: Generator produces the artifact; Spec Reviewer evaluates it; Gatekeeper decides accept, iterate, or escalate; if iterate, Reviser applies fixes and the artifact returns to Spec Reviewer.

This loop applies to:

- feature specifications
- task breakdowns
- implementation plans
- design notes
- decision notes

This loop **does NOT replace mandatory code review**.

Iteration loops must not be triggered again for the same artifact unless the artifact meaningfully changes.

---

# Iteration Rules

Maximum iterations: **3**

Do not restart the loop after Gatekeeper acceptance.

Stop earlier if:

- artifact quality threshold is reached
- no `must_fix` issues remain
- reviewer feedback becomes repetitive
- remaining feedback is stylistic only

Escalate to the user when:

- the task contradicts `docs/PRD.md` or `docs/ARCHITECTURE.md`
- the task conflicts with a decision in `docs/DECISIONS.md`
- implementation would change pipeline boundaries
- a new external dependency or provider is required
- a new infrastructure component is required
- repository context is insufficient to proceed safely

Do not make assumptions about these cases — escalate explicitly.

---

{% if analytics_by_default %}
# Analytics-by-Default Rule

If a feature affects:

- user actions
- feature adoption
- pipeline success
- output quality
- operational performance

Analytics Architect must define:

- events
- event properties
- product metrics
- operational metrics
- instrumentation locations

before Architect begins implementation planning. Analytics Validator must verify instrumentation before Reviewer approves the implementation.
{% endif %}

---

# Task Lifecycle

Tasks are tracked in:

`docs/TASKS.md`

Typical lifecycle: planned → in_progress → implemented → in_review → approved → completed

Tasks may also be set to `cancelled` by Iteration Manager with user confirmation when a task becomes obsolete, merged, or invalid. Tasks must not be deleted from `docs/TASKS.md`.

Status transitions:

- **planned → in_progress**: Builder begins implementation
- **in_progress → implemented**: Builder completes implementation
- **implemented → in_review**: Reviewer begins validation
- **in_review → approved**: Reviewer approves
- **approved → completed**: Iteration Manager confirms workflow closure or schedules follow-up tasks if Reviewer approved with minor changes

Only Iteration Manager may commit new tasks to `docs/TASKS.md` or transition task status. Product and Architect may propose tasks in their output; Reviewer may propose non-blocking follow-up tasks. Automated task creation rules are defined in `docs/TASK_BACKLOG_AUTOMATION.md`.

Significant decisions must be recorded in:

`docs/DECISIONS.md`

Architecture updates must be reflected in:

`docs/ARCHITECTURE.md`

---

# Precedence

`AGENTS.md` is the single source of truth for workflow rules (routing, agent roles, lifecycle, escalation, quality loops).

`.cursor/rules.md` is the single source of truth for coding rules (execution style, testing, error handling, safety, git).

`docs/ARCHITECTURE_GUARDRAILS.md` is the single source of truth for architectural constraints.

When these files govern different domains, all apply. When they conflict on the same matter, escalate to the user.

---

# Universal Agent Rules

These rules apply to every agent, including Iteration Manager:

- If something is unclear, make one explicit assumption, state it clearly, and proceed — do not ask multiple clarifying questions.
- Every agent output must end with a handoff block as specified in `docs/AGENT_HANDOFF_CONTRACT.md`.
- Agents must not invoke other agents directly. Control always returns to Iteration Manager.
- Builder review cycles (Builder → Reviewer → Builder fix) are limited to a maximum of **3 iterations**. If Reviewer does not approve after 3 cycles, escalate to the user.

---

# Repository Structure

```
CLAUDE.md                        # Entry point for Claude Code
AGENTS.md                        # Workflow rules (this file)
README.md                        # Project overview and setup guide
project.config.yaml              # Project configuration for template rendering
setup.py                         # Renders Jinja2 templates from config
sync.py                          # Syncs framework files to downstream projects
requirements.txt                 # Python dependencies for setup.py

agents/
  README.md                      # Agent directory overview
  discovery.md
  product.md
  designer.md
  analytics-architect.md
  architect.md
  test-strategist.md
  builder.md
  analytics-validator.md
  security-reviewer.md
  reviewer.md
  spec-reviewer.md
  reviser.md
  gatekeeper.md
  iteration-manager.md

docs/
  PRD.md                         # Product requirements document
  ARCHITECTURE.md                # Current system architecture
  ARCHITECTURE_GUARDRAILS.md     # Architectural constraints
  ARCHITECTURE_CHECKLIST.md      # Review checklist for non-trivial changes
  PIPELINE_CONTRACTS.md          # Stage-level input/output contracts
  TASKS.md                       # Task tracking with lifecycle statuses
  DECISIONS.md                   # Significant technical decisions
  FEATURES.md                    # Feature specifications (one per capability)
  FEATURE_MAP.md                 # Capability blocks and dependency map
  FEATURE_TEMPLATE.md            # Template for new feature specifications
  TASK_TEMPLATE.md               # Template for new tasks
  BRAND.md                       # Brand guide (optional, for UI tasks)
  AGENT_HANDOFF_CONTRACT.md      # Standard format for passing results between agents
  AGENT_EXECUTION_MODEL.md       # How Cursor and Claude Code execute the agent workflow
  TASK_BACKLOG_AUTOMATION.md     # Rules for automated task creation and backlog management
  ONBOARDING.md                  # Onboarding guide for new and existing projects
  features/                      # Individual feature spec files
  plans/                         # Implementation plan files
  reviews/                       # Review output files

.cursor/
  rules.md                       # Coding rules (execution, testing, safety, git)

examples/
  unfolda/                       # Reference project configuration
```

`docs/FEATURES.md` contains feature specifications, one per capability. Individual feature specs may also be stored in `docs/features/`. `docs/FEATURE_MAP.md` defines the capability blocks, their dependencies, and the canonical Capability Index used for `capability_id` references.

---

# Key Principles

- Prefer **small changes**
- Prefer **existing modules**
- Avoid **unnecessary dependencies**
- Keep **pipeline stages independent**
- Prefer **deterministic behavior**
- Prefer **measurable features**
- Record significant technical decisions
- Prefer small verifiable tasks

If uncertain:

→ choose the **simplest working solution**.