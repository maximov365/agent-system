# Agent Handoff Contract

This document defines the standard format for passing results between agents in the {{ project.name }} workflow.

Every agent that produces a result must append a structured handoff block to its output. Iteration Manager reads this block to determine the next workflow step.

---

## Purpose

Without a standard handoff format, agents may:
- use inconsistent status terms (`done`, `success`, `approved_with_notes`)
- lose workflow state across transitions
- implicitly expand scope in their "next step" suggestions
- trigger downstream agents on incomplete data

This contract eliminates those failure modes by defining a single machine-readable output interface that every agent must follow.

---

## Core principle

An agent's job ends when it appends its handoff block. It must not invoke, instruct, or imply that the next agent should start. **Only Iteration Manager decides what happens next.**

The `next_recommended_agent` field is a suggestion — Iteration Manager may override it based on current workflow state.

---

## Allowed artifact types

The `artifact_type` field must be one of the following values. Agents must not invent new artifact types.

| Value | Description |
|---|---|
| `feature_spec` | Feature specification produced by Product |
| `task_breakdown` | Task list produced by Product |
| `implementation_plan` | Implementation plan produced by Architect |
| `design_note` | Design decision or exploration note |
| `decision_note` | Technical decision record for `docs/DECISIONS.md` |
| `analytics_spec` | Analytics specification produced by Analytics Architect |
| `test_plan` | Test strategy produced by Test Strategist |
| `code` | Production code, tests, or configuration changed by Builder |
| `none` | No artifact produced (e.g. routing-only output from Iteration Manager) |

---

## artifact_path format

`artifact_path` must follow these rules depending on artifact type:

- **Documents** (`feature_spec`, `task_breakdown`, `implementation_plan`, `design_note`, `decision_note`, `analytics_spec`, `test_plan`) — repository-relative path to the file, e.g. `docs/features/FEAT-42.md`
- **Code** — array of repository-relative file paths changed by Builder, e.g. `["src/pipeline.py", "tests/test_pipeline.py"]`
- **Artifact without a file** — a short human-readable identifier, e.g. `"FEAT-42 feature spec"`
- **No artifact produced** — `null`

Agents must not mix formats within a single handoff block.

`artifact_path` must not be `null` when `artifact_type` is `feature_spec`, `implementation_plan`, `analytics_spec`, or `code` — these artifact types always produce a locatable output.

---

## Artifact identifiers

`artifact_id` in `workflow_state` is a stable identifier for the artifact being processed in the current workflow cycle.

Convention:

| Artifact type | Identifier format | Example |
|---|---|---|
| `feature_spec` | `FEAT-<number>` | `FEAT-42` |
| `implementation_plan` | `ARCH-<number>` | `ARCH-42` |
| `analytics_spec` | `AN-<number>` | `AN-42` |
| `task_breakdown` | `TASK-<number>` | `TASK-42` |
| Other | Short descriptive label | `"retry-strategy-design"` |

`AN-<number>` is reserved exclusively for analytics specification artifacts. Analytics implementation tasks use `ATASK-<number>` as defined in `docs/TASK_BACKLOG_AUTOMATION.md`.

`artifact_id` must remain stable across all quality loop iterations for the same artifact. It must not change between Spec Reviewer, Gatekeeper, and Reviser passes.

If no artifact is currently under review, `artifact_id` must be `null`.

---

## Handoff block placement

The handoff block must appear **exactly once** and must be the **final element** of the agent output. No prose, commentary, or additional JSON may follow the handoff block.

Every agent appends the following JSON block at the end of its output, after its native content (prose summary, revised artifact, review JSON, etc.).

```json
{
  "handoff": {
    "agent": "<agent name>",
    "artifact_type": "feature_spec | task_breakdown | implementation_plan | design_note | decision_note | analytics_spec | code | none",
    "artifact_path": "<path or title; JSON array of paths when artifact_type is code>",
    "status": "<see Allowed statuses>",
    "next_recommended_agent": "<agent name, or null>",
    "next_recommended_reason": "<one sentence, or null>",
    "blocking_issues": [],
    "workflow_state": {
      "task_id": "<task id from docs/TASKS.md, or 'new'>",
      "artifact_id": "<artifact id or null>",
      "current_stage": "discovery | product | analytics | architecture | implementation | validation | complete",
      "quality_loop_iteration": 0,
      "builder_cycle_count": 0,
      "analytics_used": false,
      "product_spec_accepted": false
    }
  }
}
```

