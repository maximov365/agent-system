---
name: agent-system-upgrade
description: Update agent-system framework files in child projects using its transactional sync. Use for requested framework rollout, recovery or upgrade review.
---

Locate the actual framework checkout and target projects from the task and registry.
Read [upgrade and recovery](../../../docs/FRAMEWORK_UPGRADE.md) before mutation.
Inspect target Git status, framework drift and project ownership; preserve app code,
project config, profiles, brand documents, local skills and staged work.

Preview the proposed sync with `sync.py --target PROJECT --render --dry-run` from
the framework checkout. Apply within the user's authorization, retain transaction
backups, then validate rendering/integrity and affected project checks. New tools
being present does not mean their optional dependencies are installed.

Commit only reviewed framework changes when authorized. Verify each destination
remote and branch before publishing; never include unrelated local predecessors
or assume an `origin` belongs to the expected project. Report applied version,
validation, publication and any remaining exceptions separately.
