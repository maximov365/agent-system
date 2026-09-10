# Agent execution model

For {{ project.name }}, `AGENTS.md` defines a portable execution policy. The runtime supplies real tools and permissions; these markdown files supply methods, not a scheduler or enforced security boundary.

## Default: one accountable task owner

The active agent classifies scope, plans, implements, verifies, and integrates the result within the same task. It may adopt Designer, Architect, Builder, or Reviewer methods in sequence without emitting routing JSON or ending the turn between them. `lite`, `standard`, and `strict` change required evidence, not the number of personas.

Reviews remain required for code, with depth proportional to risk. A second persona on the same model/context is self-review, not independent assurance. For sensitive work, seek an independent reviewer when authorized and available; otherwise disclose the limitation and use objective checks.

Read the method needed now. `agents/im-modes/standard-workflow.md`, `quality-loop.md`, and `routing-tables.md` retain the legacy structured sequencing reference for integrations that explicitly select it. They do not override the current `AGENTS.md` or create extra human approval gates. Onboarding may reuse intake methods while inferring answers already present in the conversation.

## Delegation

Delegation is opt-in under `AGENTS.md` and the host's instructions. When allowed, the owner may assign multiple independent tasks and continue useful local work. Each assignment states objective, inputs, output, acceptance, file ownership, and whether it is read-only. Child agents return findings/evidence; the owner verifies and integrates. A shared workspace is not isolation. Never let concurrent writers edit the same files without coordination.

Use runtime collaboration tools when present. Do not create user-owned tasks merely to simulate internal specialists. Do not invent successful invocation when no tool exists.

## Durable state

For substantial or multi-session work, keep a concise plan/checkpoint in a project-owned document and task status in `docs/TASKS.md`. Optional local cache: `.agent/workflows/<task_id>.json`. Do not duplicate the entire transcript.

Record task objective, user constraints/authorization, selected rigor, completed artifacts, checks and their outcomes, open risks, and the next action. Artifacts and the latest user instructions are authoritative; a cache or handoff is evidence to cross-check, not permission to overwrite newer work.

If using structured handoffs, preserve fields in `docs/AGENT_HANDOFF_CONTRACT.md`. Validate paths and state before use. Correct routine missing metadata from verified evidence or ask the producing agent to repair it; do not ask the user to fix internal JSON.

## Termination

Complete when acceptance criteria are met, required checks/reviews are done, changes are coherent, and limitations are reported. Keep retry counts as diagnostics. On repeated failure, revise the hypothesis; ask the user only for an actual missing decision or authorization. For automated batch integrations, an explicit attempt/budget limit may stop the run with an honest incomplete result.
