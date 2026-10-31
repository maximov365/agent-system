# Optional structured analytics review

Load only for an explicitly selected structured integration. Follow the ordinary
analytics method; the schema does not require a separate agent or approval loop.
Use accept with no blockers, revise for fixable defects, and escalate only for an
unresolved material decision/authorization. Missing evidence is a finding, not a
fabricated pass.

```json
{
  "spec_path": "<path to Analytics Specification>",
  "implementation_scope": ["<file changed by Builder>"],
  "events_expected": ["<event_name from Analytics Specification>"],
  "events_checked": ["<event_name actually validated>"],
  "validation_results": {
    "event_existence": "pass | fail",
    "trigger_correctness": "pass | fail",
    "schema_correctness": "pass | fail",
    "semantic_correctness": "pass | fail",
    "metrics_computable": "pass | fail"
  },
  "must_fix": [
    {
      "event": "<event_name>",
      "check": "event_existence | trigger_correctness | schema_correctness | semantic_correctness | metrics_computable",
      "issue": "<concise description of the problem>",
      "reason": "<why this blocks acceptance>"
    }
  ],
  "should_fix": [
    {
      "event": "<event_name>",
      "check": "<check category>",
      "suggestion": "<concise improvement>"
    }
  ],
  "verdict": "accept | revise | escalate",
  "verdict_reason": "<one sentence explaining the verdict>",
  "escalation_reason": null
}
```

`events_expected` lists specified events; `events_checked` lists events actually
verified. If one could not be checked, retain that gap in must_fix and do not add
it to events_checked. Per-category results fail when their evidence is missing
or a blocker exists. Populate escalation_reason only for a real escalation.
Preserve field names and list all findings. Add a handoff under
docs/AGENT_HANDOFF_CONTRACT.md only when an actual adapter consumes it.
