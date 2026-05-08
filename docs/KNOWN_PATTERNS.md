# Known patterns

Durable approaches and architectural choices that **proved correct** in this project (after implementation, review, or production validation). This is not a duplicate of `docs/DECISIONS.md` — decisions record *what we chose*; patterns record *what kept working in practice*.

**Maintainer:** Iteration Manager appends new patterns when a completed workflow confirms an approach (often aligned with an entry in `docs/DECISIONS.md` or `docs/ARCHITECTURE.md`).

**Audience:** Every agent reads this file (with `LESSONS_LEARNED.md`) before starting work, per `AGENTS.md`.

---

## How to write a pattern

```markdown
## Pattern: <short name>

- **Context:** When to apply this.
- **Approach:** What to do (concrete).
- **Why it worked:** Evidence from reviews, metrics, or incidents avoided.
- **Related:** `docs/DECISIONS.md` / `docs/ARCHITECTURE.md` links or section names if applicable.
```

Avoid one-off bugfixes here — those belong in `LESSONS_LEARNED.md` unless they generalize to a reusable pattern.

---

## Patterns

*(Iteration Manager appends below this line.)*

## Pattern: Framework files must not collide with app-level filenames

- **Context:** When adding files to `sync.py` `FRAMEWORK_GLOBS` for distribution to downstream projects.
- **Approach:** Use unique prefixes or suffixes for framework-owned files that share common names with application files. Example: `requirements-framework.txt` instead of `requirements.txt`.
- **Why it worked:** `requirements.txt` collision broke production three times before the rename permanently fixed it.
- **Related:** `docs/LESSONS_LEARNED.md` entry 2026-03-29.

## Pattern: Agent intake mode for document generation

- **Context:** When a new project needs foundational documents (PRD, Architecture, Brand) and the agents can't operate normally because those documents don't exist yet.
- **Approach:** Add an "onboarding intake mode" to existing agents rather than creating new onboarding-specific agents. Each agent presents structured questions, waits for answers, and produces the document as its artifact. The document then goes through the standard quality loop.
- **Why it worked:** Reuses existing agent definitions, quality loops, and handoff contracts. No new infrastructure or agent types needed. Documents get the same iterative refinement as any other artifact.
- **Related:** `AGENTS.md` Onboarding Workflow section; `docs/DECISIONS.md` DEC-001.

## Pattern: Single-source with cross-references for workflow rules

- **Context:** When the same rule (agent roles, routing logic, coding policy, quality loop details) appears in multiple framework files.
- **Approach:** Keep the normative definition in one authoritative file. Other files use a compact summary (table or one-liner) with an explicit cross-reference. Authoritative sources: `AGENTS.md` for workflow rules, `.cursor/rules.md` for coding rules, `agents/iteration-manager.md` for routing logic and state tracking, `agents/im-modes/` for transition tables, `docs/AGENT_HANDOFF_CONTRACT.md` for handoff format.
- **Why it worked:** Reduced token count by ~45% in the four heaviest files. Eliminated the class of bugs where a rule is updated in one file but not propagated to others (five such bugs found in the first audit).
- **Related:** `docs/DECISIONS.md` DEC-002.

## Pattern: Remove dead framework files rather than wiring them up

- **Context:** When an audit reveals a framework file that no agent reads, writes, or routes to, and existing documents already cover its intended purpose.
- **Approach:** Delete the file and all references. Inline any essential format guidance into the agent that would use it. Update escalation rules to reference the file that actually serves the function.
- **Why it worked:** `docs/FEATURES.md` was referenced in an escalation rule but never populated across 36+ completed tasks. Removing it (and redirecting the rule to `docs/FEATURE_MAP.md`) eliminated a false safety guarantee. Three existing docs (PRD, FEATURE_MAP, TASKS) already covered feature tracking.
- **Related:** `docs/DECISIONS.md` DEC-003.

## Pattern: Push-based auto-sync for framework distribution

- **Context:** When a framework repository produces files consumed by multiple downstream projects, and manual sync is error-prone.
- **Approach:** Use a post-commit hook that detects framework file changes in the commit, reads a local registry of downstream projects, and runs sync + template render automatically. The registry is gitignored (machine-specific paths). A `find_python` fallback chain resolves venv differences.
- **Why it worked:** Eliminated the manual sync step that was repeatedly forgotten (flagged as a follow-up in TASK-003). Zero additional infrastructure — just a git hook and a text file.
- **Related:** `docs/DECISIONS.md` DEC-004.

