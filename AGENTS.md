# AI Agent Workflow

This repository uses a structured multi-agent workflow for AI-assisted development.

The goal is to enable **predictable, safe, and increasingly autonomous product development** while preserving architectural discipline.

The system supports both:

1. **Deterministic implementation workflow**
2. **Quality loops for specifications and plans**

All production code implementation must follow the:

Architect → [Test Strategist] → Builder → [Analytics Validator] → Security Reviewer → Reviewer

cycle. Test Strategist is optional — Iteration Manager invokes it when the task has non-trivial testable logic. Analytics Validator is conditional on Analytics Architect having been used.

Earlier steps (Discovery, Product, Designer, Analytics Architect) are used to clarify scope, product design, visual direction, and measurement before implementation. When Analytics Architect is used, Analytics Validator verifies instrumentation after Builder and before Security Reviewer.

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

| Agent | Role file | Core responsibility | Does NOT |
|---|---|---|---|
| **Discovery** | `agents/discovery.md` | Explore technical options and market references; recommend the simplest viable direction | Write production code |
| **Product** | `agents/product.md` | Turn ideas into feature specs, task breakdowns, and acceptance criteria | Write production code |
| **Designer** | `agents/designer.md` | Create UI mockups and visual prototypes; iterate with user feedback | Write code; define product scope |
| **Analytics Architect** | `agents/analytics-architect.md` | Define analytics events, metrics, and instrumentation locations | Change product scope; implement code |
| **Architect** | `agents/architect.md` | Propose minimal implementation plans; define files, risks, and acceptance criteria | Write production code |
| **Test Strategist** | `agents/test-strategist.md` | Define test strategy (levels, edge cases, failure modes) for approved plans | Write code; modify the implementation plan |
| **Builder** | `agents/builder.md` | Implement the approved Architect plan with minimal file changes | Expand scope beyond the approved plan |
| **Security Reviewer** | `agents/security-reviewer.md` | Check for vulnerabilities, input validation, secrets handling, data exposure | Implement fixes; review architecture or scope |
| **Analytics Validator** | `agents/analytics-validator.md` | Verify analytics instrumentation matches the Analytics Specification | Modify implementation logic |
| **Reviewer** | `agents/reviewer.md` | Verify implementation follows the plan; approve or request changes | Implement new features |
| **Iteration Manager** | `agents/iteration-manager.md` | Route requests, manage transitions, control quality loops, enforce limits | Produce workflow artifacts (except append-only org memory) |
| **Spec Reviewer** | `agents/spec-reviewer.md` | Evaluate non-code artifact quality using a scoring rubric | Write code; rewrite artifacts |
| **Reviser** | `agents/reviser.md` | Apply `must_fix` changes from Spec Reviewer; preserve scope and intent | Produce original artifacts; change scope |
| **Gatekeeper** | `agents/gatekeeper.md` | Decide accept / iterate / escalate for quality loops | Rewrite artifacts; make architectural decisions |
| **System Auditor** | `agents/system-auditor.md` | Audit framework health across downstream projects; propose improvements | Implement changes; modify downstream files |

**Sequencing notes:**

- **Designer** is optional — runs after Product spec is accepted and before Analytics Architect or Architect, only when the feature has user-facing UI.
- **Analytics Architect** must run before Architect when required. Architect must include instrumentation in the plan. Architect must not remove or weaken defined analytics events.
- **Test Strategist** is optional — runs after Architect plan is accepted and before Builder, only for non-trivial testable logic.
- **Security Reviewer** runs after Builder (or after Analytics Validator) and before Reviewer for all code changes.
- **Analytics Validator** runs after Builder and before Security Reviewer when instrumentation was changed.
- **Reviewer** is the final mandatory step for all code changes.
- **Iteration Manager** also appends structured entries to `docs/LESSONS_LEARNED.md` and `docs/KNOWN_PATTERNS.md` after completed workflows.

---

# Agent Routing Rules

All requests are first interpreted by Iteration Manager, which determines the appropriate starting agent. Full routing logic and transition tables are in `agents/iteration-manager.md`.

| Request type | Start with | Skip when |
|---|---|---|
| Technical uncertainty, market research | Discovery | — |
| Rough feature idea, unclear scope | Product | — |
| Accepted spec with user-facing UI | Designer | Backend-only, API-only, trivial UI |
| Feature with measurable outcomes | Analytics Architect | No user-facing behavior, no observability; analytics already exist |
| Implementation planning needed | Architect | — |
| Accepted Architect plan, non-trivial testable logic | Test Strategist | Trivial change, no testable logic |
| Approved plan, ready for implementation | Builder | No approved plan exists |
| Builder completed, instrumentation changed | Analytics Validator | Analytics Architect was not used |
| Builder completed, code changes | Security Reviewer | Non-code changes only |
| Security Reviewer passed, code must be validated | Reviewer | — |
| New project setup, empty project docs | Onboarding (Discovery intake) | — |
| System audit, framework review, health check | System Auditor | — |

**Hard rules:**
- Never start with Builder unless an approved Architect plan exists.
- Never skip Security Reviewer for code changes.
- Never skip Reviewer for code changes.

**Fallback:** Technical uncertainty → Discovery; scope uncertainty → Product; design uncertainty → Designer; task already exists → Architect.

---

# Development Workflow

