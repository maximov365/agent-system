# Verified framework release 1.0.43 — 2026-09-10

All eight follow-through items are implemented within the clean-framework scope.
The original game is an optional integration example under examples/; no example
application or asset enters downstream sync, initialization or runtime requirements.

Framework source: [production tooling](https://github.com/maximov365/agent-system/commit/565e37d49448b2c9a0a157ca25e81f2fb67ea81c),
[Python 3.10-compatible asset hashing](https://github.com/maximov365/agent-system/commit/4728412fe332b8c4159d728be8d05d1ce6be1147).
[GitHub CI for 1.0.43](https://github.com/maximov365/agent-system/actions/runs/34485367101) passed.

Validation: 44 Python regression tests, four actual-browser runner tests, five
isolated game-model tests; source-render validation and audit (zero critical,
one existing optional prompt-size advisory). The tracker app's fixture journeys,
all ten reviewed game captures, and the normal-duration adaptive playthrough have
separate evidence reports. Eight actual paired Astra sessions passed their public
and held-out tests; overhead increased on tiny tasks, so no general efficiency or
artistic-quality improvement is asserted.

All 16 registered projects have version 1.0.43, validated quality profiles, current
framework contents, a migrated legacy setup entry point, and a passing render
preflight. Sources persist under tracked .agent-system/templates/ after clone;
legacy cached templates cannot override current policy. Ten repositories received
isolated framework commits. Unrelated index entries and working-file hashes were
checked before and after each commit; application edits and staged deletions were
preserved. Only framework ignore-block changes were committed where .gitignore
also contained user edits. Optional dependency/cache paths remain ignored.

| Project | Delivery |
|---|---|
| voxema | Published main: [276337e](https://github.com/maximov365/Voxema/commit/276337e86eabdb16aa34dc305ea27ddb3874f4c9) |
| unfolda | Local 3ccbda2; isolated [draft PR #1](https://github.com/maximov365/unfolda/pull/1), not merged |
| x5club | Local commit 209b64f; no remote configured |
| ecom-scout | Published main: [1083951](https://github.com/maximov365/ecom-scout/commit/1083951e910a4b0e455566b0b4bdbeb65c3302c2) |
| probey | Published main: [d28458a](https://github.com/maximov365/probey/commit/d28458a328af6b668065dced14d337ad9d1a4cf9) |
| real-estate | Published main: [2078bdc](https://github.com/maximov365/nastan/commit/2078bdcc7a0a05cabd7d3ab3f7ba78c14ffc1be9) |
| collective-purch | Updated locally; no Git repository |
| synthetic_resp | Published main: [c7cf209](https://github.com/maximov365/synthetic_resp/commit/c7cf209d6ff1f849248f2f4ae1be88e170f50efd) |
| beautyrs | Updated locally; no Git repository |
| tracker_fiz | Updated locally; no Git repository |
| Iris | Local commit 5a55cb6; no remote configured |
| game_tsx | Updated locally; no Git repository |
| disco-system | Updated locally; no Git repository |
| okr&kpi | Published main: [4c4a1fe](https://github.com/maximov365/okr-kpi-tracker/commit/4c4a1fef1542960014ecdd397b48fc81452222eb) |
| astrology | Published main: [79d51c2](https://github.com/maximov365/citlali/commit/79d51c28347256ded28bcdd6ec4b4c024a610455) |
| xslides | Updated locally; no Git repository |

Unfolda's unpublished local predecessor also contains application files. Its
publication branch was constructed from published origin/main, carries only the
framework update, and leaves local main/history untouched. The draft PR requires
review/merge; no existing application commit was published incidentally. Ecom-scout
was pushed to its ecom-scout remote, not its origin pointing at agent-system.
New repositories/remotes were not invented for the eight local-only destinations.

Recovery manifests and originals are retained in the sibling .agent-system-backups/
directory; exact per-project paths appear in ignored .agent/validation/sync-1.0.42.log,
sync-1.0.43.log and profile-rollout.json. No restore was needed in the real rollout.
The final release record does not bump the installed framework version.
