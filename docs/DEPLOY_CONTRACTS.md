# Deploy Contracts

This document defines the deployment requirements for {{ project.name }}. Architect must update this document when an implementation plan changes deployment-related configuration. Reviewer verifies compliance during code review.

---

## Environments

| Environment | Purpose | Deploy trigger | Approval required |
|---|---|---|---|
<!-- | local | Development | manual | no | -->
<!-- | staging | Pre-production validation | push to main | no | -->
<!-- | production | Live users | tag / manual | yes | -->

---

## Required Environment Variables

All variables listed below must be set before deployment. Missing variables must block the deploy.

| Variable | Environment(s) | Secret | Description | Default |
|---|---|---|---|---|
<!-- | DATABASE_URL | staging, production | yes | PostgreSQL connection string | — | -->
<!-- | REDIS_URL | staging, production | yes | Redis connection string | — | -->
<!-- | NEXTAUTH_SECRET | staging, production | yes | NextAuth session encryption | — | -->

**Validation rule:** Before deploying, verify every variable marked as required is set in the target environment. The CI pipeline should fail if any are missing.

---

## Infrastructure Dependencies

| Component | Provider | Required for | Health check |
|---|---|---|---|
<!-- | PostgreSQL | Railway / local | API, Worker | pg_isready or SELECT 1 | -->
<!-- | Redis | Railway / local | Worker queue | redis-cli ping | -->
<!-- | S3-compatible storage | MinIO / Cloudflare R2 | File storage | HEAD bucket | -->

---

## Database Migrations

| Tool | Run command | Pre-deploy | Rollback command |
|---|---|---|---|
<!-- | Alembic | alembic upgrade head | yes — before new code starts | alembic downgrade -1 | -->

**Rules:**
- Migrations run before new code starts (during deploy, not after)
- Destructive migrations (DROP, column removal) require manual approval
- Every migration must be reversible unless explicitly documented otherwise

---

## Health Checks

| Service | Endpoint / command | Expected response | Timeout |
|---|---|---|---|
<!-- | API | GET /health | 200 OK | 5s | -->
<!-- | Worker | process heartbeat in DB | last_heartbeat < 60s ago | — | -->

---

## Pre-deploy Checklist

This checklist is verified by the CI pipeline and by Reviewer during code review.

- [ ] All env vars from this document are set in the target environment
- [ ] Database migrations are ready and tested locally
- [ ] Health check endpoints respond correctly
- [ ] Tests pass (unit + integration)
- [ ] No secrets in committed code
- [ ] Rollback plan exists for this deploy
- [ ] Breaking API changes are versioned or feature-flagged

---

## Rollback Strategy

<!-- Describe how to roll back a failed deploy. For example: -->
<!-- - Railway: redeploy previous commit via dashboard or `railway up --detach` with prior commit -->
<!-- - macOS app: users keep previous version until they accept the Sparkle update -->
<!-- - Database: `alembic downgrade -1` (only if migration is reversible) -->

---

## CI/CD Pipeline

| Stage | Trigger | What runs | Blocks deploy |
|---|---|---|---|
<!-- | lint | PR / push | ruff, eslint | yes | -->
<!-- | test | PR / push | pytest, vitest | yes | -->
<!-- | build | PR / push | docker build, next build | yes | -->
<!-- | deploy staging | merge to main | Railway deploy | no | -->
<!-- | smoke test | after staging deploy | scripts/smoke_test.sh | yes (blocks prod) | -->
<!-- | deploy production | manual / tag | Railway deploy | — | -->

---

## Deploy Impact Log

Architect appends an entry here when an implementation plan changes deployment config.

| Date | Task | Change | Env vars added | Migration | CI change |
|---|---|---|---|---|---|
<!-- | 2026-03-29 | TASK-42 | Add Redis for job queue | REDIS_URL | yes (add jobs table) | add redis service to docker-compose | -->
