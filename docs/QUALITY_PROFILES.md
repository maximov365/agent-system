# Project quality profiles

Use `quality/profile.json` to record a project's actual runtime, device targets,
checks and performance budgets. The file belongs to the project. Sync never
creates or overwrites it; adopt one explicitly after inspecting the application.
Read it before choosing validation for a task. A profile does not authorize a
deployment, message, destructive command, paid service, or unrelated test run.

Supported kinds are `web`, `mobile`, `desktop`, `game`, `service`, `content`, and `tooling`;
a project may combine them. Avoid forcing games and apps into a generic data
pipeline. Retain real processing boundaries even when their names are generic.

```json
{
  "schema_version": 1,
  "kinds": ["web"],
  "targets": ["390x844 mobile browser", "1440x1000 desktop browser"],
  "navigation": {
    "source": ["src"],
    "tests": ["tests"],
    "references": ["package.json"]
  },
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
python .agent-system/profile.py summary
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

## Navigation

Optional `navigation.source`, `navigation.tests` and `navigation.references` list
existing project-relative files/directories (up to 30 per category). Record actual
entry points and test roots after inspecting the checkout; omit missing categories.
The summary prints this small map and available commands without loading framework
methods. These locators do not replace applicable instructions or source inspection.
Update the map when moving packages. A missing or symlinked locator is a validation
error; it is never silently treated as a verified project path.

## Explicit reuse of check evidence

Fresh execution is the default. Reuse is an optional convenience for repeated
local verification in one task, not a build cache or an approval mechanism. Enable
it only after reviewing the complete dependency closure of a deterministic,
side-effect-free command. Never enable it for deployments, migrations, builds that
produce needed outputs, network/device checks, benchmarks, visual review, or tests
whose inputs include unknown services, clock, randomness or mutable external data.

A configured check may include:

```json
"reuse": {
  "deterministic": true,
  "side_effect_free": true,
  "dependency_review": "Describe inspected source, test discovery, configuration and runtime dependencies here.",
  "inputs": ["src", "tests", "package.json", "package-lock.json"],
  "runtime_inputs": ["node_modules"],
  "max_age_seconds": 600
}
```

This is a schema example, not a reviewed policy for arbitrary npm commands.
Include test discovery directories, configuration, source, installed dependencies
and every imported runtime/tool input. `runtime_inputs` can name explicit absolute
runtime files/directories outside the project; use resolved paths and review them
before hashing. An empty list is valid only when there are no additional runtime
dependencies. The executable is resolved and hashed automatically; that alone does
not cover an interpreter's libraries, package-manager hooks or tool configuration.
Do not sweep credential stores or unrelated files to guess dependencies. Unknown
closure means leave reuse disabled. Hashing a large closure may cost more than
running a short check, so measure before adopting it.

```sh
python .agent-system/profile.py run --check unit --session task-42 --output .agent/evidence/quality/first
python .agent-system/profile.py run --check unit --session task-42 --reuse-from .agent/evidence/quality/first
python .agent-system/profile.py run --check unit --fresh
```

The first command executes and records evidence. The second may reuse that exact
original pass for at most 900 seconds in the same session/project/host. The last
always executes and is required for release/security approval. Mismatches, missing,
expired or corrupt evidence run the check again. No automatic cache search occurs.
`reused` explicitly means `executed: false`, keeps the original timestamp and path,
and cannot be chained to renew evidence. Full logs remain in the original directory;
the command prints a concise result and evidence location. Read relevant failure
diagnostics from the log before deciding the next step.

Fingerprints cover declared file contents, names and modes (including additions and
deletions), the complete profile, resolved executable, runner code, OS/host identity,
environment and session. Only a combined digest is persisted for the environment.
Declared trees containing symlinks, special/missing files or more than 20,000 entries
or 512 MiB are ineligible and run fresh. Paths are not followed through symlinks.
Before/after fingerprints must match to record reusable evidence. Do not mutate
inputs concurrently: this detects persistent changes, not a transient change that
is restored between snapshots. This tool is not a hermetic executor. Checksums catch
accidental evidence damage; they do not authenticate against another local writer.
