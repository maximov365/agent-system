# Pipeline Contracts

This document defines the **data contracts and responsibilities** for each stage of the Unfolda processing pipeline.

Contract version: 0.4

The pipeline processes text through the following stages:

`ingestion → segmentation → translation → formatting → export`

Each stage has:

- clearly defined inputs
- clearly defined outputs
- explicit responsibilities
- explicit non-responsibilities

These contracts prevent architectural drift and enforce predictable data flow.

All stages must comply with:

- `docs/ARCHITECTURE_GUARDRAILS.md`
- `docs/ARCHITECTURE_CHECKLIST.md`

---

# Contract Stability Rule

Stage contracts are considered **stable interfaces** between pipeline stages.

Implementation code must treat these contracts as public boundaries.

Any change that modifies:

- stage inputs
- stage outputs
- field names
- data structure semantics

must be treated as a **breaking change**.

Breaking changes require:

- updating `docs/ARCHITECTURE.md`
- recording the change in `docs/DECISIONS.md`
- updating the **contract version** at the top of this document

---

# Pipeline Principles

The pipeline follows several core principles.

---

## Deterministic stages

Where possible, stages should behave deterministically.

This is especially important for:

- segmentation
- formatting
- export
- validation

LLM stages may be partially non-deterministic but must remain controlled.

---

## Explicit data flow

Each stage must:

- accept explicit inputs
- produce explicit outputs
- avoid hidden state

No stage should depend on implicit global state.

---

## Stage isolation

Stages must remain **independently testable**.

This means:

- stage logic must not depend on internal behavior of other stages
- stages must not call downstream stages directly
- orchestration must remain external to stage implementations

---

## No stage skipping

The pipeline must be executed in order:

`ingestion → segmentation → translation → formatting → export`

Stages must not bypass earlier stages.

---

## Error handling

Each stage must validate its inputs at entry.

Errors must include structured information:

- stage name
- input type
- reason for failure

Errors must:

- never be silently swallowed
- avoid leaking sensitive input content

---

## Input validation

Each stage must treat incoming data as untrusted.

Validate structure and content before processing.

---

## Idempotency

Pipeline stages should be **idempotent whenever possible**.

Running the same stage multiple times with the same input should produce the same output.

This is especially important for:

- retries
- pipeline recovery
- batch processing

If a stage cannot be fully idempotent (for example due to LLM behavior), the implementation must ensure that repeated execution does not corrupt pipeline state.

---

# Allowed Side Effects

Pipeline stages should remain **as pure as practical**.

Allowed side effects:

- structured logging
- metrics emission
- deterministic caching (if explicitly documented)

Not allowed:

- filesystem writes (except export stage)
- network calls (except translation stage)
- external service calls in non-LLM stages
- mutation of upstream data structures

Side effects must never change pipeline correctness.

---

# Data Structures

Pipeline stages operate on **structured intermediate representations** rather than raw strings.

These representations ensure that each stage has clear responsibilities.

Typical representations include:

- normalized documents
- segment collections
- translated segment collections
- formatted documents

Exact data types may evolve but the conceptual structure must remain consistent.


Stage contracts must not depend on language-specific implementations.
The pipeline should remain portable across implementations.

---

# Data Immutability

Pipeline stages must treat incoming data as **immutable**.

Stages must not mutate objects produced by upstream stages.

Instead, stages should produce **new structures derived from the input**.

Example: `SegmentCollection → TranslatedSegmentCollection`

This ensures:

- predictable pipeline behavior
- easier debugging
- reproducible processing

---

# Out-Of-Pipeline Contract

The system includes one important non-pipeline contract that interacts with submission flow but is not part of the pipeline stage order.

This contract exists to prevent architectural drift where pre-submission analysis is accidentally treated as:

- part of upload
- part of ingestion
- a hidden early pipeline stage

---

# Pre-Submission Analysis

## Responsibility

Provide lightweight, read-only metadata after upload and before job confirmation.

This contract is not a pipeline stage.
It must not be inserted into the pipeline order:

`ingestion → segmentation → translation → formatting → export`

---

## Inputs

Validated uploaded EPUB artifact metadata and storage reference.

---

## Outputs

A **PreSubmissionAnalysis** structure.

```
PreSubmissionAnalysis
  - artifact_id
  - source_language_preview
  - estimated_word_count
  - structural_signals
  - early_eligibility_flags
  - estimated_credit_inputs
```

The output is advisory metadata for submission and policy checks.
It is not a canonical pipeline artifact.

---

## Must Not

Pre-submission analysis must not:

- produce canonical pipeline artifacts
- invoke LLM models
- replace ingestion
- mutate document-processing state
- call downstream pipeline stages

The authoritative document representation is still produced by ingestion during execution.

---

## Estimate Reconciliation Rule

Pre-submission metadata is advisory.

Authoritative document metadata is produced by ingestion during execution.

If authoritative ingestion metadata differs materially from the pre-submission estimate:

- the difference must follow an explicit reconciliation rule
- the system must not silently mutate previously confirmed user expectations

For MVP, the user-confirmed credit reservation is based on the pre-submission estimate shown before confirmation. Authoritative ingestion metadata may inform analytics and future policy tuning, but must not silently increase the reserved credit amount after confirmation.

---

# Stage Contracts

---

# 1. Ingestion

## Responsibility

Convert the uploaded EPUB into a normalized internal representation.

For MVP, the only supported input format is EPUB.
The contract remains conceptually extensible, but implementation must treat EPUB as the sole supported ingestion source.

---

## Inputs

An uploaded source artifact reference.

```text
UploadedSourceArtifact
  - artifact_id
  - source_type               = epub
  - storage_key
  - mime_type
```

