# Eval Task: API Endpoint

## Prompt

Add a read-only API endpoint that returns the current user's notification preferences. The endpoint must validate authentication, avoid exposing internal IDs, and include tests for authorized and unauthorized access.

## Intended Workflow

Use `workflow_mode: standard`.

Expected path:

```text
Product or Architect → Spec Reviewer/Gatekeeper when needed → Test Strategist → Builder → Security Reviewer → Reviewer
```

## Success Criteria

- Acceptance criteria are explicit before implementation.
- Authentication behavior is tested.
- Response shape does not leak internal implementation details.
- Security Reviewer evaluates authorization and data exposure.
