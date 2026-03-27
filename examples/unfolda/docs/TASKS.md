# Unfolda — Task Backlog

Status: active
Last updated: 2026-03-14

---

## About This File

All tasks are committed by Iteration Manager only.
Task statuses are updated by Iteration Manager only.
Agents must not write status changes directly — they surface them through handoff blocks.

Task lifecycle: planned → in_progress → implemented → in_review → approved → completed
Tasks are never deleted — use `cancelled` when a task is no longer needed.

---

## Task Index

| Task ID | Title | Feature | Status | Priority | Complexity |
|---|---|---|---|---|---|
| FEAT-1 | FEAT-AUTH — Authentication | FEAT-AUTH | completed | high | large |
| FEAT-2 | FEAT-SECURITY — Security & Privacy | FEAT-SECURITY | completed | high | large |
| TASK-1 | Create users and user_credit_account database schema | FEAT-AUTH | completed | high | small |
| TASK-2 | Configure Google OAuth and NextAuth.js in Next.js | FEAT-AUTH | completed | high | medium |
| TASK-3 | Implement FastAPI JWT authentication middleware | FEAT-AUTH | completed | high | medium |
| TASK-4 | Implement user provisioning on first login | FEAT-AUTH | completed | high | medium |
| TASK-5 | Implement admin flag and admin route guard | FEAT-AUTH | completed | medium | small |
| TASK-6 | Implement auth analytics instrumentation | FEAT-AUTH | completed | medium | small |
| TASK-7 | Add no-raw-text security guard for logs and errors | FEAT-SECURITY | approved | high | medium |
| TASK-8 | Enforce object ownership checks at API boundary | FEAT-SECURITY | completed | high | medium |
| TASK-9 | Implement signed URL policy enforcement | FEAT-SECURITY | completed | high | medium |
| TASK-10 | Add provider payload boundary validation | FEAT-SECURITY | completed | medium | medium |
| TASK-11 | Implement security audit events and break-glass log | FEAT-SECURITY | completed | medium | small |
| FIX-1 | Replace length heuristic in payload_guard with explicit key-based policy | FEAT-SECURITY | planned | low | small |
| FEAT-3 | FEAT-STORAGE — Object Storage | FEAT-STORAGE | completed | high | large |
| TASK-12 | Create artifact metadata DB model and migration | FEAT-STORAGE | completed | high | small |
| TASK-13 | Implement StorageClient adapter (boto3 wrapper) | FEAT-STORAGE | completed | high | medium |
| TASK-14 | Implement StorageService domain layer | FEAT-STORAGE | completed | high | medium |
| TASK-15 | Storage API endpoints and integration tests | FEAT-STORAGE | completed | high | medium |
| FEAT-4 | FEAT-TELEMETRY — Observability & Quality Validation | FEAT-TELEMETRY | completed | medium | large |
| TASK-16 | Create job_event DB model and migration | FEAT-TELEMETRY | completed | high | small |
| TASK-17 | Implement timeline event emitter | FEAT-TELEMETRY | completed | high | medium |
| TASK-18 | Implement benchmark infrastructure | FEAT-TELEMETRY | completed | medium | medium |
| FEAT-5 | FEAT-COST — Internal Cost Control | FEAT-COST | completed | medium | large |
| TASK-19 | Create cost_ledger_entry DB model and migration | FEAT-COST | completed | high | small |
| TASK-20 | Implement cost estimator and hard cap enforcement | FEAT-COST | completed | high | medium |
| TASK-21 | Implement cost ledger service | FEAT-COST | completed | high | medium |
| TASK-22 | Add Serbian language + LANGUAGE_CATALOG to policy; sync upload dropdown | FEAT-QUOTA | implemented | high | small |
| TASK-23 | Credit balance header + /credits/history endpoint + credits history page | FEAT-QUOTA | implemented | high | medium |
| TASK-24 | UI i18n with next-intl (14+1 languages) | FEAT-I18N | planned | high | large |
| FEAT-LEGAL | FEAT-LEGAL — Legal Pages and Cookie Consent | FEAT-LEGAL | completed | high | medium |
| TASK-73 | i18n strings for legal chrome (footer, cookie banner, login note) | FEAT-LEGAL | completed | high | small |
| TASK-74 | AppShell footer links + login ToS note | FEAT-LEGAL | completed | high | small |
| TASK-75 | Terms of Service page (/[locale]/terms) | FEAT-LEGAL | completed | high | small |
| TASK-76 | Privacy Policy page (/[locale]/privacy) | FEAT-LEGAL | completed | high | small |
| TASK-77 | Cookie consent banner component + integration | FEAT-LEGAL | completed | high | small |

