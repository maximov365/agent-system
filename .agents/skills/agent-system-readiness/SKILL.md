---
name: agent-system-readiness
description: Diagnose local launch and prerequisite problems in projects using agent-system quality profiles. Use for startup failures or explicit readiness checks.
---

Read the project's `quality/profile.json` and [readiness contract](../../../docs/PROJECT_READINESS.md).
Run the project's `.agent-system/profile.py doctor`; in the framework checkout the
entry is `tools/profiles/profile.py`. If no profile exists, inspect the actual build
manifest and documented launch; do not invent installed dependencies or commands.

Resolve the reported missing prerequisite within the task's scope. For web apps,
use the documented server URL. An explicit HTTP probe only proves a response.
When actual startup/interaction verification is required, inspect and run the
declared `--verify-launch` check fresh; preserve other sessions' servers.

Report configured versus observed model/tools, the actual check and evidence,
and any missing device/browser access. View captures before claiming visual review.
Do not infer the active model from project intent or scan private user sessions.
