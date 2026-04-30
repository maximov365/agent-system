# Decisions

<!-- Record significant technical decisions here. -->
<!-- Each decision should include: context, options considered, decision, and rationale. -->

| ID | Title | Status | Date |
|----|-------|--------|------|
| DEC-001 | Guided conversational onboarding for new projects | accepted | 2026-03-29 |
| DEC-002 | Single-source principle for workflow rules | accepted | 2026-03-29 |
| DEC-003 | Remove FEATURES.md and FEATURE_TEMPLATE.md from framework | accepted | 2026-03-29 |
| DEC-004 | Push-based auto-sync for downstream projects | accepted | 2026-03-29 |
| DEC-005 | System Auditor agent for framework self-improvement | accepted | 2026-03-29 |
| DEC-006 | Agent modes pattern for scalable Discovery roles | accepted | 2026-03-29 |
| DEC-013 | Agent-system hardening contracts | accepted | 2026-04-30 |
| DEC-014 | Backward-compatible model gateway rollout | accepted | 2026-04-30 |
| DEC-015 | Media tool-agents for image and video generation | accepted | 2026-04-30 |

---

## DEC-001 — Guided conversational onboarding for new projects

**Status:** accepted
**Date:** 2026-03-29

### Context

New project setup required users to manually write `project.config.yaml`, `docs/PRD.md`, `docs/ARCHITECTURE.md`, and other project-specific documents before agents could function. This created a high barrier to entry and meant the most critical documents were written without agent assistance.

### Options Considered

1. **Manual setup only** — user writes all docs by hand (status quo)
2. **Guided conversational onboarding** — agents ask structured questions and produce documents iteratively through quality loops
3. **Template wizard** — a CLI script that asks questions and generates files from templates

### Decision

Option 2 — Guided conversational onboarding.

### Rationale

- Leverages existing agents (Discovery, Product, Designer, Architect) and quality loops
- Documents benefit from the same iterative refinement as feature specs
- No new tooling required — works within the existing Cursor/Claude Code execution model
- Reduces barrier to entry dramatically: user only needs to answer questions
- Template wizard (option 3) would produce lower-quality one-shot output without the benefit of quality iteration

### Implications

- New `onboarding_phase` field added to `workflow_state`
- Each participating agent has an "onboarding intake mode" with structured questions
- `AGENTS.md` has a new Onboarding Workflow section
- `docs/ONBOARDING.md` updated with guided flow as the recommended approach
- Manual setup preserved as Scenario B for teams that prefer it

---

## DEC-002 — Single-source principle for workflow rules

**Status:** accepted
**Date:** 2026-03-29

### Context

Consistency audit revealed ~8,000 tokens of duplicated content across framework files. Agent Roles were described verbosely in `AGENTS.md` (~190 lines) and repeated in each agent file. Routing rules were duplicated between `AGENTS.md` and `agents/iteration-manager.md`. Coding rules in `agents/builder.md` duplicated `.cursor/rules.md`. Per-agent handoff examples in `AGENT_HANDOFF_CONTRACT.md` (~230 lines) repeated the same JSON structure 14 times.

### Options Considered

1. **Keep duplication for self-contained reading** — each file remains standalone but context window pressure grows
2. **Single-source with cross-references** — detailed definitions live in one place; other files reference them

### Decision

Option 2 — Single-source with cross-references.

### Rationale

- Reduces base prompt token count by ~45% for the four most-loaded files
- Eliminates inconsistency risk when rules change (update one place, not five)
- Agent role files remain authoritative for their own behavior; `AGENTS.md` provides the index
- `.cursor/rules.md` remains authoritative for coding rules; `agents/builder.md` references it

### Implications

- `AGENTS.md` Agent Roles section compressed from ~190 lines to a table + sequencing notes
- `AGENTS.md` Routing Rules section compressed from ~130 lines to a table + hard rules
- `AGENTS.md` Repository Structure replaced with a reference to `README.md`
- `AGENT_HANDOFF_CONTRACT.md` per-agent examples compressed from ~230 lines to a table + notes
- `AGENT_EXECUTION_MODEL.md` quality loop and analytics loop sections replaced with references
- `agents/builder.md` coding rules section replaced with a reference to `.cursor/rules.md`

