# FEAT-ADMIN — workflow record (Iteration Manager)

**Feature:** FEAT-ADMIN — Admin panel (credit balances, job monitoring)  
**Date:** 2026-03-25

## Product

MVP: admin user list with balances, signed credit delta, cross-user job list (metadata), `is_admin` gate, `/admin` UI with non-admin redirect to `/`.

## Spec Reviewer

Admin routes under `/admin` with `require_admin`; `GET /config/profile` for layout guard; safe error payloads.

## Architect

Join `Job` + `User` for email; `admin_adjust_balance` + `admin_adjustment` transaction; audit on adjust; fix `/config/credits` balance source.

## Gatekeeper

No book content; 403 for non-admin.

## Builder

See `docs/TASKS.md` TASK-65 file list.

## Reviewer

`tests/test_admin_endpoints.py`; `pytest` + `tsc` green.
