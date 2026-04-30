# Agent Execution Model

This document defines how Cursor and Claude Code must execute the {{ project.name }} agent workflow.

The system is not a free-form multi-agent conversation. It is a controlled state machine executed through repeated **Iteration Manager → Agent → Handoff** cycles.

---

## Core principle

Every execution cycle follows the same structure:

```
User request or upstream result
        ↓
  Iteration Manager
  (routing decision)
        ↓
  One specialist agent
  (produces output + handoff block)
        ↓
  Iteration Manager
  (reads handoff, decides next step)
        ↓
       ...
```

No specialist agent may invoke another specialist agent directly. No execution cycle may select more than one next agent. No routing decision may be based on prose — only on the structured handoff block.

---

## Rule 1: Iteration Manager is always the entry point

Neither Cursor nor Claude Code may invoke a specialist agent directly as the first step.

All execution begins with Iteration Manager, regardless of:
- a new user request
- a continuation of an existing workflow
- a result returned by a previous agent
- an incomplete workflow from a prior session

**The first action of every execution cycle is always: read the request or incoming result as Iteration Manager.**

---

## Rule 2: One agent per cycle

On each execution cycle, Iteration Manager selects exactly one next agent and one `next_action`.

No agent chaining is allowed inside a single response. The sequence is:

1. Iteration Manager reads the input (user request or handoff block)
2. Iteration Manager produces a single JSON routing decision
3. One specialist agent is invoked
4. That agent produces its native output and appends a handoff block
5. Control returns to Iteration Manager for the next cycle

If a workflow requires five sequential agent invocations, it takes five separate cycles — not one.

---

## Rule 3: Handoff-driven routing

The runtime must ignore prose suggestions from agents and use only the structured handoff block for routing.

Iteration Manager reads three fields from the handoff block to make its routing decision:

| Field | Used for |
|---|---|
| `handoff.status` | Maps to transition tables in `agents/im-modes/` |
| `handoff.next_recommended_agent` | Default routing suggestion (may be overridden) |
| `handoff.workflow_state` | Current state; used to enforce sequencing rules and limits |

Iteration Manager may accept the `next_recommended_agent`, override it based on workflow state, escalate to the user, or mark the workflow complete.

---

## Execution modes

### Mode 1 — Initial routing

**Trigger:** A new user request arrives with no prior handoff block.

**Execution:**
1. Iteration Manager classifies the request (see request types in `agents/iteration-manager.md`)
2. Iteration Manager initialises `workflow_state` (see state initialisation rules)
3. Iteration Manager produces an `initial_routing` JSON output selecting the first agent
4. The selected agent is invoked

**Output:** `initial_routing` JSON block from Iteration Manager.

### Mode 2 — Stage execution

**Trigger:** Iteration Manager has selected a specialist agent.

**Execution:**
1. The specialist agent is invoked with the context package (see below)
2. The agent produces its native output (prose, JSON, revised artifact, etc.)
3. The agent appends a handoff block as defined in `docs/AGENT_HANDOFF_CONTRACT.md`
4. Control returns to Iteration Manager

**Output:** Agent's native output followed by a handoff block.

When the specialist agent is Builder, the handoff block must declare whether analytics instrumentation was introduced or modified. Builder must indicate this by setting `next_recommended_agent` to `Analytics Validator` if instrumentation was changed or introduced, or to `Security Reviewer` if no instrumentation changes were made. Iteration Manager uses this field to determine whether Analytics Validator must run before Security Reviewer.

### Mode 3 — Transition routing

**Trigger:** A specialist agent has completed and returned a handoff block.

**Execution:**
1. Iteration Manager reads the handoff block
2. Iteration Manager updates `workflow_state` based on field update rules
3. Iteration Manager checks termination conditions (see below)
4. Iteration Manager produces a `stage_transition` JSON output selecting the next agent or completing the workflow

**Output:** `stage_transition` JSON block from Iteration Manager.

---

## Context package

Every specialist agent invocation must include the following context. Agents must not be invoked on a bare request without this package.

**Required for every agent call:**