---

## DEC-003 — Remove FEATURES.md and FEATURE_TEMPLATE.md from framework

**Status:** accepted
**Date:** 2026-03-29

### Context

Audit of the Voxema project (36 completed tasks, detailed PRD and FEATURE_MAP) revealed `docs/FEATURES.md` was never populated. Investigation showed no agent was wired to write to it: `agents/product.md` did not mention it, `agents/iteration-manager.md` did not route to it, `CLAUDE.md` did not include it in mandatory reads. An escalation rule in `docs/TASK_BACKLOG_AUTOMATION.md` referencing it was dead code.

### Options Considered

1. **Remove both files** — accept that PRD + FEATURE_MAP + TASKS covers the need
2. **Wire them up** — add explicit write instructions to Product agent and IM routing

### Decision

Option 1 — Remove both files from the framework.

### Rationale

- Three existing documents (PRD.md, FEATURE_MAP.md, TASKS.md) already cover feature definition, capability tracking, and task tracking
- Adding a middle layer increases maintenance overhead without clear benefit at current project scale
- The dead escalation rule was silently broken — removing the file makes the gap explicit rather than hidden
- FEATURE_TEMPLATE.md format guidance was inlined into `agents/product.md`

### Implications

- `docs/FEATURES.md` and `docs/FEATURE_TEMPLATE.md` deleted from framework, Voxema, and unfolda example
- Escalation rule in TASK_BACKLOG_AUTOMATION.md now references `docs/FEATURE_MAP.md` instead
- If a future project needs per-feature spec files, the concept can be reintroduced as an optional extension

---

## DEC-004 — Push-based auto-sync for downstream projects

**Status:** accepted
**Date:** 2026-03-29

### Context

Framework changes in agent-system required manual `sync.py --target` + `setup.py` runs for each downstream project. This was error-prone: the LESSONS_LEARNED.md entry for TASK-003 explicitly flagged "Run sync.py to propagate framework changes to Voxema" as a follow-up, but there was no mechanism to ensure it happened.

### Options Considered

1. **Git submodules** — downstream includes agent-system as a submodule; updated via `git pull --recurse-submodules`
2. **Pull-based (session check)** — downstream CLAUDE.md checks `.agent-system-version` at session start and runs sync if outdated
3. **Push-based (post-commit hook)** — agent-system auto-syncs all registered downstream projects when framework files are committed
4. **CI-based** — GitHub Actions creates PRs in downstream repos on push to main

### Decision

Option 3 — Push-based auto-sync via post-commit hook, with `downstream.projects` registry.

### Rationale

- Zero manual steps: framework commit → downstream updated automatically
- No git submodule complexity (notoriously error-prone for solo/small teams)
- No CI infrastructure required — works entirely locally
- `find_python` fallback chain ensures rendering works regardless of which python invokes the hook
- Registry file is `.gitignore`d (machine-specific paths), so no conflicts between developers
- `--all --dry-run` available for safe preview before committing

### Implications

- New `downstream.projects` file (gitignored) lists downstream project paths
- `sync.py` extended with `--all` and `--render` flags
- New `hooks/post-commit` auto-runs `sync.py --all --render` when framework files change
- `hooks/install.py` updated to install both pre-commit and post-commit hooks
- Developers must run `python hooks/install.py` once after cloning to activate the post-commit hook

---

## DEC-005 — System Auditor agent for framework self-improvement

**Status:** accepted
**Date:** 2026-03-29

### Context

Framework improvements (consistency audits, prompt optimization, dead reference detection) were performed manually by the user requesting an ad-hoc review. There was no systematic mechanism to monitor framework health across downstream projects or detect systemic issues from cross-project patterns.

### Options Considered

1. **Manual audits only** — user triggers reviews periodically (status quo)
2. **Automated checks only** — a script runs checks but has no interpretive layer
3. **System Auditor agent + audit.py** — agent interprets automated findings, analyzes cross-project patterns, and proposes improvements; never implements without user approval

### Decision

