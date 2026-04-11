# Discovery: OmniRoute Integration for Tool-Agents

**Date:** 2026-03-29
**Mode:** Technical Discovery
**Status:** Completed — awaiting Architect

---

## Discovery Question

How should OmniRoute be integrated into the agent system for tool-agents (Illustrator, Discovery research, future voice/video agents) without degrading the core agent workflow quality?

## Prior Decisions

- **DEC-011:** Illustrator as a tool-agent with MCP integration (Nano Banana 2 via `@ycse/nanobanana-mcp`)
- **DEC-012:** OmniRoute researched and deferred; contains planned integrations (Perplexity, multi-model translation, fallback chains)

## Context

Currently each tool-agent requires a separate MCP server in `.cursor/mcp.json`. As tool-agents grow (Illustrator, Discovery+Perplexity, future voice/transcription/video), this leads to: config sprawl, duplicated key management, no fallback between providers, no unified monitoring. OmniRoute can serve as a unified layer for all external models.

---

## Options Considered

1. **OmniRoute as sole proxy for tool-agents** — all external models via `localhost:20128/v1`
2. **Hybrid: OmniRoute + standalone MCP servers** — OmniRoute for multi-provider (search, image, audio), native MCP for single-provider (Perplexity deep research)
3. **Standalone MCP servers only (status quo)** — one MCP per tool-agent

---

## Comparison

### Option 1 — OmniRoute as sole proxy

**API coverage:**

| Tool-agent need | OmniRoute endpoint | Providers |
|---|---|---|
| Image generation (Illustrator) | `POST /v1/images/generations` | Nano Banana, DALL-E, FLUX, xAI, Together, Fireworks + 4 others |
| Web search (Discovery) | `POST /v1/search` | Perplexity, Brave, Serper, Exa, Tavily (6500+ free/month) |
| Audio transcription (Voxema) | `POST /v1/audio/transcriptions` | Deepgram ($200 free), AssemblyAI ($50 free), Groq Whisper, 4 others |
| Text-to-Speech (future) | `POST /v1/audio/speech` | ElevenLabs, OpenAI, Deepgram, Cartesia, PlayHT + 5 others |
| Chat completions (translation) | `POST /v1/chat/completions` | 67+ providers with auto-fallback |

- **Pros:**
  - Single endpoint for all tool-agents
  - Unified key management (OmniRoute dashboard)
  - Automatic provider fallback (Nano Banana down → FLUX → DALL-E)
  - Built-in cost tracking and analytics
  - Free web search (6500+ requests/month) for Discovery research
  - Circuit breaker prevents cascading failures
  - Semantic cache reduces cost for repeated requests
  - Future tool-agents need no new MCP — just provider config in OmniRoute
- **Cons:**
  - Additional process (Node.js) to run
  - +50-100ms latency per request (proxy overhead)
  - Perplexity via OmniRoute `/v1/search` is simpler than native MCP — lacks `sonar-deep-research` and `sonar-reasoning-pro` (basic search only)
  - OmniRoute doesn't ship as a Cursor MCP server for image gen — needs custom MCP wrapper or direct HTTP calls
- **Dependency friendliness:** Node.js 18+, npm global install. Well maintained (1.6k stars, 1316 commits, active development)
- **Implementation simplicity:** Medium. Need to: install OmniRoute, configure providers, write thin MCP wrapper for Cursor REST API calls
- **Operational simplicity:** Medium — one more process, but replaces N separate MCP servers
- **Value-to-complexity:** High — set up once, covers all current and future tool-agents
- **Reversibility:** Easy — proxy is transparent, can revert to standalone MCP anytime
- **Pipeline fit:** Fits cleanly — tool-agents are already isolated from the main workflow
- **MVP fit:** Good — covers Illustrator and Discovery research immediately
- **Long-term fit:** Strong — scales to voice, video, transcription without new MCP servers

### Option 2 — Hybrid: OmniRoute + standalone MCP