## Pattern: Agent modes for scalable sub-specializations

- **Context:** When an agent needs multiple specialized behaviors (e.g., Discovery: technical, market, branding, marketing) but embedding all in one file inflates tokens and loads unnecessary context.
- **Approach:** Refactor the agent into a lightweight dispatcher that selects a mode from a table, then loads only the relevant mode file from a subdirectory (`agents/<agent>-modes/*.md`). Each mode file is self-contained with its own responsibilities and output format. The dispatcher retains shared responsibilities, principles, and special modes (e.g., onboarding intake).
- **Why it worked:** `discovery.md` went from 316 → ~130 lines. No changes to `AGENTS.md` routing, `iteration-manager.md`, or the handoff contract. Adding a new mode requires only: (1) create a file, (2) add a row to the dispatcher table. The subdirectory is automatically covered by existing GITIGNORE_ENTRIES (`/agents/`).
- **Related:** `docs/DECISIONS.md` DEC-006.

## Pattern: Dual-invocation agents for pre/post-build quality

- **Context:** Some quality concerns (copy tone, accessibility, security) benefit from both a preparation step (before implementation) and a verification step (after implementation).
- **Approach:** Define a single agent (e.g., UX Writer) with two operating modes — "creation" (pre-Architect) and "review" (post-Builder). The standard-workflow transition table has separate rows for each invocation point. Each mode produces the same artifact type but with different status values (`produced` vs. `approved`/`changes_suggested`).
- **Why it worked:** UX Writer creates copy before Architect plans (so copy text informs implementation), and reviews strings after Builder implements (catching developer-speak). Both steps are optional with clear skip conditions, so the pipeline doesn't slow down for backend-only changes.
- **Related:** `docs/DECISIONS.md` DEC-008.

## Pattern: Deployment contracts for catch-before-deploy quality

