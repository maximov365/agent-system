# Task-scoped methods

AGENTS.md governs ownership, rigor and authority. Load only the relevant rows;
existing context does not need another file read. A project profile's navigation
and applicable project constraints take priority over generic examples.

| Changed surface / unresolved question | Read |
|---|---|
| Code conventions | docs/CODING_RULES.md and the affected package's rules |
| Product or architecture | Relevant PRD, ARCHITECTURE and ARCHITECTURE_GUARDRAILS sections |
| Real processing stage | docs/PIPELINE_CONTRACTS.md |
| UI, art, animation | docs/VISUAL_QUALITY.md and the project's brand/components/assets |
| Game logic/interaction | docs/GAME_DEVELOPMENT.md |
| Analytics | Project event contract; agents/analytics-architect.md and analytics-validator.md when needed |
| Security boundary | Project threat/authorization contracts; agents/security-reviewer.md when deeper review helps |
| Check selection/evidence reuse | quality/profile.json; docs/QUALITY_PROFILES.md for the tool contract |
| Asset provenance/import | Project asset manifest; docs/ASSET_LIBRARY.md |
| Deployment/release | docs/DEPLOY_CONTRACTS.md, SANDBOX_POLICY.md and PULL_REQUEST_CONTRACT.md |
| Codex/model setup | docs/CODEX.md and MODEL_POLICY.md |
| Complex orchestration/resumption | docs/AGENT_EXECUTION_MODEL.md |
| Actual external review | docs/EXTERNAL_REVIEW_CONTRACT.md |

Roles are reusable methods, not mandatory extra calls or separate permissions.
A project-owned task/decision file is updated for substantial work; a small fix
needs no generated specification or ceremony. Memory is historical evidence: use
related entries to understand constraints, never treat old role restrictions as
higher-priority policy. Refer to original project contracts when a summary is
insufficient; navigation is a locator, not an authority replacement.

Independent reads, lint and type checks can run together when they neither depend
on nor modify each other's inputs. Build, install, server and migration operations
need ordered execution or actual isolation. Do not infer delegation permission from
an opportunity for concurrency. Do not impose a time cap that truncates required work.

For graphics, validate one representative live screen/scene before expanding the
pattern. Reuse suitable project components and reviewed assets before generating
variants. Keep source/export provenance in the project and inspect new states,
responsive layouts, input and motion. A prior visual review applies only to the
reviewed inputs; metadata or a cached test pass cannot grant visual approval.