Option 3 — System Auditor agent backed by `audit.py` automated checks.

### Rationale

- Automated checks (`audit.py`) catch mechanical issues (version drift, dead references, prompt size) reliably
- The agent layer adds interpretive analysis (cross-project pattern recognition, root cause analysis, prioritized recommendations)
- Read-only constraint (never implements) keeps the user in control while reducing cognitive load for identifying what needs attention
- Fits naturally into existing Iteration Manager routing — `system_audit` request type

### Implications

- New `agents/system-auditor.md` agent definition (synced to downstream like other agents)
- New `audit.py` script in agent-system root (not synced — framework-level tool)
- Iteration Manager routes `system_audit` requests to System Auditor
- System Auditor output goes to user for approval; approved proposals routed to appropriate agents
- Agent produces `design_note` artifact type with structured findings JSON

---

## DEC-006 — Agent modes pattern for scalable Discovery roles

**Status:** accepted
**Date:** 2026-03-29

### Context

The user wanted to add more specialized Discovery roles (visual references, branding, marketing) but `AGENTS.md` and `agents/iteration-manager.md` were already near token limits (~3800 and ~5600 tokens respectively). Embedding full instructions for each new Discovery sub-role in `discovery.md` would have inflated the file and every request would load all sub-role context even when only one was needed.

### Options Considered

1. **Separate top-level agents** — create `agents/brand-discovery.md`, `agents/marketing-discovery.md`, etc. as independent agents with full IM routing
2. **Embed in discovery.md** — add all sub-role instructions to the existing monolithic file
3. **Agent modes pattern** — Discovery becomes a lightweight dispatcher; each mode is a separate file in `agents/discovery-modes/`; only the relevant mode file is loaded per request

### Decision

Option 3 — Agent modes pattern.

### Rationale

- Keeps `AGENTS.md` routing table unchanged (one entry for Discovery)
- Keeps `iteration-manager.md` routing unchanged (Discovery remains a single target)
- Each mode file is only loaded when needed, reducing context window pressure
- Adding a new mode requires only: (1) create a file in `agents/discovery-modes/`, (2) add a row to the dispatcher table in `discovery.md`
- Pattern is reusable for other agents if they need sub-specializations in the future

### Implications

- `agents/discovery.md` refactored from 316 lines (all-in-one) to ~130 lines (dispatcher)
- New directory `agents/discovery-modes/` with 5 mode files: `technical.md`, `market.md`, `references.md`, `brand.md`, `marketing.md`
- `FRAMEWORK_GLOBS` in `sync.py`, `hooks/pre-commit`, `hooks/post-commit`, and `audit.py` updated to include `agents/discovery-modes/*.md`
- GITIGNORE_ENTRIES unchanged — `/agents/` already covers the subdirectory
- Pattern can be applied to other large agents (e.g., Iteration Manager) if compression is needed

---

## DEC-008: UX Writer as independent agent

**Date:** 2026-03-29
**Status:** accepted
**Task:** TASK-007

### Context

The system lacked a dedicated agent for user-facing text. Copy was handled ad-hoc by Designer, Product, or Builder, leading to inconsistent tone of voice and developer-speak in UI strings.

### Decision

Create a standalone UX Writer agent rather than a Discovery mode or Designer sub-role, because:

- UX Writer produces unique artifacts (`ux_copy`) — copy documents and copy reviews — unlike any existing agent
- It has three invocation points: after Designer (copy creation), after Builder (copy review), and standalone (release notes, emails)
- It depends on `docs/BRAND.md` as a primary input, not on discovery modes
- Copy creation and copy review are distinct operations with different output formats

### Implications

- New file: `agents/ux-writer.md`
- New `artifact_type`: `ux_copy` in handoff contract
- Standard workflow extended with two optional UX Writer steps
- `ux_copy` added to Spec Reviewer, Reviser, and Gatekeeper scope
- No impact on existing workflows when UX Writer is skipped

---

## DEC-009: Deploy Contracts and CI templates for deployment quality

**Date:** 2026-03-29
**Status:** accepted
**Task:** TASK-008

### Context

