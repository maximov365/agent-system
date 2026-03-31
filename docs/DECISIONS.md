# Decisions

<!-- Record significant technical decisions here. -->
<!-- Each decision should include: context, options considered, decision, and rationale. -->

| ID | Title | Status | Date |
|----|-------|--------|------|
| DEC-001 | Guided conversational onboarding for new projects | accepted | 2026-03-29 |
| DEC-002 | Single-source principle for workflow rules | accepted | 2026-03-29 |
| DEC-003 | Remove FEATURES.md and FEATURE_TEMPLATE.md from framework | accepted | 2026-03-29 |
| DEC-004 | Push-based auto-sync for downstream projects | accepted | 2026-03-29 |
| DEC-005 | System Auditor agent for framework self-improvement | accepted | 2026-03-29 |
| DEC-006 | Agent modes pattern for scalable Discovery roles | accepted | 2026-03-29 |

---

## DEC-001 — Guided conversational onboarding for new projects

**Status:** accepted
**Date:** 2026-03-29

### Context

New project setup required users to manually write `project.config.yaml`, `docs/PRD.md`, `docs/ARCHITECTURE.md`, and other project-specific documents before agents could function. This created a high barrier to entry and meant the most critical documents were written without agent assistance.

### Options Considered

1. **Manual setup only** — user writes all docs by hand (status quo)
2. **Guided conversational onboarding** — agents ask structured questions and produce documents iteratively through quality loops
3. **Template wizard** — a CLI script that asks questions and generates files from templates

### Decision

Option 2 — Guided conversational onboarding.

### Rationale

- Leverages existing agents (Discovery, Product, Designer, Architect) and quality loops
- Documents benefit from the same iterative refinement as feature specs
- No new tooling required — works within the existing Cursor/Claude Code execution model
- Reduces barrier to entry dramatically: user only needs to answer questions
- Template wizard (option 3) would produce lower-quality one-shot output without the benefit of quality iteration

### Implications

- New `onboarding_phase` field added to `workflow_state`
- Each participating agent has an "onboarding intake mode" with structured questions
- `AGENTS.md` has a new Onboarding Workflow section
- `docs/ONBOARDING.md` updated with guided flow as the recommended approach
- Manual setup preserved as Scenario B for teams that prefer it

---

## DEC-002 — Single-source principle for workflow rules

**Status:** accepted
**Date:** 2026-03-29

### Context

Consistency audit revealed ~8,000 tokens of duplicated content across framework files. Agent Roles were described verbosely in `AGENTS.md` (~190 lines) and repeated in each agent file. Routing rules were duplicated between `AGENTS.md` and `agents/iteration-manager.md`. Coding rules in `agents/builder.md` duplicated `.cursor/rules.md`. Per-agent handoff examples in `AGENT_HANDOFF_CONTRACT.md` (~230 lines) repeated the same JSON structure 14 times.

### Options Considered

1. **Keep duplication for self-contained reading** — each file remains standalone but context window pressure grows
2. **Single-source with cross-references** — detailed definitions live in one place; other files reference them

### Decision

Option 2 — Single-source with cross-references.

### Rationale

- Reduces base prompt token count by ~45% for the four most-loaded files
- Eliminates inconsistency risk when rules change (update one place, not five)
- Agent role files remain authoritative for their own behavior; `AGENTS.md` provides the index
- `.cursor/rules.md` remains authoritative for coding rules; `agents/builder.md` references it

### Implications

- `AGENTS.md` Agent Roles section compressed from ~190 lines to a table + sequencing notes
- `AGENTS.md` Routing Rules section compressed from ~130 lines to a table + hard rules
- `AGENTS.md` Repository Structure replaced with a reference to `README.md`
- `AGENT_HANDOFF_CONTRACT.md` per-agent examples compressed from ~230 lines to a table + notes
- `AGENT_EXECUTION_MODEL.md` quality loop and analytics loop sections replaced with references
- `agents/builder.md` coding rules section replaced with a reference to `.cursor/rules.md`

