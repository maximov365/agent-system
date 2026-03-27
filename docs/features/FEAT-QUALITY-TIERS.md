# Feature: FEAT-QUALITY-TIERS — Translation Quality Tiers
Feature ID: FEAT-QUALITY-TIERS
Capability: TRANSLATE
Status: draft
Owner: unassigned
Priority: medium
Created by: Product agent
Related PRD section: Translation Options
Related Features: none
Pipeline stage: translation (cross-cutting: job submission, credit estimation)

---

# Summary

Translation Quality Tiers allow users to choose between three quality levels before submitting a translation job: **Express** (fast and cheap), **Standard** (optimal quality, recommended, default), and **Premium** (highest quality, slower and more expensive). Each tier maps to a distinct Claude model. Credit cost scales with the tier. This gives users direct control over the speed-cost-quality trade-off for each book.

---

# Problem

- Currently all jobs use the same translation model, configured globally via the `TRANSLATION_MODEL` env var. Users cannot choose a cheaper, faster option or a higher-quality option on a per-job basis.
- A user doing a quick first-read of a novel needs something different from a user studying a text in depth. There is no way to express that preference.
- All users pay the same credit cost regardless of how much quality they actually need, making the pricing feel inflexible.

---

# Goals

- Allow users to choose a quality tier at job submission time.
- Map each tier to a distinct Claude model (Express → fast/cheap model, Standard → balanced model, Premium → best model).
- Scale the credit cost by a per-tier multiplier so pricing reflects actual LLM cost.
- Display the selected tier's estimated credit cost to the user before submission.
- Maintain backward compatibility: existing jobs without a `quality_tier` field behave as Standard.

---

# Non-Goals

- Admin-configurable tier pricing overrides per user or plan.
- Per-language or per-mode tier restrictions.
- Exposing technical model names to users in the UI.
- A/B testing or automatic model selection.
- Multi-provider routing (stays single Anthropic provider per DEC-003).
- Tier-level SLA or ETA guarantees.
- Dynamic tier pricing (multipliers are config-level constants).

---

# User Flow

1. User uploads an EPUB and completes the precheck step.
2. In the job configurator, the user sees a **Quality** section with three radio options: Express, Standard (default), Premium, each with a brief description of the trade-off.
3. As the user changes the tier, the credit estimate updates to reflect the multiplier.
4. The user submits the job. The selected `quality_tier` is sent with the job config.
5. The backend validates the tier, stores it in `job_config.quality_tier`, selects the appropriate model, and applies the tier multiplier to credit reservation.

---

# Functional Requirements

- The upload page must show three tier options as radio cards, matching the `ModeCard` pattern already used for translation mode.
- Standard must be selected by default.
- The `quality_tier` value (`"express"` | `"standard"` | `"premium"`) must be included in the job submission payload.
- `POST /config/estimate` must accept an optional `quality_tier` parameter and apply the corresponding credit multiplier to the estimate.
- `POST /jobs` must validate `quality_tier`; unknown values are rejected with 422.
- The translation provider must read `quality_tier` from `job_config` and select the model accordingly.
- Jobs without `quality_tier` default to `"standard"` behavior (backward compat).
- Tier-to-model mapping is stored in `app/config/policy.py` as a constant (not hardcoded in the provider).

---

# MVP Slice

Three-tier radio selector in the upload UI, `quality_tier` stored in `job_config`, tier-aware credit multiplier in `estimate_credits`, and tier-to-model mapping read by `AnthropicProvider`. No admin controls, no per-tier SLAs, no model name exposure in UI.

---

# Constraints

- DEC-003: model selection must come from configuration, not hardcoded logic. Tier-to-model mapping must be a config constant.
- DEC-003: only the `translation` stage may invoke LLMs. Tier routing stays inside `AnthropicProvider`.
- DEC-003: single Anthropic provider only. No new providers.
- `job_config` is a JSON column — `quality_tier` is a new key, safe to add without a migration.
- Backward compat: jobs without `quality_tier` must work; provider falls back to Standard model.

---

# Open Questions

- None. Assumption: credit multipliers are Express=0.5×, Standard=1.0×, Premium=2.5×. Exact values can be tuned post-launch based on actual Anthropic pricing per model.

