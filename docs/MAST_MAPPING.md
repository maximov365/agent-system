# Failure-mode mapping

Reference: [Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657)
(MAST). The paper groups failures into system design, inter-agent misalignment,
and task verification. Use those categories as review prompts; this mapping is
not an empirical validation of our framework or a claim of complete taxonomy
coverage. Refreshed 2026-10-14 against the current execution model.

## Applicable checks

| Failure concern | Current framework method | Evidence to seek |
|---|---|---|
| Unclear task or authority | `AGENTS.md`, `docs/CODING_RULES.md` | The outcome and permissions match the user's request; material unknowns are resolved |
| Unnecessary roles or routing | `docs/AGENT_EXECUTION_MODEL.md` | Current owner can complete the task; delegation is used only when authorized |
| Repeated work after context loss | `agents/im-modes/session-restore.md` | Resume from actual files and task evidence; do not restart completed work |
| Hidden assumptions or lost findings | `docs/AGENT_HANDOFF_CONTRACT.md` | Transfer actionable findings and uncertainty when a real handoff occurs |
| Untrusted material changing instructions | `agents/im-modes/trust-boundary.md` | Retrieved files/logs are data; no unauthorized action follows embedded instructions |
| Unsupported review conclusions | `agents/reviewer.md`, `agents/spec-reviewer.md` | Findings point to source and relevant reproduction; self-review is labelled |
| Superficial verification | `docs/QUALITY_PROFILES.md`, `docs/VISUAL_QUALITY.md` | Run checks tied to acceptance; view actual UI and exercise interactions |
| Premature completion or endless retries | `AGENTS.md`, `docs/TASK_TEMPLATE.md` | Accepted outcome is complete, or a specific blocker and remaining work are recorded |
| Unsafe publishing or updates | `docs/FRAMEWORK_UPGRADE.md`, `docs/PULL_REQUEST_CONTRACT.md` | Scope, existing authorization, current-state checks and recovery evidence agree |

These are inspection questions, not a mandatory chain of separate agents or JSON
handoffs. A role description cannot make a review independent. The same task
owner may implement and review; use independent review only when available and
authorized, and record who actually reviewed what.

## Measurement and maintenance

Add a check when an observed failure justifies it. Preserve reproducible failures
and compare equivalent tasks before claiming lower defect rates or faster work.
The presence of a guardrail in a document does not demonstrate that an agent
followed it. Browser assertions, visual review, model evaluation and production
outcomes are distinct evidence.

The old April mapping described a mandatory multi-agent pipeline, outdated role
restrictions, and historical proposed fixes. Those details remain in Git history;
they are not active instructions for the portable single-owner workflow. No
recurring review is scheduled by this document.