---

## Tasks

---

### FEAT-2 — FEAT-SECURITY: Security & Privacy

```
task_id:              FEAT-2
title:                FEAT-SECURITY — Security & Privacy
type:                 feature
status:               completed
priority:             high
capability_id:        SECURITY
parent_feature:       FEAT-SECURITY
source_agent:         Product
source_artifact:      PROD-TB-SECURITY-001
description:          Implement cross-cutting security and privacy controls that prevent raw
                      book-content leakage, enforce ownership boundaries, constrain provider
                      payloads, and enforce signed URL access policy across API and storage
                      boundaries.
acceptance_criteria:
  - Raw book text is blocked from logs, telemetry, analytics payloads, and API error payloads
  - API endpoints enforce ownership checks so users cannot access data of other users
  - Signed URLs are object-scoped, short-lived, and purpose-specific
  - Provider payloads are limited to current batch + required bounded context
  - Security-relevant actions emit durable audit events
dependencies:
  - none
estimated_complexity: large
```

---

### FEAT-1 — FEAT-AUTH: Authentication

```
task_id:              FEAT-1
title:                FEAT-AUTH — Authentication
type:                 feature
status:               completed
priority:             high
capability_id:        AUTH
parent_feature:       FEAT-AUTH
source_agent:         Architect
source_artifact:      ARCH-PLAN-AUTH-001
description:          Implement full authentication for Unfolda MVP: Google OAuth login via
                      NextAuth.js, JWT-based auth boundary between Next.js and FastAPI, user
                      provisioning on first login (user record + credit account + initial grant +
                      ToS acceptance), session persistence, admin flag, and auth analytics
                      instrumentation.
acceptance_criteria:
  - User can complete Google OAuth flow and receive an active session
  - All FastAPI endpoints return HTTP 401 for missing or invalid JWT
  - First login creates exactly one user record and one credit account with the configured initial grant
  - Session survives browser refresh; logout clears session
  - tos_accepted_at is set on first login
  - is_admin users can access admin-guarded endpoints; non-admin users receive 403
  - user_registered event emitted once per new user; user_signed_in emitted on every login
dependencies:
  - none
estimated_complexity: large
```

---

### TASK-7 — Add no-raw-text security guard for logs and errors

```
task_id:              TASK-7
title:                Add no-raw-text security guard for logs and errors
type:                 implementation
status:               approved
priority:             high
capability_id:        SECURITY
parent_feature:       FEAT-SECURITY
source_agent:         Product
source_artifact:      PROD-TB-SECURITY-001
description:          Implement a shared security guard that redacts or rejects raw book text
                      before logging, telemetry emission, analytics event emission, or API error
                      serialization. This enforces POLICY-PRIVACY as a reusable boundary.
acceptance_criteria:
  - Structured logger wrappers prevent raw source/translated text fields from being emitted
  - API error payload builder strips source content and keeps metadata-only context
  - Telemetry event emission path rejects payloads containing raw text fields
  - Unit tests cover accepted metadata payloads and blocked raw-text payloads
dependencies:
  - none
estimated_complexity: medium
```

---

### TASK-8 — Enforce object ownership checks at API boundary

```
task_id:              TASK-8
title:                Enforce object ownership checks at API boundary
type:                 implementation
status:               completed
priority:             high
capability_id:        SECURITY
parent_feature:       FEAT-SECURITY
source_agent:         Product
source_artifact:      PROD-TB-SECURITY-001
description:          Add reusable API authorization helpers that verify authenticated `user_id`
                      ownership for job and artifact resources before read/write operations.
                      Requests that fail ownership checks return 403 with metadata-only error payloads.
acceptance_criteria:
  - Ownership dependency verifies `user_id` for job and artifact lookups
  - Unauthorized cross-user access attempts return 403
  - Ownership checks execute before business logic handlers
  - Integration tests cover allowed same-user access and denied cross-user access
dependencies:
  - TASK-3 (authenticated user resolution already exists)
estimated_complexity: medium
```

