# Evolution Log

Append-only log of AI landscape reviews and framework evolution decisions.

Each entry is produced by Discovery in `ai-landscape` mode (typically via `/ai-landscape-review`). The user reviews and decides which proposals to adopt; adopted items get linked here from the implementing commit.

**Maintainer:** Discovery agent appends entries; Iteration Manager links adoption commits.

**Format:** see `agents/discovery-modes/ai-landscape.md` Output format section.

---

## AI Landscape Review — 2026-04-24

**Reviewer:** Discovery (ai-landscape mode)
**Scope:** framework
**Sources scanned:** Tier 1 (Anthropic ecosystem), Tier 2 (agent frameworks), Tier 3 (arXiv research), Tier 4 (SWE-bench), Tier 5 (cost/caching), Tier 6 (observability + MCP registry)
**Time period:** all-time (this is the first review — establishes baseline)

### Summary

Two findings are immediately actionable and cost-saving: **MCP Tool Search lazy-loading** (95% context reduction for MCP servers, already in Claude Code April 2026) and **prompt cache 1-hour TTL** (Anthropic silently changed default to 5 min in early 2026 — explicit 1h TTL on stable prefixes can save 30–60% of API cost). Three medium findings worth evaluating: Skill-Creator for validating our 4 integrated skills, Opus 4.7 `xhigh` effort level for complex agent tasks, and Agent Skills as open standard (now portable to OpenAI Codex/ChatGPT). One major framework decision watching: when **Claude Mythos Preview** (93.9% on SWE-bench Verified) becomes GA, evaluate for Builder/UI Builder.

### Findings — High Priority

#### F1: MCP Tool Search (lazy loading) — 95% context reduction for MCP servers

