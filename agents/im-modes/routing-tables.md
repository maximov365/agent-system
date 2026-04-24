# Iteration Manager Mode: Routing Tables

This file contains the **initial routing tables** used by Iteration Manager when classifying new requests and selecting the starting agent.

**When to load this file:**
- Always for `initial_routing` (new request entering the system)
- Skip for `workflow_continuation` — use `agents/im-modes/standard-workflow.md` transitions instead

The two tables below are the source of truth for classification and starting-agent selection. The constitutional rules and fallback logic remain in `agents/iteration-manager.md`.

---

## Request classification

Classify every incoming request before selecting an agent.

| Request type | Description |
|---|---|
| `project_onboarding` | User requests to start or set up a new project; project docs are empty stubs |
| `technical_uncertainty` | Multiple implementation approaches possible; right choice is unclear |
| `feature_idea` | Rough feature request with unclear scope or missing acceptance criteria |
| `analytics_required_feature` | Feature with user behavior, measurable outcomes, or observability needs |
| `implementation_planning` | Task exists and is ready for Architect planning |
| `approved_plan_execution` | Architect plan exists and is approved; Builder or UI Builder can start |
| `design_review` | UI Builder completed; Design Reviewer must verify design compliance |
| `code_review` | Builder completed implementation; code must be validated |
| `analytics_validation` | Builder changed instrumentation; Analytics Validator must run |
| `copy_creation` | Feature has user-facing text; copy needs to be written or reviewed |
| `illustration_needed` | Visual briefs produced by Designer or Marketing; image generation required |
| `standalone_copy` | Release notes, emails, notifications, or other copy request |
| `marketing_strategy` | Marketing strategy, campaign creation, launch preparation, or marketing review |
| `non_code_artifact_improvement` | Feature spec, task breakdown, or plan needs quality review |
| `workflow_continuation` | Agent returned a result; next step must be determined |
| `system_audit` | User requests system audit, framework review, or health check |
| `ambiguous` | Request does not clearly match any category |

---

## Starting agent selection

| Condition | Start with |
|---|---|
| Project onboarding; user requests new project setup; project docs are empty stubs | `Discovery` (onboarding intake mode) |
| Technical uncertainty; multiple approaches; unclear architecture direction; market/competitive research needed | `Discovery` |
| User research needed; planning interviews, usability tests, or surveys | `Discovery` (user-research mode) |
| Existing research data needs synthesis into themes and recommendations | `Discovery` (research-synthesis mode) |
| Weekly or on-demand AI landscape review for framework evolution | `Discovery` (ai-landscape mode) |
| Feature idea; scope unclear; task not yet in `docs/TASKS.md` | `Product` |
| Accepted feature specification has user-facing UI and needs design review | `Designer` |
| Design approved; feature has 3+ screens / 5+ custom components / complex responsive or motion specs / user requested structured handoff | `Designer` (handoff-spec mode, before UI Builder) |
| Design approved; feature has motion, animation, or transitions | `Animator` |
| Designer or Marketing produced visual briefs needing image generation | `Illustrator` |
| Design/animation approved (or no Designer); feature has user-facing text | `UX Writer` |
| Standalone copy request (release notes, emails, notifications) | `UX Writer` |
| Marketing strategy, campaign creation, launch preparation | `Marketing` |
| Marketing review of existing copy | `Marketing` (review mode) |
| Accepted feature specification with measurable outcomes and no analytics spec exists (`product_spec_accepted: true`) | `Analytics Architect` |
| Task exists and is ready for planning; analytics spec exists or is not required | `Architect` |
| Approved Architect plan exists; task has non-trivial testable logic | `Test Strategist` |
| Approved Architect plan exists; trivial change or no testable logic; task has user-facing UI | `UI Builder` |
| Approved Architect plan exists; trivial change or no testable logic; no user-facing UI | `Builder` |
| UI Builder completed implementation | `Design Reviewer` |
| Design Reviewer approved; feature has user-facing strings | `UX Writer` (copy review) |
| Design Reviewer approved; no user-facing strings; instrumentation changed | `Analytics Validator` |
| Design Reviewer approved; no user-facing strings; no instrumentation changes | `Security Reviewer` |
| Design Reviewer returned `CHANGES REQUIRED` | `UI Builder` (design fixes) |
| Builder completed implementation; feature has user-facing strings | `UX Writer` (copy review) |
| Builder completed implementation; no user-facing strings; Analytics Architect was not used | `Security Reviewer` |
| Builder completed implementation; no user-facing strings; Analytics Architect was used and instrumentation was changed | `Analytics Validator` |
| Builder completed implementation; no user-facing strings; Analytics Architect was used but no instrumentation changes | `Security Reviewer` |
| Non-code artifact needs quality review | `Spec Reviewer` (via quality loop) |
| System audit, framework review, health check | `System Auditor` |

After selecting the starting agent, return to `agents/iteration-manager.md` for fallback logic, constitutional rules, escalation logic, and output format.
