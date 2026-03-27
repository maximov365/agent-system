# Task: <TASK-ID> — <Short task title>

Task ID: <TASK-ID>
Status: <planned / in_progress / implemented / in_review / approved / completed>
Owner: unassigned
Created by: <User / Product agent>
Priority: <low / medium / high>
Complexity: <small / medium / large>
Current agent: <Discovery / Product / Architect / Builder / Reviewer / none>
Related PRD section: <link or section name>
Pipeline stage: <{{ pipeline.stages | map(attribute='name') | join(' / ') }} / cross-cutting>

---

# Goal

Describe the purpose of the task in 1–3 sentences.
Explain what capability the system will gain after this task is completed.
Avoid describing the implementation here — focus on the outcome.

Example:
> Add the ability to accept CSV input as the first stage of the processing pipeline.

---

# Scope

Describe **what is included** in this task.
Use clear bullet points.

Example:
- Parse `.csv` files from disk
- Validate file structure and encoding
- Produce normalized internal representation
- Pass the result to the next pipeline stage

---

# Non-Goals

List things explicitly **not included in this task**.
This prevents scope creep.

Example:
- Excel format support
- PDF parsing
- Cloud storage integration
- UI for file uploads

---

# Inputs

Describe the inputs this task expects.

Example:
- `.csv` file path
- UTF-8 encoded content

---

# Outputs

Describe what this task produces.

Example:
- normalized data structure
- metadata object describing the source file

---

# Acceptance Criteria

Define clear success conditions.
Builder and Reviewer must rely on this section.

Example:
- System successfully loads `.csv` files
- Files larger than X MB are processed without crashing
- Invalid structure produces a clear error
- Output format matches the interface defined in `docs/ARCHITECTURE.md`

---

# Constraints

List important constraints that must be respected.

Examples:
- Must follow the pipeline defined in `docs/ARCHITECTURE.md`
- Must not introduce new external dependencies
- Must keep the ingest stage deterministic

---

# Dependencies

List tasks or components that must exist first.

Example:
- none

or:
- TASK-002 (processing stage interface)

---

# Risks

List possible implementation risks.

Example:
- large files may increase memory usage
- malformed CSV may require careful validation

---

# Implementation Notes

_Filled by: Product or Architect_

Optional guidance for Architect.

Examples:
- Reuse existing filesystem utilities
- Avoid adding new dependencies
- Keep the ingest logic isolated

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
- `src/ingest/parser.py`
- `tests/test_ingest.py`

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
> This task introduces a new input format, so it should remain minimal and deterministic.

# Task Size Guidelines

Tasks should be small enough to be implemented in a single Builder step whenever possible.

If a task affects many modules or requires large architectural changes,
split it into multiple tasks.