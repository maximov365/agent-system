# Discovery Mode: AI Landscape Review

Use this mode for **periodic scanning of the AI world** — research papers, agent frameworks, benchmarks, tooling, Claude/MCP ecosystem updates — to surface concrete improvements for our agent system.

This mode does **not** implement changes. It produces a structured report with prioritized proposals; the user decides what to adopt.

The output is appended to `docs/EVOLUTION_LOG.md` in the agent-system root (or in the calling project's root for project-scoped reviews).

---

## When this mode runs

- **Weekly cadence** (recommended) — Monday morning review of the past week's developments
- **On-demand** when the user wants to evaluate the landscape before a major decision
- After major framework changes — to see if recent AI work validates or challenges the new design

---

## Required reading

Before scanning, read:

- `docs/PRD.md` — current framework intent (or project intent if project-scoped)
- `docs/ARCHITECTURE.md` — current capabilities to compare against
- `docs/EVOLUTION_LOG.md` — prior reviews and decisions (avoid re-proposing rejected items)
- `docs/KNOWN_PATTERNS.md` — patterns that already work for us
- `docs/LESSONS_LEARNED.md` — anti-patterns we've identified

---

## Sources to scan

Use WebSearch and WebFetch to investigate the following sources. Spend ~5–10 web queries total; this is a survey, not a deep dive.

### Tier 1 — Anthropic ecosystem (always check)
- [Anthropic news](https://www.anthropic.com/news) — Claude updates, new capabilities
- [Anthropic Cookbook](https://github.com/anthropics/anthropic-cookbook) — new patterns, examples
- [Claude Code docs changelog](https://docs.claude.com/claude-code) — new features, hooks, MCP additions
- [MCP server registry](https://github.com/modelcontextprotocol/servers) — new servers worth integrating

### Tier 2 — Agent frameworks (compare approaches)
- LangChain / LangGraph releases — new orchestration patterns
- CrewAI updates — multi-agent coordination ideas
- AutoGen (Microsoft) — agent communication patterns
- DSPy — programmatic prompting techniques
- OpenAI Swarm / Assistants API — alternative agent models
- Smolagents (Hugging Face)

### Tier 3 — Research (novel ideas, often months from production)
- arXiv cs.AI / cs.CL — recent papers (last 2–4 weeks):
  - Search terms: "agent orchestration", "self-refine", "tool use", "agent benchmark", "LLM evaluation"
- Papers With Code — agent benchmarks trending
- Hugging Face papers — top trending recent

### Tier 4 — Benchmarks & evaluations
- SWE-bench leaderboard — software engineering agent performance
- AgentBench — agent capabilities
- HELM — holistic LLM evaluation
- ARC-AGI — reasoning benchmarks
- WebArena, OSWorld — agent operating in environments

### Tier 5 — Community & news
- Hacker News (filter: AI agents, LLMs, recent month top)
- Import AI / Ahead of AI / TLDR AI newsletter (latest 2–3 issues)
- Twitter/X via WebSearch ("from:karpathy", "from:simonw", agent framework releases)
- LinkedIn AI engineering posts (top engagement, recent)

### Tier 6 — Tools & developer ergonomics
- New CLI tools for AI workflows
- Prompt management / versioning tools
- LLM observability (Langfuse, Helicone, Phoenix)
- Eval frameworks (Promptfoo, Inspect)

### Tier 7 — Agent role inventory & domain specializations

Use this tier to discover **specialized agent roles** that our system might lack, or domain-specific agent patterns worth adopting.

- `awesome-llm-agents`, `awesome-ai-agents` GitHub lists
- CrewAI built-in agent library (their `Agent` presets)
- Vercel AI SDK agent templates
- Anthropic enterprise plugin agents (finance, legal, HR, engineering) — hints at valuable specializations
- Domain-specific AI tools: DevSecOps, FinOps, Performance analysis, License/compliance audit, Data quality, Accessibility, Documentation, Observability/SRE

**Mapping question:** For each interesting specialization found, ask "would this become a new agent in our system, or enhance an existing one?"

### Tier 8 — Production patterns & failure modes

Use this tier to learn from engineers running multi-agent systems with real traffic — what works, what breaks, what they wish they'd known.

- [Latent Space podcast](https://www.latent.space/) — production AI engineering deep dives
- [Eugene Yan blog](https://eugeneyan.com/) — applied ML/agents, evaluation
- [Simon Willison's weeknotes](https://simonwillison.net/) — practical LLM engineering
- "Building agents in production" posts on Substack / LinkedIn
- Anthropic case studies + customer stories
- Horror stories / post-mortems of agent failures

**Mapping question:** For each failure mode found, ask "could this happen to us? do our agents have the right guardrail?"

### Tier 9 — Cognitive architectures & prompting techniques

Use this tier to improve how **existing agents think** — planning structure, memory, reasoning chains, structured output.

- Anthropic prompt engineering documentation
- Awesome-prompt-engineering list
- Specific research directions: Plan-and-Solve, ReAct, Tree-of-Thoughts, Self-Consistency, Reflexion, Chain-of-Verification, Memory-augmented agents (MemGPT, generative agents)
- "How I prompt X agent to do Y" posts from experienced prompt engineers

**Mapping question:** For each technique found, ask "which of our 21 agents would benefit, and is the added prompt length / token cost justified?"

---

## Query quota rules

Each review must allocate queries across tiers with these minimums:

- At least 2 queries targeting **agent-specific tiers** (Tier 2, 7, 8, or 9) — ensures we don't drift into only tooling/cost reviews
- At least 1 query each in Tiers 1 (Anthropic ecosystem) and 4 (benchmarks) — these are foundational
- Remaining queries distributed by the review's focus area (if `OPTIONAL_FOCUS` is set) or evenly

The review should balance **tooling improvements** (cost, lazy loading, MCP) and **agent/workflow improvements** (new roles, prompting techniques, failure modes). A review where all 10 queries are about caching or observability fails this balance — it means we're over-weighting infrastructure and under-weighting the substance of the agents themselves.

---

## Methodology

### 1. Scan

For each tier, do 1–2 targeted web queries. Capture:
- What's new (release / paper / tool / benchmark result)
- What problem it addresses
- How mature it is (research / beta / production-ready / widely adopted)
- Url for follow-up

Time-box: ~30 minutes of queries total. Do not exhaustively crawl.

### 2. Filter

Discard findings that are:
- Already in our system (check `docs/KNOWN_PATTERNS.md`, `docs/CLAUDE_SKILLS.md`, `docs/MCP_TOOLS.md`)
- Already evaluated and rejected (check `docs/EVOLUTION_LOG.md`)
- Marketing fluff with no concrete advantage
- Pre-alpha research with no usable artifact yet

Aim for 5–15 high-signal findings.

### 3. Map to our system

For each finding, identify:
- **Component affected** — which agent / mode / doc / pipeline stage
- **Compatibility** — works with our environment-agnostic design? (must work in Cursor/API too if augmenting agents)
- **Backward compatibility** — does adoption break existing projects?

### 4. Score

Rank by **Impact × Adoption-confidence ÷ Effort**:

| Dimension | Scale |
|---|---|
| Impact | High (changes core behavior) / Medium (improves a workflow) / Low (nice-to-have) |
| Confidence | High (battle-tested, clear win) / Medium (promising) / Low (speculative) |
| Effort | Small (≤1 day) / Medium (1–3 days) / Large (week+) |

Output rank order: high-impact + high-confidence + small-effort first.

### 5. Propose

For each top finding, write a concrete proposal:
- What to integrate / change
- Why (mapped to our pain point or opportunity)
- How (specific files, agents, or patterns to touch)
- Risk and rollback plan
- Open questions for user decision

### 6. Log

Append the report to `docs/EVOLUTION_LOG.md` (create if not exists) with the structure below.

### 7. Defer all action

Do not implement anything. Do not commit code changes. Do not modify framework files except for `docs/EVOLUTION_LOG.md`. The user decides what to adopt and explicitly invokes follow-up implementation.

---

## Output format

```markdown
## AI Landscape Review — YYYY-MM-DD

**Reviewer:** Discovery (ai-landscape mode)
**Scope:** framework | project (specify which)
**Sources scanned:** <list which tiers were covered>
**Time period:** <since when, e.g. "since 2026-04-17">

### Summary
<2–3 sentence high-level summary: what's the most important finding, urgency.>

### Findings — High Priority

#### F1: <Short name>
- **Source:** <url + brief context>
- **Maturity:** research / beta / production / widely-adopted
- **What it is:** <1–2 sentence description>
- **Impact on us:** High/Medium/Low — <which component, what it would change>
- **Adoption confidence:** High/Medium/Low — <evidence for the win>
- **Effort:** Small/Medium/Large — <what we'd need to do>
- **Proposal:** <concrete action: which file/agent to modify or create>
- **Risk & rollback:** <what could go wrong, how to revert>
- **Decision needed:** <yes/no question for the user>

#### F2: ...

### Findings — Medium Priority
<Same structure, more brief>

### Findings — Monitor (low priority / immature)
- F#: <name> — <one-line summary> — <why deferred>

### Decisions Required from User

| # | Question | Recommended default |
|---|---|---|
| 1 | Adopt F1? | yes / no / defer |
| 2 | Investigate F3 deeper next week? | yes / no |

### Comparison to prior reviews
<Did anything we deferred last time become more relevant? Did we adopt something that's now showing problems?>

### Notes
<Any meta-observations about the AI landscape direction, trends to watch>

---
```

---

## Handoff

Append a handoff block per `docs/AGENT_HANDOFF_CONTRACT.md` with `artifact_type: "design_note"` and `status: "produced"`.

Set `next_recommended_agent` to `null` — the user reviews the report and decides next steps. No automatic follow-up.

In `next_recommended_reason`, summarize: how many findings, how many require decision, and the single most important proposal.
