# Model policy

Verified target: **GPT-6 Astra**, model identifier `gpt-6-astra`, 2026-09-10. This is the requested target for Codex use. Model access and selectable effort are determined by the current client/account; do not silently substitute a different model.

## Runtime baseline

`single_active` is the portable baseline: all methods use the current model, with no gateway. The old `claude_only` name is a compatibility alias for that behavior in Claude clients. Native tools supply browsing, image generation, and computer use when exposed. A tool's availability is verified, not inferred from a file listing it.

The project YAML documents workflow intent; it does not change the running Codex model. Use the model picker or the configuration example in `docs/CODEX.md`.

## Recommended effort policy (framework choice, not benchmarked)

| Work | Starting point | Adjustment |
|---|---|---|
| Routine bounded changes | Active model, medium | Low for demonstrably simple work if available |
| Architecture, broad audit, difficult debugging | Astra, high | Raise for unresolved complexity, not file count alone |
| Security-sensitive or contested review | Astra, high | Stronger supported effort or independent review if useful |
| Summaries and mechanical work | Active model | Optional cheaper model only when explicitly configured and validated |
| Image/video assets | Available dedicated media tool | Match brief, quality, budget, and modality |

These are recommendations. Preserve the user's model/effort setting unless a change is requested. Do not force maximum effort or separate calls for every role. Do not pretend that roleplay creates an independent reviewer.

## Astra API compatibility

For an API-backed downstream (not merely using Codex): use `gpt-6-astra` and Responses for tool calling. Remove unsupported `temperature`, `top_p`, and `top_logprobs`; inspect logprob options too. Migrate `none`/`minimal` effort to `low`; otherwise preserve effective effort. The published model page lists low, medium, high, xhigh, and max. Verify client-specific options separately. This repository does not implement an API harness.

Source: [official Astra guidance](https://developers.openai.com/api/docs/guides/latest-model) and [model specification](https://developers.openai.com/api/docs/models/gpt-6-astra), checked 2026-09-10.

## Optional multiple models

Keep existing workload classes when a downstream already has them: `frontier_reasoning`, `coding_builder`, `strict_reviewer`, `long_context_reviewer`, `cheap_summarizer`, and `local_private`. Do not collapse a working tiered router into Astra for every operation.

Gateways and external reviewers are optional infrastructure. `openrouter_pilot`, `litellm_gateway`, and `hosted_runtime` configurations may remain in existing downstreams; consult `docs/MODEL_GATEWAY_SETUP.md` only for those integrations. Each integration needs verified model IDs, capability checks, fallback policy, bounded retries, and usage records. Use only supported request parameters. No gateway is a prerequisite for high-quality Codex work.

If a configured optional model is unavailable, use an allowed fallback and disclose it. If the exact model is required, explain the blocker instead of silently changing it. External review follows `docs/EXTERNAL_REVIEW_CONTRACT.md`; source material must not be sent to another provider without authorization for that surface.

## Authority and measurement

A model change cannot grant permission to publish, merge, send messages, access secrets, or spend outside the authorized task. The task owner integrates findings and verifies evidence.

Record exact model/runtime, effort when observable, task, elapsed time, meaningful defects, interventions, and actual usage when available. Keep unknown usage/cost as null, not zero. Subscription usage is not an API invoice. Compare models on the same tasks and acceptance criteria before claiming quality or cost improvements.

Historical provider price tables and access claims from August 2026 were removed from active policy: they were time-sensitive, duplicated role guidance, and were not an executable router. History remains in git and decision logs.
