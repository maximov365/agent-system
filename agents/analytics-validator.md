# Analytics validation method

Verify instrumentation for {{ project.name }} against its event specification,
under `AGENTS.md`. Use this method when events, triggers, payloads or metrics
change. The current owner may validate locally; no separate agent or automatic
review chain is required. Preserve the active model/effort under
`docs/MODEL_POLICY.md`.

Read the event specification, affected implementation and tests. Consult real
pipeline/architecture contracts when trigger boundaries matter. Validate specified
behavior rather than designing new metrics. If the specification conflicts with
current constraints, inspect evidence and report the conflict; ask the user only
when a material decision or authorization is missing.

A review-only request returns findings. When fixes are authorized, the owner can
repair implementation defects and revalidate affected behavior. Changes to product
intent or schemas need applicable scope; the role does not grant that authority.

## Validation priorities

Validate in this order. Report all findings, not just the first failure.

### 1. Event existence

Verify that each event named in the Analytics Specification exists in the implementation.

Check:
- Event name matches exactly (case-sensitive, snake_case)
- Event is emitted in the correct pipeline stage: `{{ pipeline.stages | map(attribute='name') | join(' | ') }}`
- Event is emitted within the correct pipeline module corresponding to the declared stage — not from an adjacent or downstream stage
- Emission point is reachable under normal execution

### 2. Trigger correctness

Verify that each event fires at the correct moment as defined by its trigger in the specification.

Check:
- Event fires after the specified condition is met, not before
- Event does not fire when the trigger condition is absent
- Event fires at most once per logical action unless the schema includes an attempt or sequence counter
- Event fires on both success and failure paths if the specification requires it
- Event emission does not depend on nondeterministic conditions (random values, time-based branching, or retry loops without attempt counters)

### 3. Schema correctness

Verify that each event payload matches the specified schema.

Check:
- Required base fields are present: `event` (string) and `timestamp` (ISO8601)
- The `event` field value matches the declared event name exactly (case-sensitive)
- All required fields are present and non-null
- Field types match the specification (`string`, `int`, `float`, `bool`, `ISO8601`, `enum[...]`)
- No unexpected fields are present in the payload that are not in the schema
- The payload does not contain undocumented fields that expose internal implementation details (debug flags, stack traces, temporary values, internal state)
- Optional fields, if present, conform to their specified type

### 4. Semantic correctness

Verify that field values are meaningful and within valid ranges.

Check:
- `processing_time_ms` — positive integer
- `retry_count` — non-negative integer, 0 on first attempt
- `timestamp` — valid ISO8601 string
- `success` — correctly set to `false` when an exception or failure occurred
- `model_name` — matches the configuration constant, not a hardcoded string
- Enum fields — value is one of the allowed values
- No raw document content or full text segments in any field
- No PII: no email addresses, IP addresses, user-identifiable strings

### 5. Metrics computability

Verify that each metric defined in the Analytics Specification can be computed from the implemented events.

Check:
- The source event for each metric exists and is emitted
- The fields required to compute the metric are present in the payload
- Field types are compatible with the computation (e.g. numeric fields for averages)

---

## Error categories

### must_fix

Blocking issues that prevent acceptance. Builder must resolve before Reviewer proceeds.

- Event defined in specification is missing from implementation
- Event fires at wrong pipeline stage
- Event fires with incorrect trigger (too early, too late, not on failure path)
- Event fires multiple times for the same action without an attempt counter
- Required field missing or null
- Field type does not match specification
- Unexpected field present in payload that is absent from schema
- Field value semantically incorrect (negative time, wrong enum value)
- Metric cannot be computed due to missing event or field
- PII detected in payload
- Raw document content detected in payload

### should_fix

Non-blocking issues that reduce quality but do not prevent acceptance.

- Optional field absent when it would improve traceability (e.g. `request_id`, `pipeline_run_id`)
- Missing recommended correlation identifiers (`request_id`, `pipeline_run_id`, `item_id`) when they are available in the execution context
- Event name deviates from `<object>_<action>` naming convention
- Minor value inconsistency that does not affect metric computability

---


## Evidence and verdict

Accept only when required events, triggers, schemas, values and metrics have
supporting evidence and no material blocker remains. Revise for correctable
instrumentation defects. Escalate only a material unresolved decision/authority
conflict; an architectural question alone does not suspend authorized work.

Lead with findings, exact event/field/trigger, impact and evidence. Report all
material issues and unverified events. Names alone do not establish behavior;
never mark an event checked without inspecting its evidence. Keep PII/raw-content,
duplicate emission and failure-path checks. Separate optional improvements from
blocking omissions without adding unrequested events.

Only an explicitly selected integration needs
[the legacy JSON adapter](review-modes/structured-analytics.md). Preserve its field
names while keeping events_checked honest; an unverified expected event is a gap,
not a fabricated pass. No handoff is needed in ordinary local work.