---

## DEC-003 — Remove FEATURES.md and FEATURE_TEMPLATE.md from framework

**Status:** accepted
**Date:** 2026-03-29

### Context

Audit of the Voxema project (36 completed tasks, detailed PRD and FEATURE_MAP) revealed `docs/FEATURES.md` was never populated. Investigation showed no agent was wired to write to it: `agents/product.md` did not mention it, `agents/iteration-manager.md` did not route to it, `CLAUDE.md` did not include it in mandatory reads. An escalation rule in `docs/TASK_BACKLOG_AUTOMATION.md` referencing it was dead code.

### Options Considered

1. **Remove both files** — accept that PRD + FEATURE_MAP + TASKS covers the need
2. **Wire them up** — add explicit write instructions to Product agent and IM routing

### Decision

Option 1 — Remove both files from the framework.

### Rationale

- Three existing documents (PRD.md, FEATURE_MAP.md, TASKS.md) already cover feature definition, capability tracking, and task tracking
- Adding a middle layer increases maintenance overhead without clear benefit at current project scale
- The dead escalation rule was silently broken — removing the file makes the gap explicit rather than hidden
- FEATURE_TEMPLATE.md format guidance was inlined into `agents/product.md`

### Implications

- `docs/FEATURES.md` and `docs/FEATURE_TEMPLATE.md` deleted from framework, Voxema, and unfolda example
- Escalation rule in TASK_BACKLOG_AUTOMATION.md now references `docs/FEATURE_MAP.md` instead
- If a future project needs per-feature spec files, the concept can be reintroduced as an optional extension

---

## DEC-004 — Push-based auto-sync for downstream projects

**Status:** accepted
**Date:** 2026-03-29

### Context

Framework changes in agent-system required manual `sync.py --target` + `setup.py` runs for each downstream project. This was error-prone: the LESSONS_LEARNED.md entry for TASK-003 explicitly flagged "Run sync.py to propagate framework changes to Voxema" as a follow-up, but there was no mechanism to ensure it happened.

### Options Considered

1. **Git submodules** — downstream includes agent-system as a submodule; updated via `git pull --recurse-submodules`
2. **Pull-based (session check)** — downstream CLAUDE.md checks `.agent-system-version` at session start and runs sync if outdated
3. **Push-based (post-commit hook)** — agent-system auto-syncs all registered downstream projects when framework files are committed
4. **CI-based** — GitHub Actions creates PRs in downstream repos on push to main

### Decision

Option 3 — Push-based auto-sync via post-commit hook, with `downstream.projects` registry.

### Rationale

- Zero manual steps: framework commit → downstream updated automatically
- No git submodule complexity (notoriously error-prone for solo/small teams)
- No CI infrastructure required — works entirely locally
- `find_python` fallback chain ensures rendering works regardless of which python invokes the hook
- Registry file is `.gitignore`d (machine-specific paths), so no conflicts between developers
- `--all --dry-run` available for safe preview before committing

### Implications

- New `downstream.projects` file (gitignored) lists downstream project paths
- `sync.py` extended with `--all` and `--render` flags
- New `hooks/post-commit` auto-runs `sync.py --all --render` when framework files change
- `hooks/install.py` updated to install both pre-commit and post-commit hooks
- Developers must run `python hooks/install.py` once after cloning to activate the post-commit hook

---

## DEC-005 — System Auditor agent for framework self-improvement

**Status:** accepted
**Date:** 2026-03-29

### Context

Framework improvements (consistency audits, prompt optimization, dead reference detection) were performed manually by the user requesting an ad-hoc review. There was no systematic mechanism to monitor framework health across downstream projects or detect systemic issues from cross-project patterns.

### Options Considered

1. **Manual audits only** — user triggers reviews periodically (status quo)
2. **Automated checks only** — a script runs checks but has no interpretive layer
3. **System Auditor agent + audit.py** — agent interprets automated findings, analyzes cross-project patterns, and proposes improvements; never implements without user approval

