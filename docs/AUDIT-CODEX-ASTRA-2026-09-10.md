# Agent System audit and Codex / GPT-6 Astra adaptation

Date: 2026-09-10. Baseline: commit `fbc8b94`, framework version `1.0.40`. Changes are local and uncommitted; the version remains unchanged until an intentional release/commit.

## Assessment

The framework has useful specialist knowledge, project contracts, reference configurations, and an established downstream distribution mechanism. Its main weaknesses were contradictory execution rules, Claude-specific entry points and model assumptions, weak verification of deployment tooling, and a gap between visual specifications and inspection of a running product.

The adaptation makes Codex a supported primary workflow while retaining portable methods and optional legacy adapters. It strengthens actual tooling checks and defines what visual/game production must deliver. It does not demonstrate a measured increase in Astra output quality: that requires behavioral evaluation on representative downstream tasks.

Scope covered: root instructions and bootstraps; execution/handoff/permission/model contracts; specialist routing and graphics methods; Jinja/YAML rendering; sync ownership and Git behavior; initializer; hooks; CI; eval definitions and example fixture; metrics adapters; optional legacy installation/scheduling surfaces. Production code in downstream applications, hosted services, account settings, and live model/media providers were not exercised.

## Findings and disposition

Evidence below names the original file/function or rule at the baseline revision. Current files contain the corrections.

| ID | Priority | Baseline finding and consequence | Disposition |
|---|---|---|---|
| A01 | High | `sync.py:main` called `run_setup()` after `cmd_sync()` even with `--dry-run` or `--diff`. Preview plus render could write files. `--all --diff` did not propagate diff mode. | Fixed: one in-memory plan for apply/preview; regression tests cover both combinations and all-project diff. |
| A02 | High | `.github/pull_request_template.md` and framework CI appeared in both FRAMEWORK_GLOBS and SEED_GLOBS. The overwrite path defeated seed-only protection. | Fixed: disjoint shared ownership. PR template is seed-only; framework CI is not deployed. Existing CI is preserved. |
| A03 | High | Root `setup.py` was copied and then executed in downstreams. It could replace an application's packaging script, the same class of collision previously recorded for requirements.txt. | Fixed: renderer/dependencies live under `.agent-system/`; sync renders with its own code and never executes the target's root setup.py. |
| A04 | High | `init-downstream.sh` interpolated a target path into Python source, wrote an unescaped project name into YAML, and swallowed parse errors. Quotes or malformed configuration could break identity checks. | Fixed: arguments are data, YAML uses safe serialization, invalid config fails explicitly, registration follows successful sync. |
| A05 | High | Sync and render wrote sequentially before validating all templates; version/ignore/index changes could precede a rendering failure. | Fixed for validation failures: preflight all planned writes, then replace individual files atomically and write version last. A disk/concurrency failure is not a fully transactional rollback. |
| A06 | High | Sync followed destination symlinks; rendering could restore arbitrary old backup paths. | Fixed: reject symlinked framework destinations, scope restore/re-render to current framework-owned paths, validate before mutation. |
| A07 | High | `audit.py:main` exited successfully without a registry, and never returned failure based on findings. CI could be green without auditing local contracts. | Fixed: local audit runs without downstreams, machine output remains JSON, critical findings fail, CI runs regression tests and rendering checks. |
| A08 | Medium | Sync removed framework files from Git tracking and ignored agents/AGENTS/evals. Fresh clones/worktrees lacked their instructions; index mutation was implicit. | Fixed: no index edits, framework files can be tracked, only disposable caches remain in the managed ignore block. Custom ignore rules survive. |
| A09 | Medium | Rendering a freshly synced static replacement could fall back to an old Jinja backup and resurrect obsolete instructions. Project-owned deploy docs were also eligible for repeated template rendering. | Fixed: refresh source snapshots including template-to-static changes; project-owned seeds are rendered once and then preserved. |
| A10 | Medium | Four copies of framework glob lists drifted; some mode/reference files were absent from downstream or audit coverage. | Fixed: shared `framework_manifest.py`, explicit destination mapping, recursive role discovery, shared hook classification including deleted source paths. |
| A11 | High | Root/CLAUDE/IM rules required routing-only output, one specialist per cycle, rigid plan gates, repeated handoffs, and three-pass escalations. A task could stop after ceremony instead of finishing. | Adapted: one task owner, selective methods, risk-based evidence, continued authorized execution, honest self-review. Behavior still needs model-session evals. |
| A12 | High | Trust policy treated ordinary user role instructions as suspect while declaring repository files and agent JSON pre-trusted. Keyword confirmation did not enforce a real data/action boundary. | Adapted: instruction hierarchy and validation at each data-to-action boundary; no keyword-only halt or JSON trust exemption. Runtime permissions remain authoritative. |
| A13 | Medium | Active model policy preferred Claude variants, repeated volatile prices/access claims, and recommended temperature defaults generically. Reviewer prompts duplicated model recommendations. | Adapted: requested Astra target, current official compatibility guidance, one model policy, no gateway requirement, preserve explicit workload tiers and client settings. |
| A14 | High | UI Builder demanded pixel-perfect fidelity while Designer described loose mockups; Design Reviewer mainly inspected code. Screenshots, real interactions, asset import, and viewports were not required evidence. | Adapted: explicit reference baseline and runtime capture/view/interaction loop, with verification-pending outcome when evidence is unavailable. |
| A15 | Medium | Illustrator required a Cursor MCP server, ranked specific packages, and defaulted to two variants. Native Codex generation could be available yet the role returned blocked. | Adapted: native tools first, capability discovery, one default output, reference editing and real asset inspection, optional MCP/provider integration. |
| A16 | Medium | Graphics lacked a complete production asset contract and games were mostly covered by Discovery. No common vertical-slice, animation/import, audio, playtest, or frame-time acceptance. | Added `docs/VISUAL_QUALITY.md` and `docs/GAME_DEVELOPMENT.md`; connected Designer/UI Builder/Reviewer/Illustrator/Animator. These are contracts, not an implemented engine harness. |
| A17 | Medium | Design review labeled 44×44 targets as WCAG 2.1 AA and mixed that rule with spacing. | Corrected to a WCAG 2.2 AA baseline with the 24×24 minimum/exceptions; 44×44 remains a comfort/enhanced target. No compliance certification is claimed. |
| A18 | Medium | `metrics_workflow.py` filtered a hardcoded user path and priced every session at historical Sonnet 4 rates. Its privacy description claimed not to read message content although transcript lines were scanned. | Default telemetry no longer reads private client transcripts; unknown cost is null/unknown. Legacy analysis is explicit opt-in, labeled historical and not Codex billing. |
| A19 | Medium | Hooks could synchronize every registered project after a commit; installer unlinked existing hooks without preserving ownership. | Post-commit now previews. Installer checks all destinations first and preserves unrelated hooks; worktree Git paths are resolved through Git. No hooks were installed during this audit. |
| A20 | Medium | Existing evals checked artifacts/role names, with no executed model benchmark; the Unfolda fixture contained stale wording assertions and assumed every source snapshot contained variables. | Added native-image, steering, and playable-slice cases; updated fixture semantics and namespaced renderer; deterministic tests are distinct from model evaluation. |
| A21 | Low | In-progress tasks were labeled “stuck” without age/activity evidence. App/game defaults also forced an ingest/process/export pipeline. | Active-task notices are informational; new project stages default to empty while old configured pipelines remain supported. |