Analysis of both downstream projects revealed systematic deployment failures: Unfolda had no CI/CD, worker kills during Railway redeploys with cascading data corruption (3 consecutive failures from framework syncs); Voxema had CI without tests, broken Sparkle EdDSA signature handoff, and config drift. The agent workflow ended at Reviewer approval with no deployment coverage.

### Options considered

1. **Deploy Contracts + Architect/Reviewer extensions** — minimal, process-only
2. **Deploy Contracts + CI/CD templates + pre-deploy validation** — moderate, process + tooling
3. **Full DevOps Agent** — heavyweight, new agent in workflow

### Decision

Option 2: Deploy Contracts + CI/CD templates. Scored 37/40 vs 35/40 (Option 1) and 24/40 (Option 3).

### Rationale

- Closes all 5 identified deployment failure patterns without adding a new agent
- Deploy Contracts reuse the proven Pipeline Contracts pattern
- CI templates are a one-time investment per stack, covering both existing projects
- DevOps Agent is overkill for 2 projects and hard to reverse once integrated

### Implications

- New `docs/DEPLOY_CONTRACTS.md` template (project-specific, not synced)
- Architect output format extended with mandatory "Deployment Impact" section
- Reviewer checklist extended with deployment verification
- CI templates in `templates/ci/` (reference only, not auto-synced)
- `CLAUDE.md` mandatory reads list includes `docs/DEPLOY_CONTRACTS.md`
- `--no-redeploy` for sync.py cancelled — gitignore already prevents downstream commits from framework syncs

---

## DEC-010: Marketing Agent as standalone agent

**Date:** 2026-03-29
**Status:** Accepted

### Context

The system needs a marketing capability — product analysis, strategy definition, campaign creation, launch kits. Discovery already has a `marketing.md` mode for GTM research, but it's read-only and produces recommendations, not campaign artifacts.

### Options considered

1. **Extend Discovery marketing mode** — add campaign creation to existing mode
2. **Standalone Marketing agent** — new agent with its own artifact type and operating modes
3. **External marketing tool integration** — connect to third-party marketing platforms

### Decision

Option 2: Standalone Marketing agent.

### Rationale

- Marketing produces unique artifacts (`marketing_campaign`) that differ from any existing agent output
- Has multiple operating modes (strategy, campaign creation, launch prep, review)
- Needs to collaborate with UX Writer (tone) and Designer (visual briefs)
- Discovery marketing mode remains useful as an upstream research step; Marketing builds on those findings
- External tool integration is premature without a strategy layer to decide what to create

### Implications

- New `agents/marketing.md` agent definition
- New `marketing_campaign` artifact type in handoff contract
- IM routing updated for `marketing_strategy` request type
- Standard workflow transitions include Marketing → Quality loop and Marketing → UX Writer paths
- Spec Reviewer, Reviser, Gatekeeper updated to handle `marketing_campaign` artifacts

---

## DEC-011: Illustrator as a tool-agent with MCP integration

**Date:** 2026-03-29
**Status:** Accepted

### Context

The system needs image generation capabilities. Designer creates mockups and visual direction but cannot generate actual images. The user wants multi-model work — specifically using Google Nano Banana 2 for image generation while the rest of the system runs on Claude.

### Options considered

1. **Designer uses MCP directly** — add image generation capability to Designer agent
2. **Separate Illustrator tool-agent** — new agent type that bridges the system with external models via MCP
3. **External workflow** — generate images outside the agent system manually

### Decision

Option 2: Separate Illustrator tool-agent.

### Rationale

- Clean separation: Designer thinks (visual direction), Illustrator executes (image generation)
- Model-agnostic: can switch between Nano Banana, DALL-E, FLUX without changing Designer
- Establishes the "tool-agent" pattern — reusable for future external model integrations (voice, video, 3D)
- MCP servers run locally via npx — no infrastructure needed
- Designer remains focused on UI/UX without MCP tool dependencies
- Illustrator handles graceful degradation when MCP tool is unavailable

### Implications