---

## Allowed statuses

Status values are fixed. No agent may invent new values.

| Status | Meaning | Produced by |
|---|---|---|
| `produced` | Agent completed its artifact; no blocking issues | Discovery, Product, Analytics Architect, Architect, Reviser |
| `accepted` | Artifact passed quality review | Gatekeeper (decision: accept) |
| `revise` | Artifact has must_fix issues; send to Reviser | Spec Reviewer (verdict: revise), Gatekeeper (decision: iterate) |
| `escalate` | Conflict or blocker requires user input | Any agent |
| `approved` | Code implementation approved; no changes required | Reviewer (APPROVED or APPROVED WITH MINOR CHANGES) |
| `changes_required` | Code implementation must be corrected by Builder | Reviewer (CHANGES REQUIRED) |
| `completed` | Workflow for this task is fully complete | Iteration Manager only |
| `validation_passed` | Analytics instrumentation verified | Analytics Validator (verdict: accept) |
| `validation_failed` | Analytics instrumentation has must_fix issues | Analytics Validator (verdict: revise) |
| `security_passed` | No blocking security issues found | Security Reviewer (verdict: pass) |
| `security_failed` | Security issues require Builder fixes | Security Reviewer (verdict: fail) |

**Mapping from agent-native verdicts to handoff status:**

| Agent | Native output | Handoff status |
|---|---|---|
| Reviewer | `APPROVED` | `approved` |
| Reviewer | `APPROVED WITH MINOR CHANGES` | `approved` |
| Reviewer | `CHANGES REQUIRED` | `changes_required` |
| Spec Reviewer | `verdict: accept` | `produced` (pass-through; Gatekeeper decides) |
| Spec Reviewer | `verdict: revise` | `revise` |
| Spec Reviewer | `verdict: escalate` | `escalate` |
| Gatekeeper | `decision: accept` | `accepted` |
| Gatekeeper | `decision: iterate` | `revise` |
| Gatekeeper | `decision: escalate` | `escalate` |
| Analytics Validator | `verdict: accept` | `validation_passed` |
| Analytics Validator | `verdict: revise` | `validation_failed` |
| Analytics Validator | `verdict: escalate` | `escalate` |
| Security Reviewer | `verdict: pass` | `security_passed` |
| Security Reviewer | `verdict: fail` | `security_failed` |
| Security Reviewer | `verdict: escalate` | `escalate` |
| Builder | implementation complete | `produced` |
| Test Strategist | test plan complete | `produced` |
| Architect | plan complete | `produced` |
| Product | spec complete | `produced` |
| Discovery | recommendation complete | `produced` |
| Analytics Architect | analytics spec complete | `produced` |
| Reviser | revision complete | `produced` |

---

## Blocking issues

When `status` is `escalate`, `changes_required`, `revise`, `validation_failed`, or `security_failed`, populate `blocking_issues` with structured entries. Leave the array empty for all other statuses.

```json
"blocking_issues": [
  {
    "type": "schema_mismatch | missing_field | trigger_error | scope_conflict | architecture_conflict | prd_conflict | decision_conflict | dependency_required | iteration_limit_reached | builder_cycle_limit_reached | insufficient_context",
    "source": "<file, agent, or rule that defines the constraint being violated>",
    "message": "<one sentence describing the specific issue>"
  }
]
```

---

## Workflow state rules

Every handoff must carry the current `workflow_state`. Iteration Manager reads this to make routing decisions without re-reading all prior outputs.

**Field update rules — agent responsibilities:**