- **Source:** [Claude Code April 2026 Update](https://daily1bite.com/en/blog/ai-tutorial/claude-code-april-2026-update), [Claude Code Changelog](https://code.claude.com/docs/en/changelog)
- **Maturity:** production (shipped in Claude Code April 2026)
- **What it is:** Claude Code now lazy-loads MCP tool definitions on first @-mention instead of pre-loading at session start. `resources/templates/list` deferred. Reportedly reduces context usage by up to 95% when many MCP servers are configured.
- **Impact on us:** HIGH — we have 3 MCP servers (gsap-master, rive-mcp, nanobanana). At session start they currently pre-load tool definitions even when not used. Lazy loading means agents that don't need them save ~thousands of tokens per session.
- **Adoption confidence:** HIGH — official Anthropic feature, no opt-in needed.
- **Effort:** SMALL — likely zero work; verify Claude Code version is recent enough. Update `docs/MCP_TOOLS.md` to mention this benefit.
- **Proposal:** Verify behaviour with our 3 MCP servers (sample a session, check token counts before vs after first @-mention). Document in MCP_TOOLS.md.
- **Risk & rollback:** None — this is a Claude Code-side optimization. Reverting requires no framework change.
- **Decision needed:** Yes — should we add a section to MCP_TOOLS.md describing the benefit and mentioning that lazy-loading is automatic in recent Claude Code?

#### F2: Prompt cache TTL change (5 min default, 1h available) — 30–60% cost lever

- **Source:** [Claude Prompt Caching in 2026](https://dev.to/whoffagents/claude-prompt-caching-in-2026-the-5-minute-ttl-change-thats-costing-you-money-4363), [Anthropic Pricing Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- **Maturity:** production
- **What it is:** Anthropic silently lowered default cache TTL from 60 min to 5 min in early 2026. The 1-hour option still exists (2x write cost, pays back after 2 reads). For long-running agent workflows that re-read stable system prompts, default 5-min may have caused 30–60% effective cost increase.
- **Impact on us:** HIGH — current 30d framework cost is $295.94. If even 30% of that is unnecessary cache misses on 5-min TTL, that's ~$90/month of pure waste. Our agent system has very stable prompts (agents/*.md, AGENTS.md) that are perfect 1h cache candidates.
- **Adoption confidence:** HIGH — Anthropic-documented behavior, multiple confirmation sources.
- **Effort:** MEDIUM — caching is controlled by Claude Code, not directly by us. Need to verify whether Claude Code already requests 1h TTL on stable prompts; if not, this requires either (a) Claude Code config change, (b) feature request to Anthropic, or (c) custom integration via direct API.
- **Proposal:** First, instrument cost telemetry per session to see actual cache_read vs cache_write ratio. If ratio is low (lots of writes, few reads), that confirms 5-min TTL is hurting us. Then either configure Claude Code if there's an option, or document the lesson in `docs/LESSONS_LEARNED.md` for downstream awareness.
- **Risk & rollback:** None for the audit step. Configuration changes are reversible.
- **Decision needed:** Yes — should I extend `metrics_workflow.py` to compute cache hit ratio (cache_read / cache_write) per session? It would give us evidence for or against this finding before any change.

#### F3: Opus 4.7 with `xhigh` effort level

- **Source:** [Claude Weekly: Opus 4.7 Lands](https://www.bighatgroup.com/blog/claude-weekly-2026-04-23/), Claude Code April 2026 update
- **Maturity:** production (just released April 2026)
- **What it is:** New model Opus 4.7 + new effort level `xhigh` (between `high` and `max`). Available via `/effort xhigh`, `--effort xhigh`, or model picker.
- **Impact on us:** MEDIUM — Opus 4.7 + `xhigh` likely produces better Architect plans, Spec Reviewer audits, and complex Builder code. Cost trade-off: higher effort = more tokens per response.
- **Adoption confidence:** MEDIUM — Opus 4.7 SWE-bench Verified score is 87.6% (vs 93.9% for Mythos Preview). Real-world agent work likely benefits but needs validation.
- **Effort:** SMALL — recommend `xhigh` for specific agents in their definitions (Architect, Spec Reviewer); leave `high` or default for routine work (UX Writer, Marketing).
- **Proposal:** Add a "Recommended effort level" hint to heavy agent files (Architect, Spec Reviewer, Security Reviewer). Per-agent effort selection isn't enforced by Claude Code, but documented recommendations help users.
- **Risk & rollback:** Higher cost on those agents. Easy to revert by removing recommendation.
- **Decision needed:** Yes — should we annotate Architect, Spec Reviewer, and Security Reviewer with `Recommended effort: xhigh` notes?

#### F4: Claude Mythos Preview — 93.9% SWE-bench Verified (top of leaderboard)

- **Source:** [SWE-Bench Verified Leaderboard](https://llm-stats.com/benchmarks/swe-bench-verified)
- **Maturity:** preview — not GA
- **What it is:** New Anthropic model "Mythos Preview" tops SWE-bench Verified at 93.9%, ahead of Opus 4.7 (87.6%) and GPT-5.3 Codex (85%).
- **Impact on us:** HIGH (when GA) — for Builder/UI Builder agents, swap to Mythos when available. Could materially improve first-pass code quality and reduce Builder cycles.
- **Adoption confidence:** MEDIUM — preview status, may have rate limits or different cost structure.
- **Effort:** SMALL — model swap.
- **Proposal:** **Monitor only** for now. Set a reminder for next AI landscape review (next Monday) to check GA status. Once GA: evaluate cost/quality trade-off for Builder agents specifically.
- **Risk & rollback:** None until GA.
- **Decision needed:** No action now. Tag for next review.

#### F5: MCP scope doctor + 500K result size override

- **Source:** Claude Code April 2026 changelog
- **Maturity:** production
- **What it is:** `/doctor` now warns when MCP server is defined in multiple config scopes with different endpoints. Plus, `_meta["anthropic/maxResultSizeChars"]` annotation lets MCP tools return larger results (up to 500K chars) without truncation — useful for DB schemas, large file dumps.
- **Impact on us:** MEDIUM — we have nanobanana installed at user scope earlier with conflicting configs (we removed and re-added). `/doctor` would have caught that automatically. The 500K override doesn't apply to our current MCP tools but useful documentation.
- **Adoption confidence:** HIGH
- **Effort:** SMALL — run `/doctor`, document in MCP_TOOLS.md.
- **Proposal:** Add a "Troubleshooting" section to `docs/MCP_TOOLS.md` that includes "Run `/doctor` to detect MCP scope conflicts" and "Use `_meta` annotation for tools that return large payloads".
- **Risk & rollback:** None — documentation only.
- **Decision needed:** Yes — add MCP_TOOLS.md troubleshooting section?

### Findings — Medium Priority

#### F6: Skill-Creator for measuring our 4 integrated skills

- **Source:** [Skill-Creator article](https://medium.com/ai-software-engineer/anthropic-new-skill-creator-measures-if-your-agent-skills-work-no-more-guesswork-840a108e505f), [Anthropic skills repo](https://github.com/anthropics/skills)
- **What it is:** Anthropic's testing framework for evaluating whether agent skills actually work — eval-driven skill development.
- **Impact on us:** MEDIUM — we integrated 4 design skills (accessibility-review, user-research, research-synthesis, design-handoff) but haven't validated they materially improve agent output vs built-in fallback. Skill-Creator could give us hard data.
- **Effort:** MEDIUM — install plugin, write evals for each skill, run benchmarks.
- **Proposal:** Run skill-creator on accessibility-review first (most critical). If it shows clear improvement over fallback → keep integration. If not → simplify.
- **Decision needed:** Yes — install skill-creator and benchmark our 4 skills?

#### F7: Agent Skills as open standard — portability beyond Claude Code

- **Source:** [Anthropic Explosive Start to 2026](https://fazal-sec.medium.com/anthropics-explosive-start-to-2026-everything-claude-has-launched-and-why-it-s-shaking-up-the-668788c2c9de) (Dec 2025: open standard, OpenAI adopted same format for Codex CLI + ChatGPT)
- **What it is:** Skill format standardized; same `.md` files work in OpenAI Codex CLI and ChatGPT as well as Claude Code.
- **Impact on us:** MEDIUM — strengthens our backward-compatibility story in `docs/CLAUDE_SKILLS.md`. Same skill integrations work for users on OpenAI tools too. Worth one-line documentation update.
- **Effort:** SMALL — doc update.
- **Proposal:** Update CLAUDE_SKILLS.md compatibility matrix to reflect that skills now also work in OpenAI Codex CLI / ChatGPT.
- **Decision needed:** Yes — update CLAUDE_SKILLS.md compatibility matrix?

#### F8: MCPWatch — security scanner for MCP servers

- **Source:** [MCP roadmap article](https://thenewstack.io/model-context-protocol-roadmap-2026/) and MCP ecosystem
- **What it is:** Security scanner that detects vulnerabilities in MCP server implementations (auth bypass, injection, secrets exposure).
- **Impact on us:** MEDIUM — we use third-party MCP servers (rive-mcp, gsap-master, nanobanana) without auditing them. MCPWatch could catch supply-chain risks.
- **Effort:** SMALL — run scanner once.
- **Proposal:** Run MCPWatch on our 3 MCP servers. Document findings (if any) in LESSONS_LEARNED.md.
- **Decision needed:** Yes — run MCPWatch and report?

#### F9: Langfuse open-source observability

- **Source:** [LLM Observability comparison](https://www.firecrawl.dev/blog/best-llm-observability-tools)
- **What it is:** Most adopted open-source LLM observability platform, MIT-licensed, self-hostable. Tracing + prompt management + evaluation.
- **Impact on us:** MEDIUM — our Phase 2 metrics cover basic cost + workflow telemetry from Claude Code transcripts. Langfuse would add real-time tracing, prompt versioning, and dashboards. Probably overkill until we hit >10 active projects.
- **Effort:** LARGE — significant integration work, requires self-hosting or cloud account.
- **Proposal:** **Monitor only** — re-evaluate when active downstreams >10 or when Phase 2 metrics prove insufficient.
- **Decision needed:** No — defer.

### Findings — Monitor (low priority / immature)

- **F10:** [Self-Revising Agent paper](https://arxiv.org/abs/2604.07236) — externalizes agent state into inspectable runtime structure. Interesting concept; our `workflow_state` in handoff blocks already covers similar ground but less rigorously. **Defer** — academic, no production library.
- **F11:** [MAR: Multi-Agent Reflexion](https://arxiv.org/html/2512.20845) — multi-agent reflection improves reasoning. Our quality loop (Spec Reviewer + Reviser) is comparable. **Defer** — incremental gains, not a structural change.
- **F12:** [10,000+ MCP servers across registries](https://registry.modelcontextprotocol.io/) — ecosystem signal. Worth periodic browsing during landscape reviews for domain-specific tools. **No immediate action.**
- **F13:** [SWE-Bench Pro](https://labs.scale.com/leaderboard/swe_bench_pro_public) — much harder benchmark (top scores ~46%). Useful for measuring real model upgrades, since SWE-Bench Verified is saturating. **Use as reference** when comparing future model options.
- **F14:** [LangGraph deep MCP integration](https://www.datacamp.com/tutorial/crewai-vs-langgraph-vs-autogen) — alternative agent framework with MCP-native nodes. Our framework is simpler and Claude-specific. **No action** — different design philosophy.

### Decisions Required from User

| # | Question | Recommended default |
|---|---|---|
| 1 | F1: Add MCP Tool Search benefit note to docs/MCP_TOOLS.md? | yes (small effort, useful) |
| 2 | F2: Extend `metrics_workflow.py` to compute cache hit ratio? | yes (concrete cost evidence) |
| 3 | F3: Add `Recommended effort: xhigh` notes to Architect/Spec Reviewer/Security Reviewer? | yes (no enforcement, just guidance) |
| 4 | F4: Mark Claude Mythos Preview for next-week recheck? | yes (just a reminder) |
| 5 | F5: Add MCP_TOOLS.md troubleshooting section (`/doctor`, 500K override)? | yes (small effort) |
| 6 | F6: Install Skill-Creator and benchmark our 4 integrated skills? | maybe — only if we suspect they're not helping |
| 7 | F7: Update CLAUDE_SKILLS.md compatibility matrix (Codex CLI / ChatGPT)? | yes (one-line update) |
| 8 | F8: Run MCPWatch on our 3 MCP servers? | yes (security hygiene) |
| 9 | F9: Adopt Langfuse for observability? | defer (overkill for current scale) |

### Comparison to prior reviews

This is the first review. No prior decisions to compare against. From this point onward, future reviews will check whether items deferred or accepted here changed status.

### Notes

**Trends to watch:**
- **Lazy loading is the new default** — MCP Tool Search reduced context by 95% in Claude Code; expect similar lazy patterns in agent skills, plugins, and eventually agent definitions themselves. Our framework already follows this with "Required reading" + "Optional reading" pattern (KNOWN_PATTERNS.md), so we're well-positioned.
- **Cost is becoming a first-class concern** — multiple sources discussing TTL changes, cache strategies, model tiering. Our `/metrics` command tracks cost which is correct direction; needs cache-hit ratio to be fully useful.
- **Benchmark saturation** — SWE-Bench Verified is approaching ceiling (top model 93.9%, human ceiling ~95%). The interesting frontier is moving to harder benchmarks (SWE-Bench Pro, multi-step reasoning) and to agent-specific evaluation rather than per-task scores.
- **Open standards winning** — Agent Skills format, MCP protocol both became cross-vendor standards. Our framework's design (markdown agent files, MCP tools, optional skills) aligns with this trajectory.

---

## Adoption Notes — 2026-04-24 (same-day implementation)

Decisions executed within hours of the review:

- **F1 ✅ adopted** — Added "MCP Tool Search (lazy loading)" section to `docs/MCP_TOOLS.md`. No agent changes needed; benefit is automatic in Claude Code.
- **F2 ⚠ debunked by data** — Extended `metrics_workflow.py` with `_cache_ratios()` computing `cache_hit_ratio`, `cache_coverage`, `cache_write_cost_estimate_usd`, and a `health` enum (`efficient`/`mixed`/`poor`). First snapshot showed **98% hit ratio across all projects (efficient ✓)**, 100% cache coverage of input. The 5-min TTL concern from the review **does not apply to our workflow** — Claude Code already efficiently caches our stable agent prompts. Saved $~63/month estimated cache write cost is the price for routing 98% of input through cheap reads. Net: caching is a clear win for us. Keep monitoring; revisit if hit ratio drops below 70%.
- **F3 ✅ adopted** — Added "Recommended thinking effort" sections to `agents/architect.md`, `agents/spec-reviewer.md`, `agents/security-reviewer.md` recommending `xhigh` effort for complex tasks. Optional, gracefully falls back to `high`.
- **F4 ✅ scheduled** — Mythos Preview GA status will be re-checked on next Monday's review (cron e948bfb3 fires 2026-04-27 10:08 + persistent launchd at same time).
- **F5 ✅ adopted** — Added "Performance notes" + "Troubleshooting" sections to `docs/MCP_TOOLS.md` covering lazy loading, 500K result override, `/doctor`, common server failures, security audit step.
- **F6 deferred** — Skill-Creator benchmark requires deliberate experiment. Postponing until we have a workflow where one of the 4 integrated skills clearly underperforms.
- **F7 ✅ adopted** — Updated `docs/CLAUDE_SKILLS.md` compatibility matrix to reflect Agent Skills as open standard (Dec 2025) — same skill files now work in OpenAI Codex CLI and ChatGPT.
- **F8 ⏸ blocked on tooling** — `npx mcpwatch` returned 404 from npm. The tool exists per articles but the npm package name differs or is not yet published. Deferred until package availability confirmed. Manual MCP server review still recommended (read source of `@rive-mcp/server-core`, `bruzethegreat-gsap-master-mcp-server`, `@ycse/nanobanana-mcp` before relying on them with sensitive data).
- **F9 ⏸ defer confirmed** — Langfuse remains overkill at our scale (6 active projects, $295/mo).

**Net effect on framework:** 4 docs updated, 3 agents annotated, 1 metric added. Zero quality regression — all changes either documentation, optional hints, or read-only metric tooling. Cost analysis (F2) revealed no waste; framework's caching efficiency validated by data.

---

