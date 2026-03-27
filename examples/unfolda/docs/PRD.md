# Unfolda — Product Requirements Document

Status: draft  
Version: 0.6  
Last updated: 2026-03-07

---

## Vision

Unfolda is a web-based AI service that transforms EPUB books into structured formats for reading and understanding in a foreign language.

A user uploads an EPUB, selects a mode and target language, and receives a transformed EPUB — either a high-quality context-aware translation, or a guided reading version with translations and explanations built into the text.

Unfolda is not a translator and not a library. It is a tool that **unfolds the meaning** of a text.

---

## Positioning

**Upload an EPUB book → get it back translated and explained.**

Unfolda is an AI service that turns EPUB books in many languages into a readable, understandable version in your language — with context-aware translation, idiom explanations, and cultural notes. Not a dictionary. Not a machine translator. A tool that makes foreign books readable.

---

## Core Value

Reading books in a foreign language is hard because:

- looking up words manually interrupts the reading flow
- dictionaries and translators miss cultural context and idioms
- existing tools are designed for short texts, not full books
- machine translation loses genre, tone, and character consistency

Unfolda solves this by transforming a complete book into a structured, AI-enhanced version that preserves the natural reading experience while making the foreign text understandable.

---

## Target Users


| Segment                 | Need                                                                |
| ----------------------- | ------------------------------------------------------------------- |
| Language learners       | Read real books as part of language practice                        |
| Expats and immigrants   | Understand books in the language of their new country               |
| Original-text readers   | Read books in the original language with comprehension support      |
| Quick-translation users | Get a high-quality, context-aware book translation for personal use |


---

## Product Modes

### Translate Mode

Full AI translation of the book with:

- genre and tone awareness
- consistent translation of names, titles, and gendered terms
- preservation of book structure and formatting

The user gets a high-quality translated EPUB that reads naturally.

### Guided Mode

Each paragraph is transformed into a structured reading block:

1. **Original text** — the source paragraph
2. **Translation** — full translation of the paragraph
3. **Explanations** — brief notes on idioms, cultural references, and non-obvious meaning
4. **Original text (shown again)** — the source paragraph again, for reinforced comprehension

This format allows the reader to understand the text in context and then re-read the original with fresh understanding.

In Guided Mode, translation and explanation generation may run as **separate internal passes**. This means Guided Mode is more expensive and slower than Translate Mode, but it also opens the possibility of regenerating explanations without a full retranslation in the future.

---

## Translation Options

When submitting a book, the user configures translation settings:


| Option              | Values                        | Effect                                                                       |
| ------------------- | ----------------------------- | ---------------------------------------------------------------------------- |
| Mode                | Translate / Guided            | Output format (see Product Modes)                                            |
| Target language     | user selection                | Language of translation and explanations                                     |
| Source language     | auto-detected                 | Can be overridden manually                                                   |
| Translation style   | literal / natural             | Literal stays close to the original wording; natural prioritizes readability |
| User language level | A1 / A2 / B1 / B2 / C1        | Controls vocabulary complexity and explanation depth in the output           |
| Explanation depth   | minimal / standard / detailed | Amount of cultural and idiomatic notes (Guided Mode only)                    |


**Translation style** affects how the AI translates:

- **Literal** — preserves the author's sentence structure and word choices where possible; useful for advanced learners who want to see how the original language works
- **Natural** — rephrases for fluency in the target language; useful for readers who want to understand the content comfortably

**User language level** adjusts the output to the reader's proficiency:

- A1–A2: simpler vocabulary in translations, more detailed explanations
- B1–B2: moderate vocabulary, standard explanations
- C1: advanced vocabulary, minimal explanations unless culturally significant

### Supported Languages (MVP)

The following languages are supported as both source and target for MVP:


| Language             | Code |
| -------------------- | ---- |
| English              | en   |
| Russian              | ru   |
| Serbian              | sr   |
| German               | de   |
| French               | fr   |
| Spanish              | es   |
| Italian              | it   |
| Portuguese           | pt   |
| Chinese (Simplified) | zh   |
| Japanese             | ja   |
| Korean               | ko   |
| Turkish              | tr   |
| Dutch                | nl   |
| Polish               | pl   |


Any combination of source and target from this list is a valid language pair.

Other languages may work (the underlying LLM supports them), but they are **not validated or guaranteed** for MVP. Additional languages can be added post-MVP based on demand.

---

## User Scenarios

### Scenario 1 — Guided reading for language learning

A user learning Italian logs in with Google, uploads an Italian novel as EPUB, and selects Guided Mode with their native language as the target. The service starts processing and shows a progress bar with estimated time. When the job completes, the user downloads a new EPUB where each paragraph includes the original text, translation, brief explanations of idioms, and a repeat of the original.

### Scenario 2 — Quick book translation

