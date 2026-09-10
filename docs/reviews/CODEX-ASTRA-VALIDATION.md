# Codex / Astra migration validation

Date: 2026-09-10. Review type: task-owner self-review, including correctness/security review. Final deterministic checks passed as recorded below; no independent model review or live model benchmark is claimed.

Scope: preview/apply behavior, ownership, template source precedence, preserved project data and Git index, initializer identity/path handling, local audit/CI failure semantics, metadata honesty, and agreement among current workflow/model/visual contracts.

The existing Unfolda fixture was deployed into a temporary directory. Five checks passed: expected files, current content assertions, resolved templates, preserved source snapshots, and idempotent restore/re-render. The stale string assertions were updated to match actual role wording and the new renderer path.

Model behavior evaluation prompts exist for eight cases. They were not executed as Astra sessions. No production game/app was run, and no actual image-generation quality or device performance claim is made.

Residual limits: local framework customizations need diff review; retired downstream files remain; the sync batch is not a concurrent-writer transaction. Legacy Claude adapters and scheduling utilities are optional and have not been exercised against live services.

## Final results

| Check | Result |
|---|---|
| `python -m unittest discover -s tests -v` | 22 tests passed |
| Isolated Unfolda example deployment and fixture runner | All 5 checks passed |
| `python setup.py --check` | 28 dynamic templates validated, no writes |
| `python audit.py --local --json --fail-on critical` | 0 critical, 1 advisory prompt-size warning, no dead references detected |
| Shell and Python syntax checks | Passed |
| CI YAML and Codex TOML parsing | Passed |
| `git diff --check` | Passed |

Local runtime: macOS, Python 3.14.3, existing Jinja2/PyYAML environment. CI is configured for Python 3.11; hosted CI was not run in this task. The deterministic audit output is saved in `docs/reviews/CODEX-ASTRA-AUDIT.json`.

The advisory concerns `agents/discovery-modes/ai-landscape.md` (~5,015 estimated tokens), an optional method outside the ordinary development path. This does not invalidate the passing functional checks.

Outcome: local adaptation complete and reviewable. Real downstream rollout, commits/pushes, global settings, services, and paid/model calls were not performed.