Standard workflow for features with measurable outcomes:

Discovery → Product → [Designer] → Analytics Architect → Architect → [Test Strategist] → Builder → Analytics Validator → Security Reviewer → Reviewer

Standard workflow for internal technical changes (refactors, configuration, dependency upgrades):

Discovery → Architect → [Test Strategist] → Builder → Security Reviewer → Reviewer

Brackets indicate optional steps. Designer runs only for features with user-facing UI. Test Strategist runs only for tasks with non-trivial testable logic. Earlier stages (Discovery, Product) are optional depending on the request. Test Strategist is optional — invoked when the task has non-trivial testable logic. When Analytics Architect is used, Analytics Validator must run after Builder — unless Builder made no changes to analytics instrumentation, in which case Analytics Validator is skipped. Security Reviewer runs for all code changes; it is skipped only for non-code changes.

All code changes must go through **Security Reviewer** and **Reviewer**. Iteration Manager confirms workflow completion after Reviewer approval.

---

# Onboarding Workflow

Guided conversational onboarding creates a new project. Agents ask structured questions and produce project documents iteratively. Detailed transitions are in `agents/iteration-manager.md` — Onboarding workflow transitions.

**Phases:**

| Phase | Agent | Produces | Quality loop | Artifact type |
|---|---|---|---|---|
| 1 | Discovery | Discovery brief | No | `design_note` |
| 2 | Product | `docs/PRD.md` | Yes | `feature_spec` |
| 3 | Designer | `docs/BRAND.md` | Yes | `design` |
| 4 | Architect | `docs/ARCHITECTURE.md`, `docs/PIPELINE_CONTRACTS.md`, `docs/FEATURE_MAP.md` | Yes | `implementation_plan` |
| 5 | Iteration Manager | `project.config.yaml`, stub docs | No | `none` |

**Skip rules:** Skip Phase 1 if the user provides comprehensive upfront context. Skip Phase 3 if no user-facing UI. Phases 2 and 4 are always required.

**Phase rules:** Each phase starts with structured intake questions → user answers → agent produces draft → quality loop (max 3 iterations) → Gatekeeper acceptance → next phase. Each agent reads approved outputs of all previous phases as context.

**Intake conversation rules:** During onboarding, agents do **not** read project docs as inputs (these are being created). They **do** read `project.config.yaml` for pre-filled context and outputs of previous onboarding phases.

**Assembly (Phase 5):** Iteration Manager generates `project.config.yaml`, runs `python setup.py`, creates stub docs, commits, and presents the closing summary.

**Workflow state:** `onboarding_phase` field in `workflow_state` tracks progress (1–5). See `agents/iteration-manager.md` for state initialisation and transition details.

---

# Quality Iteration Workflow

The Iteration Manager decides when the Quality Iteration Workflow should be used:

- when a new feature spec is created
- when an implementation plan affects multiple modules
- when architectural risk is detected
- when artifact clarity is insufficient for implementation

Non-code artifacts may use a structured quality loop:

Generator → Spec Reviewer → Gatekeeper → Reviser → Spec Reviewer (repeat)

Generator is typically the Product or Architect agent that created the artifact and remains responsible for its intent. The loop runs as follows: Generator produces the artifact; Spec Reviewer evaluates it; Gatekeeper decides accept, iterate, or escalate; if iterate, Reviser applies fixes and the artifact returns to Spec Reviewer.

This loop applies to:

- feature specifications
- task breakdowns
- implementation plans
- design notes
- decision notes
- analytics specifications
- onboarding documents (PRD, Architecture, Brand — during the Onboarding Workflow)

This loop **does NOT replace mandatory code review**.

Quality loops must not be triggered again for the same artifact unless the artifact meaningfully changes.

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

`docs/LESSONS_LEARNED.md` and `docs/KNOWN_PATTERNS.md` capture organizational experience; they must not override PRD, architecture, guardrails, or `docs/DECISIONS.md`.

When these files govern different domains, all apply. When they conflict on the same matter, escalate to the user.

---

# Universal Agent Rules

These rules apply to every agent, including Iteration Manager:

- Before starting work, read `docs/LESSONS_LEARNED.md` and `docs/KNOWN_PATTERNS.md` (after `AGENTS.md` and alongside other mandatory reads in `CLAUDE.md`). Apply lessons and patterns; do not repeat documented mistakes without addressing why this time is different.
- Organizational memory does **not** override `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/ARCHITECTURE_GUARDRAILS.md`, or `docs/DECISIONS.md`. If a lesson conflicts with those sources, escalate.
- If something is unclear, make one explicit assumption, state it clearly, and proceed — do not ask multiple clarifying questions.
- Every agent output must end with a handoff block as specified in `docs/AGENT_HANDOFF_CONTRACT.md`.
- Agents must not invoke other agents directly. Control always returns to Iteration Manager.
- Builder review cycles (Builder → [Analytics Validator] → Security Reviewer → Reviewer → Builder fix) are limited to a maximum of **3 iterations**. If Reviewer does not approve after 3 cycles, escalate to the user.

---

# Repository Structure

See `README.md` for the full project structure. Key locations:

- `agents/*.md` — agent role definitions
- `docs/` — project documentation, templates, and workflow contracts
- `.cursor/rules.md` — coding rules
- `project.config.yaml` — project configuration for template rendering

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