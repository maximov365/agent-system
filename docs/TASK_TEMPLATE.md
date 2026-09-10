# <TASK-ID> — <Outcome>

Owner: <current task owner>
Status: <planned / in_progress / completed; review states if needed>
Priority: <low / medium / high>
Complexity: <small / medium / large>
Source: <user request, accepted plan, or verified defect>
Related capability: <optional>

## Objective and scope

Describe the outcome and boundaries. Include only decisions necessary to implement and verify it. For a small fix, the backlog row and focused evidence may be sufficient.

## Acceptance

- <Observable result and its verification>
- <Relevant failure or recovery behavior>

## Approach and dependencies

List affected components, necessary steps, dependencies, significant risks, and rollback where relevant. Use the actual architecture; a processing stage is optional, not a universal task field.

## Checkpoint and evidence

Record completed work, checks actually run, evidence paths, remaining work, and unresolved decisions. Identify self-review versus independent review. Completion follows `docs/TASK_BACKLOG_AUTOMATION.md` and `AGENTS.md`; a separate role or handoff JSON is not required for local work.
