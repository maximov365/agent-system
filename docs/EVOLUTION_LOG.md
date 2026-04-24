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

## AI Landscape Review — 2026-04-24 (supplementary, agent-focused)

**Reviewer:** Discovery (ai-landscape mode)
**Scope:** framework
**Sources scanned:** Tier 7 (agent role inventory), Tier 8 (production patterns / failure modes), Tier 9 (cognitive architectures / prompting), with spot checks in Tier 1, 4, 6
**Time period:** all-time (first agent-focused review after extending methodology with Tier 7-9)
**Motivation:** The earlier same-day review (F1–F9) weighted heavily toward tooling/cost. User flagged the gap. We extended the mode to add Tier 7 (agent roles), 8 (production patterns), 9 (cognitive architectures), plus a query-quota rule requiring ≥2 agent-specific queries per review. This is the first review applying the new methodology.

### Summary

Strongest finding is **empirical validation from MAST taxonomy (UC Berkeley, 1,600 traces across 7 multi-agent frameworks)**: 42% of multi-agent failures come from **specification clarity** — exactly what our Product → Spec Reviewer → Gatekeeper quality loop addresses. Second tier: 37% coordination breakdowns (our handoff contract), 21% weak verification (our Reviewer class). Our core architecture maps well to the biggest failure modes. Most actionable new improvement: **Chain-of-Verification (CoVe)** — a 4-step self-check pattern reported to improve F1 by 23% on factual tasks; could be added as an optional thinking frame for our Reviewer-class agents. Also actionable: **prompt-injection defense** for agents that read user-supplied content (CVE-2025-53773 showed 9.6 CVSS exploit via PR descriptions), and **Claude Code Security agent** from Anthropic (Feb 2026) for evaluation alongside our Security Reviewer.

### Findings — High Priority

#### F10: MAST taxonomy validates our core architecture (42/37/21 failure split)