A user wants to read a Japanese business book but does not speak Japanese well enough. They log in, upload the EPUB, and select Translate Mode. The service processes the book — the user can close the browser and come back later. When the job is done, they download a translated EPUB that preserves the book's structure, formatting, and consistent use of terms and names.

### Scenario 3 — Cultural context for a classic

A user reads a French classic novel in Guided Mode. Beyond translation, the explanations highlight historical references, literary idioms, and cultural nuances that a standard dictionary would miss. The user sees processing progress and ETA before downloading the result.

---

## System Overview

### Delivery Model

Unfolda is a **SaaS web service**:

- users access the product through a web browser
- authentication via Google login
- books are uploaded to object storage (max EPUB size: **50 MB**)
- processing runs as background jobs with a queue
- users see progress and ETA during processing
- completed books are available for download
- credit-based usage limits control how many books a user can process
- source language is auto-detected

### Storage Policy

The service does **not** retain user book files permanently.

File lifecycle:

- the **uploaded EPUB** is stored until the job reaches a terminal state (completed, failed, or expired), plus a retention window — then eventually deleted
- the **generated EPUB** is stored until the first download or until the retention window expires — whichever comes first — then eventually deleted
- **retry** of a failed job is possible only while the uploaded file still exists (within the retention window)
- after all files are deleted, only **job metadata** is stored long-term (job ID, status, timestamps, settings, file size — no book content)

This is a legal and privacy requirement. Unfolda processes books on behalf of the user but does not store or redistribute them.

### Credits & Usage Limits

Unfolda uses a **credits** system to control access to processing.

**Credit unit:**

- credits are an **abstract unit**, not raw words
- the conversion formula maps source word count, processing mode, and settings to a credit cost (e.g. Guided Mode costs more than Translate Mode because it requires additional explanation passes)
- exact multipliers are admin-configurable constants, not hardcoded
- this abstraction supports attaching a monetary price per credit in the future without changing the pipeline

**Credit lifecycle:**

- each user has a **credit balance** visible in the UI at all times
- on registration, the user receives an **initial credit grant** (amount configurable by admin)
- before job confirmation, the system displays the **estimated credit cost** based on word count, mode, and settings
- credits are **reserved** when the job is submitted
- on **successful completion**, reserved credits are consumed
- on **failure or cancellation**, reserved credits are **refunded** to the user's balance
- when the balance is insufficient, the user cannot submit new jobs
- users can see a basic **credit transaction history** (grant, reservation, consumption, refund)
- credit reservations, consumption, and refunds must be **idempotent per job run**

**Credit management for MVP:** admin manages credit balances — grant credits, adjust balances, view credit history. Self-service purchase (payment provider integration) and monthly resets are post-MVP. The credits model is designed so that a payment layer can be added later without changing the core pipeline or credit logic.

**Cost guardrail:** jobs exceeding internal processing limits (e.g. estimated word count too high for a single run) may be rejected before processing starts. This protects against unexpected LLM costs.

### Job Lifecycle

Each book transformation is a **job**.

**Active states** (at most one per user):


| Status     | Meaning                                        |
| ---------- | ---------------------------------------------- |
| validating | EPUB uploaded, being validated                 |
| queued     | Validated, waiting in the processing queue     |
| processing | Pipeline is running (progress and ETA visible) |


**Terminal states:**


| Status    | Meaning                                         |
| --------- | ----------------------------------------------- |
| completed | Generated EPUB ready for download               |
| failed    | Processing failed — error message shown to user |
| cancelled | Processing stopped on user or operator request  |
| expired   | Files deleted after retention window            |


Rules:

- each user may have only **one active job** at a time (validating, queued, or processing)
- users can close the browser while processing is running — the job continues on the server
- completed jobs remain available for download until the retention window expires
- users can return later and download the generated EPUB
- a successfully honored cancellation resolves to **cancelled**, not **failed**
- estimated book size (word count), approximate processing time, and credit cost are shown before the user confirms the job

### Jobs List

Users can view a list of their submitted jobs, showing:

- book title
- mode and target language
- status (processing, completed, failed, cancelled, expired)
- progress and ETA (for active jobs)
- download link (for completed jobs)

### Processing Pipeline

The backend processes each book through a sequential pipeline:

```
ingestion → segmentation → translation → formatting → export
```


| Stage        | Responsibility                                                  |
| ------------ | --------------------------------------------------------------- |
| Ingestion    | Parse EPUB, extract text and structure                          |
| Segmentation | Split text into processing units (see Segmentation Model below) |
| Translation  | AI-powered translation and explanation generation               |
| Formatting   | Assemble output structure (Translate or Guided format)          |
| Export       | Produce the final EPUB file                                     |


Each stage has clear input/output boundaries and is independently testable.

### Segmentation Model

