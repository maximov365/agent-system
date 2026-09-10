# Claude Skills Integration

> Legacy optional adapter reference. Not required in Codex. Verify current provider/client documentation before using commands or model IDs. `AGENTS.md`, `docs/CODEX.md`, and `docs/MODEL_POLICY.md` govern current defaults.

This document describes how agents in the system use **optional** Claude Code skills as methodological augmentation while preserving full backward compatibility with environments where skills are unavailable.

Claude skills (also called "agent skills") are pre-built prompt templates and methodologies installed via Claude Code plugins (e.g., Cowork plugins). They extend agent capabilities with battle-tested patterns from Anthropic and the community.

**Key principle: agents must work fully without skills.** Skills augment, never replace, built-in agent logic.

---

## Compatibility matrix

The Agent Skills format became an open standard in December 2025 and was adopted by OpenAI for Codex CLI and ChatGPT (the same `.md` skill files work across vendors).

| Environment | Skills available? | What agents do |
|---|---|---|
| Claude Code + plugin installed | Yes | Use skill as primary methodology |
| Claude Code without plugin | No | Use built-in fallback methodology |
| OpenAI Codex CLI + skill installed | Yes | Use skill as primary methodology (open standard since Dec 2025) |
| ChatGPT + skill installed | Yes | Use skill as primary methodology (open standard since Dec 2025) |
| Cursor (via `.cursor/rules.md`) | No | Use built-in fallback methodology |
| Anthropic API direct | No | Use built-in fallback methodology |
| Other Claude clients | No | Use built-in fallback methodology |

The framework is designed to be **environment-agnostic by default**. Skills are an opt-in enhancement, not a dependency. Backward-compatibility contract (below) ensures every agent works without skills regardless of environment.

---

## Backward compatibility contract

Every agent that references a Claude skill MUST satisfy these rules:

1. **Self-contained baseline.** The agent definition must include a complete fallback methodology that works without any skill present.
2. **Conditional invocation.** Skill usage must be wrapped in a conditional check ("if skill X is available...").
3. **No execution dependency.** The agent's `Output format` and `Handoff` sections must not depend on skill output structure.
4. **Equivalent outputs.** Agent output quality should be comparable with or without skill — skills improve depth and rigor, not basic functionality.
5. **No skill required for verdict.** Reviewer-class agents (Design Reviewer, Spec Reviewer, etc.) must be able to produce a valid verdict without invoking any skill.

If a skill is unavailable, the agent proceeds silently with its built-in methodology. No error, no escalation, no user-visible warning.

---

## Skill availability detection

Agents detect skill availability through two signals (in priority order):

1. **Skill name appears in the available-skills list** in the conversation context (system reminder block).
2. **The user explicitly invoked the skill** via `/skill-name` in their message.

If neither signal is present, the agent treats the skill as unavailable and uses its built-in fallback. Agents must never guess or assume skill availability based on training data.

---

## Skill catalog (current integrations)

The following skills are referenced by framework agents. Each entry lists: which agent uses it, what it provides, and what the fallback is.

### `design:accessibility-review`

| Field | Value |
|---|---|
| Used by | Design Reviewer |
| Provides | WCAG 2.1 AA reference, structured audit format with severity levels, color contrast/keyboard/screen reader checklists |
| Built-in fallback | Design Reviewer's `Accessibility` row in the Review checklist (basic contrast / touch target / semantic markup checks) |
| Source plugin | `frontend-design` / Cowork design plugin |

### `design:user-research`

| Field | Value |
|---|---|
| Used by | Discovery (in `user-research` mode) |
| Provides | Research methods table, interview guide structure, analysis frameworks (affinity mapping, JTBD, journey maps), deliverable templates |
| Built-in fallback | Built-in research methodology section in `agents/discovery-modes/user-research.md` |
| Source plugin | `frontend-design` / Cowork design plugin |

### `design:research-synthesis`

| Field | Value |
|---|---|
| Used by | Discovery (in `research-synthesis` mode) |
| Provides | Structured synthesis output (themes with prevalence + quotes, insights → opportunities matrix, user segments, prioritized recommendations) |
| Built-in fallback | Built-in synthesis methodology in `agents/discovery-modes/research-synthesis.md` |
| Source plugin | `frontend-design` / Cowork design plugin |

### `design:design-handoff`

| Field | Value |
|---|---|
| Used by | Designer (in `handoff-spec` mode — opt-in for complex UI) |
| Provides | Structured developer handoff: design tokens table, components/props/states tables, responsive behavior, edge cases, animation specs |
| Built-in fallback | Built-in handoff-spec output format in `agents/designer.md` (Handoff-spec mode section) |
| Source plugin | `frontend-design` / Cowork design plugin |

### `web-quality:*` (Core Web Vitals, performance, SEO)

