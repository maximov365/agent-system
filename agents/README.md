# {{ project.name }}

{{ project.description }}

---

## Processing pipeline

```
{{ pipeline.stages | map(attribute='name') | join(' → ') }}
```

---

## Development workflow

This repository uses a structured multi-agent workflow for AI-assisted development. All work follows a spec-first approach: no code is written without an Architect plan, and no plan is written without a clear feature specification.

**Full workflow for features with measurable outcomes:**

Discovery → Product → [Designer] → Analytics Architect → Architect → [Test Strategist] → Builder → Analytics Validator → Security Reviewer → Reviewer

**Lightweight workflow for internal technical changes:**

Discovery → Architect → [Test Strategist] → Builder → Security Reviewer → Reviewer

Brackets indicate optional steps.

Non-code artifacts (feature specs, implementation plans) go through a quality loop before implementation begins:

Generator → Spec Reviewer → Gatekeeper → Reviser → Spec Reviewer (repeat until accepted)

All requests are interpreted by the **Iteration Manager**, which selects the correct starting agent and manages workflow transitions.

---

## Key documents

| Document | Purpose |
|---|---|
| `CLAUDE.md` | Entry contract for Claude Code — default role, routing, and core constraints |
| `AGENTS.md` | Agent roles, routing rules, and workflow definitions |
| `.cursor/rules.md` | Execution policy for Cursor |
| `docs/AGENT_EXECUTION_MODEL.md` | How Cursor and Claude Code execute the agent workflow |
| `docs/AGENT_HANDOFF_CONTRACT.md` | Standard format for passing results between agents |
| `docs/TASK_BACKLOG_AUTOMATION.md` | Rules for automated task creation and backlog management |
| `docs/PRD.md` | Product requirements |
| `docs/ARCHITECTURE.md` | System architecture |
| `docs/ARCHITECTURE_GUARDRAILS.md` | Architectural constraints that must not be violated |
| `docs/ARCHITECTURE_CHECKLIST.md` | Checklist for reviewing non-trivial changes |
| `docs/PIPELINE_CONTRACTS.md` | Stage-level input/output contracts |
| `docs/DECISIONS.md` | Significant technical decisions |
| `docs/LESSONS_LEARNED.md` | Workflow lessons and repeated review themes (read before work; IM appends) |
| `docs/KNOWN_PATTERNS.md` | Validated approaches in practice (read before work; IM appends) |
| `docs/TASKS.md` | Task tracking |
| `docs/FEATURE_MAP.md` | Capability blocks, dependency map, and capability index |

---

## Agent roles

| Agent | Role |
|---|---|
| Iteration Manager | Workflow orchestrator — routes requests, manages transitions via modes (see `im-modes/`) |
| Discovery | Explores options via specialized modes (see `discovery-modes/`): technical, market, references, brand, marketing |
| Product | Turns ideas into feature specifications and task breakdowns |
| Designer | Creates UI mockups and iterates with user feedback (optional) |
| Analytics Architect | Defines analytics events, metrics, and instrumentation requirements |
| Architect | Plans implementation before coding begins |
| Test Strategist | Defines test strategy before implementation (optional) |
| Builder | Implements approved plans |
| Analytics Validator | Verifies analytics instrumentation against the Analytics Specification |
| Security Reviewer | Validates code for security vulnerabilities and unsafe patterns |
| Reviewer | Reviews code implementation for correctness and architecture compliance |
| Spec Reviewer | Evaluates non-code artifact quality |
| Reviser | Applies fixes to non-code artifacts based on Spec Reviewer feedback |
| Gatekeeper | Decides whether a non-code artifact should be accepted, iterated, or escalated |
| System Auditor | Audits framework health across downstream projects; proposes improvements (never implements) |

---

## Language

- Repository artifacts (code, documentation, prompts, comments): **English**
- Conversational responses in chat: follow the user's language