The output is **paragraph-based** — the user sees translations and explanations at the paragraph level.

Internally, large paragraphs may be split into smaller processing segments to fit within LLM context limits, but the output is assembled back into paragraph-level blocks. The segmentation boundary visible to the user is always the paragraph.

### EPUB Structure Preservation

The system preserves the original EPUB structure including:

- spine order
- chapter structure
- images
- footnotes
- links
- CSS styling (when possible)

The output EPUB must feel like a proper book, not a raw text dump.

If the source EPUB structure is partially malformed, the system attempts to recover readable text while preserving chapter boundaries when possible. Broken markup may be cleaned or ignored. Severely malformed files that cannot be parsed are rejected at the validation stage with a clear error.

### Output Metadata

The generated EPUB includes updated metadata:

- **title** — original title with a suffix indicating the mode and target language (e.g. "Il Nome della Rosa — Guided, EN")
- **author** — original author preserved
- **language** — set to the target language
- **description** — note indicating AI-generated content and the mode used
- **disclaimer page** — a short page inserted at the beginning of the book explaining that the content was generated by Unfolda and is not an official translation

### Output Consumption

Generated EPUB files are intended to be read in standard EPUB readers such as Apple Books, Moon Reader, KOReader, and similar applications.

Unfolda does not include a built-in reader. The user downloads the EPUB and opens it in their preferred reading app.

### Translation Consistency

The system maintains translation consistency by passing previous context and term mappings between segments. This ensures:

- character names are translated or kept consistently throughout the book
- gendered terms remain correct across chapters
- domain-specific terminology is used uniformly
- previously established translations are not contradicted later in the text

The specific mechanism (transient glossary, rolling context window, extracted named entities, chapter memory) is an architectural decision to be defined by the Architect. The PRD defines the requirement; the implementation approach is deferred to `docs/ARCHITECTURE.md`.

### Infrastructure Components


| Component      | Role                                           |
| -------------- | ---------------------------------------------- |
| Web frontend   | Upload, settings, progress, download           |
| API backend    | Auth, job management, pipeline orchestration   |
| Job queue      | Async processing of book transformation jobs   |
| Object storage | Store uploaded and generated EPUB files        |
| Database       | Users, jobs, credits, metadata                 |
| Admin panel    | Monitor jobs, manage users and credit balances |


---

## Interface Design

Unfolda follows a **mobile-first** interface design.

The primary interaction model assumes usage on smartphones, with layouts optimized for small screens and touch interaction. Desktop layouts adapt from the same design system.

Key design goals:

- minimal steps to upload a book
- clear processing status
- simple download of the generated EPUB

### Upload Experience

- file upload via **file picker** or **drag-and-drop**
- the system **validates the uploaded EPUB** before processing (file format, size limit, structure, no DRM)
- DRM-protected EPUBs are rejected with a clear message — the system does not circumvent copy protection
- validation errors are shown immediately with a clear message
- after successful validation, the user configures translation options and confirms the job
- estimated book size (word count), approximate processing time, and **estimated credit cost** are displayed before confirmation
- if the user's credit balance is insufficient, submission is blocked with a clear message

### Error Handling

- if EPUB validation fails, the user sees a clear error before any processing starts
- if processing fails mid-job, the job status changes to **failed** with an error message
- if a cancellation request is honored, the job status changes to **cancelled**
- failed or cancelled jobs do not consume credits — reserved credits are refunded
- retry of a failed job is supported within the retention window, using the original uploaded file if still available; if the file has expired, the user must re-upload
- the system does not silently drop jobs — every job reaches a terminal state (completed, failed, cancelled, or expired)

---

## Key Principles

- **Context-aware AI** — the AI understands genre, tone, character names, and maintains consistency across the book
- **Preserve the reading experience** — the output should feel like reading a book, not using a tool
- **Async processing** — book transformation is a background job; the user does not need to wait with the browser open
- **Transparent progress** — the user always knows where their job is and how long it will take
- **Reproducible pipeline** — the pipeline is structured and predictable; same input and settings should produce functionally consistent output (minor LLM variation is expected)

---

## MVP Scope

The MVP delivers a working web service with both product modes:

- Web interface for upload, settings, progress, jobs list, and download
- Mobile-first responsive design
- Google login for authentication
- Upload EPUB via file picker or drag-and-drop (max 50 MB)
- EPUB validation before processing
- Auto-detect source language
- Select mode (Translate Mode or Guided Mode) and target language
- Translation options: style (literal / natural), user language level (A1–C1), explanation depth
- Estimated book size (word count), approximate processing time, and credit cost shown before job confirmation
- One active job per user at a time
- Background job processing with progress bar and ETA
- *(nice-to-have)* Optional email notification on job completion
- Full pipeline: ingestion → segmentation → translation → formatting → export
- EPUB structure preservation (spine, chapters, images, footnotes, links, CSS)
- Translation consistency across segments (context and term mappings)
- Jobs list with status, progress, and download links
- Download the generated EPUB when the job completes
- Error handling: validation errors, failed jobs with clear messages, retry within retention window
- Storage policy: files deleted after terminal state + retention window, only metadata retained long-term
- Credit-based usage limits with user-visible balance, managed per user by admin
- Initial credit grant on registration (admin-configurable)
- Minimal admin panel for managing user credits and monitoring jobs

