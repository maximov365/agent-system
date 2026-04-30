# Eval Task: Analytics Instrumentation

## Prompt

Instrument a feature so the product team can measure when users complete onboarding. Define the event, properties, and validation plan before implementation.

## Intended Workflow

Use `workflow_mode: standard` or `strict` depending on product risk.

Expected path:

```text
Product → Analytics Architect → Architect → Test Strategist → Builder → Analytics Validator → Security Reviewer → Reviewer
```

## Success Criteria

- Analytics Architect defines event name, properties, and instrumentation location.
- Architect includes instrumentation in the implementation plan.
- Builder implements the event without weakening product logic.
- Analytics Validator verifies the implementation before Security Reviewer.
