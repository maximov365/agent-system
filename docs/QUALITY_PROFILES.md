# Project quality profiles

Use `quality/profile.json` to record a project's actual runtime, device targets,
checks and performance budgets. The file belongs to the project. Sync never
creates or overwrites it; adopt one explicitly after inspecting the application.
Read it before choosing validation for a task. A profile does not authorize a
deployment, message, destructive command, paid service, or unrelated test run.

Supported kinds are `web`, `mobile`, `desktop`, `game`, `service`, and `content`;
a project may combine them. Avoid forcing games and apps into a generic data
pipeline. Retain real processing boundaries even when their names are generic.

```json
{
  "schema_version": 1,
  "kinds": ["web"],
  "targets": ["390x844 mobile browser", "1440x1000 desktop browser"],
  "checks": [{
    "id": "typecheck",
    "status": "configured",
    "command": ["npm", "run", "typecheck"],
    "cwd": ".",
    "defined_by": ["package.json"],
    "timeout_seconds": 300
  }],
  "budgets": []
}
```

Only use commands actually defined by the project. `configured` means the
command was identified; it does not claim its dependencies exist or it passed.
For a missing capability use `status: "unavailable"` with a concrete `reason`
and omit `command`. Never replace a missing native-device test with a browser
build and mark it passed. Budget entries contain `metric`, positive `limit`,
`unit`, `target` device/runtime and `measurement` method. They are acceptance
targets, not observations; a check passing does not implicitly satisfy budgets.

```sh
python .agent-system/profile.py validate
python .agent-system/profile.py run --check typecheck
```

In the framework checkout use `tools/profiles/profile.py`. Validation does not
execute commands. Run requires one explicit check ID, invokes its argv without a
shell, has a bounded timeout, and writes logs/results under ignored
`.agent/evidence/quality/`. Existing evidence is never overwritten. Inspect local
logs for private product data before sharing them. On POSIX, owned process groups
are cleaned up after completion/timeout; on Windows only the direct process is
terminated. A successful check is not a visual, security or release approval.

Choose evidence by kind: web state/viewports and keyboard; mobile real touch and
device performance; desktop permissions/window lifecycle; game input, pause,
save, frame time and playtest; service contracts/authorization/fixtures; content
rendered pages, source attribution and editorial review. Load only the methods
needed by the current change. Optional examples are never application defaults.