### MVP Non-Goals

- Non-EPUB input formats (TXT, PDF)
- Non-EPUB output formats (MOBI, PDF)
- Payment provider integration (credits abstraction is in MVP; Stripe / payment processing is not)
- User-editable glossaries or prompt customization
- Native mobile app (iOS / Android)
- Batch upload (multiple books at once)
- Social login providers other than Google

---

## Success Criteria

1. A user can sign in with Google, upload an EPUB, and receive a processed EPUB
2. Both Translate Mode and Guided Mode produce correct, well-formatted output
3. The output EPUB is valid, preserves book structure, and renders correctly in standard EPUB readers
4. Guided Mode output contains: original text, translation, explanations, and repeated original text for each paragraph
5. Translate Mode output is a coherent, context-aware translation preserving book structure
6. Translation options (style, level, explanation depth) visibly affect the output
7. Translation consistency is maintained across the book (names, terms, gender)
8. Source language is auto-detected correctly
9. The user sees real-time progress and estimated time remaining during processing
10. The user can close the browser and return later to download the result
11. Jobs list shows all submitted jobs with correct statuses
12. Failed jobs show clear error messages; retry works within retention window
13. Cancelled jobs are clearly distinguished from failed jobs
14. The pipeline processes a typical book (50,000–100,000 words) without failure
15. Processing is reproducible — same input and settings produce functionally consistent results
16. Uploaded and generated files are deleted according to the storage policy — no book content stored long-term
17. Output EPUB includes correct metadata (title suffix, author, language, disclaimer page)
18. Credit-based limits prevent abuse; user sees balance and per-job cost; failed or cancelled jobs refund reserved credits
19. Admin can view jobs, manage user credit balances, and configure initial credit grants

---

## Open Questions

- What LLM provider and model should be used for MVP? (→ Discovery)
- How should the system handle very long books that exceed context window limits? (→ Discovery)
- What tech stack for frontend and backend? (→ Discovery)
- What object storage provider? (→ Discovery)
- What job queue system? (→ Discovery)
- What is the exact retention window duration? (→ Product)
- How should language auto-detection work — per-book or per-segment? (→ Discovery)
- What is the default initial credit grant per user for MVP? (→ Product)
- What are the credit conversion multipliers per mode? (→ Product / Architect)
- What is the consistency mechanism between segments — transient glossary, rolling context, named entity extraction? (→ Architect)

---

## Risks


| Risk                                    | Impact                             | Mitigation                                                                 |
| --------------------------------------- | ---------------------------------- | -------------------------------------------------------------------------- |
| LLM output quality varies               | Inconsistent translations          | Low-temperature settings; output format validation                         |
| Large books exceed context limits       | Processing fails mid-book          | Segment into small units; process incrementally                            |
| EPUB parsing complexity                 | Edge cases in formatting           | Start with well-formed EPUBs; handle errors gracefully                     |
| Token cost for large books              | High processing cost               | Credit cost shown before processing; enforce limits; reserve credits       |
| Translation consistency across segments | Names/terms translated differently | Maintain glossary context passed to each segment                           |
| Long processing times                   | Poor user experience               | Progress bar, ETA, async processing, email notification                    |
| Object storage costs                    | Running costs grow with users      | 50 MB file limit; storage policy with retention window                     |
| Stored book content                     | Legal / copyright exposure         | Storage policy: files deleted per lifecycle rules; only metadata long-term |
| DRM-protected EPUBs                     | Legal risk if processed            | Reject DRM-protected files at validation; never circumvent copy protection |


---

## Future Directions

These are explicitly out of scope for MVP but represent the product roadmap:

- **Email notifications** — notify user when job completes (requires email provider, templates, opt-in)
- **Self-service credit purchase** — user buys credits via payment provider (Stripe); paid tiers with higher limits
- **Monthly credit resets** — automated credit management instead of manual admin control
- **Format support** — TXT, PDF input; MOBI, PDF output
- **Glossary management** — user-editable term translations and overrides
- **Batch processing** — process multiple books in a queue
- **Additional auth providers** — Apple, email/password
- **Push notifications** — browser push for job completion
- **Reading analytics** — track vocabulary progress across books
- **Collaborative glossaries** — shared term lists for language learning groups
- **Monetary cost display** — show estimated monetary price alongside credit cost before processing