---

# Risks

- Anthropic may deprecate specific model slugs. Mitigated: model names are in config constants, not hardcoded.
- Premium model may be significantly slower, affecting user UX expectations. Mitigated: tier description in UI sets expectations.
- Credit multiplier values may not accurately reflect actual LLM cost differences. Mitigated: multipliers are constants, easily adjusted.

---

# Success Criteria

- Upload form shows three tier options; Standard is selected by default.
- Selecting a tier updates the credit estimate in the UI.
- `quality_tier` is stored in `job_config` and visible in job detail.
- Translation uses the correct model for each tier.
- Jobs without `quality_tier` complete successfully using Standard behavior.
- Unknown `quality_tier` values are rejected with 422 by the API.
- Unit tests cover tier validation, credit multiplier, and model selection.

---

# Tasks

## Task 1 — Add quality tier policy constants and validation [MVP]
- complexity: small
- goal: Add `QUALITY_TIERS`, `TIER_CREDIT_MULTIPLIERS`, and `VALID_QUALITY_TIERS` to `app/config/policy.py`; extend `validate_job_config` to validate `quality_tier`; add `estimate_credits` multiplier support.
- scope: `app/config/policy.py`
- dependencies: none
- acceptance criteria:
  - `QUALITY_TIERS` constant defines `express`, `standard`, `premium` with their credit multipliers
  - `validate_job_config` rejects unknown `quality_tier` values with a descriptive error
  - `estimate_credits` applies the tier multiplier when `quality_tier` is provided
  - Existing calls without `quality_tier` continue to work (defaults to `"standard"`)

## Task 2 — Tier-to-model mapping in translation provider [MVP]
- complexity: small
- goal: Add `TIER_MODELS` config constant in `app/config/policy.py`; update `AnthropicProvider` to read `quality_tier` from job config and select the correct model.
- scope: `app/config/policy.py`, `app/pipeline/translation/provider.py`
- dependencies: Task 1
- acceptance criteria:
  - `TIER_MODELS` maps each tier to a Claude model name (overridable via env vars)
  - `AnthropicProvider` selects model from `job_config["quality_tier"]` when present
  - Falls back to `TRANSLATION_MODEL` env var for jobs without `quality_tier`

## Task 3 — Expose `quality_tier` in estimate and job submission API [MVP]
- complexity: small
- goal: Add `quality_tier` to `EstimateRequest` and `SubmitJobRequest`; apply multiplier in estimate endpoint; pass tier through job submission.
- scope: `app/api/routers/config.py`, `app/api/routers/jobs.py` (or the submit router)
- dependencies: Task 1
- acceptance criteria:
  - `POST /config/estimate` accepts optional `quality_tier` and applies multiplier
  - `POST /jobs` validates `quality_tier` and stores it in `job_config`
  - Unknown `quality_tier` in submission returns 422

## Task 4 — Tier selector in upload UI [MVP]
- complexity: small
- goal: Add three-option tier radio selector to `web/app/[locale]/upload/page.tsx`; pass `quality_tier` in `estimateCredits` and `submitJob` calls; add i18n strings.
- scope: `web/app/[locale]/upload/page.tsx`, `web/lib/api.ts`, `web/messages/en.json`, `web/messages/ru.json`, `web/messages/sr.json`
- dependencies: Tasks 1–3
- acceptance criteria:
  - Three tier radio cards shown; Standard selected by default
  - Changing tier triggers estimate refresh
  - `quality_tier` included in job submission payload
  - UI strings translated in en/ru/sr

## Recommended Next Task
Task 1 — foundational policy constants that all other tasks depend on.

## docs/TASKS.md Update
Add tasks TASK-25 through TASK-28 for FEAT-QUALITY-TIERS (Task 1–4 above).

## Assumptions Made
- Credit multipliers: Express=0.5×, Standard=1.0×, Premium=2.5×. Specific Claude model slugs assigned at Architect stage.
- `quality_tier` stored as a string key inside the existing `job_config` JSON column — no DB migration needed.
- Tier UI description text written in Product spec; Architect confirms no changes needed to prompt templates.
