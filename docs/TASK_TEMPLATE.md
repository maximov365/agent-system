# Task: <TASK-ID> — <Short task title>

Task ID: <TASK-ID>
Status: <planned / in progress / implemented / in review / approved / completed>
Owner: unassigned
Created by: <User / Product agent>
Priority: <low / medium / high>
Complexity: <small / medium / large>
Current agent: <Discovery / Product / Architect / Builder / Reviewer / none>
Related PRD section: <link or section name>
Pipeline stage: <ingestion / segmentation / translation / formatting / export / other>

---

# Goal

Describe the purpose of the task in 1–3 sentences.
Explain what capability the system will gain after this task is completed.
Avoid describing the implementation here — focus on the outcome.

Example:
> Add the ability to ingest plain text files as the first stage of the processing pipeline.

---

# Scope

Describe **what is included** in this task.
Use clear bullet points.

Example:
- Load `.txt` files from disk
- Validate file encoding
- Produce normalized internal text representation
- Pass the result to the segmentation stage

---

# Non-Goals

List things explicitly **not included in this task**.
This prevents scope creep.

Example:
- EPUB ingestion
- PDF parsing
- OCR support
- UI for file uploads

---

# Inputs

Describe the inputs this task expects.

Example:
- `.txt` file path
- UTF-8 encoded text

---

# Outputs

Describe what this task produces.

Example:
- normalized text string
- metadata object describing the source file

---

# Acceptance Criteria

Define clear success conditions.
Builder and Reviewer must rely on this section.

Example:
- System successfully loads `.txt` files
- Files larger than X MB are processed without crashing
- Invalid encoding produces a clear error
- Output format matches the interface defined in `docs/ARCHITECTURE.md`

---

# Constraints

List important constraints that must be respected.

Examples:
- Must follow the pipeline defined in `docs/ARCHITECTURE.md`
- Must not introduce new external dependencies
- Must keep the ingestion stage deterministic

---

# Dependencies

List tasks or components that must exist first.

Example:
- none

or:
- TASK-002 (segmentation interface)

---

# Risks

List possible implementation risks.

Example:
- large files may increase memory usage
- encoding detection may require careful validation

---

# Implementation Notes

_Filled by: Product or Architect_

Optional guidance for Architect.

Examples:
- Reuse existing filesystem utilities
- Avoid adding new dependencies
- Keep the ingestion logic isolated

Do **not** write code here.

---

# Architect Plan

_Filled by: Architect_

Link or paste the approved implementation plan once planning is complete.

- none (not yet planned)

---

# Files Likely Affected

_Filled by: Architect_

Optional section to help Architect during planning.

Example:
- `src/ingestion/loader.py`
- `tests/test_ingestion.py`

Architect may revise this list during planning.

---

# Definition of Done

> Note: Acceptance Criteria define *what* must work.
> Definition of Done defines *when the task is closed*.

The task is considered complete when:

- Implementation satisfies all acceptance criteria
- Reviewer approves the changes
- `docs/TASKS.md` status is updated to `completed`
- Relevant documentation is updated if needed

---

# Notes

Any extra context useful for Product, Architect, or Builder.

Example:
> This task introduces the first pipeline stage, so it should remain minimal and deterministic.

# Task Size Guidelines

Tasks should be small enough to be implemented in a single Builder step whenever possible.

If a task affects many modules or requires large architectural changes,
split it into multiple tasks.