| Agent | Field to update | Rule |
|---|---|---|
| All agents | `current_stage` | Set to the enum value matching the current workflow position |
| Product | `artifact_id` | Set to the feature spec identifier |
| Gatekeeper (accept for Product spec) | `product_spec_accepted` | Set to `true` |
| Analytics Architect | `analytics_used` | Set to `true` |
| Reviewer (approved) | `builder_cycle_count` | Reset to `0` |
| Reviewer (changes_required) | `builder_cycle_count` | Increment by `1` |
| Any agent starting quality loop | `quality_loop_iteration` | Set to `1` on first invocation; increment on each Reviser cycle |
| Gatekeeper (accept or escalate) | `quality_loop_iteration` | Reset to `0` |

Each agent receives the current `workflow_state` from the previous handoff and updates only the fields relevant to its action. Fields not listed above must be echoed unchanged.

---

## Per-agent handoff requirements

### Discovery

```json
{
  "handoff": {
    "agent": "Discovery",
    "artifact_type": "design_note",
    "artifact_path": "<path to discovery output, or null>",
    "status": "produced | escalate",
    "next_recommended_agent": "Product | Architect | null",
    "next_recommended_reason": "<one sentence>",
    "blocking_issues": [],
    "workflow_state": { ... }
  }
}
```

### Product

```json
{
  "handoff": {
    "agent": "Product",
    "artifact_type": "feature_spec",
    "artifact_path": "<path to feature specification>",
    "status": "produced | escalate",
    "next_recommended_agent": "Spec Reviewer",
    "next_recommended_reason": "New feature specification produced; quality loop required.",
    "blocking_issues": [],
    "workflow_state": { ... }
  }
}
```

### Analytics Architect

```json
{
  "handoff": {
    "agent": "Analytics Architect",
    "artifact_type": "analytics_spec",
    "artifact_path": "<path to analytics specification>",
    "status": "produced | escalate",
    "next_recommended_agent": "Architect",
    "next_recommended_reason": "Analytics specification complete; ready for implementation planning.",
    "blocking_issues": [],
    "workflow_state": { ... }
  }
}
```

### Architect

```json
{
  "handoff": {
    "agent": "Architect",
    "artifact_type": "implementation_plan",
    "artifact_path": "<path or title of implementation plan>",
    "status": "produced | escalate",
    "next_recommended_agent": "Spec Reviewer",
    "next_recommended_reason": "Implementation plan produced; quality loop required.",
    "blocking_issues": [],
    "workflow_state": { ... }
  }
}
```

### Test Strategist

```json
{
  "handoff": {
    "agent": "Test Strategist",
    "artifact_type": "test_plan",
    "artifact_path": "<path to test plan, or null>",
    "status": "produced | escalate",
    "next_recommended_agent": "Builder",
    "next_recommended_reason": "Test plan produced; Builder can begin implementation.",
    "blocking_issues": [],
    "workflow_state": { ... }
  }
}
```

### Builder

```json
{
  "handoff": {
    "agent": "Builder",
    "artifact_type": "code",
    "artifact_path": ["src/pipeline.py", "tests/test_pipeline.py"],
    "status": "produced | escalate",
    "next_recommended_agent": "Analytics Validator | Security Reviewer",
    "next_recommended_reason": "<one sentence: instrumentation changed or not>",
    "blocking_issues": [],
    "workflow_state": { ... }
  }
}
```

### Spec Reviewer

Appended after the native JSON output block.

```json
{
  "handoff": {
    "agent": "Spec Reviewer",
    "artifact_type": "<same as reviewed artifact>",
    "artifact_path": "<same as reviewed artifact>",
    "status": "revise | escalate | produced",
    "next_recommended_agent": "Gatekeeper",
    "next_recommended_reason": "Review complete; Gatekeeper decides whether to accept or iterate.",
    "blocking_issues": [],
    "workflow_state": { ... }
  }
}
```

Note: Spec Reviewer always routes to Gatekeeper. Gatekeeper reads the review output and decides `accept`, `iterate`, or `escalate`.

### Reviser

```json
{
  "handoff": {
    "agent": "Reviser",
    "artifact_type": "<same as revised artifact>",
    "artifact_path": "<same as revised artifact>",
    "status": "produced | escalate",
    "next_recommended_agent": "Spec Reviewer",
    "next_recommended_reason": "Revision complete; return to Spec Reviewer for next iteration.",
    "blocking_issues": [],
    "workflow_state": { ... }
  }
}
```

### Gatekeeper

