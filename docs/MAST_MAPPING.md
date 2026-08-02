# MAST Failure-Mode Mapping (framework guardrails audit)

**Source:** [MAST — Multi-Agent System Failure Taxonomy](https://sky.cs.berkeley.edu/project/mast/) (UC Berkeley Sky Computing Lab + IBM Research). Analysis of **1,600+ traces across 7 multi-agent frameworks**. Paper: [arxiv:2503.13657](https://arxiv.org/abs/2503.13657).

**Purpose:** Cross-reference each MAST failure mode against our framework's existing guardrails. Identify gaps. Each gap becomes either a new guardrail or a known accepted risk.

**Mapping status:** 9 of 14 modes documented in public sources at audit time (2026-04-25). Remaining 5 require reading the full PDF — flagged for quarterly review.

---

## Failure category distribution (industry observation)

- **Category 1 — Specification & System Design:** 41.8% of failures
- **Category 2 — Inter-Agent Misalignment:** 36.9% of failures
- **Category 3 — Task Verification & Termination:** 21.3% of failures

Our framework's three structural pillars map directly to these categories (validated in `docs/EVOLUTION_LOG.md` F10):

| MAST category | Our pillar |
|---|---|
| Specification | Product → Spec Reviewer → Gatekeeper (quality loop on every artifact) |
| Inter-agent | Handoff contract (structured JSON, every agent, every transition) |
| Task verification | Spec Reviewer / Reviewer / Security Reviewer / Design Reviewer / Analytics Validator (multi-layer review) |

---

## Per-mode mapping

### Category 1 — Specification & System Design

#### Mode 1.1: Role and Task Ambiguity
*"Agents disobey roles, e.g., subordinate agent unilaterally making executive decisions"*

| Our guardrail | Strength |
|---|---|
| Every agent file has explicit "You do NOT..." boundaries section | ✓ Strong |
| `AGENTS.md` roster table — `Does NOT` column per agent | ✓ Strong |
| Handoff contract: `next_recommended_agent` constrained to documented list per agent | ✓ Strong |
| Specialist agents forbidden from editing `docs/TASKS.md` (only IM commits) | ✓ Strong |

**Status: WELL COVERED.** No gap.

#### Mode 1.2: Step Repetition (looping)
*"Systems trapped in loops, repeating completed actions"*

| Our guardrail | Strength |
|---|---|
| `builder_cycle_count` with explicit max = 3 (escalation when reached) | ✓ Strong |
| `quality_loop_iteration` capped at 3 (Reviser → Spec Reviewer cycle) | ✓ Strong |
| `analytics_used` boolean prevents re-invoking Analytics Architect | ✓ Strong |
| Gatekeeper has explicit `escalate` verdict when no progress between cycles | ✓ Strong |

**Status: WELL COVERED.** No gap.

#### Mode 1.3: Loss of History (memory leaks / conversation resets)
*"Agents experience unexpected conversation resets, losing contextual continuity"*

| Our guardrail | Strength |
|---|---|
| `workflow_state` in handoff JSON carries state forward | ⚠ Moderate |
| `docs/TASKS.md` persists task lifecycle | ✓ Strong |
| Artifact files (`docs/PRD.md`, `ARCHITECTURE.md`, etc.) persist substance | ✓ Strong |
| Optional `.agent/workflows/<task_id>.json` cache (per-machine) | ✓ Optional |

**Gap identified:** No explicit "restore from artifact + handoff history" instruction for IM when a session loses context mid-task. Currently IM would re-read the most recent handoff and infer — but no explicit recovery protocol is documented.

**Recommendation:** Add to `agents/iteration-manager.md` a brief "Session-restore protocol" section: "When resuming after context loss (new session, history pruned), reconstruct state from (1) latest handoff JSON visible in current context, (2) `docs/TASKS.md` for task lifecycle, (3) artifact files for substance. Cache file optional."

**Severity:** LOW (workaround exists implicitly; explicit documentation would prevent confusion).

#### Mode 1.4: Unaware of Termination (failing to stop)
*"Tasks continue indefinitely or fail to recognize completion"*

| Our guardrail | Strength |
|---|---|
| IM has explicit `next_action = "complete_workflow"` with completion conditions | ✓ Strong |
| Gatekeeper `decision: accept` triggers workflow completion check | ✓ Strong |
| Reviewer `APPROVED` is terminal verdict (not a continuation) | ✓ Strong |
| Required closing summary template in `CLAUDE.md` (forces visible completion) | ✓ Strong |

**Status: WELL COVERED.** No gap.

### Category 2 — Inter-Agent Misalignment

#### Mode 2.1: Communication Breakdown
*"Agents fail to clarify confusing instructions, leading to faulty assumptions"*

| Our guardrail | Strength |
|---|---|
| Handoff contract: `next_recommended_reason` documents intent | ⚠ Moderate |
| Handoff contract: `assumptions_made` field explicit (forces documentation) | ✓ Strong |
| Spec Reviewer flags `source_conflicts` between artifact and source docs | ✓ Strong |
| Idea-intake mode: "If you have more than 8 ambiguous forks, prioritize and defer the rest" | ✓ Strong |

**Gap identified:** No explicit "ask before acting when intent is genuinely unclear" rule. Currently agents document assumptions and proceed. This is fine for low-stakes work but risky for irreversible actions (deletions, deployments, external API calls).

**Recommendation:** Add to `.cursor/rules.md` and to Builder + UI Builder definitions: "Before performing irreversible actions (file deletion, force-push, external API mutations, database migrations), if intent is ambiguous in the plan, ASK the user. Documenting an assumption is not sufficient for irreversible operations."

**Severity:** MEDIUM (one of the few real production-risk areas).

#### Mode 2.2: Information Withholding
*"Critical data discovered by one agent remains unshared with others"*

| Our guardrail | Strength |
|---|---|
| Handoff contract REQUIRES `blocking_issues` array (non-empty for any failure status) | ✓ Strong |
| Handoff contract REQUIRES `source_conflicts` array (for Spec Reviewer) | ✓ Strong |
| Handoff contract REQUIRES `assumptions_made` for documented uncertainty | ✓ Strong |
| Reviewer's `Required Changes` section explicitly blocks downstream | ✓ Strong |
| Spec Reviewer's `must_fix` items propagate to Reviser unchanged | ✓ Strong |

**Status: WELL COVERED.** Structured JSON forces explicit propagation.

#### Mode 2.3: Reasoning Mismatch
*"Agent actions lack logical consistency with their internal reasoning"*

| Our guardrail | Strength |
|---|---|
| Spec Reviewer `verdict_reason` requires single sentence justifying verdict | ✓ Strong (post-hoc) |
| Optional CoVe frame in Spec Reviewer (4-step self-check) | ✓ Optional |
| Reviewer's `Required Changes` must reference plan step or rule | ✓ Strong (post-hoc) |

**Gap identified:** All consistency checks happen POST-HOC (during review). No in-flight check for the producing agent. If Architect's plan reasoning contradicts its plan steps, the inconsistency is caught only by Spec Reviewer downstream — wasting tokens on a flawed artifact.

**Recommendation:** Consider extending CoVe pattern to producer agents (Architect, Product, Designer) in addition to review agents. Self-verification at production time. Defer — wait for `cove_applied` data from Spec Reviewer to validate the pattern's actual ROI in our workflow first.

**Severity:** LOW (existing review catches it; ROI of additional in-flight check unproven).

### Category 3 — Task Verification & Termination

#### Mode 3.1: Superficial Verification
*"Verifiers perform low-level checks rather than validating alignment with business requirements"*

| Our guardrail | Strength |
|---|---|
| Spec Reviewer 10-dimension rubric (forces multi-axis evaluation) | ✓ Strong |
| Reviewer's 6 priority categories (scope, architecture, safety, correctness, tests, clarity) | ✓ Strong |
| Security Reviewer's 7 check categories (auth, input, secrets, etc.) | ✓ Strong |
| Design Reviewer's 9 visual dimensions + WCAG audit | ✓ Strong |
| Analytics Validator's per-event, per-field, per-metric verification | ✓ Strong |
| Optional CoVe verification questions for high-stakes reviews | ✓ Optional |
| Gatekeeper independent of producer (separate agent) | ✓ Strong |

**Status: VERY WELL COVERED.** Our review layer is the framework's strongest area.

#### Mode 3.2: Premature or Unaware Stop
*"Tasks terminate prematurely or fail to recognize completion"*

| Our guardrail | Strength |
|---|---|
| Gatekeeper makes explicit `accept`/`iterate`/`escalate` decision (no implicit termination) | ✓ Strong |
| Reviewer's `APPROVED` verdict triggers completion gate check | ✓ Strong |
| IM checks `current_stage == "complete"` plus completion conditions before terminating workflow | ✓ Strong |
| Required closing summary in CLAUDE.md prevents silent termination | ✓ Strong |

**Status: WELL COVERED.** No gap.

---

## Modes pending (not publicly enumerated at audit time)

5 of MAST's 14 modes were not detailed in publicly accessible sources at audit time (2026-04-25). To complete the mapping, read the full paper:

- [Why Do Multi-Agent LLM Systems Fail? (arxiv 2503.13657)](https://arxiv.org/abs/2503.13657)
- [MAST GitHub — taxonomy_definitions_examples folder](https://github.com/multi-agent-systems-failure-taxonomy/MAST)

**Action:** Schedule for next quarterly review (Q2 2026) — read PDF, complete mapping for remaining 5 modes, update this document.

---

## Summary of gaps and recommendations

| # | Gap | Severity | Recommendation | Status |
|---|---|---|---|---|
| 1 | No explicit session-restore protocol for IM after context loss | LOW | Add brief "Session-restore protocol" section to `agents/iteration-manager.md` | **✅ Patched 2026-04-25** — protocol now lives in `agents/im-modes/session-restore.md` (extracted 2026-08 during IM lean-down; loaded on demand) |
| 2 | No "ask before acting" rule for irreversible operations | MEDIUM | Add to `.cursor/rules.md` and Builder/UI Builder definitions | **✅ Patched 2026-04-25** — see `.cursor/rules.md` "Irreversible-action protocol" + per-agent elaborations in `agents/builder.md` and `agents/ui-builder.md` |
| 3 | No in-flight reasoning consistency check for producer agents | LOW | Wait for `cove_applied` data; revisit if Spec Reviewer's CoVe shows clear ROI | Deferred (need data) |
| 4 | 5 of 14 MAST modes not yet mapped | INFO | Read full PDF at next quarterly review | Scheduled Q2 2026 (cron-like reminder via AI Landscape Review weekly cadence) |

---

## Overall assessment

**9 of 9 mapped modes have at least Moderate coverage; 7 of 9 are Well Covered.** Two real gaps identified (Mode 1.3 session restore, Mode 2.1 ask-before-irreversible). Both are LOW–MEDIUM severity with workarounds; both fixable via additive documentation, no behavior changes required.

This audit validates the framework's structural integrity against an empirical industry taxonomy. No critical failures detected. The framework's three pillars (specification quality loop / structured handoff / multi-layer review) align well with the three MAST categories that cover 100% of observed failure modes.

**Provenance:** This document is a snapshot at 2026-04-25 against MAST taxonomy as published. Refresh on each MAST taxonomy update or quarterly, whichever comes first.