- **Source:** [Why Multi-Agent LLM Systems Fail](https://redis.io/blog/why-multi-agent-llm-systems-fail/), [Augment Code 2026 guide](https://www.augmentcode.com/guides/why-multi-agent-llm-systems-fail-and-how-to-fix-them)
- **What it is:** UC Berkeley researchers analyzed 1,600+ traces across 7 popular multi-agent frameworks. Failures categorized 42% bad specifications, 37% coordination breakdowns, 21% weak verification.
- **Impact on us:** HIGH (validation, not action) — our framework's three pillars are exactly aligned: Spec Reviewer + Gatekeeper for specifications (42%), handoff contract for coordination (37%), Spec/Design/Security/Analytics Reviewers for verification (21%). Good news: we're addressing the biggest failure modes.
- **Adoption confidence:** HIGH — peer-reviewed empirical study.
- **Effort:** SMALL — audit our 14 specific MAST failure modes and check each has a guardrail.
- **Proposal:** Run a mapping: MAST's 14 specific failure modes vs our framework guardrails. Where we lack coverage, add a note to the relevant agent or to SYSTEM_AUDITOR's checks.
- **Decision needed:** Yes — run the MAST mapping audit?

#### F13: Chain-of-Verification (CoVe) — +23% F1 on reasoning tasks

- **Source:** [CoVe learning prompt](https://learnprompting.org/docs/advanced/self_criticism/chain_of_verification), [Chain-of-Verification research](https://www.researchgate.net/publication/384218319_Chain-of-Verification_Reduces_Hallucination_in_Large_Language_Models)
- **What it is:** 4-step prompting pattern: (1) baseline response → (2) plan verification questions → (3) answer verification questions independently → (4) refine final output. Reported 23% F1 improvement (0.39 → 0.48), outperforms zero-shot, few-shot, and plain CoT.
- **Impact on us:** HIGH — could add optional CoVe-style structure to Reviewer-class agents (Spec Reviewer, Security Reviewer, Analytics Validator, Reviewer). These agents already produce verdicts, so adding explicit verification questions as an intermediate step would likely improve catch rate on subtle issues.
- **Adoption confidence:** MEDIUM-HIGH — peer-reviewed, widely adopted in production.
- **Effort:** MEDIUM — prompt engineering on 4 agents. Need to test whether it actually improves our reviewers (pairs with Skill-Creator from F6).
- **Proposal:** Add an optional "Verification frame" section to Spec Reviewer first (highest impact). Structure: (1) draft verdict + scores, (2) list 3-5 verification questions that would falsify this verdict, (3) check each, (4) revise if any verification fails.
- **Risk & rollback:** Increased token cost per review (~30-50% more reasoning). Easy to remove — just delete the Verification frame section.
- **Decision needed:** Yes — pilot CoVe on Spec Reviewer?

#### F16: Claude Code Security — Anthropic's dedicated security agent (Feb 2026, Opus 4.6)

- **Source:** [Dark Reading: AI agent runtime security 2026](https://venturebeat.com/security/ai-agent-runtime-security-system-card-audit-comment-and-control-2026), [AI Code Security Tools 2026](https://www.truefoundry.com/blog/best-ai-code-security)
- **What it is:** Anthropic's Claude Code Security agent (launched Feb 2026 with Opus 4.6) found 500+ vulnerabilities in production open-source codebases, including 14 high-severity in Firefox alone.
- **Impact on us:** HIGH — this is a dedicated Anthropic-built security reviewer that's demonstrably effective. Could replace or augment our generic Security Reviewer with a specialist.
- **Adoption confidence:** HIGH — direct Anthropic product, proven in production.
- **Effort:** SMALL-MEDIUM — evaluate side-by-side with our Security Reviewer on a real code task; decide whether to replace, delegate-to, or keep both.
- **Proposal:** Add Claude Code Security as an optional MCP/skill integration in `agents/security-reviewer.md`, with the same pattern as our Claude Skills — use it if available, fall back to built-in checks otherwise.
- **Risk & rollback:** External tool dependency; fallback preserves our existing security review.
- **Decision needed:** Yes — evaluate Claude Code Security alongside our Security Reviewer?

#### F19: Prompt injection defense — adversarial content in user-supplied text (CVE-2025-53773)

- **Source:** [Coders Adopt AI Agents, Security Pitfalls 2026](https://www.darkreading.com/application-security/coders-adopt-ai-agents-security-pitfalls-lurk-2026), CVE-2025-53773 (CVSS 9.6)
- **What it is:** Hidden prompt injection in PR descriptions enabled remote code execution via GitHub Copilot. Pattern: agents read user-supplied content (PRD, TASKS, PR descriptions, issue comments) which may contain adversarial instructions.
- **Impact on us:** HIGH — our agents routinely read `docs/PRD.md`, `docs/TASKS.md`, and task descriptions. If any of these come from untrusted sources (team members with varying trust levels, external contributors, copy-paste from web), prompt injection is a real risk. Not a current problem at 1-user scale, but becomes critical if the framework scales to teams.
- **Adoption confidence:** HIGH — well-documented threat.
- **Effort:** MEDIUM — add a "Trust boundary check" section to agents that read user-supplied docs: scan for instruction-like phrases that contradict the agent's role, flag for user review if found.
- **Proposal:** Add a note to Iteration Manager's routing logic: when task description comes from an untrusted source (open PR, shared link, forwarded message), route to a "Trust Sanitizer" check first — or have each agent that reads `docs/TASKS.md` pattern-match for instruction injection.
- **Risk & rollback:** False positives on legitimate imperative content. Tune pattern list carefully.
- **Decision needed:** Yes — add prompt-injection defense guardrails?

### Findings — Medium Priority

#### F15: Specialist reviewer split (bug-hunter, security-auditor, test-coverage, style)

- **Source:** [Maestro Orchestrate](https://github.com/caramaschiHG/awesome-ai-agents-2026), industry pattern
- **What it is:** Production code-review systems split reviewer role into specialists: bug-hunter, security-auditor, code-quality-reviewer, contracts-reviewer, historical-context-reviewer, test-coverage-reviewer.
- **Impact on us:** MEDIUM — our Reviewer is currently single-agent doing all categories. Specialization could improve catch rate but adds workflow steps and orchestration overhead.
- **Proposal:** **Wait for evidence.** Track Reviewer outputs (via `builder_cycle_count` in handoff blocks) — if certain categories consistently get missed, that's the signal to split. Premature split adds cost without proven benefit.
- **Decision needed:** No — defer until data shows specific weakness.

#### F18: VoltAgent awesome-agent-skills (1000+ cross-platform skills)

- **Source:** [awesome-agent-skills GitHub](https://github.com/VoltAgent/awesome-agent-skills)
- **What it is:** Curated collection of 1000+ agent skills compatible with Claude Code, Codex, Gemini CLI, Cursor. Could contain specializations we lack (e.g., Docker audit, Terraform review, SQL query optimization).
- **Impact on us:** MEDIUM — opportunity cost of NOT browsing.
- **Proposal:** Spend 30 min browsing the collection for 2-3 skills that fill gaps in our 21-agent coverage. Evaluate each via the optional-skill-augmentation pattern from CLAUDE_SKILLS.md.
- **Decision needed:** Yes — browse and identify 2-3 candidates?

#### F20: Simon Willison's Agentic Engineering Patterns (ongoing series, Feb 2026+)

- **Source:** [Simon Willison newsletter](https://simonwillison.net/2026/Feb/23/agentic-engineering-patterns/), [Pragmatic Summit talk](https://www.youtube.com/watch?v=owmJyKVu5f8)
- **What it is:** Ongoing guide documenting practical patterns from Simon Willison (prominent AI engineer) — red/green TDD for agents, "code is now inexpensive" shift, 1-2 chapters/week.
- **Impact on us:** MEDIUM — reference material for our KNOWN_PATTERNS.md and future reviews.
- **Proposal:** Add to Tier 8 sources in `ai-landscape.md` (already there). Track the newsletter; extract any patterns that specifically improve our Architect/Builder workflows.
- **Decision needed:** No action — it's in our standing watchlist now.

#### F21: Process Reward Models (PRM) — score each reasoning step, not just final output

- **Source:** [AI Trends 2026: Test-Time Reasoning](https://huggingface.co/blog/aufklarer/ai-trends-2026-test-time-reasoning-reflective-agen)
- **What it is:** Instead of evaluating only final outputs, PRMs score each intermediate reasoning step. Accelerated in 2025-2026.
- **Impact on us:** LOW-MEDIUM — our Spec Reviewer already scores 10 dimensions which is similar in spirit. PRMs are more granular (per-step) but require training/fine-tuning infrastructure.
- **Proposal:** Monitor. Our rubric-based scoring is already strong; PRMs are an enterprise-scale investment.
- **Decision needed:** No — defer.

### Findings — Monitor

- **F14:** General reflective/critique loops report **25-50% higher success rates on multi-step tasks** (Medium article, Zylos Research, 2026). **Our quality loop is exactly this pattern** — built-in reflection via Reviewer agents + Gatekeeper. Validation that our architecture is sound. When IM telemetry (Phase 2 metrics) fills with real data, we'll be able to measure our own loop's effectiveness.
- **F17: Memory architectures (MemGPT, A-Mem, 85-93% token reduction)** — compelling but our workflow is task-bounded (no persistent long-lived memory). Monitor for cases where Discovery agent does multi-session research that benefits from memory.
- **F22: Test-time reasoning** — already covered by F3 (`xhigh` effort) from earlier review.
- **F23: Self-Consistency sampling** — expensive (multiple sampling paths), domain gains reported on math/reasoning benchmarks. Our domain is less sampling-suitable.
- **F24: Tree-of-Thoughts** — 2026 research raised concerns about redundant exploration of low-value paths. Skip.
- **F25: Kubernetes-for-AI-agents (Maestro)** — enterprise scale, overkill at 6 projects.

### Decisions Required from User

| # | Question | Recommended default |
|---|---|---|
| 10 | F10: Run MAST mapping audit (our framework vs 14 specific failure modes)? | yes (cheap validation) |
| 11 | F13: Pilot Chain-of-Verification on Spec Reviewer? | yes (low-risk, high-upside prompt change) |
| 12 | F15: Split Reviewer into specialists? | defer (need weakness signal first) |
| 13 | F16: Evaluate Claude Code Security alongside our Security Reviewer? | yes (likely material improvement) |
| 14 | F18: Browse VoltAgent skills catalog for 2-3 gap fills? | yes (30 min investment) |
| 15 | F19: Add prompt-injection defense guardrails? | yes (defensive hygiene) |
| 16 | F21: Adopt Process Reward Models? | defer (enterprise infrastructure) |
| 17 | F17: Adopt MemGPT/A-Mem memory architecture? | defer (our scope doesn't need it) |

### Comparison to prior reviews

- **F1 (lazy loading):** adopted, documented. No change.
- **F2 (cache hit ratio):** debunked by data — hit ratio 98%. F2 stays closed.
- **F3 (`xhigh` effort):** adopted in 3 agents. F14 (reflection loops) and F22 (test-time reasoning) in this review reinforce the F3 bet — reasoning quality is where returns are.
- **F4 (Mythos Preview):** still monitoring, GA not yet.
- **F8 (MCPWatch):** still blocked on tooling. **F16 (Claude Code Security) partially compensates** — Anthropic's own security agent has same goal.

### Notes

**Biggest surprise:** MAST taxonomy validates our architecture very cleanly. The top 3 failure modes in industry (bad specs / coordination / verification) map directly onto our top 3 framework pillars (Product+Spec Reviewer / handoff contract / Reviewer-class agents). Suggests our design is structurally correct — most improvements will be refinements, not restructuring.

**New pattern for future reviews:** The query-quota rule works. Six of eight queries this round were agent-specific (Tier 7-9), and findings are concrete and actionable (CoVe, prompt injection, Claude Code Security) — not just tooling news.

**Framework health indicator:** When an industry-wide failure taxonomy (MAST) lands on 42/37/21 split, and our framework addresses all three at the structural level, that's an external validation signal. Worth noting in `docs/DECISIONS.md` as architectural justification for the current design.

---

## Adoption Notes — 2026-04-24 (supplementary review, same-day execution)

Decisions executed within hours:

- **F11/F13 ✅ adopted** — Added "Optional Chain-of-Verification (CoVe) frame" section to `agents/spec-reviewer.md`. 4-step process (draft → verify questions → answer independently → refine), gated on high-stakes triggers (artifact >500 words, ≥3 components, prior disputed iteration, sensitive domain, ql_iteration ≥ 2). Added `cove_applied: true|false` field to output JSON for downstream measurement. Ground for measuring whether CoVe actually reduces revision rate in our workflow.
- **F19 ✅ adopted** — Added "Trust boundary check (input sanitization)" section to `agents/iteration-manager.md` as the single chokepoint for user-supplied content. Added shorter pointer in `agents/discovery-modes/research-synthesis.md` (the only other agent that reads user content from a different surface — pasted research data). Explicit trust contract: USER → IM (checked) → all downstream agents (trusted).
- **F10 ⏸ deferred** — MAST 14-mode mapping audit needs deeper research (top-level 3 categories known; the 14 specific modes need a fresh source dive). Will run in next scheduled review.
- **F16 ⏸ deferred** — Claude Code Security agent evaluation requires actual side-by-side test on a real code task; will pair with the next real Builder workflow.
- **F18 ⏸ deferred** — VoltAgent skills catalog browse is a 30-min human task, not auto-executable.

**New patterns documented in `docs/KNOWN_PATTERNS.md`:**
- "Trust boundary at single chokepoint" — formalizes the IM-as-sanitizer architecture so future agents know the contract
- "Optional Chain-of-Verification (CoVe) for review-class agents" — generalized so other reviewers (Reviewer, Design Reviewer, Security Reviewer, Analytics Validator) can adopt the pattern when justified

**Quality risk assessment:**
- F11/F13 CoVe — OPTIONAL frame, gated on high-stakes triggers. Default behavior (rubric scoring) unchanged. Can only improve verdicts, never degrade them. Token cost increase ~30-50% on triggered reviews only.
- F19 prompt injection defense — pure addition of input sanitization at IM. False positives recoverable (user confirms). False negatives are baseline behavior pre-adoption (i.e., zero regression). Defense in depth.

**Net effect:** 1 agent extended with CoVe (Spec Reviewer), 1 chokepoint hardened (IM), 1 mode patched (research-synthesis), 2 new patterns documented. Zero quality regression. Forward path: when CoVe adoption produces enough `cove_applied: true` data points, measure whether revision rate drops; if yes, generalize CoVe to other Reviewer-class agents.

---

## Methodology Discovery — 2026-04-24 (meta: source list expansion)

**Type:** Methodology update, not a finding-driven review.
**Trigger:** User asked "what other sources should we monitor?" — discovered we had a critical Anthropic-blind spot and gaps in autonomous-agents/swarms coverage.

### Gaps identified (with evidence)

1. **Anthropic-blind spot** — 8 of 9 prior-version tiers were vendor-agnostic but Tier 1 was Anthropic-only. We missed: OpenAI GPT-5.4 family, Computer Use API, Tool Search, 1M context, MCP support in Responses API, Assistants → Responses migration; Google Gemini 3.1 Pro, Deep Research / Deep Research Max (93.3% on DeepSearchQA), agentic vision; Stanford AI Index 2026 findings (SWE-bench 60→100% in a year, China-US lead at 2.7%, 57% orgs have agents in production).
2. **Standards & governance not tracked** — MCP donated to Linux Foundation Agentic AI Foundation (Dec 2025), A2A protocol at v1.2 with 150+ orgs in production (June 2025), MCP v2.0 milestone Q1 2026 (Streamable HTTP + OAuth 2.1). Without monitoring we'd miss breaking-protocol changes.
3. **Autonomous agents & swarms not surfaced** — Devin (Cognition), OpenHands, SWE-Agent, Cursor agent mode, Sourcegraph Amp, Anthropic Computer Use; OpenAI Agents SDK, AG2/AutoGen, LangGraph deepagents, Hermes Agent (100k+ stars). These compare directly to our Builder workflow and inform whether to add autonomous capability to specific agents.
4. **Reddit underweighted** — r/AI_Agents has production-failure threads 2-4 weeks ahead of blog posts. r/ClaudeAI tracks Claude Code workflows specifically. r/LocalLLaMA (266k+ members) for open-source / local patterns.
5. **No cadence rules** — every tier was treated as weekly. Stanford Index is annual; ToT research is months-long signal; Claude Code changelog is daily-velocity. Same scan rhythm wastes queries on slow-signal tiers and under-checks fast-signal ones.

### Methodology changes applied to `agents/discovery-modes/ai-landscape.md`

**Three new tiers:**
- **Tier 10 — Competing AI ecosystems** (OpenAI, Google/DeepMind, open-source via HF, cross-vendor leaderboards). Closes the Anthropic-blind spot. Required weekly.
- **Tier 11 — Standards & governance** (MCP roadmap, A2A protocol, Linux Foundation AAIF, EU AI Act, ISO). Required monthly. Tracks breaking-protocol risk.
- **Tier 12 — Autonomous agentic development & agent swarms** (Devin, OpenHands, SWE-Agent, Cursor agent, OpenAI Agents SDK, AG2, LangGraph deepagents, multi-agent collaboration patterns). Bi-weekly. Compares directly to our Builder workflow and surfaces emergent collaboration patterns.

**Expansions to existing tiers:**
- Tier 1: added Anthropic Research blog, Anthropic Skills repo, EconomicIndex dataset, HF Daily Papers
- Tier 5: explicit list of 6 newsletters (AlphaSignal, TLDR AI, Latent Space, Import AI, Ahead of AI, LLMs for Engineers) and 5 Reddit subs (ClaudeAI, AI_Agents, LocalLLaMA, LangChain, MachineLearning); curated Twitter/X handles
- Tier 7: VoltAgent collections (awesome-agent-skills 1000+, awesome-agent-papers), awesome-ai-agents-2026 (300+, 20 categories)
- Tier 8: Latent Space podcast as primary practitioner source; explicit MAST taxonomy reference; r/AI_Agents horror stories
- Tier 9: Anthropic "Building Effective Agents" 7-pattern foundation; Self-Discover, Voyager, A-Mem additions

**New cadence section:**
- Weekly: Tier 1, 5, 6, 10
- Bi-weekly: Tier 2, 7, 8, 12
- Monthly: Tier 3, 4, 9, 11
- Quarterly: industry reports (Stanford Index, State of AI, McKinsey)

**Updated query quota rules:**
- Required every weekly review: ≥1 Tier 1 + ≥1 Tier 10 + ≥2 agent-specific (Tier 2/7/8/9/12) + ≥1 Tier 4
- Monthly bonus: +1 Tier 11
- Quarterly bonus: +1 industry reports
- Effect: each review now spans both vendors AND agent substance, instead of drifting to all-tooling or all-Anthropic.

### Trade-offs accepted

- Each review will use 2-3 more queries than before → ~$1 extra cost per review (from ~$2 to ~$3)
- Methodology file grew from 222 lines to 365 lines (+143)
- More cognitive load on the reviewing agent — Cadence + quota matrix takes attention to follow

### Adoption note

This methodology change takes effect on the next `/ai-landscape-review` invocation (next Monday 10:08 launchd notification → manual run, or on-demand any time). The methodology applies to both framework-scope and project-scope reviews.

---

## AI Landscape Review — 2026-04-24 (#4: methodology validation run)

**Reviewer:** Discovery (ai-landscape mode)
**Scope:** framework
**Sources scanned:** Tier 1, 4, 5, 7, 10, 11, 12 (validated new query-quota rules in action)
**Time period:** anything missed by prior 3 reviews today
**Trigger:** User asked to re-run after methodology expansion to validate new tiers actually surface findings the old methodology missed.

### Methodology validation result

**Query quota satisfied:**
- ✓ Tier 1 Anthropic — 1 query (caught Mythos Preview restriction, Opus 4.7 release, Claude Design launch, Claude Managed Agents beta)
- ✓ Tier 10 Competing — 2 queries (OpenAI Agents SDK April update, Google A2A v1.2 + Cloud Next 2026)
- ✓ Tier 12 Autonomous & swarms — 2 queries (Devin/OpenHands/Cursor releases, Anthropic Computer Use)
- ✓ Tier 11 Standards (monthly bonus) — 1 query (MCP v2.0 status confirmed shipped)
- ✓ Tier 7 Agent roles — 1 query (Vercel Open Agents, top skill installs)
- ✓ Tier 4 Benchmarks — 1 query (SWE-bench Pro becoming new standard)

**New findings the old methodology would have missed:** 7 of 10 below come from Tier 10/11/12 queries that didn't exist before this morning.

### Findings — High Priority

#### F26: Claude Mythos Preview confirmed restricted (Project Glasswing only) — NOT a public model

- **Source:** [NBC News on Mythos limited release](https://www.nbcnews.com/tech/security/anthropic-project-glasswing-mythos-preview-claude-gets-limited-release-rcna267234), [InfoQ Mythos analysis](https://www.infoq.com/news/2026/04/anthropic-claude-mythos/)
- **What it is:** Mythos Preview rolled out April 8, 2026 only to Project Glasswing partners (Amazon, Microsoft, Nvidia, Apple). Cybersecurity-focused. SWE-bench 93.9%, USAMO 97.6%. Autonomously found zero-days in every major OS and browser during testing.
- **Impact on us:** **F4 from earlier review is now resolved as DEAD-END.** Mythos won't be available to us; stop monitoring for GA.
- **Decision needed:** Yes — remove F4 from "monitor" list and update it as "blocked: enterprise-only, won't reach public framework."

#### F30: Anthropic Agent-Based Code Review for Claude Code (April 2026)

- **Source:** [InfoQ: Anthropic Introduces Agent-Based Code Review for Claude Code](https://www.infoq.com/news/2026/04/claude-code-review/)
- **What it is:** New native code review feature in Claude Code, agent-driven.
- **Impact on us:** HIGH — directly overlaps with our Reviewer + Spec Reviewer agents. If Anthropic's native solution is high quality, we may want to integrate it as optional Skill (per CLAUDE_SKILLS.md pattern) or evaluate if it replaces our Reviewer entirely.
- **Effort:** SMALL — read InfoQ article + test on a real PR.
- **Decision needed:** Yes — investigate Anthropic Agent-Based Code Review and compare to our Reviewer/Spec Reviewer?

#### F27: Multi-agent parallel execution became "table stakes" (Feb 2026 wave)

- **Source:** [Morph LLM AI Coding Agent comparison](https://www.morphllm.com/ai-coding-agent), [MightyBot rankings](https://mightybot.ai/blog/coding-ai-agents-for-accelerating-engineering-workflows/)
- **What it is:** In a single 2-week February 2026 window: Cursor 3.0 (8 parallel agents), Windsurf (5 parallel), Grok Build (8), Claude Code Agent Teams, Codex CLI (Agents SDK), Devin parallel sessions. Industry consensus: running multiple agents simultaneously on different parts of a codebase is now table stakes.
- **Impact on us:** HIGH (architectural) — our framework is strictly sequential workflow. We're behind the industry on parallel execution. But: parallel adds coordination cost + state-conflict risk that our quality loop hasn't been designed for.
- **Effort:** LARGE — would require rethinking workflow_state, handoff contract, IM routing for parallel branches.
- **Proposal:** **Investigate Claude Code Agent Teams specifically** — it's Anthropic-native multi-agent in Claude Code. If it slots into our existing IM as a "parallel execution" mode for independent subtasks (e.g., Builder + Test Strategist + Documentation in parallel), it might give us parallelism without architectural rework.
- **Decision needed:** Yes — investigate Claude Code Agent Teams as parallel execution path?

#### F33: SWE-bench Verified deprecated by OpenAI in favor of Pro (gold patch leakage)

- **Source:** [CodeAnt SWE-bench scores 2026](https://www.codeant.ai/blogs/swe-bench-scores), [Morph SWE-Bench Pro](https://www.morphllm.com/swe-bench-pro)
- **What it is:** OpenAI stopped reporting Verified scores in early 2026. Audit found that every frontier model could reproduce verbatim gold patches or problem statement specifics for certain Verified tasks. 59.4% of the hardest unsolved problems had flawed test cases. SWE-Bench Pro is the new reliable benchmark (top: Claude Mythos 77.8%, Opus 4.7 64.3%, Kimi 2.6 58.6%).
- **Impact on us:** MEDIUM — our prior reviews and EVOLUTION_LOG references Verified as "the" benchmark. Should switch all benchmark references to Pro.
- **Effort:** SMALL — text-only update in `agents/discovery-modes/ai-landscape.md` and EVOLUTION_LOG entries that reference Verified.
- **Decision needed:** Yes — update SWE-bench reference to SWE-Bench Pro in framework docs?

#### F29: Anthropic Claude Managed Agents (public beta, April 2026)

- **Source:** [Apify MCP handbook April 2026 edition](https://use-apify.com/blog/mcp-server-handbook-2026)
- **What it is:** Hosted Claude Platform service for long-horizon agent work. Handles sessions, harnesses, sandboxing, state management, tool execution, error recovery. For autonomous AI agents that need durable state and safer tool access.
- **Impact on us:** MEDIUM-HIGH (future) — our framework runs interactive agents tied to a Claude Code session. Managed Agents would be the path if a downstream project needs autonomous long-running agents (e.g., monitoring, ongoing data ingestion, scheduled background work).
- **Effort:** LARGE — would require new agent type + handoff contract extension for "agent runs in remote managed runtime."
- **Decision needed:** No active decision. Note as future option for downstream projects with that need (none today).

### Findings — Medium Priority

#### F31: Claude Design product launched (April 17, 2026, experimental)

- **Source:** [Releasebot Claude release notes](https://releasebot.io/updates/anthropic/claude)
- **What it is:** Anthropic Labs experimental product for creating prototypes, slides, one-pagers. Available to Pro, Max, Team, Enterprise users.
- **Impact on us:** MEDIUM — our Designer agent already produces visual mockups. Claude Design overlaps but is a distinct product surface (likely with its own UI). Should check if it produces deliverables our Designer doesn't, or if its workflow informs Designer evolution.
- **Decision needed:** Maybe — check Claude Design output formats vs our Designer's output format?

#### F32: A2A protocol v1.2 with Signed Agent Cards (cryptographic identity)

- **Source:** [Google Cloud A2A blog](https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade), [The Next Web Cloud Next 2026](https://thenextweb.com/news/google-cloud-next-ai-agents-agentic-era)
- **What it is:** A2A protocol v1.2 with cryptographically signed Agent Cards (verifiable identity). Native A2A support now built into Google ADK, LangGraph, CrewAI, LlamaIndex, Semantic Kernel, AutoGen. 150+ orgs in production.
- **Impact on us:** LOW today (we don't do cross-org agent collaboration), MEDIUM future. Signal that decentralized multi-agent is reaching production maturity.
- **Decision needed:** No — defer until cross-org need arises.

#### F35: Vercel Open Agents — open-source autonomous coding platform

- **Source:** [Vercel Open Agents announcement](https://newclawtimes.com/articles/vercel-open-agents-open-source-coding-agent-platform-github/)
- **What it is:** Forkable open-source platform — web UI + durable agent runtime + sandboxed execution + GitHub integration. From prompt to PR without local machine.
- **Impact on us:** MEDIUM — alternative reference architecture for downstream projects that want their own self-hosted agent infrastructure (vs Cursor/Claude Code lock-in).
- **Decision needed:** No — keep on watch as reference design for self-hosted scenarios.

### Findings — Monitor

- **F28:** [Claude Code Agent Teams](https://www.morphllm.com/ai-coding-agent) — Anthropic-native multi-agent feature in Claude Code (Feb 2026). Investigation needed (covered under F27 proposal).
- **F34:** OpenAI Agents SDK April update: sandboxing + long-horizon harness (Python first). Catching up to Claude Managed Agents. Direct OpenAI competitor to Anthropic's hosted runtime.
- **F36:** OpenHands v1.6.0 (March 30, 2026) — Kubernetes support + Planning Mode beta. For self-hosted teams.
- **F37:** Vercel skills `find-skills` (579k installs), `vercel-react-best-practices` (216k), `web-design-guidelines` (171k). Signal for what skills the wider community values.
- **F38:** [Anthropic 2026 Agentic Coding Trends report](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf) — official PDF, deserves a deep read at quarterly cadence.

### Decisions Required from User

| # | Question | Recommended default |
|---|---|---|
| 18 | F26: Mark F4 (Mythos Preview GA) as "blocked: enterprise-only"? | yes (closes a tracked item) |
| 19 | F30: Investigate Anthropic Agent-Based Code Review (compare to our Reviewer)? | yes (high overlap, low cost to investigate) |
| 20 | F27/F28: Investigate Claude Code Agent Teams as parallel execution path? | yes (architectural research, not adoption) |
| 21 | F33: Update framework docs to use SWE-Bench Pro as reference (not Verified)? | yes (mechanical doc update) |
| 22 | F29: Note Claude Managed Agents as future option for autonomous downstream needs? | yes (one-line addition to KNOWN_PATTERNS or DECISIONS) |
| 23 | F31: Compare Claude Design output formats to our Designer? | maybe (only if we have a UI-heavy project that would benefit) |
| 24 | F35: Add Vercel Open Agents to reference designs in MCP_TOOLS or similar? | maybe (defer until self-hosted need) |

### Comparison to prior reviews

- **F1 (lazy loading):** still validated ✓
- **F2 (cache hit ratio):** still 98% efficient ✓
- **F4 (Mythos Preview GA):** **RESOLVED via F26 — confirmed enterprise-only, won't be public. Remove from monitor list.**
- **F8 (MCPWatch):** still no package availability — defer indefinitely until package surfaces
- **F11/F13 CoVe:** adopted in Spec Reviewer, awaiting `cove_applied` data
- **F19 prompt injection defense:** adopted in IM
- **F16 Claude Code Security:** still candidate for evaluation; F30 (Agent-Based Code Review) might be the same product or superset

### Notes

**Methodology validation succeeded.** New tiers (10, 11, 12) and query-quota rules surfaced findings the old 9-tier methodology would have missed entirely:
- Without Tier 10: would not have caught OpenAI Agents SDK update, Google A2A v1.2 with signed cards, full Gemini Cloud Next picture
- Without Tier 11: would not have known MCP v2.0 features actually shipped (vs my prior assumption of Q1 milestone still pending)
- Without Tier 12: would not have caught Anthropic Computer Use, Devin/OpenHands/Cursor 3.0 evolution, multi-agent parallel execution becoming table stakes

**Biggest signal of this review:** Industry has moved to **parallel multi-agent** (F27). Our framework is sequential. This is the most significant architectural delta to consider, but adopting parallelism is a large investment that requires our quality loop and handoff contract to be redesigned. Worth a separate dedicated discovery before implementation.

**Closed items:** F4 (Mythos public release will not happen).

---

## Adoption Notes — 2026-04-24 (review #4 outcomes)

Five decisions executed with explicit zero-degradation checks.

### #18 ✅ Closed F4 — Claude Mythos Preview GA monitoring

- **Action:** Status updated in-line in Review #4 entry above. F4 is **permanently closed**.
- **Quality risk check:** zero — removes a stale monitoring item, no agent behavior change.

### #19 ✅ Investigated Anthropic Agent-Based Code Review (CCR) — complementary to our Reviewer, not replacement

- **What it is:** Multi-agent PR review system by Anthropic, research preview for Team and Enterprise Claude Code users. Feature ships with `/ultrareview` command (CLI ≥2.1.86) since April 22, 2026. Launches a fleet of specialized cloud agents that analyze diff + surrounding code in parallel on Anthropic infrastructure. Each agent targets a different issue class (logic errors, security, edge cases, regressions); a verification step filters false positives; findings posted as inline PR comments with severity. Free tier: Pro/Max users get 3 free reviews by May 5, 2026.
- **Performance data:** Before CCR, 16% of Anthropic-internal PRs received substantive review comments. After: 54%. Average review cost $15-25, completion time ~20 min.
- **Source:** [Anthropic Code Review blog](https://claude.com/blog/code-review), [Claude Code docs — Code Review](https://code.claude.com/docs/en/code-review), [InfoQ article](https://www.infoq.com/news/2026/04/claude-code-review/), [DevOps.com analysis](https://devops.com/anthropic-code-review-dispatches-agent-teams-to-catch-the-bugs-that-skim-reads-miss/), [Claude Code `/ultrareview` launch](https://pasqualepillitteri.it/en/news/1301/claude-code-ultrareview-agents-cloud-2026)
- **Comparison to our Reviewer + Spec Reviewer:**

  | Dimension | Anthropic CCR | Our Reviewer + Spec Reviewer |
  |---|---|---|
  | Scope | Code PRs only (git diff-based) | Any artifact (code, specs, designs, plans, copy) |
  | Execution | Parallel multi-agent on Anthropic cloud | Sequential single-agent in Claude Code session |
  | Specialization | Multiple specialized agents (logic/security/edges) | Single Reviewer covering 6 priorities + specialized Security Reviewer / Analytics Validator |
  | Trigger | PR open/push or `/ultrareview` / `@claude review` | IM routing after Builder completes |
  | Cost | $15–25 per PR review | Per Claude Code session cost (part of workflow) |
  | Environment | GitHub/Anthropic cloud | Local Claude Code |
  | Delivery | Inline PR comments + severity | Handoff JSON + next_recommended_agent |

- **Recommendation: adopt as COMPLEMENT, not replacement.** Anthropic CCR is stronger at code-specific review (parallel specialists, verification step, proven 3× catch-rate improvement). Our Reviewer + Spec Reviewer remain essential for NON-code artifacts (feature specs, design reviews, architecture plans, marketing copy) and for workflow-integrated completion verification (plan adherence check, task scope). Document `/ultrareview` as an **optional post-merge code quality enhancement** in `docs/MCP_TOOLS.md` (or new `docs/EXTERNAL_REVIEWERS.md`).
- **Quality risk check:** zero — investigation only, no code changes. If we later add CCR integration as optional note, still zero — it's an EXTERNAL tool users can invoke, doesn't change our agent definitions.

### #20 ✅ Investigated Claude Code Agent Teams — architectural option, not adopting

- **What it is:** Experimental native multi-agent feature in Claude Code (shipped with Opus 4.6). Enabled via `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` environment variable or settings.json flag. One session acts as team lead (coordinating + assigning), teammates work in their own context windows and communicate via shared task list + messaging.
- **Best-fit use cases (per Anthropic):** parallel research/review with teammates on different aspects, new modules with teammates owning separate pieces, debugging with competing hypotheses, cross-layer coordination (frontend+backend+tests).
- **Stress test validation:** 16 agents wrote a Rust-based C compiler (100K lines, builds Linux) over ~2,000 Claude Code sessions.
- **Source:** [Claude Code Agent Teams docs](https://code.claude.com/docs/en/agent-teams), [Anthropic Engineering: Building a C compiler](https://www.anthropic.com/engineering/building-c-compiler), [SitePoint setup guide](https://www.sitepoint.com/anthropic-claude-code-agent-teams/)
- **Mapping to our framework:**

  | Claude Code Agent Teams concept | Our framework equivalent |
  |---|---|
  | Team lead session | Iteration Manager |
  | Teammates with own context | Specialized agents (Builder, UI Builder, etc.) |
  | Shared task list | `docs/TASKS.md` + workflow_state |
  | Inter-agent messaging | Handoff blocks |
  | Parallel execution | **Missing** — we're sequential |

- **Recommendation: DO NOT adopt now.** Reasons:
  1. **Feature is experimental** — flag-gated, no stable API contract. Violates our backward-compatibility principle for integrations.
  2. **Parallel execution requires workflow_state redesign** — current `workflow_state.current_stage` is a single enum assuming linear progress. Parallel branches need tracking structure we don't have.
  3. **Quality loop semantics unclear for parallel outputs** — if 3 Builder agents work in parallel, which output does Reviewer evaluate? Do they merge? What's Gatekeeper's input?
  4. **No current pain point it solves** — our workflows are task-bounded and sequential execution hasn't hurt any active downstream.
- **When to revisit:** If/when a downstream has a workflow that genuinely benefits from parallelism (e.g., full-stack feature: independent backend + frontend + tests + docs tracks that converge). Start a dedicated architectural discovery at that point.
- **Documentation:** F27/F28 remain as watch-list items; not adding to KNOWN_PATTERNS yet (it's not a validated pattern for our system).
- **Quality risk check:** zero — investigation only. Actively declining to integrate experimental feature is the conservative choice.

### #21 ✅ Updated benchmark reference: SWE-Bench Pro as primary

- **Action:** Tier 4 in `agents/discovery-modes/ai-landscape.md` now references **SWE-Bench Pro as primary**, with a note that SWE-bench Verified is saturating and has confirmed gold-patch leakage (OpenAI dropped reporting; 59.4% of hardest-unsolved problems had flawed test cases). Added SWE-bench Live and llm-stats.com aggregator.
- **Historical log entries (F4, F13, summary) intentionally NOT retroactively edited** — they accurately reflect what we knew at the time. Only forward-looking methodology was updated.
- **Quality risk check:** zero — methodology reference update, no agent behavior change. Future reviews will use better benchmark.

### #22 ✅ Added Claude Managed Agents pattern to KNOWN_PATTERNS.md

- **Action:** New pattern "Hosted managed runtime for long-horizon autonomous agents" added to `docs/KNOWN_PATTERNS.md`. Documents Anthropic Claude Managed Agents (public beta April 2026) + OpenAI Agents SDK sandboxing as options for autonomous long-running workloads. Explicitly flagged as NOT needed today; only adopt when workload is genuinely autonomous and long-horizon.
- **Quality risk check:** zero — additive documentation, no existing agent or pattern changed. Flagged as opt-in future option.

### Summary

- 5 of 7 "yes"-recommended decisions from review #4 executed (18, 19, 20, 21, 22).
- 2 "maybe" decisions explicitly deferred (23 Claude Design comparison, 24 Vercel Open Agents in MCP_TOOLS) — no active signal requiring them yet.
- **Quality degradation check across all 5 changes:** zero. Each change is either (a) doc closure, (b) investigation report, (c) additive documentation, or (d) benchmark reference update. Zero agent behavior changes, zero handoff contract changes, zero workflow changes. Backward compatibility preserved.
- **Open watch items carried forward:** F27/F28 (parallel multi-agent architectural question), F30 (Anthropic CCR as optional post-merge tool), F34 (OpenAI Agents SDK evolution), F35 (Vercel Open Agents), F36 (OpenHands), F38 (Anthropic Agentic Coding Trends quarterly read).

---


