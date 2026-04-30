# Model Policy

This document defines how the agent workflow may use multiple LLMs through Cursor, Claude Code, LiteLLM, OpenRouter, local models, or another gateway.

The policy applies to model selection and model authority only. Workflow sequencing remains governed by `AGENTS.md`; coding behavior remains governed by `.cursor/rules.md`; external review I/O is governed by `docs/EXTERNAL_REVIEW_CONTRACT.md`.

---

## Goals

- Keep model routing predictable across roles.
- Prevent multiple reviewer models from becoming competing decision-makers.
- Allow cheaper or specialized models where risk is low.
- Preserve a single accountable path for code changes, review decisions, and merges.

---

## Model Classes

Use model classes in framework documents and project configuration. Concrete provider names belong in project-specific configuration or the active model gateway.

| Class | Intended use |
|---|---|
| `frontier_reasoning` | Architecture, high-risk product decisions, complex code review |
| `coding_builder` | Implementation, test repair, refactoring |
| `strict_reviewer` | Code review, security review, acceptance criteria validation |
| `long_context_reviewer` | Large diffs, long specs, repository-wide review |
| `cheap_summarizer` | Summaries, log compression, non-authoritative drafts |
| `local_private` | Sensitive local summarization when available |

Example mappings:

```yaml
roles:
  architect:
    primary: frontier_reasoning
    reviewer: strict_reviewer
  builder:
    primary: coding_builder
    fallback: frontier_reasoning
  code_reviewer:
    primary: strict_reviewer
    secondary: long_context_reviewer
  long_context_reviewer:
    primary: long_context_reviewer
  security_reviewer:
    primary: strict_reviewer
  cheap_summarizer:
    primary: cheap_summarizer
    fallback: local_private
```

---

## Compatibility Requirement

The framework must work when no model gateway is deployed.

Supported runtime levels:

| Level | Available models | Required behavior |
|---|---|---|
| `claude_only` | Only the active Claude/Cursor/Claude Code model | All agents run on the active model; external reviews and cheap summarization are skipped or performed by the active model |
| `openrouter_pilot` | Active Claude model plus OpenRouter for external reviewers | Primary workflow stays in Claude; OpenRouter produces advisory review reports only |
| `litellm_gateway` | LiteLLM with provider keys and optional local models | Role-to-model routing, fallbacks, budgets, logs, and local models are enabled |
| `hosted_runtime` | OpenHands, OpenAI Agents SDK, LangGraph, or similar runtime | Runtime calls the approved gateway endpoint; workflow authority remains in agent-system |

If a configured model, gateway, or local endpoint is unavailable, Iteration Manager must degrade to the next available level rather than stopping the workflow, unless the user explicitly required that model or external review as a hard gate.

Baseline guarantee:

- `claude_only` is always valid.
- LiteLLM is recommended for production multi-model routing, but never required for basic workflow correctness.
- OpenRouter is recommended for fast experimentation and external review pilots, but never required for mandatory Security Reviewer or Reviewer steps.
- Local models are optional accelerators for low-risk summaries only.

---

## Recommended Concrete Mapping

Concrete model names change over time. Treat this table as a recommended starting map, not a permanent benchmark claim.

| Model class | Primary | Fallback | Use when gateway is unavailable |
|---|---|---|---|
| `frontier_reasoning` | Claude Opus 4.7 | Claude Sonnet 4.6, GPT-5.5 | Active Claude model |
| `coding_builder` | Claude Sonnet 4.6 | GPT-5.3 Codex, GPT-5.5, Claude Opus 4.7 | Active Claude model |
| `strict_reviewer` | GPT-5.5 | GPT-5.4, Claude Opus 4.7 | Active Claude model acting as Reviewer |
| `long_context_reviewer` | Gemini 3.1 Pro | Claude Opus 4.7, Kimi K2.6 | Active Claude model with narrowed context |
| `cheap_summarizer` | Gemini Flash / GPT mini class | Kimi/Qwen/DeepSeek hosted cheap model | Active Claude model, or skip if summary is nonessential |
| `local_private` | Ollama Qwen/DeepSeek/Llama class | None | Skip local-only optimization |

Role mapping:

| Agent | Primary class | Concrete preference | Fallback behavior |
|---|---|---|---|
| Iteration Manager | `frontier_reasoning` | Claude Sonnet 4.6; Opus for strict/high-risk routing | Active Claude model |
| Discovery | `frontier_reasoning` plus web/search tool when available | Perplexity/Sonar for current research, Claude for synthesis | Claude-only synthesis from available context |
| Product | `frontier_reasoning` | Claude Opus for ambiguous scope; Sonnet for standard specs | Active Claude model |
| Designer | `frontier_reasoning` | Claude Sonnet/Opus | Active Claude model |
| Animator | `frontier_reasoning` | Claude Sonnet/Opus | Active Claude model |
| UX Writer | `frontier_reasoning` or `cheap_summarizer` for drafts | Claude Sonnet; cheap model for variants | Active Claude model |
| Marketing | `frontier_reasoning` or `cheap_summarizer` for drafts | Claude Sonnet; GPT/Gemini for variants | Active Claude model |
| Illustrator | External media tool model | Nano Banana / GPT Image / Imagen / FLUX via MCP or provider API | Return `blocked` if tool unavailable |
| Video Producer | External media tool model | Kling / Veo / Runway / Pika via MCP or provider API | Return `blocked` if tool unavailable |
| Analytics Architect | `frontier_reasoning` | Claude Opus/Sonnet | Active Claude model |
| Architect | `frontier_reasoning` | Claude Opus for strict; Sonnet for standard | Active Claude model |
| Test Strategist | `strict_reviewer` | GPT-5.5/GPT-5.4 | Active Claude model |
| Builder | `coding_builder` | Claude Sonnet; GPT Codex for terminal-heavy repair | Active Claude model |
| UI Builder | `coding_builder` | Claude Sonnet; Gemini/Kimi as advisory external UI reviewer | Active Claude model |
| Security Reviewer | `strict_reviewer` | GPT-5.5 plus CI/security scan evidence | Active Claude model |
| Reviewer | `strict_reviewer` | GPT-5.5, with Opus/Gemini/Kimi for secondary long-context pass | Active Claude model |
| Spec Reviewer | `strict_reviewer` | GPT-5.5 or Claude Opus | Active Claude model |
| Reviser | `frontier_reasoning` | Claude Sonnet | Active Claude model |
| Gatekeeper | `frontier_reasoning` | Claude Opus/Sonnet | Active Claude model |

