# Framework update and recovery

Run updates from the agent-system checkout on macOS or Linux. Preview computes rendering and recognized migrations without creating files, backups, or locks:

```bash
python3 sync.py --target /path/to/project --render --diff
python3 sync.py --target /path/to/project --render
```

Each changed project gets a recovery directory under its parent's `.agent-system-backups/`. The command prints the exact location. `--backup-dir /path/outside/project` changes storage for a single target. Backups contain replaced framework file contents, original modes, before/after hashes, the target identity, and transaction status; keep them private. A no-op update creates no recovery record.

The writer uses a per-project OS lock, validates all changes, saves originals before writing, applies each file atomically, and writes the version last. A caught write failure attempts rollback. If another process changed a file, recovery preserves that edit and records a conflict. Cooperative locking prevents another sync process from writing concurrently; it does not stop application editors. Backups support recovery after a killed process. This is not an all-project or power-loss atomic transaction.

## Legacy entry point

`migrations/legacy-files.json` recognizes exact SHA-256 hashes from known framework revisions. An exact legacy root setup.py becomes a small compatibility entry point for `.agent-system/setup.py`. Unknown or locally modified setup.py remains untouched. The old file is in the recovery directory. Ordinary application setup/requirements/CI/product documents are not framework replacement targets.

## Restore

Use the backup path printed by the update:

```bash
python3 sync.py --target /path/to/project --restore /path/to/recovery-record --dry-run
python3 sync.py --target /path/to/project --restore /path/to/recovery-record
```

Restore validates target identity, paths, backup hashes, and every current file before writing. It removes newly created files and restores replaced/deleted files only when their content still matches the recorded before/after state. A newer local edit blocks the restore rather than being overwritten. Preserve that edit and reconcile it before retrying. Restore itself creates a reverse-operation backup. Empty directories may remain; no Git index or remote is changed.

For interrupted updates, inspect manifest.json (`prepared`, `applied`, `rolled_back`, or `recovery_required`) and preview restore. Do not edit hashes to force a restore or delete unrelated files. For multiple updates, restore newest first. Review framework changes and commit them normally after validation; project code remains separately owned.

Original render templates now live in tracked `.agent-system/templates/`, so a fresh clone can reconfigure without an ignored cache. The legacy `.templates/` directory is not read by the downstream renderer; preserve local backups if desired, and remove legacy cache entries from Git tracking during migration.

Release version hooks exclude project history in TASKS/DECISIONS/LESSONS_LEARNED/KNOWN_PATTERNS: downstream initialization uses fixed empty seed content for those files, so completing a local release record does not alter the installed framework.
