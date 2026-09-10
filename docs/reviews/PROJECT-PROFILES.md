# Project profile review — 2026-09-10

All 16 registered downstreams now have project-owned `quality/profile.json`.
These files are never overwritten by framework sync. Checks cite actual package
scripts, source tests, or build manifests. Missing applications/devices remain
explicit unavailable checks. Budgets are proposed targets, not measured claims.

| Project | Inspected surface / profile |
|---|---|
| Voxema | Swift package and native macOS targets; unit command, device/audio permission gap |
| Unfolda | Next/Vitest frontend and Python authorization/provider tests; web + service |
| x5club | Browser mockups and product documents; implementation not yet present |
| ecom-scout | Python digest pipeline; no test suite identified, delivery not run |
| probey | Phaser/Vite game; actual build, real WebView playtest remains unavailable |
| real-estate | Next.js lint/typecheck; ingestion/ranking/delivery boundaries retained |
| collective-purch | Product documents only; unused generic pipeline removed |
| synthetic_resp | Python 3.12 + Next.js; real corpus/persona/export constraints retained |
| beautyrs | Business and PDF deliverables; content profile, unused generic pipeline removed |
| tracker_fiz | Go + React/Vite; type-check/build and fixture browser journeys |
| Iris | Python voice assistant; actual audio/permission/router boundaries retained |
| game_tsx | Game concept PDF; engine/device not selected, unused generic pipeline removed |
| disco-system | Document workflow and standalone prototypes; retain discovery/PRD/prototype stages |
| okr&kpi | Python backend + Vite frontend; frontend build identified |
| astrology | Design mockups, planned Expo app; native checks unavailable |
| xslides | Planning documents; content profile, unused generic pipeline removed |

Only the exact unmodified English ingest/process/export placeholder was removed
from four project YAMLs. Domain-specific pipelines, architectural documents and
model routes were retained. Changes were backed up with the transaction tool in
the sibling `.agent-system-backups/` directory (20260910T133326Z records).

Validation: all profiles satisfy the schema and source-path checks; runner tests
cover success, nonzero exit, timeout, no overwrite, symlink/traversal refusal,
unavailable checks and malformed budgets. Actual tracker_fiz frontend type-check
and probey build passed through the runner. Other configured commands were not
run; source validation is not application validation. Browser evidence and game
evidence have separate review reports. No product release approval is implied.