- New `agents/illustrator.md` agent definition (tool-agent type)
- New `docs/MCP_TOOLS.md` — MCP tool configuration guide
- New `illustration` artifact type in handoff contract
- Designer updated with "Visual brief format" section
- Workflow: Designer → Illustrator → Designer (review loop)
- Illustrator can also serve Marketing for campaign visuals
- `.cursor/mcp.json` is project-specific and should be gitignored if it contains API keys

---

## DEC-012: OmniRoute as future multi-model infrastructure (deferred)

**Date:** 2026-03-29
**Status:** Researched — deferred

### Context

The agent system currently runs on Claude (via Cursor) with a single MCP integration for image generation (Nano Banana 2). As the system grows (more tool-agents, higher usage, more downstream projects), multi-model routing, cost optimization, and fallback resilience may become necessary.

[OmniRoute](https://github.com/diegosouzapw/OmniRoute) (MIT, 1.6k stars) is an open-source AI gateway that provides: unified endpoint for 67+ providers, automatic fallback chains (Subscription → API Key → Cheap → Free), format translation (OpenAI ↔ Claude ↔ Gemini), multi-account round-robin, MCP server, cost tracking, circuit breakers.

### Options considered

1. **Adopt OmniRoute now** — run as local proxy, route all agent traffic through it
2. **Defer** — keep current architecture (Claude + individual MCP servers), adopt later when needed
3. **Ignore** — stay single-model permanently

### Decision

Option 2: Defer. Record for future consideration.

### Rationale

**Useful for:**
- Multi-model routing for tool-agents (Illustrator, future voice/video agents)
- Free providers for draft tasks (Marketing first drafts, UX Writer iterations, Discovery research)
- Fallback chains when Claude hits rate limits mid-workflow
- Image generation via unified `/v1/images/generations` (10+ providers)

**Not useful yet because:**
- Agent prompts are optimized for Claude; other models may not follow complex role instructions reliably
- Two downstream projects don't justify the infrastructure overhead
- Current MCP-per-tool approach is simpler and sufficient
- Adding a proxy layer increases debugging complexity

**Triggers to revisit:**
- 3+ tool-agents requiring different external models
- Claude costs become a concern (free providers for low-stakes tasks)
- Rate limits disrupt workflows regularly
- Need for model A/B testing across agents

**Planned integrations (pre-OmniRoute or via OmniRoute):**

1. **Perplexity API** — for Discovery agent research tasks (technical, market, competitive, legal modes). Perplexity provides real-time web search + LLM synthesis, which is stronger than Claude's knowledge cutoff for current data. Can be integrated as a standalone MCP server or routed through OmniRoute.

2. **Multi-model translation for Unfolda** — OmniRoute enables testing and selecting optimal models per language pair for Unfolda's translation pipeline. Current state: all 3 quality tiers use Claude (Haiku/Sonnet/Opus). Opportunity: express tier could use cheaper models (DeepSeek, GLM, Kimi) at comparable quality for certain language pairs; standard tier could use Gemini Pro at ~3x lower cost. OmniRoute's Translator Playground enables side-by-side comparison. Architecturally Unfolda is ready — env vars (`TRANSLATION_MODEL_EXPRESS/STANDARD/PREMIUM`) and single-provider adapter pattern support swapping. This is a natural post-MVP step.

3. **Fallback chains for long workflows** — both Voxema (local LLM summarization) and Unfolda (100K word book translation taking 20-30 min) benefit from automatic fallback when provider rate limits or outages interrupt mid-workflow.

---

## DEC-013: Agent-system hardening contracts

**Date:** 2026-04-30
**Status:** accepted

### Context

The framework already defines roles, routing, handoff semantics, quality loops, task lifecycle, and organizational memory. As the system is positioned as an SDLC process layer above Cursor/Claude Code, optional runtimes, model gateways, and CI/CD, several boundaries needed first-class contracts: model authority, external review, durable workflow state, sandbox behavior, evals, and PR evidence.

### Decision

Add process contracts rather than replacing the existing Iteration Manager state machine:

- `docs/MODEL_POLICY.md` for model classes, role mappings, and model authority.
- `docs/EXTERNAL_REVIEW_CONTRACT.md` for strict external review JSON.
- `docs/SANDBOX_POLICY.md` for runtime and command safety.
- Mandatory `.agent/workflows/<task_id>.json` workflow state.
- `workflow_mode: lite | standard | strict` as a rigor axis.
- First-class `evals/` for process evaluation.
- `docs/PULL_REQUEST_CONTRACT.md`, PR template, and quality workflow for PR-based delivery.

### Rationale

- Preserves the existing markdown SDLC layer and handoff model.
- Keeps optional runtimes and model gateways as implementation details.
- Prevents reviewer models from becoming competing decision-makers.
- Makes CI/CD and PRs the objective enforcement surface without giving models merge authority.
- Provides evals so workflow changes can be compared with evidence rather than impressions.

### Implications

- New framework files must be included in audit and sync coverage.
- Downstream projects receive governance contracts through framework sync.
- Project-specific PR/CI files are seeded only when absent to avoid overwriting local GitHub configuration.
- Future model gateway adoption must update `docs/MODEL_POLICY.md` instead of hardcoding providers in agent prompts.

---

## DEC-014: Backward-compatible model gateway rollout

**Date:** 2026-04-30
**Status:** accepted

### Context

The framework needs concrete model guidance for each agent role and a recommended way to connect LiteLLM, OpenRouter, local models, and future automated runtimes. At the same time, the system must keep working when no gateway is deployed and only the active Claude model is available in Cursor or Claude Code.

### Decision

Adopt a staged model gateway strategy:

1. `claude_only` is the required compatibility baseline.
2. `openrouter_pilot` may be used for advisory external review reports and model experiments.
3. `litellm_gateway` is the recommended production gateway for routing, fallbacks, budgets, logs, and local model integration.
4. `hosted_runtime` integrations call the approved gateway endpoint and must preserve Iteration Manager authority.

`docs/MODEL_POLICY.md` defines the role-to-model matrix and fallback behavior. `docs/MODEL_GATEWAY_SETUP.md` defines operational setup guidance.

### Rationale

- Preserves zero-infrastructure operation for Cursor and Claude Code.
- Lets the framework experiment with GPT, Kimi, Gemini, and local models without changing workflow authority.
- Keeps LiteLLM as the eventual policy gateway while using OpenRouter for fast model access when useful.
- Avoids making external review a hard dependency for normal workflows.

### Implications

- Missing LiteLLM/OpenRouter must degrade to `claude_only`, not block execution.
- External reviewers remain advisory unless the user explicitly makes them a hard gate.
- Automated runtimes should call LiteLLM when deployed and must not bypass `docs/MODEL_POLICY.md`.
- Future model changes should update the model map rather than agent role prompts.

---

## DEC-015: Media tool-agents for image and video generation

**Date:** 2026-04-30
**Status:** accepted

### Context

The framework already had Illustrator for image generation via MCP tools such as Nano Banana. The media workflow also needs to support GPT Image, Kling, Veo, Runway, Pika, and similar models without treating them as autonomous agents or giving them design/product authority.

### Decision

Keep media generation as a tool-agent pattern:

- `Illustrator` generates image assets from visual briefs using GPT Image, Nano Banana, Imagen, FLUX, or similar media models.
- `Video Producer` generates video assets from video briefs using Kling, Veo, Runway, Pika, or similar media models.
- Designer owns visual direction.
- Animator owns motion direction.
- Marketing owns campaign context when it requests campaign media.
- Media models execute briefs and return assets with metadata; they do not make workflow decisions.

### Rationale

- Preserves separation between thinking agents and tool models.
- Keeps GPT Image/Nano Banana/Kling/Veo optional and replaceable.
- Allows media provider APIs to evolve without changing core workflow authority.
- Supports graceful degradation: if no media tool is configured, the tool-agent returns `blocked`.

### Implications

- `docs/MCP_TOOLS.md` documents image and video tool setup.
- `docs/AGENT_HANDOFF_CONTRACT.md` includes `video` artifacts.
- Iteration Manager may route Designer, Animator, or Marketing briefs to `Video Producer`.
- Generated media must be reviewed by the requesting direction owner before downstream implementation or campaign use.
