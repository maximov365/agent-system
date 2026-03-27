## Analytics Specification

**Feature:** FEAT-QUALITY-TIERS — Translation Quality Tiers
**Prepared for:** Architect and Builder
**Related tasks:** TASK-25, TASK-26, TASK-27, TASK-28

---

### Analytics Goal

Measure which quality tier users select when submitting translation jobs, how tier choice correlates with credit consumption and pipeline success, and whether tier selection patterns shift over time — to inform pricing, model selection defaults, and product positioning.

---

### Events

#### Event: `job_tier_selected`
**Pipeline stage:** translation (emitted at job submission / queue admission)
**Trigger:** A job is successfully enqueued (status transitions from `validating` to `queued`) and a `quality_tier` value is present in `job_config`.
**Properties:**
- `event`: string — always `"job_tier_selected"`
- `timestamp`: ISO8601 — when the event is emitted
- `job_id`: string — UUID of the job
- `user_id`: string — UUID of the submitting user
- `quality_tier`: enum["express", "standard", "premium"] — selected tier
- `mode`: string — `"translate"` or `"guided"`
- `target_language`: string — BCP-47 target language code
- `estimated_credits`: int — credit estimate shown to user at submission time
- `model_name`: string — resolved Claude model name for this tier

**Example payload:**
```json
{
  "event": "job_tier_selected",
  "timestamp": "2026-03-25T10:00:00Z",
  "job_id": "a1b2c3d4-...",
  "user_id": "u1u2u3u4-...",
  "quality_tier": "standard",
  "mode": "translate",
  "target_language": "ru",
  "estimated_credits": 45,
  "model_name": "claude-sonnet-4-5-20251001"
}
```

---

### Event Schema

#### `job_tier_selected`
```json
{
  "event": "string",
  "timestamp": "ISO8601",
  "job_id": "string",
  "user_id": "string",
  "quality_tier": "enum[express, standard, premium]",
  "mode": "string",
  "target_language": "string",
  "estimated_credits": "int",
  "model_name": "string"
}
```

All fields are required.

---

### Metrics

**Product metrics:**
- `tier_adoption_rate`
  definition: count(job_tier_selected where quality_tier=X) / count(job_tier_selected) grouped by quality_tier
  source: `job_tier_selected`

- `tier_credit_volume`
  definition: sum(estimated_credits) grouped by quality_tier
  source: `job_tier_selected`

**Quality metrics:**
- `tier_model_distribution`
  definition: count(job_tier_selected) grouped by model_name — verifies each tier routes to a distinct model
  source: `job_tier_selected`

**System metrics:**
- `tier_submission_rate`
  definition: count(job_tier_selected) per hour grouped by quality_tier — operational volume by tier
  source: `job_tier_selected`

---

### Instrumentation Requirements

Builder must:
- Emit `job_tier_selected` once per job at the point where the job transitions to `queued` status (inside `submit_job` in `app/domain/services/job_service.py` or the jobs API router, after successful queue admission).
- Set `quality_tier` from `job_config.get("quality_tier", "standard")`.
- Set `model_name` to the resolved model for that tier (read from `TIER_MODELS` config constant).
- Set `estimated_credits` from `job_config.get("credit_estimate", 0)`.
- Emit using the existing `log_structured` infrastructure (same pattern as `emit_event` in `app/analytics/events.py`).
- The event must not fire if the job fails validation or queue admission fails.
- No PII (user email, raw text) in the payload.

---

### Validation Rules

Analytics Validator must verify:
- `job_tier_selected` is emitted exactly once per successfully queued job.
- `quality_tier` is one of `"express"`, `"standard"`, `"premium"`.
- `model_name` is a non-empty string.
- `estimated_credits` is a non-negative integer.
- `job_id` and `user_id` are valid UUID strings.
- The event is NOT emitted when job submission fails (validation error, insufficient credits, active job exists).
- No PII fields (`email`, raw text content) are present.
- Event timestamp is a valid ISO8601 string.

---

### Assumptions Made
- Reusing `log_structured` for event emission (same pattern as existing auth events). No new analytics infrastructure required.
- Jobs that predate this feature (no `quality_tier` in `job_config`) do not emit `job_tier_selected` — only new submissions do.
