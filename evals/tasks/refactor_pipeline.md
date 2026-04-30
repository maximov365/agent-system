# Eval Task: Refactor Pipeline

## Prompt

Refactor a pipeline stage so validation happens at the stage boundary instead of inside downstream consumers. Preserve existing behavior and tests. Do not introduce a new pipeline stage.

## Intended Workflow

Use `workflow_mode: strict` when the change touches multiple stages or shared contracts.

Expected path:

```text
Discovery → Architect → Spec Reviewer/Gatekeeper → Test Strategist → Builder → Security Reviewer → Reviewer
```

## Success Criteria

- Pipeline boundaries remain explicit.
- Stage input/output contracts are preserved or documented.
- Existing tests still pass.
- New tests cover boundary validation.
- Architecture guardrails are not weakened.