## What was intentionally simplified or retired

- Mandatory output JSON and a separate handoff after every local role switch.
- Requiring Claude Code or a Cursor image MCP server to use the system.
- Global model/price rankings repeated in active role prompts.
- Automatic downstream writes and Git untracking on a routine framework update.
- File-count approval thresholds and blanket repeat approval for routine reversible edits.
- Memory entries for every uneventful change and unconditional loading of large histories.
- Treating static code review as visual approval, or persona switching as independent review.

Specialist knowledge, project-owned guardrails, real code/security review, structured handoffs for actual delegation, deterministic tests, and optional provider adapters remain useful. The framework still supports existing pipeline configurations.

Claude slash commands, launchd reminders, and gateway instructions remain optional compatibility surfaces. They are not the Codex default. Old model/service claims inside those legacy references must be verified before use; their presence does not prove current support. Existing installed services, user's worktrees/logs, and old downstream files were not removed.

## Highest-value next improvements

These are proposals beyond the implemented portable contracts. Choose a real downstream task before installing another tool or adding many more agent roles.

| Priority | Improvement | Concrete deliverable | Evidence of value |
|---|---|---|---|
| 1 | Reference scene/screen at final quality | One polished playable encounter or complete application journey; explicit art direction and baseline | Visual comparison, real interaction/playtest, measured target budgets |
| 1 | Asset library with lineage | Project-owned manifest, reference sheets, originals/exports, revision graph, import settings, automated size/alpha/frame/pivot checks | Reusable coherent assets, fewer regeneration/import errors, predictable runtime budgets |
| 1 | Engine/browser verification adapters | A small command set for start, scene/route selection, deterministic fixture, capture, interaction, and profiling | Repeatable evidence without manual setup on every task |
| 1 | Baseline comparison of plain Codex vs this framework | Same frozen tasks, exact Astra effort/runtime, repeated runs, defect/intervention/time records | Decide whether each workflow method actually pays for itself |
| 2 | Project-specific quality profiles | Web UI, 2D game, and 3D game profiles with different artifacts/device budgets | No irrelevant pipeline or review burden on unrelated products |
| 2 | Independent visual critique at milestones | Separate review with reference and runtime evidence, only when delegation is authorized | Fewer escaped design/usability defects; measure benefit against time/cost |
| 2 | Asset/source automation | Engine import/export, sprite atlas construction, 3D/material validation, audio loop checks | Deterministic production pipeline around generated assets |
| 2 | Player/user testing kit | First-session tasks, observation template, recording protocol, feedback linked to changes | Observed comprehension, control quality, recovery and task completion |
| 3 | A small set of reusable Codex skills | Package proven visual QA, game-slice validation, and safe framework upgrade methods | Better triggering and selective loading than dozens of always-loaded roles |
| 3 | Portable telemetry export | Task-scoped records from supported runtime outputs, with unknown values preserved | Quality/cost/latency decisions without scraping private transcript formats |

