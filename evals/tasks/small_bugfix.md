# Eval Task: Small Bugfix

## Prompt

A downstream project has a function that returns `None` when it receives an empty input list. It should return an empty list instead. Fix the behavior and add the smallest relevant test.

## Intended Workflow

Use `workflow_mode: lite` unless the repository context shows broader risk.

Expected path:

```text
Architect → Builder → Security Reviewer → Reviewer
```

## Success Criteria

- The fix is local and minimal.
- A focused test covers the empty-input behavior.
- No unrelated files are modified.
- Security Reviewer and Reviewer are not skipped.
