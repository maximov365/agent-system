# Efficiency implementation and evaluation — 2026-09-10

Release: agent-system **1.0.44**, source commit `87b3699`.
The framework now has a compact entry, task-scoped methods, verified project
navigation, concise check evidence and opt-in validated reuse. Acceptance criteria,
the requested model/effort, security review and live visual requirements remain.
No application or game behavior was added. [Research and sources](EFFICIENCY-RESEARCH.md)
explain the design choices.

## What was measured

Two iterations each ran eight native Codex evaluations: baseline 1.0.43 versus a
frozen candidate, two synthetic Python tasks, two repeats, reversed condition order
on the second repeat. Every run requested GPT-6 Astra at medium effort, used the
same fixture/held-out grader hashes, and had no manual intervention or delegation.
Both public and held-out checks passed in **all 16 runs**. Pagination covers 144
held-out boundary combinations; authorization covers 22 cases and immutability.

| Final experiment | Baseline mean | Candidate mean | Change |
|---|---:|---:|---:|
| All tasks, wall time | 76.470s | 63.855s | −16.50% |
| Pagination, wall time | 49.295s | 50.534s | +2.51% |
| Authorization, wall time | 103.645s | 77.176s | −25.54% |
| Cumulative input tokens | 120,431 | 102,130 | −15.20% |
| Input tokens excluding reported cache hits | 15,247 | 13,842 | −9.21% |
| Output tokens | 1,563 | 1,492 | −4.56% |
| Observed shell commands | 3.75 | 4.50 | +20.00% |

The gain was concentrated in authorization, not universal. Command count did not
fall; some output remained large because useful failing-test reproduction was
retained. This sample does not identify a causal timing breakdown or demonstrate
statistical reliability. It supports keeping the clearer task entry and measuring
larger real tasks next, not promising a fixed percentage improvement.

The **initial candidate was slower**: 56.622s to 64.301s (+13.56%), with cumulative
input +18.18%. Its shorter entry still prompted unnecessary method discovery.
The second version named the coding rules directly and batched initial source/test
reads. Both iterations and every result are retained; they are not pooled into one
claim about a single prompt.

The evaluated second entry contained 434 rendered words versus 927 in baseline.
Final review restored explicit strict-mode wording for all security boundaries and
releases, bringing the shipped entry to **438 words** (−52.75%). The timing table
describes the frozen 434-word candidate; the four-word scope clarification was not
another model timing experiment. It preserves broader rigor outside these fixtures.

Limitations: only two small Python tasks, two repeats per condition, one host and
sequential runs under variable service load. No graphics/game model quality
comparison, no independent reviewer, no API dollar-cost estimate. CLI metadata
records the requested model but does not independently identify the resolved model.
Passing these graders is evidence for these contracts, not proof of unchanged
quality on every future application. Project navigation and evidence reuse were
validated separately; these fixtures do not exercise real application navigation.

## Check reuse: measure before enabling

The existing optional reference example's five deterministic logic tests were used
for a local three-repeat mechanics/timing check. Source was inspected; only Node
builtins and fake in-memory storage are used. No example code changed.

| Operation | Mean elapsed time |
|---|---:|
| Fresh execution | 0.074s |
| Execution plus reusable evidence recording | 0.163s |
| Valid reuse of the original pass | 0.040s |

Three subsequent reuse hits are needed to recover initial recording overhead on
this short suite. The actual tracker_fiz type check also passed fresh in 0.568s.
**No downstream check was opted into reuse.** The tool is available for a reviewed,
expensive deterministic check whose full dependency closure is known and whose
measured benefit exceeds fingerprinting cost. It is not an automatic test skipper.
The local example experiment assumed unchanged same-host OS runtime; it did not
establish a portable hermetic cache policy.

Reuse requires an explicit original evidence path and task ID; checksums, status,
content/configuration/runtime/environment fingerprints and expiry must validate.
Missing/corrupt/changed evidence runs fresh. A reused result is labelled as such and
cannot renew the original timestamp. Release/security approval always runs fresh.
Negative tests cover source/test/config/runtime/environment changes, additions and
deletions, different sessions, expiry/future timestamps, failed/corrupt evidence,
mid-run changes, symlinks, incomplete inputs and hashing limits. See the full
[contract and limitations](../QUALITY_PROFILES.md).

## Verification and rollout

- 54 Python regression tests passed fresh, including evaluation snapshot and
  evidence-reuse negative tests. Four actual browser-runner tests passed; five
  existing example logic tests passed. No visual approval was inferred from them.
- Template checks and local audit passed; the pre-existing large optional
  landscape prompt remains an advisory, with no critical audit finding.
- Navigation was inspected and added to all 16 project-owned profiles. Existing
  checks were preserved; empty implementations still report unavailable capability.
- All 16 projects received 1.0.44; profiles, template rendering and framework
  integrity passed. Transaction backups are local. Ten Git repositories received
  isolated commits with unrelated index entries and working files verified intact.
- Seven existing downstream main branches were published. Unfolda's existing
  [draft PR #1](https://github.com/maximov365/unfolda/pull/1) was updated from its
  published framework branch, preserving the unpublished application commit on
  local main. Two Git projects have no remote; six projects have no Git repository.
- Source release [GitHub CI passed](https://github.com/maximov365/agent-system/actions/runs/34489929947).

For graphics the method now emphasizes early inspection of a representative live
screen/scene, reuse of reviewed project components/assets, and provenance before
expanding variants. Native playtesting, responsive states, accessibility and measured
runtime performance remain required where relevant. This is framework guidance;
no new product assets, dependencies or game files were deployed.

## Reproducible records

- [Initial experiment](../../evals/results/astra-efficiency-initial-2026-09-10.json)
- [Final experiment](../../evals/results/astra-efficiency-final-2026-09-10.json)
- [Reuse measurements](../../evals/results/evidence-reuse-2026-09-10.json)
- [Initial snapshot delta](../../evals/results/astra-efficiency-v1-2026-09-10.patch)
  and [final snapshot delta](../../evals/results/astra-efficiency-v2-2026-09-10.patch)

Snapshot deltas apply to the corresponding rendered baseline using
`git apply --unidiff-zero`. Exact reconstruction was verified against each recorded
rendered snapshot digest. They are evaluation artifacts, not patches to apply to
an application. Full synthetic command transcripts remain in ignored local evidence;
no private project content or personal session transcripts entered the model runs.