- **Pros:**
  - OmniRoute for multi-provider endpoints (images, search, audio)
  - Native Perplexity MCP (`@perplexity-ai/mcp-server`) provides `sonar-deep-research` and `sonar-reasoning-pro` — significantly more powerful than OmniRoute `/v1/search`
  - 4 Perplexity MCP tools: `perplexity_search`, `perplexity_ask`, `perplexity_research`, `perplexity_reason`
  - Each component can be enabled/disabled independently
- **Cons:**
  - Two approaches to external models — complexity
  - Must manage both OmniRoute and standalone MCP servers
  - No unified fallback for Perplexity (if it goes down, no replacement)
- **Dependency friendliness:** OmniRoute (npm) + Perplexity MCP (npm). Both well maintained
- **Implementation simplicity:** Medium. OmniRoute for bulk, Perplexity MCP for deep research
- **Operational simplicity:** Medium-low — two integration types
- **Value-to-complexity:** Medium — more capabilities but more complex
- **Reversibility:** Easy
- **Pipeline fit:** Fits cleanly
- **MVP fit:** Good
- **Long-term fit:** Good — but dual approach creates cognitive overhead

### Option 3 — Standalone MCP servers only (status quo)

- **Pros:**
  - Already works (Illustrator + Nano Banana MCP)
  - Zero new infrastructure
  - Direct Cursor ↔ MCP connection, minimal latency
  - Perplexity MCP provides full toolset
- **Cons:**
  - Each new tool-agent = new MCP server in `.cursor/mcp.json`
  - No fallback between providers (Nano Banana down = Illustrator broken)
  - No unified monitoring, cost tracking, analytics
  - At 5+ tool-agents, config becomes unwieldy
  - No web search fallback (Perplexity down = Discovery without data)
- **Dependency friendliness:** One npm package per tool-agent
- **Implementation simplicity:** High for each individual, Low for the system overall
- **Operational simplicity:** Low at scale
- **Value-to-complexity:** High now, Low as system grows
- **Reversibility:** Easy
- **Pipeline fit:** Fits cleanly
- **MVP fit:** Already implemented
- **Long-term fit:** Weak — doesn't scale

---

## Decision Quality Score

| Criterion | Option 1 (OmniRoute only) | Option 2 (Hybrid) | Option 3 (MCP only) |
|---|---|---|---|
| MVP fit | 4 | 4 | 5 |
| Architecture fit | 4 | 4 | 3 |
| Implementation simplicity | 3 | 3 | 4 |
| Reversibility | 5 | 4 | 5 |
| Dependency friendliness | 4 | 3 | 4 |
| Operational simplicity | 4 | 3 | 2 |
| Testability | 4 | 3 | 4 |
| Long-term fit | 5 | 4 | 2 |
| **Total** | **33** | **28** | **29** |

---

## Decision Stability

Revisit after MVP — start with hybrid, migrate to OmniRoute-only when Perplexity deep research becomes available through OmniRoute or when 3+ tool-agents are active.

## Recommendation

**Option 2 (Hybrid)** with a clear migration path to Option 1.

Why not Option 1 immediately: native Perplexity MCP provides `sonar-deep-research` and `sonar-reasoning-pro` — significantly more powerful than OmniRoute `/v1/search`. For Discovery research this is critical.

Why not Option 3: Illustrator already benefits from OmniRoute (fallback Nano Banana → FLUX → DALL-E), and free web search for Discovery is immediate value.

**Target configuration:**

```
.cursor/mcp.json (downstream project):
├── OmniRoute proxy (localhost:20128)  → images, audio, search, chat
└── Perplexity MCP (native)            → deep research, reasoning
```

## Why This Is the Simplest Viable Choice

Hybrid adds OmniRoute only for what it does better (multi-provider image/audio/search with fallback) and preserves native MCP where it provides unique capabilities (Perplexity deep research). Neither interferes with the other — both work through `.cursor/mcp.json`.

