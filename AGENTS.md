# AI Agent Workflow

This repository uses a structured multi-agent workflow for AI-assisted development.

The goal is to enable **predictable, safe, and increasingly autonomous product development** while preserving architectural discipline.

The system supports both:

1. **Deterministic implementation workflow**
2. **Quality-improvement loops for specifications and plans**

All production code implementation must follow the:

Architect → Builder → Reviewer

cycle.

Earlier steps (Discovery, Product, Analytics Architect) are used to clarify scope, product design, and measurement before implementation.

---

# Project

**Unfolda**

Unfolda is a **web-based SaaS service** that transforms EPUB books into structured formats for reading and understanding in a foreign language.

Users upload a book, select a mode and target language, and receive a processed EPUB — either a high-quality context-aware translation, or a guided reading version with translations and explanations built into the text.

The system processes each book through a pipeline: ingestion → segmentation → translation → formatting → export

The project prioritizes:

- deterministic pipelines
- clear architecture boundaries
- minimal dependencies
- predictable AI behavior
- async background processing
- measurable product outcomes

---

# Agent Roles

The repository defines several agent roles.

## Discovery

Defined in: `agents/discovery.md`

Responsibilities:

- Explore technical options
- Compare realistic approaches
- Identify trade-offs and risks
- Recommend the simplest viable direction
- Suggest whether the decision should be recorded in `docs/DECISIONS.md`

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

## Builder

Defined in: `agents/builder.md`

Responsibilities:

- Implement the approved Architect plan
- Modify the smallest possible number of files
- Keep changes simple and reviewable
- Respect pipeline boundaries
- Run verification steps during implementation
- Prefer changes affecting fewer than 5 files unless the Architect plan explicitly requires more

Builder **does not expand scope beyond the approved plan**.

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

Analytics Validator runs **after Builder and before Reviewer** when the feature required Analytics Architect instrumentation.

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

Coordinates the workflow.

Responsibilities:

- Determine the correct starting agent
- Decide whether a quality iteration loop is required
- Enforce iteration limits
- Move artifacts to the next workflow stage
- Decide when user input is required
- Escalate to the user when necessary

Iteration Manager **does not produce artifacts itself**.

---

## Spec Reviewer

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

Used within the quality iteration loop to improve non-code artifacts based on Spec Reviewer feedback.

Responsibilities:

- Apply all `must_fix` changes identified by Spec Reviewer
- Preserve intent and scope of the original artifact
- Avoid introducing new scope or architectural decisions
- Produce a revised artifact ready for Gatekeeper evaluation

Reviser **does not produce original artifacts** and **does not change product scope**.

---

## Gatekeeper

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

---

## Use Product first when:

- the request is a rough feature idea
- scope is unclear
- the feature must be turned into implementation-ready tasks
- acceptance criteria or non-goals are missing
- the task is not yet in `docs/TASKS.md`

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

## Use Builder when:

- an approved Architect plan exists
- a specific implementation step has been approved
- no further discovery or specification is required

---

## Use Analytics Validator when:

- Builder has completed implementation
- the feature went through Analytics Architect
- instrumentation must be verified before code review

---

## Use Reviewer when:

- Builder completed implementation
- Analytics Validator has run (if applicable)
- code must be validated

---

## Routing fallback rule

If the request is ambiguous:

- use Discovery if the uncertainty is technical
- use Product if the uncertainty is about feature scope
- use Architect if the task already exists

Never start with Builder unless an implementation step is approved.

Never skip Reviewer for code changes.

---

# Development Workflow

Standard workflow for features with measurable outcomes:

Discovery → Product → Analytics Architect → Architect → Builder → Analytics Validator → Reviewer

Standard workflow for features without measurable outcomes (internal refactors, configuration changes):

Discovery → Product → Architect → Builder → Reviewer

Earlier stages (Discovery, Product) are optional depending on the request. Analytics Architect and Analytics Validator are **required together** — if one is used, the other must also be used. Analytics Validator runs only when the Builder changed or introduced analytics instrumentation.

All code changes must go through the **Reviewer** step. Iteration Manager confirms workflow completion after Reviewer approval.

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

- artifact conflicts with `docs/DECISIONS.md`
- architecture or pipeline boundaries may change
- a new dependency is required
- repository context is insufficient

---

# Analytics-by-Default Rule

If a feature affects:

- user actions
- feature adoption
- pipeline success
- translation accuracy
- output quality
- operational performance

Analytics Architect must define:

- events
- event properties
- product metrics
- operational metrics
- instrumentation locations

before Architect begins implementation planning. Analytics Validator must verify instrumentation before Reviewer approves the implementation.

---

# Task Lifecycle

Tasks are tracked in:

`docs/TASKS.md`

Typical lifecycle: planned → in progress → implemented → in review → approved → completed

Tasks may also be set to `cancelled` by Iteration Manager with user confirmation when a task becomes obsolete, merged, or invalid. Tasks must not be deleted from `docs/TASKS.md`.

Status transitions:

- **planned → in progress**: Builder begins implementation
- **in progress → implemented**: Builder completes implementation
- **implemented → in review**: Reviewer begins validation
- **in review → approved**: Reviewer approves
- **approved → completed**: Iteration Manager confirms workflow closure or schedules follow-up tasks if Reviewer approved with minor changes

Only Iteration Manager may commit new tasks to `docs/TASKS.md` or transition task status. Product and Architect may propose tasks in their output; Reviewer may propose non-blocking follow-up tasks. Automated task creation rules are defined in `docs/TASK_BACKLOG_AUTOMATION.md`.

Significant decisions must be recorded in:

`docs/DECISIONS.md`

Architecture updates must be reflected in:

`docs/ARCHITECTURE.md`

---

# Repository Structure

```
agents/
  discovery.md
  product.md
  analytics-architect.md
  architect.md
  builder.md
  analytics-validator.md
  reviewer.md
  spec-reviewer.md
  reviser.md
  gatekeeper.md
  iteration-manager.md

docs/
  PRD.md                    # Product requirements document
  ARCHITECTURE.md           # Current system architecture
  ARCHITECTURE_GUARDRAILS.md
  ARCHITECTURE_CHECKLIST.md
  PIPELINE_CONTRACTS.md
  TASKS.md                  # Task tracking with lifecycle statuses
  DECISIONS.md              # Significant technical decisions
  FEATURES.md               # Feature specifications (one per capability)
  FEATURE_MAP.md            # Capability blocks, dependency map, and capability index
  FEATURE_TEMPLATE.md       # Template for new feature specifications
  TASK_TEMPLATE.md          # Template for new tasks
  AGENT_HANDOFF_CONTRACT.md # Standard format for passing results between agents
  AGENT_EXECUTION_MODEL.md  # How Cursor and Claude Code execute the agent workflow
  TASK_BACKLOG_AUTOMATION.md # Rules for automated task creation and backlog management

.cursor/
  rules.md

CLAUDE.md
AGENTS.md
```

`FEATURES.md` contains feature specifications, one per capability. `FEATURE_MAP.md` defines the capability blocks, their dependencies, and the canonical Capability Index used for `capability_id` references. `FEATURE_TEMPLATE.md` is the template used by Product when creating new feature specifications.

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