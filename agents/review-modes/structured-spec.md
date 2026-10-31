# Optional structured specification review

Load only when the caller explicitly selects the legacy structured adapter.
The current owner retains authority under AGENTS.md; these fields do not create
separate agents, permissions or an extra user approval step.

## Scoring rubric

Score each dimension from 1 to 10:

| Score | Meaning |
|---|---|
| 9–10 | Excellent — no meaningful gaps |
| 7–8 | Good — minor issues, no blockers |
| 5–6 | Acceptable — fixable gaps present |
| 3–4 | Weak — significant issues that will cause problems downstream |
| 1–2 | Poor — missing or fundamentally unclear |

### Dimensions

- **problem_clarity** — is the problem well defined and grounded in a real user need?
- **goal_clarity** — is the desired outcome specific and measurable?
- **scope_discipline** — is the scope tight? No hidden scope creep, no bundled unrelated work?
- **prd_alignment** — does the artifact align with `docs/PRD.md`?
- **architecture_fit** — is the approach compatible with `docs/ARCHITECTURE.md` and pipeline constraints?
- **acceptance_criteria_quality** — are criteria testable, concrete, and sufficient to verify completion?
- **task_decomposition_quality** — are tasks independent, small enough to review, and sequenced correctly?
- **risk_dependency_clarity** — are risks, blockers, and dependencies identified and actionable?
- **ambiguity_control** — are all assumptions explicit? Are open questions listed rather than silently resolved?
- **mvp_fit** — does the artifact scope the smallest valuable increment? Is MVP clearly separated from follow-ups?

**overall_score** is the arithmetic mean of all ten dimension scores, rounded to one decimal place.

---


Emit the following JSON schema and a handoff only when an actual adapter consumes
it. Preserve an iteration supplied by the caller; do not invent completed passes.
Use the listed artifact types. `accept` requires overall_score >= 7.5 and no
must_fix findings; `revise` covers remaining correctable gaps. `escalate` takes
priority only for a material unresolved decision/authorization that the owner
cannot resolve from current evidence. Architectural changes or dependencies alone
do not require user escalation. Scores are review judgments, not measured quality.

```json
{
  "artifact_type": "feature_spec | task_breakdown | implementation_plan | design_note | decision_note | analytics_spec | design | animation | ux_copy | marketing_campaign | illustration | video | test_plan",
  "artifact_path": "<path or title of the artifact being reviewed>",
  "iteration": "<current iteration number, e.g. 1>",
  "cove_applied": true,
  "dimension_scores": {
    "problem_clarity": 0.0,
    "goal_clarity": 0.0,
    "scope_discipline": 0.0,
    "prd_alignment": 0.0,
    "architecture_fit": 0.0,
    "acceptance_criteria_quality": 0.0,
    "task_decomposition_quality": 0.0,
    "risk_dependency_clarity": 0.0,
    "ambiguity_control": 0.0,
    "mvp_fit": 0.0
  },
  "overall_score": 0.0,
  "must_fix": [
    {
      "dimension": "<dimension name>",
      "issue": "<concise description of the problem>",
      "reason": "<why this will cause problems downstream>"
    }
  ],
  "should_fix": [
    {
      "dimension": "<dimension name>",
      "suggestion": "<concise improvement suggestion>"
    }
  ],
  "source_conflicts": [
    {
      "source": "<AGENTS.md | docs/PRD.md | docs/DECISIONS.md | docs/ARCHITECTURE.md | …>",
      "conflict": "<what the artifact says vs what the source says>"
    }
  ],
  "verdict": "accept | revise | escalate",
  "verdict_reason": "<one sentence explaining the verdict>"
}
```

Record actual source conflicts, observed evidence and honest CoVe usage. Keep
field names compatible. An actual handoff follows docs/AGENT_HANDOFF_CONTRACT.md.
