# Implementation workflow reference

Optional method for substantial implementation. The task owner follows `AGENTS.md`; selecting this method does not enable delegation or add another approval gate.

## Work loop

1. Read the request and relevant project state. Identify the outcome, acceptance criteria, and material unknowns.
2. Choose lite, standard, or strict evidence according to risk. Create a concise durable plan only when useful or required by rigor.
3. Resolve necessary product, architecture, visual, copy, analytics, and test decisions using relevant specialist methods. Perform them locally unless delegation is explicitly permitted.
4. Implement the accepted outcome. Review affected correctness and security; inspect visual work in the running product. Verify changed instrumentation when present.
5. Fix demonstrated defects, repeat affected checks, and continue until acceptance is met or a concrete dependency prevents progress. Change approach after repeated failures rather than escalating at an arbitrary count.
6. Update task state and report result, evidence, and limitations. Do not finish with routing-only output when implementation is authorized.

## Selective methods

| Need | Reference |
|---|---|
| Unclear product intent or technical direction | Discovery / Product / Architect |
| UI, art, or motion | Designer / Illustrator / Animator, then UI Builder and Design Reviewer |
| Meaningful logic and failure cases | Test Strategist / Builder |
| Changed analytics | Analytics Architect and Analytics Validator |
| Correctness/security assessment | Reviewer / Security Reviewer |
| Non-code artifact ambiguity | Spec Reviewer / Reviser / Gatekeeper |

A design or plan is accepted when it fits the authorized outcome and explicit constraints; user sign-off is needed only for a material unresolved choice or when explicitly requested. Available native image tools are sufficient: a missing MCP integration is not a blocker. When generation fails, inspect the error and use an available suitable capability; report a real tool dependency without inventing outputs.

## Optional structured transport

An explicitly selected adapter may use `task_id`, `current_stage`, `workflow_mode`, `quality_loop_iteration`, and `analytics_used`. Persist a checkpoint when helpful. Counters describe attempts, not permission or completion. `agents/im-modes/routing-tables.md` lists useful classifications; `docs/AGENT_HANDOFF_CONTRACT.md` governs an actual handoff.
