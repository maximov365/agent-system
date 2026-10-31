# Optional structured code review

Load only when a caller requests the legacy sectioned report. Follow the ordinary
review method; include evidence and applicability in each section. This format
does not require another agent or a new approval gate. Use only supported model
parameters; deterministic acceptance does not imply deterministic model output.

```text
## Review Result

Status: APPROVED / APPROVED WITH MINOR CHANGES / CHANGES REQUIRED

## Scope Check
<did the implementation follow the approved scope?>
<were all approved plan steps addressed?>

## Architecture Check
<any pipeline or architecture concerns?>

## Prompt Integrity
<were prompt templates modified? are they still in prompts/?>

## AI / LLM Check
<model names, token logging, providers, supported request settings>

## Code Quality
<clarity, maintainability, complexity>

## Dependencies
<any unnecessary dependencies?>

## Tests
<coverage and determinism>

## Security
<any risks or unsafe patterns?>

## Deployment
<env vars documented? migrations reversible? CI updated? DEPLOY_CONTRACTS.md current?>

## Required Changes
- [blocking] <issue that must be fixed before proceeding>

## Suggested Improvements
- [optional] <improvement that would be nice but is not blocking>

## Next Step
<what should happen next — one sentence>
```

Append docs/AGENT_HANDOFF_CONTRACT.md only for an actual structured handoff.