| Field | Value |
|---|---|
| Used by | Design Reviewer (audit) + UI Builder (during implementation) |
| Provides | Lighthouse-style audits: Core Web Vitals (LCP, INP, CLS), performance budget analysis, SEO crawlability + structured data, best-practices (modern web APIs, deprecated patterns) |
| Built-in fallback | Cross-check `docs/ARCHITECTURE_GUARDRAILS.md` performance targets + [web.dev](https://web.dev) best practices manually |
| Source plugin | [addyosmani/web-quality-skills](https://github.com/addyosmani/web-quality-skills) (Addy Osmani, Google Chrome team) |
| Specific skill IDs | `web-quality:core-web-vitals`, `web-quality:performance`, `web-quality:seo`, `web-quality:best-practices` |

### `supabase:*` (RLS, migrations, edge functions, vector search)

| Field | Value |
|---|---|
| Used by | Builder (when project uses Supabase backend) |
| Provides | Supabase-specific implementation patterns: RLS policy design (security-critical), idiomatic SQL migrations, Deno Edge Functions, pgvector semantic search setup |
| Built-in fallback | Standard PostgreSQL + Supabase docs at [supabase.com/docs](https://supabase.com/docs) |
| Source plugin | Supabase official agent skills (when published / community equivalents) |
| Specific skill IDs | `supabase:rls`, `supabase:migrations`, `supabase:edge-functions`, `supabase:vector-search` |
| Critical for | Nastan (uses Supabase per `project.config.yaml` stack). Optional for any project that adopts Supabase. |

### `marketing:*` (SaaS marketing — SEO, A/B, ad creative, cold email)

| Field | Value |
|---|---|
| Used by | Marketing agent (when producing channel-specific artifacts) |
| Provides | Channel-specific best-practice templates: AI-SEO, A/B test setup, ad creative for Google/Meta/LinkedIn/X/TikTok, cold-email deliverability, churn-prevention sequences, analytics taxonomy, competitor analysis |
| Built-in fallback | Generic best-practice copy + channel patterns from `docs/BRAND.md` tone |
| Source plugin | [Corey Haines](https://github.com/coreyhaines) official marketing skills (or equivalent SaaS marketing collections) |
| Specific skill IDs | `marketing:ai-seo`, `marketing:ab-test-setup`, `marketing:ad-creative`, `marketing:cold-email`, `marketing:churn-prevention`, `marketing:analytics-tracking`, `marketing:competitor-analysis` |

---

## Integration pattern (for agent authors)

When adding a skill reference to an agent definition, use this exact pattern to preserve backward compatibility:

```markdown
## Methodology

### Optional skill augmentation

If the Claude skill `design:accessibility-review` is available in the current environment, invoke it as a methodological reference for the audit. Pass the design or implementation under review as the argument.

If the skill is not available (Cursor, API, or no plugin installed), follow the built-in WCAG checklist below — it covers the same essential criteria.

### Built-in fallback methodology

<full self-contained methodology here — must produce valid output on its own>
```

**Anti-patterns to avoid:**

- ❌ "Use skill X. Otherwise escalate." — escalation breaks portability
- ❌ "The skill output is required for the handoff." — creates execution dependency
- ❌ "Format your response according to skill X's output." — output format must be agent-defined
- ❌ Calling a skill without an explicit availability check
- ❌ Putting the skill reference in the `Output format` or `Handoff` section

---

## Skills vs MCP tools

These two extension mechanisms serve different purposes:

| | Claude Skills | MCP Tools |
|---|---|---|
| Nature | Prompt templates / methodologies | External capabilities (image gen, browsers, APIs) |
| Failure mode | Optional augmentation — agents work without | Required for tool-agents (Illustrator without MCP = blocked) |
| Configuration | Plugin install in Claude Code | `claude mcp add` or `.cursor/mcp.json` |
| Documented in | `docs/CLAUDE_SKILLS.md` (this file) | `docs/MCP_TOOLS.md` |
| Used by | Methodological augmentation in any agent | Tool-agents that bridge to external services |

A workflow agent (Designer, Discovery, Reviewer) may reference a Skill as augmentation. A tool-agent (Illustrator) requires an MCP tool to function — that's a hard dependency, not augmentation.

---

## Adding a new skill integration

When integrating a new Claude skill into the framework:

1. **Verify the gap.** Read the skill's SKILL.md and compare to the existing agent's methodology. Only integrate if there is a real gap, not duplication.
2. **Preserve the fallback.** Keep the agent's existing methodology as the built-in baseline. Only add optional augmentation on top.
3. **Add an entry to this file's catalog** with the four required fields (Used by, Provides, Built-in fallback, Source plugin).
4. **Update the agent definition** using the integration pattern above.
5. **Verify portability.** Confirm the agent still produces valid output when the skill is absent. Test in at least one non-Claude-Code environment (Cursor or direct API).
6. **Document in DECISIONS.md** if the integration changes the workflow's structure (e.g., a new Discovery mode).

---

## Removing a skill integration

If a skill is deprecated or no longer beneficial:

1. Remove the conditional augmentation block from the agent definition.
2. Remove the catalog entry from this file.
3. Verify the agent's built-in fallback still produces valid output (it should — the fallback was self-sufficient by design).
4. No data migration needed — handoff blocks and artifacts were never tied to skill structure.

The backward compatibility contract guarantees that removing skill integrations is non-breaking.
