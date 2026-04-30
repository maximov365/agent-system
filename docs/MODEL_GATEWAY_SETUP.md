# Model Gateway Setup

This document describes how to connect optional model gateways while preserving the baseline Claude-only workflow.

The policy source of truth is `docs/MODEL_POLICY.md`. This file is operational guidance.

---

## Compatibility First

The framework must run in four levels:

```text
claude_only → openrouter_pilot → litellm_gateway → hosted_runtime
```

`claude_only` is the required baseline. If no gateway is configured, every agent runs on the active Claude/Cursor/Claude Code model and the workflow remains valid.

Optional gateway features must degrade gracefully:

- External reviews are skipped unless the user required them as a hard gate.
- Cheap summarization falls back to the active model or is skipped.
- Long-context review narrows the context package instead of failing.
- Local private summarization is skipped when no local model is available.

---

## Recommended Architecture

```text
Cursor / Claude Code
  = primary interactive coding interface

LiteLLM
  = production policy gateway for automated runtimes

OpenRouter
  = optional upstream behind LiteLLM, or direct pilot for external review

OpenHands / OpenAI Agents SDK / LangGraph
  = optional automated runtime calling the approved gateway endpoint
```

Use LiteLLM as the official gateway when production governance matters. Use OpenRouter directly only for fast experiments and external review pilots.

---

## Level 1: Claude-Only Baseline

No setup required.

Behavior:

- Iteration Manager runs in Cursor or Claude Code.
- All specialist agents run on the active model.
- `docs/EXTERNAL_REVIEW_CONTRACT.md` is inactive unless the user supplies an external report manually.
- `docs/MODEL_POLICY.md` still governs authority: model choice never changes who may write code, review, or approve.

This mode is appropriate for solo work, early projects, and environments without gateway infrastructure.

---

## Level 2: OpenRouter Pilot

Use OpenRouter when you want fast access to many reviewer models without operating infrastructure.

Recommended uses:

- External GPT/Kimi/Gemini review reports.
- Long-context review experiments.
- Model comparison runs in `evals/`.
- Low-risk draft generation.

Not recommended at this level:

- Making OpenRouter the mandatory Builder path.
- Sending secrets, `.env` contents, private customer data, or unredacted production data.
- Treating OpenRouter review verdicts as workflow authority.

Configuration belongs outside framework docs, usually in local environment or project-specific runtime config:

```text
OPENROUTER_API_KEY=<set outside repo>
MODEL_GATEWAY_LEVEL=openrouter_pilot
```

External review reports must follow `docs/EXTERNAL_REVIEW_CONTRACT.md`.

---

## Level 3: LiteLLM Gateway

Use LiteLLM when you need controlled routing, fallbacks, budgets, provider keys, and local models.

Recommended responsibilities:

- Map model classes from `docs/MODEL_POLICY.md` to concrete provider models.
- Enforce fallback chains.
- Track spend and token usage.
- Route local models through Ollama, vLLM, or another local endpoint.
- Provide one endpoint for automated runtimes.
- Keep OpenRouter as an upstream provider when broad model access is useful.

Minimal conceptual LiteLLM config:

```yaml
model_list:
  - model_name: frontier_reasoning
    litellm_params:
      model: anthropic/claude-opus-4-7
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: coding_builder
    litellm_params:
      model: anthropic/claude-sonnet-4-6
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: strict_reviewer
    litellm_params:
      model: openai/gpt-5.5
      api_key: os.environ/OPENAI_API_KEY

  - model_name: long_context_reviewer
    litellm_params:
      model: gemini/gemini-3.1-pro
      api_key: os.environ/GEMINI_API_KEY

  - model_name: cheap_summarizer
    litellm_params:
      model: openrouter/kimi-k2.6
      api_key: os.environ/OPENROUTER_API_KEY

  - model_name: local_private
    litellm_params:
      model: ollama/qwen
      api_base: http://localhost:11434

router_settings:
  num_retries: 2
  timeout: 60
  fallbacks:
    frontier_reasoning: [coding_builder]
    coding_builder: [frontier_reasoning]
    strict_reviewer: [frontier_reasoning]
    long_context_reviewer: [frontier_reasoning]
    cheap_summarizer: [local_private, frontier_reasoning]
```

Do not commit real API keys. Keep provider secrets in local environment, CI secrets, or runtime secret storage.

---

## Level 4: Hosted Runtime

OpenHands, OpenAI Agents SDK, LangGraph, or a similar runtime may execute tasks outside the interactive IDE.

Rules:

- The runtime calls the approved gateway endpoint.
- The runtime persists workflow state under `.agent/workflows/`.
- The runtime respects `docs/SANDBOX_POLICY.md`.
- The runtime stores external review reports under `docs/reviews/` when they are task evidence.
- The runtime does not bypass Iteration Manager or invent workflow transitions.

If the runtime cannot guarantee sandboxing, state persistence, or model policy compliance, use the interactive Claude-only workflow instead.

---

## Rollout Checklist

1. Start with `claude_only` and run a normal workflow.
2. Add OpenRouter for one advisory external review.
3. Store the report under `docs/reviews/` and verify it matches `docs/EXTERNAL_REVIEW_CONTRACT.md`.
4. Run at least one `evals/` task with and without the external reviewer.
5. Deploy LiteLLM only after the model map and fallback order are stable.
6. Point automated runtimes to LiteLLM, not directly to providers.
7. Keep `claude_only` documented and tested as the fallback mode.
