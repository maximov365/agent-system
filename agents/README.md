# {{ project.name }}

{{ project.description }}

---

## Processing pipeline

```
{{ pipeline.stages | map(attribute='name') | join(' → ') }}
```

---

## Development workflow

The active task owner follows `AGENTS.md`, using `lite`, `standard`, or `strict` evidence according to risk. Specialist files are selectively loaded methods, not mandatory separate calls. Codex can plan, build, inspect, review, and continue in one task. Delegation and structured legacy transitions are opt-in under the runtime's instructions.

For UI and graphics use `docs/VISUAL_QUALITY.md`; for games use `docs/GAME_DEVELOPMENT.md`. A self-review is identified as such. Native tools are used when available; MCP is optional.

---

## Key documents

| Document | Purpose |
|---|---|
| `CLAUDE.md` | Claude Code compatibility pointer to AGENTS.md |
| `AGENTS.md` | Agent roles, routing rules, and workflow definitions |
| `docs/CODING_RULES.md` | Portable coding policy |
| `docs/AGENT_EXECUTION_MODEL.md` | Portable execution and state model, including Codex |
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
| Iteration Manager | Accountable task owner; selects methods and integrates results |
| Discovery | Explores options via specialized modes (see `discovery-modes/`): technical, market, references, brand, marketing |
| Product | Turns ideas into feature specifications and task breakdowns |
| Designer | Creates UI mockups and iterates with user feedback (optional) |
| UX Writer | Writes and reviews all user-facing text; ensures consistent tone of voice (optional) |
| Marketing | Analyzes product, defines marketing strategy, creates campaigns and launch kits (on demand) |
| Illustrator | Generates images via native tools or optional MCP/provider APIs from visual briefs (tool-agent) |
| Video Producer | Generates video assets via MCP tools or provider APIs (Kling, Veo, etc.) from video briefs (tool-agent) |
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