---

### TASK-9 — Implement signed URL policy enforcement

```
task_id:              TASK-9
title:                Implement signed URL policy enforcement
type:                 implementation
status:               completed
priority:             high
capability_id:        SECURITY
parent_feature:       FEAT-SECURITY
source_agent:         Product
source_artifact:      PROD-TB-SECURITY-001
description:          Implement policy-level signed URL issuance rules to ensure URLs are
                      object-scoped, short-lived, and purpose-specific (upload/download). Deny
                      issuance when ownership or purpose constraints are not satisfied.
acceptance_criteria:
  - URL issuance requires explicit object key and purpose
  - Expiration window is bounded by configuration and validated
  - Upload and download URLs cannot be used interchangeably
  - Ownership is verified before URL issuance
  - Tests cover valid issuance and policy-denied issuance
dependencies:
  - TASK-8 (ownership checks)
estimated_complexity: medium
```

---

### TASK-10 — Add provider payload boundary validation

```
task_id:              TASK-10
title:                Add provider payload boundary validation
type:                 implementation
status:               completed
priority:             medium
capability_id:        SECURITY
parent_feature:       FEAT-SECURITY
source_agent:         Product
source_artifact:      PROD-TB-SECURITY-001
description:          Add pre-flight payload validation for translation-provider calls to ensure
                      payloads contain only current batch source text, bounded consistency context,
                      and required configuration fields. Reject overscoped payloads before dispatch.
acceptance_criteria:
  - Validator rejects payloads containing full-book or unrelated chapter content
  - Validator enforces required fields for batch-only translation requests
  - Rejected payloads produce policy error class with metadata-only details
  - Unit tests cover accepted minimal payload and rejected overscoped payload
dependencies:
  - none
estimated_complexity: medium
```

---

### TASK-11 — Implement security audit events and break-glass log

```
task_id:              TASK-11
title:                Implement security audit events and break-glass log
type:                 implementation
status:               completed
priority:             medium
capability_id:        SECURITY
parent_feature:       FEAT-SECURITY
source_agent:         Product
source_artifact:      PROD-TB-SECURITY-001
description:          Implement durable audit events for signed URL issuance, policy rejections,
                      and exceptional break-glass access. Store metadata-only audit records with
                      actor, action, target identifiers, timestamp, and reason.
acceptance_criteria:
  - Signed URL issuance emits durable audit events
  - Security policy rejections emit durable audit events
  - Break-glass access path emits mandatory audit events with reason and actor
  - Audit records contain no raw book content
dependencies:
  - TASK-9 (signed URL policy path)
estimated_complexity: small
```

---

### FIX-1 — Replace length heuristic in payload_guard with explicit key-based policy

```
task_id:              FIX-1
title:                Replace length heuristic in payload_guard with explicit key-based policy
type:                 fix
status:               planned
priority:             low
capability_id:        SECURITY
parent_feature:       FEAT-SECURITY
source_agent:         Reviewer
source_artifact:      TASK-7
description:          Replace len(value) > 120 heuristic with an explicit forbidden-key
                      registry. This eliminates false positives on long metadata strings
                      while preserving raw-text protection.
acceptance_criteria:
  - No length-based checks remain in payload_guard.py
  - Forbidden keys are defined in an explicit registry/config
  - Existing 18 tests still pass
  - No false positives on display_name, email, error messages
dependencies:
  - TASK-7
estimated_complexity: small
```

---

### TASK-1 — Create users and user_credit_account database schema

```
task_id:              TASK-1
title:                Create users and user_credit_account database schema
type:                 implementation
status:               completed
priority:             high
capability_id:        AUTH
parent_feature:       FEAT-AUTH
source_agent:         Architect
source_artifact:      ARCH-PLAN-AUTH-001
description:          Create the users and user_credit_account tables via Alembic migration
                      and define SQLAlchemy ORM models. The users table holds Google identity,
                      admin flag, and ToS acceptance timestamp. The user_credit_account table
                      holds the current credit balance linked to a user.
acceptance_criteria:
  - users table created with columns: user_id (UUID PK), google_sub (unique), email,
    display_name, is_admin (bool default false), tos_accepted_at (nullable timestamp), created_at
  - user_credit_account table created with columns: account_id (UUID PK), user_id (FK → users),
    balance (int default 0), created_at, updated_at
  - Alembic migration applies cleanly on a fresh database and rolls back cleanly
  - SQLAlchemy models are importable and reflect table structure
  - No raw user content fields beyond email and display_name
dependencies:
  - none
estimated_complexity: small
```

