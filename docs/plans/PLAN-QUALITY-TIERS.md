# Implementation Plan: FEAT-QUALITY-TIERS — Translation Quality Tiers

**Task Restatement:** Add Express/Standard/Premium quality tiers to the job submission flow, mapping each tier to a distinct Claude model, scaling credit estimates by a per-tier multiplier, and surfacing a tier selector in the upload UI.

---

## Plan

### Step 1 — Add quality tier constants to `app/config/policy.py` [small]
Add:
- `VALID_QUALITY_TIERS: FrozenSet[str]` = `{"express", "standard", "premium"}`
- `TIER_CREDIT_MULTIPLIERS: dict[str, Decimal]` = `{"express": 0.5, "standard": 1.0, "premium": 2.5}`
- `TIER_MODELS: dict[str, str]` mapping each tier to a Claude model env var or fallback slug
- Update `estimate_credits(...)` to accept optional `quality_tier: str = "standard"` and multiply by `TIER_CREDIT_MULTIPLIERS[quality_tier]`
- Update `validate_job_config(...)` to accept and validate optional `quality_tier` parameter

Tier-to-model mapping (all overridable via env vars per DEC-003):
- `express`: `TRANSLATION_MODEL_EXPRESS` → default `"claude-haiku-4-5-20251001"`
- `standard`: `TRANSLATION_MODEL_STANDARD` → default `"claude-sonnet-4-5-20251001"`
- `premium`: `TRANSLATION_MODEL_PREMIUM` → default `"claude-opus-4-5-20251001"`

### Step 2 — DB migration: add `quality_tier` column to `jobs` table [small]
Create `alembic/versions/0015_add_job_quality_tier.py`:
- `ALTER TABLE jobs ADD COLUMN quality_tier VARCHAR(20) NULL`
- No default at DB level (NULL means Standard; application-level default handles it)
- No downgrade data loss risk

Update `app/db/models/job.py`:
- Add `quality_tier: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)`

### Step 3 — Add `quality_tier` to `TranslationConfig` and update orchestrator [small]
In `app/pipeline/translation/models.py`:
- Add `quality_tier: str = "standard"` to `TranslationConfig`

In `app/worker/orchestrator.py` (`_run_translate`):
- Read `job.quality_tier or "standard"` and pass to `TranslationConfig`
- Resolve model via `TIER_MODELS.get(quality_tier, _DEFAULT_MODEL)` from policy
- Pass resolved model to `AnthropicProvider(model=resolved_model)`

### Step 4 — Update `submit_job` service and jobs API router [small]
In `app/domain/services/job_service.py` (`submit_job`):
- Add optional `quality_tier: str = "standard"` parameter
- Validate via `validate_job_config` (which now checks `quality_tier`)
- Store in `job.quality_tier`

In `app/api/routers/jobs.py` (`SubmitJobRequest`):
- Add `quality_tier: Optional[str] = "standard"` field
- Pass to `submit_job(..., quality_tier=body.quality_tier)`
- Emit `job_tier_selected` analytics event after successful queue admission (per analytics spec)

### Step 5 — Update `POST /config/estimate` to accept quality_tier [small]
In `app/api/routers/config.py` (`EstimateRequest`):
- Add `quality_tier: Optional[str] = "standard"` field
- Pass to `estimate_credits(...)` and `validate_job_config(...)`

### Step 6 — Add tier selector to upload UI [small]
In `web/app/[locale]/upload/page.tsx`:
- Add `quality_tier` state (default `"standard"`)
- Add `QUALITY_TIERS` array with three options (using `t("tierExpressLabel")` etc.)
- Render as `ModeCard` radio buttons (same pattern as mode selection)
- Include `quality_tier` in `fetchEstimate(...)` call and `estimateCredits` API params
- Include `quality_tier` in `handleSubmit` → `api.submitJob(...)` payload

In `web/lib/api.ts`:
- Add `quality_tier?: string` to `SubmitJobRequest` interface
- Add `quality_tier?: string` to `estimateCredits` params and request body

In `web/messages/en.json`, `ru.json`, `sr.json`:
- Add tier label/description strings for Express, Standard, Premium