---

## Risks / Trade-offs

- OmniRoute is an additional process. If forgotten, tool-agents break. Mitigation: document in `docs/MCP_TOOLS.md`, add check to `audit.py`
- Perplexity API costs $6-14/1000 requests (sonar-pro). For Discovery research this is acceptable (tens of requests per research, not thousands)
- Latency: +50-100ms through OmniRoute. For image generation (seconds) and search (hundreds of ms) — negligible
- **Critical guardrail:** Claude for agent workflow NEVER goes through OmniRoute. Only tool-agents and data-agents

## Follow-up Implications

1. Update `docs/MCP_TOOLS.md` — add OmniRoute configuration and Perplexity MCP
2. Update `agents/illustrator.md` — Illustrator switches from direct MCP to OmniRoute endpoint
3. Update Discovery modes (technical, market, legal) — add Perplexity tools
4. Create startup script or documentation for running OmniRoute in downstream projects
5. Add OmniRoute health check to `audit.py`
6. Update DEC-012 → accept with guardrails

## Should This Go Into DECISIONS.md?

Yes — update DEC-012 from "deferred" to "accepted" with guardrails and concrete plan.

## Assumptions Made

- OmniRoute `/v1/images/generations` supports Nano Banana 2 (confirmed from README — "10 providers and 20+ models" including NanoBanana)
- Perplexity MCP server is stable (v0.9.0, official from Perplexity)
- OmniRoute can be called from Cursor via custom MCP wrapper or Illustrator agent extension for HTTP calls

## Recommended Next Step

Architect: plan phased integration — (1) install OmniRoute + Perplexity MCP in Unfolda, (2) update Illustrator for OmniRoute, (3) update Discovery modes for Perplexity tools.

---

## Perplexity API Reference

**Pricing (March 2026):**

| Model | Input | Output | Per 1K requests | Best for |
|---|---|---|---|---|
| sonar | $1/1M | $1/1M | $5 | Quick search |
| sonar-pro | $3/1M | $15/1M | $6-14 | Complex queries |
| sonar-deep-research | $2/1M | $8/1M | $5 | Exhaustive multi-source research |
| sonar-reasoning-pro | $2/1M | $8/1M | $5 | Advanced reasoning with search |

**MCP tools (via `@perplexity-ai/mcp-server` v0.9.0):**

| Tool | Model | Use case |
|---|---|---|
| `perplexity_search` | sonar | Direct web search with ranked results |
| `perplexity_ask` | sonar-pro | Conversational AI with search |
| `perplexity_research` | sonar-deep-research | Deep research across hundreds of sources |
| `perplexity_reason` | sonar-reasoning-pro | Advanced reasoning with web data |

**Cursor configuration:**

```json
{
  "mcpServers": {
    "perplexity": {
      "command": "npx",
      "args": ["-y", "@perplexity-ai/mcp-server"],
      "env": {
        "PERPLEXITY_API_KEY": "<your-key>"
      }
    }
  }
}
```

---

## OmniRoute Reference

**Version:** v3.4.1 (March 2026)
**License:** MIT
**Install:** `npm install -g omniroute && omniroute`
**Docker:** `diegosouzapw/omniroute:latest`
**Local endpoint:** `http://localhost:20128/v1`
**Dashboard:** `http://localhost:20128`

**Key endpoints for tool-agents:**

| Endpoint | Capability | Providers |
|---|---|---|
| `POST /v1/images/generations` | Image generation | 10+ providers, 20+ models |
| `POST /v1/search` | Web search | 5 providers, 6500+ free/month |
| `POST /v1/audio/transcriptions` | Audio transcription | 7 providers |
| `POST /v1/audio/speech` | Text-to-speech | 10 providers |
| `POST /v1/chat/completions` | Chat/translation | 67+ providers |
| `POST /v1/embeddings` | Embeddings | 6 providers |
