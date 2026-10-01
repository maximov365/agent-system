# Design craft methods

Use the relevant section for an actual design decision. `docs/VISUAL_QUALITY.md`
defines acceptance and runtime evidence; this reference supplies practical methods.
These are contextual techniques, not a mandatory style or a second approval loop.

## Direction and project memory

First identify what the visitor needs on this surface: decide, operate, read, or
explore. A marketing page and a settings screen in the same product can need very
different density and motion. Games also need play-specific readability and input
feedback; interface advice is not a replacement for playtesting.

Use the project's existing brand document and actual tokens as the source of truth.
`docs/BRAND.md` is the framework's optional seed. Extract the current visual system
from running screens and source when that document is empty. Do not create a
parallel DESIGN.md/PRODUCT.md hierarchy simply because a third-party skill uses it.
Record audience/task, product character, reference observations, type roles,
spacing/density, semantic colors, component shapes, imagery and motion intent.
Link real token/component files; avoid copying values that will drift.

For a genuinely open direction, compare a few structurally different sketches of
one representative screen. Change information order, grouping, image treatment or
the relationship of text and controls. A palette swap is not a different concept.
Choose with reasons tied to content and users; user feedback can steer the choice
without requiring approval for every reversible refinement.

References are evidence: view them, explain which property helps, and interpret it
for this product. Preserve factual content and asset provenance. Do not invent
testimonials, customer logos or metrics to fill a persuasive composition.

## Composition and density

Define one primary action or reading anchor per meaningful region. Use alignment
and relative spacing to make groups legible before adding outlines, cards or
decorative backgrounds. Repeated surfaces should represent repeated concepts.

**Before:** every field, label and action has its own bordered card with equal
spacing. **After:** related fields share a group; larger gaps separate tasks; a
single primary action follows the fields it acts on. Keep distinct status or
comparison cards when their boundaries help interpretation.

Choose density for the job. A professional table can be compact and a museum page
spacious. Test both with actual content, including long names, empty data, errors
and realistic counts. Break layouts when the content no longer fits, rather than
blindly inheriting device breakpoints. Preserve visible actions at narrow widths,
zoom and translated text lengths; fix overflow instead of hiding the page edge.

## Typography and fine detail

Use a small role-based type scale: display, heading, body, label, supporting text.
Choose fonts for character, readability, language coverage and available weights.
Existing system fonts or Inter can be appropriate; no family is inherently a
design defect. Check Cyrillic and other required scripts in the rendered result.

Inspect real line breaks, not only CSS declarations. Keep long reading measures
comfortable; distinguish dense UI labels from paragraphs. Consider balanced
wrapping for short headings where supported, but retest narrow widths and long
translations. Load actual weights; avoid accidental synthetic bold/italic.

**Before:** a timer changes width on every tick. **After:** use the font's tabular
digits for changing numeric values (`font-variant-numeric: tabular-nums`) and verify
that the selected font supports them. Do not apply numeric styling to all text.

**Before:** nested rounded surfaces have unrelated corners and cramped inner
padding. **After:** tune the inner radius and inset together, then inspect optical
alignment at actual display size. A radius formula is a starting point, not proof
of visual balance. Match icon stroke, optical size and baseline across controls.

## Color and imagery

Name colors by purpose: surface, elevated surface, main text, secondary text,
accent/action, focus, success, warning and error. Define light/dark behavior where
the product supports both. Perceptual spaces such as OKLCH can help construct
scales; they do not establish accessible contrast. Measure actual rendered pairs
under the project's accessibility target. APCA research does not replace the
WCAG 2.2 conformance checks named by this framework.

**Before:** lowering an entire control's opacity also dims its label and focus
indicator. **After:** define the individual surface/text/state tokens and inspect
the resulting contrast. Do not use color alone to convey a critical status.

Use meaningful imagery at the right crop and scale. Generate bitmap assets only
when they help the intended direction. For APIs exposing quality/model controls,
compare inexpensive drafts before producing final selected assets; preserve the
actual prompt, exposed parameters and parent revision. Native tools may not expose
those controls: record unknowns honestly. A high-quality setting cannot establish
character consistency, correct alpha edges or successful in-product integration.
[Current image API options](https://developers.openai.com/api/docs/guides/image-generation).

## Motion with a purpose

Name the purpose before adding motion: feedback, continuity, state change,
explanation or deliberate celebration. Tune frequent operations for responsiveness;
do not turn routine navigation into a repeated presentation. Playful game feedback
and an administrative form have different needs.

**Before:** reopening a panel during its closing animation snaps it to an old
position. **After:** retarget from its current state and test repeated activation,
reverse, cancel and focus return. Use an existing motion system, or a small CSS
transition when sufficient. New animation libraries require an actual need.

Measure the result under load. Prefer compositor-friendly properties where suitable,
but verify rather than assuming any CSS animation is automatically smooth. Check
touch/hover differences, reduced-motion behavior and recordings at normal speed.
No universal curve, duration or ban on bounce fits every product.

## Critique, correction and stopping

First examine the running result as a whole: task clarity, reading order, visual
character, consistency and the relationship of content to composition. Then inspect
details and technical evidence. Automated lint/pixel differences can find defects;
they cannot decide whether the product has an appropriate visual identity.

Prioritize a few root causes. State the element/state, observed issue, user impact,
proposed correction and evidence. Separate a blocked action or inaccessible label
from an aesthetic preference. Apply coherent fixes together, inspect affected
states, and stop when acceptance is met and no material defect remains. Repeat
only for new defects or changed inputs, without an arbitrary cap that leaves a
known serious problem unresolved. Describe self-review as self-review.

For a design-process comparison use identical briefs/content/devices and preserved
interaction requirements. Present captures without method labels when possible;
record the evaluator's reasons and preferences alongside failures and timing.
Do not turn a self-assigned visual score into a measured improvement.

## Sources and adaptation

Original framework guidance informed by inspected upstream methods (2026-10-01):
[Impeccable](https://github.com/pbakaus/impeccable) for focused design operations;
[Hallmark](https://github.com/Nutlope/hallmark) for composition and reference analysis;
[Jakub Krehel](https://github.com/jakubkrehel/skills) for typography/layout detail;
[Emil Kowalski](https://github.com/emilkowalski/skills) for motion decisions;
[Color Expert](https://github.com/meodai/skill.color-expert) for color research.
No upstream code, executable engine, hook or full skill bundle is vendored. Their
stylistic bans, automatic delegation and additional approval rules are not adopted.