Appended after the native JSON output block.

```json
{
  "handoff": {
    "agent": "Gatekeeper",
    "artifact_type": "<same as reviewed artifact>",
    "artifact_path": "<same as reviewed artifact>",
    "status": "accepted | revise | escalate",
    "next_recommended_agent": "Reviser | Test Strategist | Architect | Analytics Architect | Builder | null",
    "next_recommended_reason": "<one sentence>",
    "blocking_issues": [],
    "workflow_state": { ... }
  }
}
```

### Analytics Validator

Appended after the native JSON output block.

```json
{
  "handoff": {
    "agent": "Analytics Validator",
    "artifact_type": "code",
    "artifact_path": ["src/pipeline.py", "src/events.py"],
    "status": "validation_passed | validation_failed | escalate",
    "next_recommended_agent": "Security Reviewer | Builder | null",
    "next_recommended_reason": "<one sentence>",
    "blocking_issues": [],
    "workflow_state": { ... }
  }
}
```

### Security Reviewer

Appended after the native JSON output block.

```json
{
  "handoff": {
    "agent": "Security Reviewer",
    "artifact_type": "code",
    "artifact_path": ["src/api.py", "src/auth.py"],
    "status": "security_passed | security_failed | escalate",
    "next_recommended_agent": "Reviewer | Builder | null",
    "next_recommended_reason": "<one sentence>",
    "blocking_issues": [],
    "workflow_state": { ... }
  }
}
```

### Reviewer

Appended after the native review output.

```json
{
  "handoff": {
    "agent": "Reviewer",
    "artifact_type": "code",
    "artifact_path": ["src/pipeline.py", "tests/test_pipeline.py"],
    "status": "approved | changes_required | escalate",
    "next_recommended_agent": "null | Builder",
    "next_recommended_reason": "<one sentence, or null if approved>",
    "blocking_issues": [],
    "workflow_state": { ... }
  }
}
```

---

## How Iteration Manager uses the handoff block

Iteration Manager reads the `handoff` block from the previous agent's output and uses it as follows:

1. Read `status` — map to transition table in `agents/iteration-manager.md`
2. Read `blocking_issues` — if present and `status` is `escalate`, surface to user
3. Read `workflow_state` — update internal state, check `builder_cycle_count` and `quality_loop_iteration` limits
4. Read `next_recommended_agent` — use as default routing suggestion; override if workflow state requires it
5. Produce a `stage_transition` output with updated `workflow_state` and a single `next_action`

Iteration Manager must not assume the next agent from prose content — only from the `handoff.status` and `handoff.next_recommended_agent` fields.

---

## Validation rules for handoff blocks

A handoff block is invalid if:
- `status` is not one of the allowed values
- `workflow_state` is missing entirely
- `workflow_state.current_stage` is not one of the enum values
- `blocking_issues` is non-empty when `status` is `produced`, `accepted`, `approved`, `validation_passed`, or `security_passed`
- `artifact_type` is not one of the allowed values
- `agent` does not match the name of the producing agent
- `artifact_path` is `null` when `artifact_type` is `feature_spec`, `implementation_plan`, `analytics_spec`, or `code`
- `artifact_path` format does not match the expected format for the specified `artifact_type` (see artifact_path format section)
- more than one handoff block appears in the agent output
- the handoff block is not the final element of the output

If Iteration Manager receives an invalid handoff block, it must treat it as `insufficient_context` and escalate to the user rather than attempt to infer the correct values.

### Stage regression rules

Agents must not move `workflow_state.current_stage` backwards unless explicitly in a correction cycle.

**Allowed regressions:**
- `validation` → `implementation` — Reviewer returned `changes_required`; Builder must correct
- Quality loop internal cycles — `Spec Reviewer` ↔ `Reviser` iterations do not change `current_stage` (it stays at `product` or `architecture` for the duration of the loop)

**Forbidden regressions** (must trigger escalation):
- `implementation` → `product` or earlier
- `architecture` → `product` or earlier
- `analytics` → `product`
- `complete` → any earlier stage
- Any regression not listed in allowed regressions above

If an agent produces a handoff with a forbidden stage regression, Iteration Manager must escalate to the user.