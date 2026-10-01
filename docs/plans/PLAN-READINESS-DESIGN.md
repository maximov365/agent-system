# Readiness and design craft — 2026-10-01

Baseline: 1.0.44 / 84ec177. Owner: current task owner.
The user authorized implementing the researched improvements in order, beginning
with general framework work. Earlier commit, downstream update and publication
authorization continues. Keep application code and test examples out of the core.

| Task | Acceptance | Status |
|---|---|---|
| TASK-024 Current contracts and compatibility | Remove active legacy contradictions; document optional speed tiers without changing model/effort; CI covers Python 3.10 and a current supported runtime | completed |
| TASK-025 Project readiness | Read-only diagnostics distinguish declared configuration, installed prerequisites, HTTP response, executed journey and visual review; explicit verification uses existing project checks; negative tests and real example evidence | completed |
| TASK-026 Focused native skills and design craft | Portable, narrowly triggered readiness/design/review procedures; project-owned design passport; practical typography/layout/color/motion guidance and examples; no compulsory third-party engine or extra agents | completed |
| TASK-027 Representative evaluation | Add executable multi-file/UI fixtures and a reproducible visual comparison protocol; preserve honest separation of tooling tests and actual model/visual results | completed |
| TASK-028 Validate and propagate | Fresh checks, pilot sync/restore coverage, preserved child project content and staged changes, isolated commits and existing authorized GitHub destinations | in_progress |

Decisions: keep Astra and selected effort; do not enable paid speed tiers or install
external skill bundles. Reuse existing quality checks/browser lifecycle for launch
verification. A responsive HTTP endpoint is not proof that buttons work. Native
skills contain framework-specific routing; the shared design references remain
usable without skills. Treat stylistic preferences as contextual advice.

Research already inspected in this task: official OpenAI changelog/speed/skills
guides (2026-10-01); Impeccable, Hallmark, Jakub Krehel and Emil Kowalski upstream
instructions. Record precise sources beside the resulting guidance. No general
design-quality or speed claim without comparative evidence.

Checkpoint: implementation and focused validation complete. 62 Python tests,
5 browser/grader tests and 5 game logic tests passed locally. Explicit example
launch verification passed four viewport/journey combinations. New multi-file/UI
fixtures and graders are executable and tested against broken/repaired fixtures;
no new actual-model comparison or independent design assessment is claimed.
Release validation, safe downstream rollout and publication remain in progress.