---

## Outputs

A **NormalizedDocument** structure.

```text
NormalizedDocument
  - document_id
  - source_type               = epub
  - title
  - author
  - text
  - detected_language       (auto-detected; can be overridden)
  - detection_confidence
  - source_word_count
  - chapter_refs[]
  - structural_refs[]
  - metadata
```

The ingestion output is authoritative for execution-time document metadata.
If it differs from pre-submission analysis, the explicit reconciliation rule above applies.
`text` may be stored as chapter-structured text segments rather than as one monolithic string.

---

## Must Not

The ingestion stage must not:

- perform segmentation
- perform translation
- perform formatting
- call downstream stages
- invoke LLM models

Its role is strictly **input normalization**.

---

# 2. Segmentation

## Responsibility

Split the normalized document into paragraph-visible segments ready for translation.

Segmentation prepares the document for translation while preserving structural information needed for reconstruction and batch planning.

---

## Inputs

```
NormalizedDocument
```

---

## Outputs

A **SegmentCollection**.

```text
SegmentCollection
  - document_id
  - mode                    (translate / guided)
  - segments[]
  - batch_planning

Segment
  - id
  - paragraph_id
  - chapter_ref
  - structural_ref
  - original_text
  - token_estimate

BatchPlanning
  - chapter_boundaries[]
  - batch_boundary_hints[]
  - estimated_batch_count
```

The user-visible segmentation boundary remains the paragraph.
Batch-planning metadata is deterministic planning data and must not change user-visible segmentation semantics.
`Segment.id` must be deterministic and stable for the same document.

Recommended structure:

`segment_id = hash(document_id + chapter_ref + paragraph_index)`

---

## Must Not

Segmentation must not:

- perform translation
- modify the meaning of original text
- perform formatting
- introduce LLM-based rewriting
- call downstream stages

Segmentation should remain deterministic where possible.

---

# 3. Translation

## Responsibility

Translate each segment into the target language.

This is the **primary LLM-driven stage**.

Translation is the **only pipeline stage allowed to invoke LLM models**.

No other stage may invoke LLM models directly or indirectly.

---

## Inputs

```
SegmentCollection
```

---

## Outputs

A **TranslatedSegmentCollection**.

```text
TranslatedSegmentCollection
  - document_id
  - mode                    (translate / guided)
  - translated_segments[]

TranslatedSegment
  - id
  - paragraph_id
  - chapter_ref
  - structural_ref
  - original_text
  - translated_text
  - explanations            (Guided Mode only, empty list in Translate Mode)
```

This contract describes stage output only.
Orchestration-owned runtime persistence fields such as `batch_index`, `input_hash`, `token_usage`, and `consistency_memory_snapshot` belong to runtime artifacts, not to the translation stage contract itself.

---

## Must Not

Translation must not:

- change segmentation boundaries
- perform formatting
- embed presentation logic
- alter upstream data structures

Formatting decisions belong to the formatting stage.

---

# 4. Formatting

## Responsibility

Convert translated segments into the mode-specific reading structure used by Unfolda.

This stage prepares mode-specific reading content for export.

Typical formatting behavior:

- combine source and translated content into mode-specific blocks
- assemble deterministic structures for `Translate` and `Guided` modes
- preserve paragraph order and mode-specific reading behavior

---

## Inputs

```
TranslatedSegmentCollection
```

---

## Outputs

A **FormattedDocument**.

```text
FormattedDocument
  - document_id
  - mode                    (translate / guided)
  - formatted_blocks[]

FormattedBlock
  - paragraph_id
  - chapter_ref
  - original
  - translation
  - explanations            (Guided Mode only, may be empty in Translate Mode)
  - original_repeat         (Guided Mode only, may be null in Translate Mode)
```

---

## Must Not

Formatting must not:

- perform translation
- call LLM models
- access external sources
- alter original segmentation

Formatting should remain deterministic.

---

# 5. Export

## Responsibility

Convert formatted output into the final EPUB file for delivery to the user.

The output format is **EPUB** — the only supported output format for MVP.

The export stage is responsible for:

- assembling formatted blocks into the EPUB structure
- preserving the original EPUB structure (spine order, chapters, images, footnotes, links, CSS)
- applying mode-specific layout (Translate Mode or Guided Mode)
- injecting output metadata (title suffix, author, language, disclaimer page)

---

## Inputs

```
FormattedDocument
```

---

## Outputs

A generated **EPUB file**.

```
ExportedEpub
  - file (binary EPUB)
  - metadata
      - title               (original title + mode/language suffix)
      - author              (original author)
      - language            (target language)
      - description         (AI-generated content note)
      - disclaimer_page     (inserted at start of book)
```

---

## Must Not

Export must not:

- perform translation
- modify segmentation
- alter formatting logic
- call upstream pipeline stages
- call LLM models

Export is strictly **structure assembly and EPUB generation**.

---

# Orchestration

Pipeline orchestration must remain separate from stage logic.

Orchestration responsibilities include:

- executing pipeline stages in order
- passing outputs between stages
- managing pipeline errors
- handling retries if required

Orchestration must not contain domain logic.

Stage logic must remain inside stage modules.

Stages themselves must remain **pure processing units**.

Orchestration must not modify the data structures defined by pipeline stages.

---

# Contract Evolution

Stage contracts may evolve over time.

However, changes that affect:

- stage inputs
- stage outputs
- pipeline order
- stage responsibilities

must be treated as **architectural changes**.

Such changes require:

- updates to `docs/ARCHITECTURE.md`
- a decision entry in `docs/DECISIONS.md`
- an update to the **contract version** at the top of this document