### Step 7 — Emit `job_tier_selected` analytics event [small]
In `app/api/routers/jobs.py` (after successful `submit_job` + `session.commit()`):
- Emit `job_tier_selected` event via `log_structured` with fields: `job_id`, `user_id`, `quality_tier`, `mode`, `target_language`, `estimated_credits`, `model_name`
- Read `model_name` from `TIER_MODELS` constant

### Step 8 — Tests [small]
- `tests/test_quality_tiers.py`: unit tests for tier validation, credit multiplier, model mapping
- Update `tests/test_credits_api.py` or add to existing tests: estimate endpoint with quality_tier param
- Update `tests/test_job_retry.py` or add submission tests: job submission with quality_tier stored correctly

---

## Acceptance Criteria
- Three tier options visible in the upload UI; Standard selected by default
- Changing tier updates credit estimate in the UI
- `quality_tier` stored in `job.quality_tier` column after submission
- Unknown `quality_tier` (e.g. `"ultra"`) returns 422 from `POST /jobs`
- Translation uses the correct model per tier (verified via test with provider mock)
- Jobs without `quality_tier` (NULL) complete using Standard model behavior
- `job_tier_selected` event emitted exactly once per successfully queued job
- All existing tests continue to pass

---

## Non-goals
- DB migration for historical jobs (NULL = standard is acceptable)
- Admin UI for tier pricing
- UI exposure of model names
- Multi-provider routing

---

## Dependencies
- external: none
- internal: `app/config/policy.py`, `app/db/models/job.py`, `app/domain/services/job_service.py`, `app/pipeline/translation/models.py`, `app/worker/orchestrator.py`, `app/api/routers/jobs.py`, `app/api/routers/config.py`

---

## Files
- modify: `app/config/policy.py` — add VALID_QUALITY_TIERS, TIER_CREDIT_MULTIPLIERS, TIER_MODELS; update estimate_credits, validate_job_config
- modify: `app/db/models/job.py` — add quality_tier column
- create: `alembic/versions/0015_add_job_quality_tier.py` — migration
- modify: `app/pipeline/translation/models.py` — add quality_tier to TranslationConfig
- modify: `app/worker/orchestrator.py` — pass quality_tier to TranslationConfig and AnthropicProvider
- modify: `app/domain/services/job_service.py` — accept and store quality_tier
- modify: `app/api/routers/jobs.py` — add quality_tier to SubmitJobRequest; emit analytics event
- modify: `app/api/routers/config.py` — add quality_tier to EstimateRequest
- modify: `web/app/[locale]/upload/page.tsx` — add tier selector UI
- modify: `web/lib/api.ts` — add quality_tier to SubmitJobRequest and estimateCredits
- modify: `web/messages/en.json`, `web/messages/ru.json`, `web/messages/sr.json` — add tier i18n strings
- create: `tests/test_quality_tiers.py` — new tests

---

## Risks
- `AnthropicProvider` model is currently set at construction time. In the orchestrator, it is constructed with `AnthropicProvider()`. This plan changes that to `AnthropicProvider(model=resolved_model)` — safe, the constructor already accepts an optional `model` parameter.
- The `claude-sonnet-4-5-20251001` and `claude-opus-4-5-20251001` slugs are assumptions; if Anthropic changes naming, they must be updated in env vars. This is consistent with DEC-003 (model from config).

---

## Architectural Notes
- `quality_tier` is a first-class column on `Job`, not stored in a JSON blob, consistent with how all other config fields are stored on `Job`.
- Model resolution happens in the orchestrator (at pipeline start), not in the provider itself, to keep model selection visible and testable at the orchestration boundary.
- The analytics event is emitted in the API layer (after queue admission), not in the worker, so it fires exactly once per submission regardless of retry behavior.

---

## Assumptions Made
- Claude model slugs: express = `claude-haiku-4-5-20251001`, standard = `claude-sonnet-4-5-20251001`, premium = `claude-opus-4-5-20251001`. All overridable via env vars.
- Credit multipliers: express = 0.5, standard = 1.0, premium = 2.5. Stored as `Decimal` constants.
- NULL `quality_tier` in the DB defaults to standard behavior in all code paths.

---

## Smallest Next Step
Add `VALID_QUALITY_TIERS`, `TIER_CREDIT_MULTIPLIERS`, and `TIER_MODELS` to `app/config/policy.py` and update `estimate_credits` and `validate_job_config`.
