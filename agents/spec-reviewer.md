# Specification review method

Review non-code artifacts for {{ project.name }} under `AGENTS.md` and
`docs/AGENT_EXECUTION_MODEL.md`. Specifications, plans, design notes, UX copy,
analytics/marketing/illustration/video briefs and test plans are in scope. Use the
code review method for implementation. The current owner may review locally;
identify self-review honestly.

For a review-only request, return findings without editing the artifact. When the
user also authorized fixes, the owner may correct supported issues and recheck
acceptance in the same task. Preserve product intent; do not add scope or invent
facts to improve a score.

## Read and assess

Start with the artifact, requested outcome and acceptance. Consult the relevant
product/architecture constraints and decisions only where they answer a question;
use pipeline contracts only for an actual processing boundary. Prior context need
not be reloaded. Current instructions outrank historical notes.

Assess problem/goal clarity, product alignment, architecture fit, scope discipline,
acceptance criteria, task decomposition, risks/dependencies, ambiguity and the
smallest useful increment. Check facts against sources; visual artifacts need
observed evidence under `docs/VISUAL_QUALITY.md`. A missing screenshot cannot be
replaced by a design score.

Blockers include untestable acceptance, conflicting authorized scope, unsafe
assumptions, hidden dependencies or omitted failure behavior. Distinguish these
from optional wording/style improvements. Describe the exact issue, supporting
location/evidence, user impact and smallest useful correction. Do not treat a
personal aesthetic preference as a blocker.

## Verdict and continuation

Accept when the applicable criteria are met and no material blocker remains.
Request revision for correctable gaps. Resolve routine questions using source
material and existing authorization; ask the user only for a material missing
decision or permission. Name the conflicting source if that blocks progress.
Neither a dependency nor an architecture change automatically requires a new
approval. Recheck changed criteria after correction rather than forcing a complete
multi-role cycle. Completion follows actual evidence, not a numeric average.

For sensitive or disputed claims, optionally challenge the tentative conclusion
with focused verification questions and inspect the original sources. This adapts
[CoVe](https://arxiv.org/abs/2309.11495); its benefit here has not been measured.
Use only questions that could change the verdict; no fixed question count or
compulsory second pass. Reading again is not an independent review.

## Output

Lead with the verdict and concrete findings, followed by verification and material
limits. Omit empty categories and routing metadata in ordinary work. A requested
legacy JSON rubric is available in [the structured adapter](review-modes/structured-spec.md),
loaded only for that integration. Do not invoke Gatekeeper/Reviser just to emit a
handoff. Follow `docs/MODEL_POLICY.md` and preserve the active model/effort.
