# FEAT-ADMIN — Admin panel

**Capability:** ADMIN (FEATURE_MAP)  
**Status:** implemented (MVP)  
**Depends on:** AUTH (`is_admin`), QUOTA (credit accounts), QUEUE (jobs metadata)

## MVP

- `GET /admin/users` — users with balances
- `POST /admin/users/{user_id}/credits` — body `{ "delta": int }`
- `GET /admin/jobs` — recent jobs (cap 500), with user email
- `GET /config/profile` — `is_admin`, `balance` for server-side UI guard
- Web: `/admin` (server layout enforces admin; tables for users + jobs)

## References

- Workflow: `docs/reviews/FEAT-ADMIN-workflow.md`
- Tasks: `docs/TASKS.md` — FEAT-18, TASK-65