For web projects, Playwright provides screenshot comparison; keep baselines in the same rendering environment and still view the actual result. [Official visual-comparison documentation](https://playwright.dev/docs/test-snapshots).

For a Godot project, a CLI adapter can run/import/export selected project scenes and support headless build checks. A headless pass still does not prove rendered art quality or game feel. [Official command-line documentation](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html).

For 3D, retain actual editable scene/material/rig sources and verify exports inside the target engine. Select tooling to match the existing engine and team; do not infer a complete 3D production capability from a raster generator.

## Verified compatibility sources

The current Astra guide emphasizes autonomous follow-through, clear precedence for skills, concise communication, and proportional testing. Those principles informed the prompt changes; this is an adaptation, not evidence of measured speedup. [Official Astra guidance](https://developers.openai.com/api/docs/guides/latest-model).

`gpt-6-astra` and published effort options were checked against the [official model specification](https://developers.openai.com/api/docs/models/gpt-6-astra). Codex client/account options are checked separately; no personal model settings were rewritten.

Entry/configuration/skills references: [AGENTS.md discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [configuration layers](https://learn.chatgpt.com/docs/config-file/config-basic), and [progressively loaded skills](https://learn.chatgpt.com/docs/build-skills).

Accessibility correction: [W3C target-size minimum](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html).

## Verification and limitations

The root AGENTS.md decreased from **18,355 to 6,928 bytes (62.3%)**. This measures instruction-file size, not model tokens, runtime, or quality. The remaining specialist library is loaded selectively.

Deterministic regression coverage includes preview+render, all-project diff, identity/YAML quoting, existing app setup/requirements/config/CI, no Git-index mutation, fresh seeds, invalid-config/template preflight, symlink refusal, repeat sync, static-template upgrades, project-doc preservation, old pipeline configuration, restore/re-render, local audit/exit behavior, content drift, default telemetry privacy, and hook preservation. See `tests/test_framework.py` and the final validation record in `docs/reviews/CODEX-ASTRA-VALIDATION.md`.

The existing Unfolda configuration was deployed to a temporary folder and its five fixture checks passed after correcting stale assertions. No real downstream project was changed. Local audit has zero critical findings and one advisory size warning for the optional AI-landscape method (~5,015 estimated tokens); it is not loaded for ordinary development.

Review was performed locally by the task owner, including a security/correctness pass. No independent subagent review, live Astra behavioral benchmark, generated asset comparison, actual game build, device performance run, or real-user playtest was performed. CI configuration was verified locally; hosted GitHub Actions were not triggered.

Residual operational limits: sync intentionally replaces framework-owned files, so review local customizations with `--diff`; it does not delete retired downstream files, override custom ignore rules, roll back an entire batch after disk failure, or provide concurrent-writer locking. The old root setup.py in legacy downstreams remains untouched and should not be used for the new renderer. The legacy transcript parser, scheduler, and optional gateway examples are not portable Codex integrations.

## Suggested rollout

Commit/review the framework migration when ready, then trial one downstream with `--render --diff`. Apply only after checking local overrides and run a meaningful app/game task under Astra. Compare that result with the baseline before updating the rest of the registry. Promote additional visual automation from demonstrated bottlenecks, not the number of roles in the framework.
