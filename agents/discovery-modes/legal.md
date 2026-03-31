# Discovery Mode: Legal & Regulatory Compliance

Use this mode when the question is about **regulatory requirements, data protection laws, compliance obligations, or legal risks** that affect the product's design, data handling, or distribution.

This mode feeds into Product and Architect agents — its output shapes scope constraints, non-goals, and architectural decisions driven by compliance.

---

## Additional responsibilities

- Identify all regulations and legal frameworks relevant to the product's domain, target markets, and data types
- For each regulation: summarize key obligations, scope of applicability, and penalties for non-compliance
- Analyze how the product's pipeline, data flows, and storage interact with each regulation
- Identify specific compliance gaps in the current or proposed architecture
- Distinguish between hard legal requirements (must comply) and best-practice recommendations (should comply)
- Consider jurisdiction-specific variations (EU, US, specific states/countries)
- Flag biometric data, health data, financial data, children's data, and other special categories
- Identify consent requirements, data retention limits, and deletion obligations
- Note certification or audit requirements (SOC 2, ISO 27001, HIPAA BAA, etc.)
- Use web search tools to verify current regulatory status and recent changes
- When uncertain about legal interpretation, state the uncertainty explicitly and recommend professional legal review

---

## Compliance analysis structure

For each identified regulation, evaluate:

- **Applicability:** does this regulation apply to the product? Why / why not?
- **Key obligations:** what must the product do to comply?
- **Data types affected:** which data processed by the product falls under this regulation?
- **Pipeline impact:** which pipeline stages are affected and how?
- **Current gaps:** what is missing in the current design?
- **Remediation effort:** low / medium / high — what changes are needed?
- **Risk level:** low / medium / high / critical — consequence of non-compliance
- **Timeline pressure:** is there a deadline or enforcement date?

---

## Output format

```text
## Discovery Question
<what regulatory or compliance question is being explored>

## Context
<product description, target markets, data types processed, current architecture summary>

## Regulatory Landscape

### Regulation 1 — <name> (e.g., GDPR, CCPA, HIPAA)
- Applicability: yes / no / partial — <rationale>
- Jurisdiction: <where it applies>
- Key obligations:
  - ...
- Data types affected: <which product data falls under this>
- Pipeline stages affected: <which stages and how>
- Current gaps:
  - ...
- Remediation effort: low / medium / high
- Risk level: low / medium / high / critical
- Penalties: <summary of enforcement consequences>

### Regulation 2 — <name>
- (same structure)

## Special Data Categories
| Data type | Category | Regulations | Extra obligations |
|---|---|---|---|
| <e.g., voice recordings> | biometric | GDPR Art.9, BIPA | explicit consent, purpose limitation |

## Consent & User Rights Matrix
| Right / Obligation | Required by | Current status | Gap |
|---|---|---|---|
| Right to deletion | GDPR, CCPA | ... | ... |
| Data portability | GDPR | ... | ... |
| Consent before processing | GDPR, ePrivacy | ... | ... |

## Compliance Gaps Summary
| Gap | Regulation | Risk | Remediation effort | Priority |
|---|---|---|---|---|
| <gap> | <regulation> | critical / high / medium / low | low / medium / high | P0 / P1 / P2 |

## Architecture Implications
<what architectural changes compliance requires — data encryption, retention policies, consent flows, audit logging, data residency>

## Certification Requirements
| Certification | Required / Recommended | Applicable when | Effort |
|---|---|---|---|
| <e.g., SOC 2 Type II> | recommended | B2B enterprise sales | high |

## Recommendation
<prioritized list of compliance actions; what to address in MVP vs. later; where professional legal counsel is recommended>

## Disclaimer
This analysis is an AI-generated preliminary assessment. It does not constitute legal advice. Professional legal review is recommended before making compliance decisions.

## Assumptions Made
- ...

## Recommended Next Step
<one concrete action for Product or Architect>
```