**Files:**
- `create: src/db/models/user.py` — SQLAlchemy User and UserCreditAccount models
- `create: alembic/versions/<hash>_create_auth_tables.py` — migration

---

### TASK-2 — Configure Google OAuth and NextAuth.js in Next.js

```
task_id:              TASK-2
title:                Configure Google OAuth and NextAuth.js in Next.js
type:                 implementation
status:               completed
priority:             high
capability_id:        AUTH
parent_feature:       FEAT-AUTH
source_agent:         Architect
source_artifact:      ARCH-PLAN-AUTH-001
description:          Configure NextAuth.js with the Google provider in the Next.js web app.
                      On OAuth callback, NextAuth calls the backend provisioning endpoint to
                      resolve or create the user_id, then issues a signed JWT. The session
                      persists via a signed HTTP-only cookie. Protected routes are guarded by
                      Next.js middleware. Logout clears the session.
acceptance_criteria:
  - User is redirected to Google sign-in when clicking "Sign in with Google"
  - After successful OAuth, user is redirected to the main screen with an active session
  - Session cookie is HTTP-only and signed
  - Session survives browser refresh within the configured expiry window
  - Logout endpoint clears the session and redirects to the login screen
  - Protected routes redirect unauthenticated users to the login screen
  - Required env vars are documented in .env.local.example: GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET, NEXTAUTH_SECRET, NEXTAUTH_URL, BACKEND_URL
  - No Google credentials or access tokens are logged
dependencies:
  - TASK-4 (provisioning endpoint must exist before NextAuth callback can call it)
estimated_complexity: medium
```

**Files:**
- `create: web/app/api/auth/[...nextauth]/route.ts` — NextAuth.js route handler
- `create: web/lib/auth.ts` — NextAuth config (Google provider, JWT callback, session)
- `create: web/middleware.ts` — route protection middleware
- `modify: web/.env.local.example` — document required env vars

---

### TASK-3 — Implement FastAPI JWT authentication middleware

```
task_id:              TASK-3
title:                Implement FastAPI JWT authentication middleware
type:                 implementation
status:               completed
priority:             high
capability_id:        AUTH
parent_feature:       FEAT-AUTH
source_agent:         Architect
source_artifact:      ARCH-PLAN-AUTH-001
description:          Implement a FastAPI dependency (get_current_user) that validates the
                      Authorization: Bearer JWT on every authenticated request. The dependency
                      verifies the JWT signature using the shared NEXTAUTH_SECRET, decodes the
                      user_id, and injects it into the request context. Requests with missing
                      or invalid tokens receive HTTP 401. All protected routers declare this
                      dependency. Uses PyJWT as the JWT validation library.
acceptance_criteria:
  - Requests with a valid JWT return the resolved user_id
  - Requests with a missing Authorization header return HTTP 401
  - Requests with an invalid or expired JWT return HTTP 401
  - Requests with a malformed token return HTTP 401 (not 500)
  - The JWT secret is read from NEXTAUTH_SECRET environment variable, never hardcoded
  - get_current_user is the sole entry point for resolving user_id from a request
  - A unit test covers valid token, missing token, expired token, and invalid signature cases
dependencies:
  - TASK-1 (user model must exist for DB lookup)
estimated_complexity: medium
```

**Files:**
- `create: src/api/dependencies.py` — get_current_user dependency
- `create: tests/test_auth_middleware.py` — unit tests for JWT validation cases

---

### TASK-4 — Implement user provisioning on first login

