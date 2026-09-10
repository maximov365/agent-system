# Execution efficiency research — 2026-09-10

Baseline: agent-system 1.0.43, commit 850af3e. Scope: retain GPT-6 Astra,
the selected reasoning effort and task acceptance; reduce avoidable work.

## Evidence and decisions

The earlier eight synthetic runs averaged 54.318 seconds without framework and
61.164 with it (+12.6%). Cumulative input tokens averaged 75,970.2 and 110,494.5
(+45.4%). All passed the same public and held-out checks. These are observations
from two Python tasks, not evidence of a general speed or quality difference.
Logs show broad framework searches and repeated instruction reads. Large initial
failing-test output included intentional defect reproduction; that work is useful.
Source: [prior evaluation](ASTRA-PAIRED-EVAL.md) and its published result JSON.

[OpenAI's Astra guidance](https://developers.openai.com/api/docs/guides/latest-model)
describes strong sensitivity to repository instructions and potentially excessive
testing for small changes. Keep clear ownership/authority/completion rules, select
checks by affected behavior, and repeat passing checks for changed inputs, failures
or unresolved concerns. This does not justify reducing acceptance or security checks.

[OpenAI's latency guide](https://developers.openai.com/api/docs/guides/latency-optimization)
recommends reducing unnecessary round trips and parallelizing independent steps.
It cautions that reducing input tokens alone often has a small latency effect.
Therefore a shorter entry is a hypothesis to measure, not a proportional speed
claim. Retain full diagnostics on disk while retrieving the relevant parts.

[Bazel's cache documentation](https://bazel.build/remote/caching) explains action
inputs and highlights concurrent input changes, environment differences and
untracked external tools as cache correctness hazards. Our narrower adaptation
uses explicit local evidence references, declared dependency closure, content and
environment/runtime fingerprints, short same-task expiry, integrity checks and
before/after snapshots. Fresh execution remains the default. We do not introduce
Bazel, a remote cache or a new service dependency.

## Changes selected

1. Compact entry with a lazy method map; retain rigor, permission and live visual
   requirements. Source/test navigation is project-owned and validated.
2. Verified project commands and concise summaries. Batch only independent work;
   dependent writes, installation and shared server lifecycles stay ordered.
3. Opt-in reuse of reviewed deterministic check evidence. No automatic adoption
   for application checks with incomplete dependency closure. Measure hashing cost.
4. For graphics, inspect one representative live screen/scene early and reuse
   reviewed components/assets with provenance before expanding variants. This is
   workflow guidance; the framework receives no new application/game behavior.

## Validation design

Freeze baseline and candidate framework bytes before native Codex runs; compare
the same synthetic tasks and graders with Astra/medium, alternate condition order,
and report every result. Keep model identity limitations and small sample size
visible. Verify evidence invalidation and path handling with meaningful negative
tests. Real project navigation/commands provide adoption evidence, while a small
deterministic fixture can demonstrate reuse mechanics without claiming a general
performance gain. Release checks execute fresh. Record measured results separately.
