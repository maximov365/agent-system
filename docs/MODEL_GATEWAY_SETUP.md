# Optional model gateway adapters

Codex with an existing account needs no gateway. `single_active` is the portable
baseline; `claude_only` is a compatibility alias in older Claude configurations,
not a framework requirement. `docs/MODEL_POLICY.md` governs model choice and
`docs/EXTERNAL_REVIEW_CONTRACT.md` governs sending work to another provider.

Keep an existing project router when it solves an actual need. Before changing it,
inspect its configuration, authentication method, supported request format and
current provider documentation. Verify each selected model and tool capability
on that route. A model available in a subscription client may have different API
availability, parameters, billing and retirement dates.

Preserve configured workload classes (`frontier_reasoning`, `coding_builder`,
`strict_reviewer`, `long_context_reviewer`, `cheap_summarizer`, `local_private`).
Define permitted fallbacks, bounded retries, timeout, spend limits and redacted
usage evidence. A fallback must not change an exact requested model silently or
send data to an additional provider outside the task's authorization.

OpenRouter, LiteLLM and hosted runtimes are optional adapters, not installed by
framework sync. Adopt one only for an identified project requirement; keep its
configuration and credentials project/operator-owned. Check tool round trips,
streaming, cancellation, overload recovery and unavailable-model behavior before
relying on it. Never copy historical provider prices or model IDs as current facts.

Older setup recipes remain in Git history. They included Claude-only assumptions
and time-sensitive model maps and should not be used as current installation
instructions. No gateway code or paid API harness is bundled with this framework.