```
task_id:              TASK-4
title:                Implement user provisioning on first login
type:                 implementation
status:               completed
priority:             high
capability_id:        AUTH
parent_feature:       FEAT-AUTH
source_agent:         Architect
source_artifact:      ARCH-PLAN-AUTH-001
description:          Implement the /auth/provision endpoint called by NextAuth.js during
                      sign-in. On first login: create user record, create user_credit_account
                      with the configured initial grant, create a credit_transaction record
                      (type: grant), record tos_accepted_at, and emit user_registered analytics
                      event. On subsequent logins: return existing user_id and emit
                      user_signed_in analytics event. The endpoint is idempotent: duplicate
                      calls for the same google_sub never create duplicate records. ToS
                      acceptance is implicit on first login per POLICY-COPYRIGHT MVP note; the
                      frontend shows a ToS link before the sign-in button is enabled.
acceptance_criteria:
  - First login creates exactly one user record and one user_credit_account record
  - user_credit_account.balance equals INITIAL_CREDIT_GRANT env var (default 100)
  - A credit_transaction record of type grant is created for the initial balance
  - tos_accepted_at is set on first login
  - Subsequent logins for the same google_sub return the existing user_id without
    creating duplicate records (idempotent)
  - user_registered event is emitted exactly once per new user
  - user_signed_in event is emitted on every login (first and subsequent)
  - Analytics event failures do not block the provisioning response
  - The endpoint is only callable with a valid Google identity token from NextAuth
  - A test covers: first login, duplicate first-login call, subsequent login
dependencies:
  - TASK-1 (users and user_credit_account tables must exist)
  - TASK-3 (JWT dependency required for endpoint authentication)
estimated_complexity: medium
```

**Files:**
- `create: src/api/routers/auth.py` — /auth/provision endpoint
- `create: src/domain/services/user_service.py` — provisioning logic, analytics emission
- `create: tests/test_user_provisioning.py` — provisioning integration tests

---

### TASK-5 — Implement admin flag and admin route guard

```
task_id:              TASK-5
title:                Implement admin flag and admin route guard
type:                 implementation
status:               completed
priority:             medium
capability_id:        AUTH
parent_feature:       FEAT-AUTH
source_agent:         Architect
source_artifact:      ARCH-PLAN-AUTH-001
description:          Add a require_admin FastAPI dependency that wraps get_current_user and
                      returns HTTP 403 if the resolved user does not have is_admin = true.
                      Admin status is set via a configurable ADMIN_EMAILS env var (comma-
                      separated list of email addresses) that is checked at provisioning time.
                      All admin-only routes declare the require_admin dependency.
acceptance_criteria:
  - require_admin dependency returns 403 for non-admin users
  - require_admin passes for users with is_admin = true
  - is_admin is set to true during provisioning if the user email is in ADMIN_EMAILS
  - is_admin defaults to false for all other users
  - A unit test covers admin-allowed and non-admin-forbidden cases
dependencies:
  - TASK-3 (get_current_user dependency must exist)
  - TASK-4 (provisioning must set is_admin correctly)
estimated_complexity: small
```

**Files:**
- `modify: src/api/dependencies.py` — add require_admin dependency
- `modify: src/domain/services/user_service.py` — check ADMIN_EMAILS at provisioning

---

### TASK-6 — Implement auth analytics instrumentation

```
task_id:              TASK-6
title:                Implement auth analytics instrumentation
type:                 implementation
status:               completed
priority:             medium
capability_id:        AUTH
parent_feature:       FEAT-AUTH
source_agent:         Architect
source_artifact:      ARCH-PLAN-AUTH-001
description:          Emit user_registered and user_signed_in analytics events per
                      POLICY-ANALYTICS. Events are fire-and-forget and must not block the
                      auth flow. Events contain only metadata (user_id, timestamp) and no
                      raw personal data or book content. Instrumentation is placed in
                      user_service.py within the provisioning path.
acceptance_criteria:
  - user_registered event is emitted on first login with user_id and timestamp
  - user_signed_in event is emitted on every login with user_id and timestamp
  - An exception in analytics emission is caught and logged at warning level; it does not
    propagate or block the provisioning response
  - Events contain no raw personal data beyond user_id (no email, name, or raw tokens)
  - Event schema is documented inline (event_name, user_id, timestamp)
dependencies:
  - TASK-4 (analytics calls are inside user_service.py provisioning logic)
estimated_complexity: small
```