- **Context:** When deployment bugs repeat across projects (missing env vars, untested migrations, broken CI, config drift) and the agent workflow has no deployment coverage.
- **Approach:** Add `docs/DEPLOY_CONTRACTS.md` as a project-specific document (not framework-synced). Extend Architect with a mandatory "Deployment Impact" section in every plan. Extend Reviewer with a deployment checklist. Provide CI/CD templates as reference files per stack. Deployment concerns are handled by existing agents rather than a new DevOps Agent.
- **Why it worked:** Follows the established pattern of extending existing agents rather than creating new ones (same as UX Writer's dual-invocation pattern). Deploy Contracts mirror the proven Pipeline Contracts structure. CI templates give projects a starting point without locking them into a specific workflow.
- **Related:** `docs/DECISIONS.md` DEC-009.

## Pattern: On-demand creative agents with quality loop integration

- **Context:** Some agents (Marketing, UX Writer) produce creative artifacts that benefit from quality review but are not mandatory in every workflow run. Inserting them as mandatory steps would slow down internal/technical changes unnecessarily.
- **Approach:** Define the agent with multiple operating modes (strategy, campaign, review). Route via IM on demand or at specific workflow points. Integrate with the quality loop for complex artifacts. Connect to UX Writer for tone consistency and Designer for visual briefs. Do not insert as mandatory step in the standard implementation workflow.
- **Why it worked:** Marketing Agent can run independently (user request), after Product spec (strategy), or before launch (launch kit) without blocking the implementation pipeline. Quality loop handles complex strategies; simple campaigns go directly to the user.
- **Related:** `docs/DECISIONS.md` DEC-010.

## Pattern: Tool-agents for external model integration via MCP

- **Context:** The agent system runs on a single LLM (Claude), but some tasks benefit from specialized external models (image generation, voice synthesis, video, etc.). Adding these capabilities directly to existing agents creates MCP tool dependencies and bloats their definitions.
- **Approach:** Define a "tool-agent" — a lightweight agent that receives a structured brief from another agent, calls an external model via MCP, and returns results to the requesting agent for review. The tool-agent has no decision authority; it executes briefs. The requesting agent (e.g., Designer) owns creative direction and reviews results. MCP configuration is documented in `docs/MCP_TOOLS.md` and is project-specific (`.cursor/mcp.json`).
- **Why it worked:** Clean separation of concerns — Designer thinks, Illustrator generates. Model-agnostic — switching from Nano Banana to DALL-E requires only MCP config change, not agent redesign. Graceful degradation — if MCP tool is unavailable, Illustrator returns `blocked` status. Pattern scales to any external model (voice, video, 3D) by creating new tool-agents with the same brief→execute→review workflow.
- **Related:** `docs/DECISIONS.md` DEC-011.

## Pattern: Required + Optional reading sections per agent

- **Context:** Agents accumulated reading lists of 7–12 framework docs over time, all marked as "required". This loaded thousands of tokens per invocation, even when most docs were irrelevant to the current task. A single Architect invocation could load 12 docs (~10K tokens) before doing any work.
- **Approach:** Restructure each agent's reading section into two parts: **Required reading** (3–6 docs critical to every invocation, as a bullet list with one-line "why" each) and **Optional reading (when relevant)** (situational docs with explicit conditions, e.g., "`docs/DECISIONS.md` — when the task touches an area with prior decisions"). The agent reads required docs always, optional docs only when their condition is met.
- **Why it worked:** Reduced per-invocation context by 30–60% across heavy agents (Architect 9→5, Product 8→4, Builder 8→4, UI Builder 8→5, Reviewer 9→6, Spec Reviewer 11→4, Analytics Architect 8→4, Security Reviewer 6→4). No verdict regressions because the optional docs were genuinely situational. Pattern is portable — works in Cursor and direct API as well as Claude Code.
- **Related:** Inverse of the "load everything to be safe" anti-pattern. Pairs well with "Agent modes" pattern (which loads mode-specific content only when needed).

## Pattern: Optional skill augmentation with mandatory built-in fallback

- **Context:** Claude Code skills (e.g., `design:accessibility-review`) provide battle-tested methodologies but are environment-specific (only available in Claude Code with a plugin installed). Hard-coding skill calls would break the framework in Cursor, direct API, and other Claude clients.
- **Approach:** Reference skills as **optional augmentation** in agent definitions. Each agent has a self-sufficient built-in methodology that produces valid output without any skill. Skill usage is wrapped in a conditional check ("If the skill is available in the current environment..."). Skill output is supplementary depth, never an output dependency. Verdict, handoff format, and routing decisions never depend on skill output. Skill availability is detected only via the available-skills list in the conversation context — agents never guess.
- **Why it worked:** Framework remains environment-agnostic — agents work fully in Cursor, direct API, and Claude Code without plugins. Adding a skill integration is non-breaking: removing it later just deletes the conditional block, leaving the built-in fallback intact. Skills enhance quality where available without creating dependencies.
- **Related:** `docs/CLAUDE_SKILLS.md` Backward compatibility contract.

## Pattern: Trust boundary at single chokepoint

- **Context:** Multi-agent systems read user-supplied content (task descriptions, PRD updates, research data, code snippets). Adversarial users can embed prompt-injection payloads to redirect agents away from their assigned roles (CVE-2025-53773, CVSS 9.6 — proven in production via PR descriptions in 2026).
- **Approach:** Apply pattern-match input sanitization at exactly **one chokepoint** — Iteration Manager — for general user input. Apply additionally only at agents that read user content from a different surface (e.g., Discovery in `research-synthesis` mode reads pasted research data outside the IM-routed task description). All other downstream agents trust their inputs were sanitized. Markers checked: role override ("Ignore previous instructions"), persona substitution ("Act as"), instruction redirection ("The real task is"), authority impersonation, hidden payloads. On detection: halt routing, show user the suspect text, ask explicit confirmation. False positives are recoverable (user confirms); false negatives documented as residual risk.
- **Why it worked:** Single chokepoint avoids defense duplication and contradictory results across agents. Trusted/untrusted boundaries are explicit in the contract. Pattern-matching is fast (no LLM call needed for the sanitize step itself). Agents downstream don't need defensive prompts — they remain task-focused.
- **Related:** `agents/iteration-manager.md` "Trust boundary check" section; `docs/EVOLUTION_LOG.md` F19 (2026-04-24 supplementary review).

## Pattern: Optional Chain-of-Verification (CoVe) for review-class agents

- **Context:** Reviewer-class agents produce a verdict from a one-pass scan of an artifact. They miss subtle issues — misread alignment with prior decisions, over- or under-score certain dimensions, default to prior expectations rather than fresh re-reading. Industry research reports ~23% F1 improvement on factual reasoning when LLMs apply Chain-of-Verification.
- **Approach:** Add an OPTIONAL 4-step CoVe frame BEFORE the agent produces its final structured output: (1) draft baseline verdict (internal scratch only), (2) generate 3–5 verification questions whose "no" answer would invalidate the draft, (3) answer each question independently by re-reading source documents, (4) refine if any verification contradicts the draft. Track usage via a boolean field (`cove_applied: true|false`) in the output JSON so downstream metrics can measure impact on revision rate. Apply CoVe only for high-stakes reviews (large artifacts, contested prior iterations, sensitive domains, quality_loop_iteration ≥ 2). Skip for trivial artifacts where the added reasoning cost isn't justified.
- **Why it worked:** Verification questions force the agent to challenge its own conclusions rather than confirm them. Independent re-reading prevents anchoring on the draft. Cove_applied flag enables measurement so the framework can validate whether CoVe is actually improving outcomes for this specific workflow before deciding to make it mandatory.
- **Related:** `agents/spec-reviewer.md` "Optional Chain-of-Verification (CoVe) frame" section; `docs/EVOLUTION_LOG.md` F13 (2026-04-24 supplementary review).

## Pattern: Inference-first onboarding (idea-intake)

- **Context:** Structured form-filling onboarding (13+ questions in Discovery, 11 in Designer, 14 in Architect, etc.) felt like a survey, not a conversation. Most users showing up with a real idea already have answers to 70-80% of the questions in their head — but the agent forced them through every question regardless. Net effect: ~50 questions for typical onboarding, slow time-to-MVP, friction at the most enthusiastic moment of the project.
- **Approach:** Replace structured intake with **inference-first onboarding** — the user describes their idea in any free-form length (one sentence to several paragraphs); the Discovery agent (in `idea-intake` mode) parses it, builds a structured "What I understood" summary, identifies only genuinely ambiguous forks (multiple equally-valid choices that materially change the product), and asks a capped 5–8 disambiguation questions. Each question is presented as **multiple-choice with concrete options, brief rationale per option, and an explicit recommendation** — never open-ended. Provenance tags (`inferred from idea`, `user-confirmed`, `default for vertical`, `open question`) propagate to the Discovery Brief so downstream agents (Product, Designer, Architect) know which fields are firm vs assumed and apply cascading inference: read the Brief, ask only their domain's remaining gaps, cap at 3–5 disambiguations per phase. Total: 1 idea + ~14 picks instead of ~50 questions.
- **Why it worked:** Three reasons. (1) Honest about what the agent can know — most onboarding "questions" have obvious answers from the idea description; asking them feels condescending. (2) Options-with-rationale beats open-ended every time — users want guidance, not raw choice; rationale teaches them which trade-offs the framework cares about. (3) Provenance tags create explicit handoffs — a downstream agent can see "this field is `inferred`, push back if it doesn't fit" instead of treating all Brief content as user-confirmed truth. Falls back gracefully to the structured 13-question intake when the user's first message is too thin to infer from, or when user explicitly asks for it.
- **Related:** `agents/discovery-modes/idea-intake.md` full methodology; `agents/im-modes/onboarding.md` Phase 1 mode selection logic; cascading inference principle propagates through Product, Designer, Architect onboarding modes.

## Pattern: Hosted managed runtime for long-horizon autonomous agents

- **Context:** Some workflows need agents that run for hours or days without user supervision — monitoring, scheduled ingestion, continuous background tasks. The framework's default is interactive agents tied to a live Claude Code session, which doesn't fit these needs. Running long-lived agents locally forces the user to keep a session open.
- **Approach:** For autonomous long-running workloads, delegate to a **hosted managed agent runtime** like [Anthropic Claude Managed Agents](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) (public beta April 2026). The hosted runtime handles sessions, harnesses, sandboxing, state persistence, tool execution, and error recovery. The downstream project retains the framework's agent definitions (roles, handoff contract) but the EXECUTION happens on Anthropic infrastructure with stable interfaces rather than in a local Claude Code window. Not needed for interactive development workflows — only adopt when the workload is genuinely autonomous and long-horizon.
- **Why it worked (when adopted):** Offloads session management, sandboxing, and durable state to a purpose-built hosted service. Lets the framework focus on WHAT agents do (role definitions, handoff semantics) while hosted runtime handles WHERE and HOW LONG. No downstream project currently needs this — flagged as a future option.
- **Related:** `docs/EVOLUTION_LOG.md` F29 (2026-04-24 review #4). OpenAI Agents SDK offers similar capability with sandboxing + long-horizon harness (Python).