No fallback may grant a model extra authority. A fallback reviewer remains a reviewer; a fallback builder remains Builder only when Iteration Manager routed to Builder.

Media models such as GPT Image, Nano Banana, Kling, Veo, Runway, and Pika are tool models. They receive structured briefs and return assets; they do not own design direction, motion direction, product scope, review verdicts, or workflow routing.

---

## Gateway Strategy

Use one official gateway front door for automated runtimes.

Recommended rollout:

1. **Baseline: `claude_only`** — the system runs entirely in Cursor or Claude Code using the active Claude model. This is the compatibility floor.
2. **Pilot: `openrouter_pilot`** — use OpenRouter only for external review reports and model comparison. Do not route mandatory Builder/Security Reviewer/Reviewer authority through it at first.
3. **Production: `litellm_gateway`** — deploy LiteLLM as the controlled gateway for automated reviewers, eval runs, local models, budgets, logs, and fallback chains.
4. **Runtime integration: `hosted_runtime`** — OpenHands, OpenAI Agents SDK, LangGraph, or similar runtimes call LiteLLM. They must not bypass `docs/MODEL_POLICY.md`.

Do not run LiteLLM and OpenRouter as competing top-level gateways. If both are used, LiteLLM is the policy gateway and OpenRouter is just one upstream provider.

Detailed setup guidance lives in `docs/MODEL_GATEWAY_SETUP.md`.

---

## Role Authority

Model choice does not change agent authority.

- Only `Builder` or `UI Builder` may modify production code.
- Reviewer models may only produce review reports.
- External reviewer findings are advisory until accepted by the workflow authority defined in `docs/EXTERNAL_REVIEW_CONTRACT.md`.
- `Gatekeeper` decides which external review findings become `must_fix` for non-code artifacts and policy reviews.
- `Reviewer` decides which external review findings become blocking for code after `Security Reviewer` has passed.
- No model may merge, push to `main`, force-push, publish releases, or bypass human approval.
- No model may read secrets or `.env` files unless the user explicitly grants permission for that operation.

---

## Gateway Contract

LiteLLM, OpenRouter, local Ollama, provider SDKs, or hosted agent runtimes are optional implementation details. When a gateway is used, it must provide:

- A project-specific model map from model class to concrete provider/model.
- Fallback order per role.
- Cost and token logging where supported.
- Temperature defaults per class.
- A denylist for models that may not receive sensitive data.
- A record of which model produced each review report or artifact.

The gateway must not choose a different workflow role. It only chooses the model used to execute the role selected by Iteration Manager.

When no gateway is used, the active interactive model is the implicit gateway and must follow the same authority rules.

---

## Defaults

| Agent | Default model class | Notes |
|---|---|---|
| Discovery | `frontier_reasoning` | May use web/search tools when available |
| Product | `frontier_reasoning` | Product scope and acceptance criteria are high leverage |
| Designer | `frontier_reasoning` | Visual decisions remain with Designer, not tool-agents |
| Illustrator | external tool model | Follows `docs/MCP_TOOLS.md`; no design authority |
| Video Producer | external tool model | Follows `docs/MCP_TOOLS.md`; no design or motion authority |
| Analytics Architect | `frontier_reasoning` | Metrics and instrumentation plans affect downstream validation |
| Architect | `frontier_reasoning` | Plans must be minimal and implementation-ready |
| Test Strategist | `strict_reviewer` | Focus on edge cases and objective verification |
| Builder | `coding_builder` | May modify code only when routed by Iteration Manager |
| UI Builder | `coding_builder` | Must follow approved design artifacts |
| Security Reviewer | `strict_reviewer` | Blocks security issues before final review |
| Reviewer | `strict_reviewer` | Final code validation role |
| Spec Reviewer | `strict_reviewer` | Produces structured review for Gatekeeper |
| Reviser | `frontier_reasoning` | Revises artifacts within accepted scope |
| Gatekeeper | `frontier_reasoning` | Decides accept / iterate / escalate |
| Iteration Manager | `frontier_reasoning` | Routing authority; does not create artifacts |
| Summarization-only tasks | `cheap_summarizer` | Never authoritative for acceptance or merge decisions |

---

## Sensitive Data Rules

- Prefer `local_private` or the primary interactive model for sensitive summaries when the user has approved the input surface.
- Do not send secrets, tokens, `.env` values, customer data, or private keys to external reviewers.
- Redact secrets before review packages are built.
- If redaction would remove context required for review, escalate to the user rather than sending the data.

---

## Change Control

Adding a new model provider, gateway, or role mapping requires:

1. Explicit user approval.
2. A decision entry in `docs/DECISIONS.md` when the change affects the framework or a downstream project architecture.
3. Updates to this file and any project-specific model gateway configuration.
4. Verification that review reports still satisfy `docs/EXTERNAL_REVIEW_CONTRACT.md`.