**Files:**
- `modify: src/domain/services/user_service.py` — analytics event emission (already created in TASK-4; this task finalises the instrumentation)
- `create: src/analytics/events.py` — analytics event emitter interface (fire-and-forget wrapper)

---

### FEAT-3 — FEAT-STORAGE: Object Storage

```
task_id:              FEAT-3
title:                FEAT-STORAGE — Object Storage
feature:              FEAT-STORAGE
status:               in_progress
priority:             high
complexity:           large
parent_feature:       FEAT-STORAGE
```

---

### TASK-12 — Create artifact metadata DB model and migration

```
task_id:              TASK-12
title:                Create artifact metadata DB model and migration
feature:              FEAT-STORAGE
status:               in_progress
priority:             high
complexity:           small
parent_feature:       FEAT-STORAGE
dependencies:         TASK-1
```

**Files:**
- `create: app/db/models/artifact.py`
- `create: alembic/versions/0003_create_artifacts.py`
- `modify: app/db/models/__init__.py`

**Acceptance criteria:**
- `Artifact` model has fields: artifact_id (UUID PK), user_id (UUID NOT NULL FK → users), job_id (UUID nullable), artifact_type (String NOT NULL), object_key (String NOT NULL UNIQUE), size_bytes (BigInteger nullable), storage_status (String NOT NULL default 'active'), created_at (DateTime UTC), deleted_at (DateTime UTC nullable)
- Migration creates and rolls back `artifacts` table cleanly
- Model is importable without errors

---

### TASK-13 — Implement StorageClient adapter (boto3 wrapper)

```
task_id:              TASK-13
title:                Implement StorageClient adapter (boto3 wrapper)
feature:              FEAT-STORAGE
status:               planned
priority:             high
complexity:           medium
parent_feature:       FEAT-STORAGE
dependencies:         TASK-12
```

**Files:**
- `create: app/storage/__init__.py`
- `create: app/storage/client.py`
- `modify: requirements.txt`