### Decision

Option 3 — System Auditor agent backed by `audit.py` automated checks.

### Rationale

- Automated checks (`audit.py`) catch mechanical issues (version drift, dead references, prompt size) reliably
- The agent layer adds interpretive analysis (cross-project pattern recognition, root cause analysis, prioritized recommendations)
- Read-only constraint (never implements) keeps the user in control while reducing cognitive load for identifying what needs attention
- Fits naturally into existing Iteration Manager routing — `system_audit` request type

### Implications

- New `agents/system-auditor.md` agent definition (synced to downstream like other agents)
- New `audit.py` script in agent-system root (not synced — framework-level tool)
- Iteration Manager routes `system_audit` requests to System Auditor
- System Auditor output goes to user for approval; approved proposals routed to appropriate agents
- Agent produces `design_note` artifact type with structured findings JSON

---

## DEC-006 — Agent modes pattern for scalable Discovery roles

**Status:** accepted
**Date:** 2026-03-29

### Context

The user wanted to add more specialized Discovery roles (visual references, branding, marketing) but `AGENTS.md` and `agents/iteration-manager.md` were already near token limits (~3800 and ~5600 tokens respectively). Embedding full instructions for each new Discovery sub-role in `discovery.md` would have inflated the file and every request would load all sub-role context even when only one was needed.

### Options Considered

1. **Separate top-level agents** — create `agents/brand-discovery.md`, `agents/marketing-discovery.md`, etc. as independent agents with full IM routing
2. **Embed in discovery.md** — add all sub-role instructions to the existing monolithic file
3. **Agent modes pattern** — Discovery becomes a lightweight dispatcher; each mode is a separate file in `agents/discovery-modes/`; only the relevant mode file is loaded per request

### Decision

Option 3 — Agent modes pattern.

### Rationale

- Keeps `AGENTS.md` routing table unchanged (one entry for Discovery)
- Keeps `iteration-manager.md` routing unchanged (Discovery remains a single target)
- Each mode file is only loaded when needed, reducing context window pressure
- Adding a new mode requires only: (1) create a file in `agents/discovery-modes/`, (2) add a row to the dispatcher table in `discovery.md`
- Pattern is reusable for other agents if they need sub-specializations in the future

### Implications

- `agents/discovery.md` refactored from 316 lines (all-in-one) to ~130 lines (dispatcher)
- New directory `agents/discovery-modes/` with 5 mode files: `technical.md`, `market.md`, `references.md`, `brand.md`, `marketing.md`
- `FRAMEWORK_GLOBS` in `sync.py`, `hooks/pre-commit`, `hooks/post-commit`, and `audit.py` updated to include `agents/discovery-modes/*.md`
- GITIGNORE_ENTRIES unchanged — `/agents/` already covers the subdirectory
- Pattern can be applied to other large agents (e.g., Iteration Manager) if compression is needed

---

## DEC-008: UX Writer as independent agent

**Date:** 2026-03-29
**Status:** accepted
**Task:** TASK-007

### Context

The system lacked a dedicated agent for user-facing text. Copy was handled ad-hoc by Designer, Product, or Builder, leading to inconsistent tone of voice and developer-speak in UI strings.

### Decision

Create a standalone UX Writer agent rather than a Discovery mode or Designer sub-role, because:

- UX Writer produces unique artifacts (`ux_copy`) — copy documents and copy reviews — unlike any existing agent
- It has three invocation points: after Designer (copy creation), after Builder (copy review), and standalone (release notes, emails)
- It depends on `docs/BRAND.md` as a primary input, not on discovery modes
- Copy creation and copy review are distinct operations with different output formats

### Implications

- New file: `agents/ux-writer.md`
- New `artifact_type`: `ux_copy` in handoff contract
- Standard workflow extended with two optional UX Writer steps
- `ux_copy` added to Spec Reviewer, Reviser, and Gatekeeper scope
- No impact on existing workflows when UX Writer is skipped
