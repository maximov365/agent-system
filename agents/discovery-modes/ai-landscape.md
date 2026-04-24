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
- [Anthropic Research](https://www.anthropic.com/research) — agent-specific papers (e.g., "Building Effective Agents" — foundational 7-pattern reference)
- [Anthropic Cookbook](https://github.com/anthropics/anthropic-cookbook) — production patterns, evaluation examples
- [Anthropic Skills repo](https://github.com/anthropics/skills) — official agent skills + Skill-Creator framework
- [Claude Code docs changelog](https://docs.claude.com/claude-code) — new features, hooks, MCP additions
- [MCP server registry](https://github.com/modelcontextprotocol/servers) — new servers worth integrating
- [Anthropic Economic Index on Hugging Face](https://huggingface.co/datasets/Anthropic/EconomicIndex) — usage data signals

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

**Newsletters (rotate, sample 1–2 per review):**
- [AlphaSignal](https://alphasignal.ai/) — weekly research-grade for ML practitioners (180k+ subs, GitHub trending coverage)
- [TLDR AI](https://tldr.tech/ai) — daily, technical professionals (500k+ subs)
- [Latent Space](https://www.latent.space/) — AI engineer newsletter + podcast (Swyx + Alessio Fanelli)
- [Import AI](https://importai.substack.com/) — Jack Clark's deep commentary
- [Ahead of AI](https://magazine.sebastianraschka.com/) — Sebastian Raschka, weekly research
- [LLMs for Engineers](https://www.llmsforengineers.com/) — Arjun Bansal, production scaling

**Reddit (read top weekly threads):**
- [r/ClaudeAI](https://www.reddit.com/r/ClaudeAI/) — Claude Code workflows, usage limits, bug reports
- [r/AI_Agents](https://www.reddit.com/r/AI_Agents/) — production failure rates, security problems, agent-touches-real-systems
- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/) — open-source models, hardware, privacy-first patterns (266k+ members)
- [r/LangChain](https://www.reddit.com/r/LangChain/) — agent dev community
- [r/MachineLearning](https://www.reddit.com/r/MachineLearning/) — research signal

**Forums & social:**
- [Hacker News](https://news.ycombinator.com/) — filter: AI agents, LLMs, recent month top
- Twitter/X via WebSearch — handles to track: `from:karpathy`, `from:simonw`, `from:swyx`, `from:rasbt`, `from:soumithchintala`, `from:_jasonwei`, `from:sama`

### Tier 6 — Tools & developer ergonomics
- New CLI tools for AI workflows
- Prompt management / versioning tools
- LLM observability (Langfuse, Helicone, Phoenix)
- Eval frameworks (Promptfoo, Inspect)

### Tier 7 — Agent role inventory & domain specializations

Use this tier to discover **specialized agent roles** that our system might lack, or domain-specific agent patterns worth adopting.

- [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) — 1000+ skills cross-platform (Claude Code, Codex, Cursor, Gemini CLI), official from Anthropic/Google/Vercel/Stripe/Cloudflare/Sentry
- [VoltAgent/awesome-agent-papers](https://github.com/VoltAgent/awesome-agent-papers) — curated 2026 agent research (engineering, memory, evaluation, workflows)
- [awesome-ai-agents-2026](https://github.com/caramaschiHG/awesome-ai-agents-2026) — 300+ agents/frameworks/tools, 20+ categories, monthly updates
- CrewAI built-in agent library (their `Agent` presets)
- Vercel AI SDK agent templates
- Anthropic enterprise plugin agents (finance, legal, HR, engineering) — hints at valuable specializations
- Domain-specific AI tools: DevSecOps, FinOps, Performance analysis, License/compliance audit, Data quality, Accessibility, Documentation, Observability/SRE

**Mapping question:** For each interesting specialization found, ask "would this become a new agent in our system, or enhance an existing one?"

### Tier 8 — Production patterns & failure modes

Use this tier to learn from engineers running multi-agent systems with real traffic — what works, what breaks, what they wish they'd known.

- [Latent Space podcast](https://www.latent.space/) — primary AI engineering production source (interviews + technical deep dives)
- [Eugene Yan blog](https://eugeneyan.com/) — applied ML/agents, evaluation
- [Simon Willison's weeknotes](https://simonwillison.net/) — practical LLM engineering, [Agentic Engineering Patterns series](https://simonwillison.net/2026/Feb/23/agentic-engineering-patterns/) (ongoing)
- "Building agents in production" posts on Substack / LinkedIn
- Anthropic case studies + customer stories
- MAST taxonomy & failure-mode literature (UC Berkeley, post-mortems)
- Horror stories from r/AI_Agents (Tier 5)

**Mapping question:** For each failure mode found, ask "could this happen to us? do our agents have the right guardrail?"

### Tier 9 — Cognitive architectures & prompting techniques

Use this tier to improve how **existing agents think** — planning structure, memory, reasoning chains, structured output.

- [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — foundational 7-pattern taxonomy: augmented LLM, prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer, autonomous agents
- Anthropic prompt engineering documentation
- Awesome-prompt-engineering list
- Specific research directions: Plan-and-Solve, ReAct, Tree-of-Thoughts, Self-Consistency, Reflexion, Chain-of-Verification (CoVe), Self-Discover, Memory-augmented agents (MemGPT, A-Mem, generative agents), Voyager (skill library bootstrapping)
- "How I prompt X agent to do Y" posts from experienced prompt engineers

**Mapping question:** For each technique found, ask "which of our 21 agents would benefit, and is the added prompt length / token cost justified?"

### Tier 10 — Competing AI ecosystems (closes the Anthropic-blind spot)

Use this tier to track what OpenAI, Google, Meta, and the open-source community ship. Our framework is Anthropic-first but our users compare us to alternatives — and best ideas often migrate cross-vendor.

**OpenAI:**
- [OpenAI API Changelog](https://developers.openai.com/api/docs/changelog) — model releases, API changes
- [ChatGPT release notes](https://help.openai.com/en/articles/6825453-chatgpt-release-notes)
- [OpenAI Codex changelog](https://developers.openai.com/codex/changelog)
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) (formerly Swarm) — multi-agent orchestration
- OpenAI DevDay announcements

**Google / DeepMind:**
- [Gemini API release notes](https://ai.google.dev/gemini-api/docs/changelog)
- [Google blog AI section](https://blog.google/technology/ai/) — Deep Research, Gemini updates, A2A protocol
- Google Cloud Next AI track

**Open source models / orgs:**
- [Hugging Face trending models](https://huggingface.co/models?sort=trending) — Llama, Mistral, Qwen, DeepSeek
- [Hugging Face Daily Papers](https://huggingface.co/papers) — daily research feed across all vendors
- Meta AI / FAIR releases
- Mistral AI changelog

**Cross-vendor trackers:**
- [llm-stats.com](https://llm-stats.com/) — model leaderboards across vendors
- Aider leaderboards (coding-specific)

**Mapping question:** For each non-Anthropic capability found, ask "is this a competitive must-have we should match, a portable pattern we can adopt, or environment-specific (skip)?"

### Tier 11 — Standards & governance

Use this tier to track protocol roadmaps, standards bodies, and regulatory shifts that affect our framework's compatibility surface.

- [Model Context Protocol blog & roadmap](https://blog.modelcontextprotocol.io/) — official MCP evolution (now governed by Linux Foundation Agentic AI Foundation since Dec 2025)
- [Linux Foundation Agentic AI Foundation](https://www.lfaidata.foundation/) — AAIF announcements, A2A protocol governance
- [A2A protocol releases](https://github.com/google-a2a/A2A) — Agent-to-Agent protocol (donated to LF June 2025, v1.2 in production at 150+ orgs)
- W3C AI activity (slow-moving but worth checking quarterly)
- EU AI Act updates (high-impact for European downstream projects)
- ISO AI standards (long horizon, monitor only)

**Key 2026 milestones to track:**
- Q1 2026: MCP v2.0 (Streamable HTTP + OAuth 2.1)
- Q2 2026: Cross-protocol Interoperability spec draft

**Mapping question:** For each standards change found, ask "does this affect our agent definitions, MCP integrations, or downstream sync? Do we need to update CLAUDE_SKILLS.md / MCP_TOOLS.md?"

### Tier 12 — Autonomous agentic development & agent swarms

Use this tier to monitor **fully autonomous coding agents**, **multi-agent swarms / collaborative orchestration**, and **emergent agent collaboration patterns**. Our framework is curated-workflow style; this tier surfaces alternatives that may inform our evolution.

**Autonomous coding agents (most directly comparable to our Builder/UI Builder):**
- [Cognition Devin](https://cognition.ai/) — fully autonomous coding agent (commercial)
- [OpenHands](https://github.com/All-Hands-AI/OpenHands) (formerly OpenDevin) — open-source autonomous coding
- [SWE-Agent](https://github.com/princeton-nlp/SWE-agent) — academic baseline autonomous coding
- Cursor agent mode releases
- [Sourcegraph Amp](https://sourcegraph.com/amp) — autonomous coding agent
- GitHub Copilot Workspace (autonomous coding mode)
- [Anthropic Computer Use](https://www.anthropic.com/news/3-5-models-and-computer-use) — agent operating a computer

**Multi-agent swarm frameworks:**
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) — handoffs, guardrails, sessions
- [AG2](https://github.com/ag2ai/ag2) (formerly AutoGen) — multi-agent conversations, GroupChat orchestration
- [Microsoft AutoGen](https://github.com/microsoft/autogen) — current Microsoft fork
- [LangGraph hierarchical agents](https://github.com/langchain-ai/langgraph) — supervisor / hierarchical / network topologies
- [LangGraph deepagents](https://github.com/langchain-ai/deepagents) — agent harness with planning + filesystem + subagent spawning
- [CrewAI Flows](https://github.com/crewAIInc/crewAI) — hierarchical and sequential crews
- [Hermes Agent](https://github.com/NousResearch) — reference open-source agent (100k+ stars, 2026)

**Emergent agent collaboration patterns (research):**
- Voyager (Minecraft skill library agent — bootstraps a skill repo over time)
- Generative Agents (Park et al. — Stanford generative agent simulacra, social dynamics)
- Multi-Agent Reflexion (MAR) — reflection across agent pairs
- Agent debate / consensus mechanisms
- Hierarchical orchestration (manager-worker, supervisor-team)
- Mesh / network topologies vs sequential pipelines
- Agent specialization vs generalization trade-off literature

**Mapping question:** For each autonomous or swarm pattern found, ask three things:
1. "Does this validate or challenge our curated-workflow architecture?"
2. "Is there a specific role in our framework where autonomous behavior would help (e.g., Builder doing exploratory bug fixes)?"
3. "Is the collaboration pattern (debate, consensus, hierarchy) something our quality loop should adopt?"

---

## Cadence — when to check each tier

Not every tier needs weekly attention. Match cadence to signal velocity:

| Cadence | Tiers | Why |
|---|---|---|
| **Weekly** (every review) | Tier 1 (Anthropic), Tier 10 (competing ecosystems), Tier 5 newsletters/Reddit, Tier 6 tools | Fast-signal: changelogs, releases, production stories |
| **Bi-weekly** (every 2nd review) | Tier 2 (frameworks), Tier 7 (agent roles), Tier 8 (production patterns), Tier 12 (autonomous & swarms) | Medium signal: framework updates, role inventory grows weekly |
| **Monthly** (1st review of month) | Tier 3 (research), Tier 4 (benchmarks), Tier 9 (cognitive arch), Tier 11 (standards) | Slow signal: papers/benchmarks/protocol changes lag |
| **Quarterly** (1st review of quarter) | Stanford AI Index, State of AI Report, McKinsey reports, EU AI Act milestones | Very slow signal: aggregate industry shifts |

For weekly reviews, prioritize Tier 1 + Tier 10 + Tier 5 every time. Rotate bi-weekly tiers. Hit monthly tiers on the first review of each month. Quarterly on first review of each quarter.

---

## Query quota rules

Each review must allocate queries across tiers with these minimums:

- **At least 1 query in Tier 1** (Anthropic ecosystem) — foundational, weekly
- **At least 1 query in Tier 10** (competing ecosystems) — closes Anthropic-blind spot, weekly
- **At least 2 queries targeting agent-specific tiers** (Tier 2, 7, 8, 9, or 12) — ensures we don't drift into only tooling/cost reviews
- **At least 1 query in Tier 4** (benchmarks) — model performance baseline
- **Monthly bonus:** add 1 query in Tier 11 (standards) on first review of month
- **Quarterly bonus:** add 1 query in industry reports (Stanford Index, State of AI) on first review of quarter

Remaining queries distributed by the review's focus area (if `OPTIONAL_FOCUS` is set) or evenly across the cadence-appropriate tiers.

The review should balance **vendor signal** (Tier 1 + 10), **tooling improvements** (Tier 6, 11), and **agent/workflow improvements** (Tier 2, 7, 8, 9, 12). A review with all 10 queries on caching or observability fails this balance — it means we're over-weighting infrastructure and under-weighting the substance of the agents themselves. Equally, a review with all queries on Anthropic alone fails the competitive check.

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