**Acceptance criteria:**
- `StorageClientProtocol` defines `get_presigned_upload_url`, `get_presigned_download_url`, `delete_object`
- `BotoStorageClient` implements the protocol using boto3
- `FakeStorageClient` in-memory implementation for tests
- `get_storage_client()` FastAPI dependency returns `StorageClientProtocol`, overridable via `dependency_overrides`
- Configured from env: `S3_BUCKET_NAME`, `S3_ENDPOINT_URL`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`

---

### TASK-14 — Implement StorageService domain layer

```
task_id:              TASK-14
title:                Implement StorageService domain layer
feature:              FEAT-STORAGE
status:               planned
priority:             high
complexity:           medium
parent_feature:       FEAT-STORAGE
dependencies:         TASK-12, TASK-13
```

**Files:**
- `create: app/storage/service.py`

**Acceptance criteria:**
- `build_object_key(user_id, job_id, artifact_type, artifact_id)` → `users/{user_id}/jobs/{job_id}/{artifact_type}/{artifact_id}`; raises ValueError if job_id is None
- `register_artifact(session, client, user_id, job_id, artifact_type, size_bytes, expires_in_seconds)` → `(Artifact, upload_url_str)`; creates DB record before URL is issued
- `issue_download_url(session, client, artifact_id, user_id, expires_in_seconds)` → str; validates ownership and active status; emits AUDIT_SIGNED_URL_ISSUED
- `mark_artifact_deleted(session, artifact_id)` → None; sets storage_status='deleted', deleted_at=now; not exposed via API (used by FEAT-RETENTION cleanup worker)
- Expiry bounds enforced by `SignedUrlPolicyConfig.from_env()` before calling storage client
- Unit tests with FakeStorageClient cover: key format, ownership enforcement, expiry enforcement, deletion

---

### TASK-22 — Add Serbian + LANGUAGE_CATALOG; sync upload dropdown

```
task_id:              TASK-22
title:                Add Serbian language + LANGUAGE_CATALOG to policy; sync upload dropdown
feature:              FEAT-QUOTA
status:               implemented
priority:             high
complexity:           small
parent_feature:       FEAT-QUOTA
dependencies:         none
```

**Files:**
- `create: app/config/__init__.py`
- `create: app/config/policy.py`
- `create: web/app/(main)/upload/page.tsx`
- `create: tests/test_policy_languages.py`

**Changes:**
- `SUPPORTED_LANGUAGES` frozenset contains `"sr"` (Serbian) alongside 13 other MVP codes
- `LANGUAGE_CATALOG` tuple provides `code / name / tier` metadata for all 14 languages (used by API and UI)
- Upload dropdown `TARGET_LANGUAGES` aligned with backend set: `cs` and `ar` removed (not in MVP), `sr` (Serbian) added
- `GET /config/credits` backend endpoint returns current user's credit balance

**Acceptance criteria:**
- `"sr"` present in `SUPPORTED_LANGUAGES`
- `LANGUAGE_CATALOG` codes exactly equal `SUPPORTED_LANGUAGES`
- Serbian entry: `name = "Serbian"`, `tier = "standard"`
- Upload dropdown contains Serbian; does not contain `cs` or `ar`
- All 3 policy tests pass

---

### TASK-23 — Credit balance header + /credits/history endpoint + credits page

```
task_id:              TASK-23
title:                Credit balance in header + GET /credits/history + web credits page
feature:              FEAT-QUOTA
status:               implemented
priority:             high
complexity:           medium
parent_feature:       FEAT-QUOTA
dependencies:         TASK-1, TASK-4
```

**Files:**
- `create: app/api/routers/config.py` — `GET /config/credits` returning `{balance}`
- `create: app/api/routers/credits.py` — `GET /credits/history` returning transaction list
- `modify: app/main.py` — register config + credits routers
- `create: web/lib/backend-jwt.ts` — server-side HS256 JWT helper
- `create: web/app/api/backend/[...path]/route.ts` — BFF proxy using `getToken`
- `create: web/components/HeaderBar.tsx` — client component fetching balance on mount
- `create: web/components/AppShell.tsx` — shell with brand / nav / HeaderBar / logout
- `create: web/app/(main)/layout.tsx` — route group layout wrapping all main pages
- `create: web/app/(main)/page.tsx` — home page inside AppShell
- `create: web/app/(main)/credits/page.tsx` — transaction history table (client component)
- `modify: web/middleware.ts` — exclude `/api/backend` from auth redirect matcher
- `modify: web/lib/auth.ts` — fix strict-mode TypeScript narrowing for `profile.sub/email`
- `modify: web/package.json` — add `typescript`, `@types/*` devDependencies
- `create: web/tsconfig.json`
- `create: web/package-lock.json`
- `create: tests/test_credits_api.py`

**Acceptance criteria:**
- `GET /config/credits` returns `{"balance": N}` for authenticated user
- `GET /credits/history` returns list of `CreditHistoryRow` (type, amount, balance_after, created_at, job_id)
- Unauthenticated requests return 401
- Header shows "Credits: N" on load; shows "Credits: …" while loading
- `/credits` page shows transaction table; shows empty-state row when list is empty
- `npm run build` compiles without errors (env vars required at runtime, not build time)
- All backend tests pass (113 tests)

---

### TASK-24 — UI i18n with next-intl (14+1 languages)

```
task_id:              TASK-24
title:                UI i18n with next-intl — support all 14+1 target languages as UI languages
feature:              FEAT-I18N
status:               planned
priority:             high
complexity:           large
parent_feature:       FEAT-I18N
dependencies:         TASK-22, TASK-23
```

**Scope:** Route through Product → Architect → Builder before implementation.

---

### TASK-15 — Storage API endpoints and integration tests

```
task_id:              TASK-15
title:                Storage API endpoints and integration tests
feature:              FEAT-STORAGE
status:               planned
priority:             high
complexity:           medium
parent_feature:       FEAT-STORAGE
dependencies:         TASK-12, TASK-13, TASK-14
```

**Files:**
- `create: app/api/routers/storage.py`
- `modify: app/main.py`
- `create: tests/test_storage_service.py`
- `create: tests/test_storage_endpoints.py`

**Endpoints:**
- `POST /storage/artifacts` — register artifact + issue presigned upload URL; requires `artifact_type` and `job_id` in body; auth via `get_current_user`
- `GET /storage/artifacts/{artifact_id}/download-url` — issue presigned download URL; auth via `get_current_user`

**Acceptance criteria:**
- Valid upload URL issuance returns artifact_id, object_key, upload_url, expires_in_seconds
- Valid download URL issuance returns artifact_id, object_key, download_url, expires_in_seconds
- Cross-user access to download URL returns 403
- Artifact not found returns 404
- Invalid artifact_type returns 422
- Expiry out of policy bounds returns 400
- All error payloads use `build_safe_error_detail`
- No raw content in any log or response

---

### FEAT-LEGAL — Legal Pages and Cookie Consent

```
task_id:              FEAT-LEGAL
title:                FEAT-LEGAL — Legal Pages and Cookie Consent
type:                 feature
status:               completed
priority:             high
capability_id:        LEGAL
parent_feature:       FEAT-LEGAL
source_agent:         Product
description:          GDPR-compliant legal infrastructure: Terms of Service and Privacy Policy
                      static pages at localised routes, cookie consent banner, footer links,
                      and login page ToS note. Pure frontend feature — no backend changes.
acceptance_criteria:
  - /en/terms, /ru/terms, /sr/terms render with localised headings and English body
  - /en/privacy, /ru/privacy, /sr/privacy render with localised headings and English body
  - Cookie consent banner shown on first visit, hidden after Accept, not shown on return visit
  - AppShell footer shows Terms and Privacy links on all pages
  - Login page shows ToS/Privacy note beneath sign-in button
  - npm run build compiles successfully (tsc --noEmit exits 0)
dependencies:
  - FEAT-I18N (next-intl already in place)
estimated_complexity: medium
```

---

### TASK-73 — i18n strings for legal chrome

```
task_id:              TASK-73
title:                i18n strings for legal chrome (footer, cookie banner, login note)
type:                 task
status:               completed
priority:             high
capability_id:        LEGAL
parent_feature:       FEAT-LEGAL
source_agent:         Builder
description:          Add legal, cookieConsent namespaces and nav.terms, nav.privacy,
                      login.tosNote, login.tosLink, login.privacyLink keys to en/ru/sr message files.
estimated_complexity: small
```

---

### TASK-74 — AppShell footer links + login ToS note

```
task_id:              TASK-74
title:                AppShell footer links + login ToS note
type:                 task
status:               completed
priority:             high
capability_id:        LEGAL
parent_feature:       FEAT-LEGAL
source_agent:         Builder
description:          Update AppShell footer with Terms/Privacy navigation links.
                      Update login page with ToS/Privacy agreement note beneath sign-in button.
estimated_complexity: small
```

---

### TASK-75 — Terms of Service page

```
task_id:              TASK-75
title:                Terms of Service page (/[locale]/terms)
type:                 task
status:               completed
priority:             high
capability_id:        LEGAL
parent_feature:       FEAT-LEGAL
source_agent:         Builder
description:          Create web/app/[locale]/terms/page.tsx with 11 substantive sections
                      covering service description, copyright, data retention (30 days),
                      credits, liability, governing law. Uses AppShell. Localised headings
                      via getTranslations; body in English.
estimated_complexity: small
```

---

### TASK-76 — Privacy Policy page

```
task_id:              TASK-76
title:                Privacy Policy page (/[locale]/privacy)
type:                 task
status:               completed
priority:             high
capability_id:        LEGAL
parent_feature:       FEAT-LEGAL
source_agent:         Builder
description:          Create web/app/[locale]/privacy/page.tsx with 11 substantive sections
                      covering data collection (email, EPUB, job metadata), Anthropic sub-processor,
                      30-day retention, no data selling, strictly necessary cookies, user rights.
estimated_complexity: small
```

---

### TASK-77 — Cookie consent banner component

```
task_id:              TASK-77
title:                Cookie consent banner component + integration
type:                 task
status:               completed
priority:             high
capability_id:        LEGAL
parent_feature:       FEAT-LEGAL
source_agent:         Builder
description:          Create web/components/CookieConsent.tsx as a client component using
                      localStorage to track consent. Banner fixed to bottom of viewport,
                      styled in navy, keyboard accessible (role=dialog, aria-live=polite).
                      Integrated into web/app/[locale]/layout.tsx so it appears on all pages.
estimated_complexity: small
```

---