| Context item | Source |
|---|---|
| Current user request or upstream result | User input or previous agent output |
| Current `workflow_state` | From the latest handoff block |
| Latest handoff block | From the previous agent |
| Agent role file | `agents/<agent-name>.md` |
| `AGENTS.md` | Workflow rules and routing definitions |
| `.cursor/rules.md` | Execution policy |
| `CLAUDE.md` | Entry contract and default behavior |

**Additional context loaded by the agent itself** (as defined in each agent's Inputs section):

- `docs/PRD.md`
- `docs/ARCHITECTURE.md`
- `docs/ARCHITECTURE_GUARDRAILS.md`
- `docs/PIPELINE_CONTRACTS.md`
- `docs/DECISIONS.md`
- `docs/TASKS.md`
- The artifact under work (if applicable)
- Any relevant prior outputs (analytics spec, architect plan, etc.)

Priority within an agent invocation: `AGENTS.md` governs workflow, `.cursor/rules.md` governs coding, and `docs/ARCHITECTURE_GUARDRAILS.md` governs architecture. The agent role file is the highest-priority instruction for agent-specific behavior. See the Precedence section in `AGENTS.md` for full conflict resolution rules.

---

## Workflow persistence

The runtime must persist the latest `workflow_state` and latest handoff block between execution cycles in a dedicated workflow state file:

```text
.agent/workflows/<task_id>.json
```

The state file is the durable source of truth. `handoff.workflow_state` is the in-cycle payload that lets the next Iteration Manager turn validate and update the durable state.

Conversation state may cache the same information for convenience, and `docs/TASKS.md` remains the task backlog source of truth, but neither replaces the workflow state file.

On the next execution cycle, Iteration Manager must reconstruct workflow context from `.agent/workflows/<task_id>.json` before making a routing decision.

Without persisted state, the workflow must not continue — Iteration Manager must treat it as `insufficient_context` and escalate to the user.

### State file schema

Each workflow state file must contain:

```json
{
  "task_id": "TASK-123",
  "current_stage": "discovery | product | analytics | architecture | implementation | validation | complete",
  "status": "in_progress | blocked | completed | escalated",
  "workflow_mode": "lite | standard | strict",
  "last_agent": "Architect",
  "next_agent": "Builder",
  "artifact_id": "ARCH-123",
  "quality_loop_iteration": 0,
  "builder_cycle_count": 0,
  "analytics_used": false,
  "product_spec_accepted": false,
  "onboarding_phase": null,
  "artifacts": {
    "spec": "docs/features/TASK-123.md",
    "plan": "docs/plans/TASK-123.md",
    "reviews": []
  },
  "latest_handoff": {},
  "updated_at": "YYYY-MM-DDTHH:MM:SSZ"
}
```

`latest_handoff` stores the complete most recent handoff block. The top-level state fields are the routing index that Iteration Manager reads before selecting the next agent.

### State file rules

- Iteration Manager creates the state file during initial routing.
- Iteration Manager updates the state file after every valid handoff and before invoking the next agent.
- Specialist agents do not edit state files directly; they only return handoff blocks.
- The handoff `workflow_state` must match the durable state after Iteration Manager applies the transition.
- If a handoff and state file disagree, Iteration Manager must prefer the state file, inspect the latest handoff, and escalate unless the mismatch is a deterministic transition it can validate from the previous state.
- State files must not contain secrets, raw `.env` values, customer data, or unrelated file contents.
- Completed workflow state files may be retained as audit evidence or archived by project policy.

---

## Parallel workflow rule

Only one active workflow may exist per `task_id`.

If Iteration Manager detects multiple concurrent workflows attempting to modify the same task, it must escalate to the user rather than proceed.

Parallel workflows for different `task_id` values are allowed.

---

## Quality loop execution

The quality loop is controlled exclusively by Iteration Manager. No quality loop agent (Spec Reviewer, Reviser, Gatekeeper) may invoke another agent directly.

Trigger conditions, loop sequence, and termination rules are defined in:
- `AGENTS.md` — Quality Loop and Iteration Rules sections
- `agents/im-modes/quality-loop.md` — Quality loop control

**Execution-specific rule:** Each loop cycle is a separate Iteration Manager → Agent → Handoff cycle. `quality_loop_iteration` is tracked in `workflow_state` and echoed in every handoff.

---

## Analytics loop execution

The analytics instrumentation flow is controlled by Iteration Manager. Analytics Architect and Analytics Validator never invoke each other or other agents directly.

Trigger conditions, flow sequence, and validation logic are defined in:
- `AGENTS.md` — Development Workflow section
- `agents/im-modes/standard-workflow.md` — Implementation workflow transitions

**Execution-specific rules:**
- Builder indicates instrumentation changes via `next_recommended_agent` (`Analytics Validator` if changed, `Security Reviewer` if not)
- `analytics_used` is set to `true` in `workflow_state` when Analytics Architect is invoked and must not revert to `false`

---

## Termination conditions

### Successful completion

| Condition | Trigger | Action |
|---|---|---|
| Workflow complete | Reviewer returned `approved` and all completion conditions are met | `next_action: complete_workflow` |

### Error and escalation stops

Iteration Manager must stop execution and escalate when any of the following occurs:

| Condition | Trigger |
|---|---|
| Invalid handoff block | `workflow_state` missing, unknown `status`, invalid enum, wrong format |
| Escalation returned | Any agent sets `status: escalate` |
| Quality loop iteration limit | `quality_loop_iteration` reached 3 without Gatekeeper acceptance |
| Builder review cycle limit | `builder_cycle_count` reached 3 (Reviewer `CHANGES REQUIRED` or Security Reviewer `security_failed`, combined) |
| Missing `workflow_state` | Handoff block present but `workflow_state` field absent |
| Forbidden stage regression | `current_stage` moved backwards outside of allowed correction cycles |
| No meaningful progress | Two consecutive quality loop iterations did not change the set of `must_fix` issues |
| Conflict with source of truth | See escalation conditions in `AGENTS.md` — Iteration Rules section |
| Insufficient context | Repository context is insufficient to make a correct routing decision |

On escalation: Iteration Manager must produce a `stage_transition` output with `next_action: escalate_to_user` and a specific `escalation_reason`. It must not attempt to continue or infer a workaround.

---

## Cursor execution behavior

- Cursor always opens in Iteration Manager mode
- On each user message, Cursor invokes Iteration Manager first — never a specialist agent directly
- When Iteration Manager selects a specialist agent, Cursor loads `agents/<name>.md` as the active role
- The specialist agent produces its output and appends a handoff block
- After the agent response, Cursor returns to Iteration Manager mode for the next routing decision
- Cursor treats the conversation as an interactive runtime — each turn is one execution cycle
- Cursor must not "stay in" a specialist role across multiple turns without returning to Iteration Manager

---

## Claude Code execution behavior

- Claude Code defaults to Iteration Manager as defined in `CLAUDE.md`
- When Iteration Manager selects a specialist agent, Claude Code switches to the corresponding `agents/<name>.md` role file
- The specialist agent produces its output and appends a handoff block
- After completing the agent's work, Claude Code returns to Iteration Manager mode for the next routing decision
- Claude Code must not continue acting as a specialist agent after the handoff block is appended
- Claude Code must not chain specialist agents in a single response

---

## Handoff block requirement

Every agent output must end with a handoff block. The handoff block must be:

- The **last element** of the agent output — nothing may follow it
- Present **exactly once** — not duplicated
- Structured as defined in `docs/AGENT_HANDOFF_CONTRACT.md`

If an agent output does not contain a valid handoff block, Iteration Manager must treat it as `insufficient_context` and escalate to the user rather than attempt to infer the next step.

---

## Related documents

| Document | Purpose |
|---|---|
| `agents/iteration-manager.md` | Routing logic, state tracking; transition tables in `agents/im-modes/` |
| `docs/AGENT_HANDOFF_CONTRACT.md` | Handoff block format, allowed statuses, validation rules |
| `AGENTS.md` | Agent roles, workflow definitions, routing rules |
| `CLAUDE.md` | Entry contract for Claude Code |
| `.cursor/rules.md` | Execution policy for Cursor |