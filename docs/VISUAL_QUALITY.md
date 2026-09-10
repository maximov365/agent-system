# Visual production and acceptance

Use this contract for UI, illustration, visual effects, and animation. The goal is a coherent, usable product with evidence from the actual implementation. Role methods are optional; these acceptance checks are part of standard visual work.

## Establish a direction

Read the product goal, audience, existing brand, and reference images before editing. For a new visual identity, make a compact art-direction note: mood, composition, silhouette/shape language, typography, palette, materials, lighting, motion, and explicit avoid-list. Separate references for quality, layout, and mood; explain what each contributes. Preserve the user's identity and existing design system.

When the direction is unknown, explore a small number of meaningfully different directions or a focused prototype, then choose a defensible direction and continue within authorization. Do not require approval of every sketch or token. Ask when an unresolved choice would substantially change the product. Build one representative screen or scene to the intended finish before expanding the asset set.

## Define acceptance before asset production

Record the target platform, devices, viewport sizes/densities, input methods, reference baseline, important states, and performance budgets. The visual contract should name concrete outcomes: readable hierarchy, distinctive composition, consistent typography/materials, usable focus and error states, and coherent transitions. “Modern”, “premium”, or “pixel-perfect” alone is not acceptance criteria.

Use tokens/components for UI structure and text. Prefer existing vectors/icons for exact scalable geometry. Use image-generation tools for illustrations, textures, concept art, and bitmap assets. A screenshot of a dashboard is not a production dashboard. A generated image of a 3D scene is not a mesh, rig, or interactive level.

## Asset brief and provenance

Every production asset needs a stable ID and an entry in the project's asset manifest (JSON, YAML, or an existing asset database):

- Purpose and in-product location; original/source and runtime export paths.
- Author/provider, model/version when exposed, date, reference provenance, permitted use/license, and review status.
- Generation/edit prompt and references, parameters/seed only if actually supported, parent revision, and chosen variation. Never promise deterministic regeneration from a seed.
- Dimensions/aspect, file format, color/alpha requirements, maximum runtime size, intended scale/crop/safe area.
- For sprites: frame size/count/order, FPS, pivot, ground line, facing directions, loop/transition behavior, padding/extrusion, and atlas metadata.
- For 3D: units, coordinate orientation, topology/LOD targets, materials/textures, skeleton/rig, animation clips, collision, and import settings.

Keep editable originals separate from optimized runtime exports. Use consistent reference sheets for recurring characters, props, and environments. Edit approved assets when changing a detail so identity survives across variations. Do not generate each frame or character independently without checking consistency.

Inspect actual outputs before accepting them: transparent edges/halos, crop, seams/tiling, sharpness at display size, character identity, lighting consistency, text legibility, and correct import. Missing provenance or an unfinished asset is visible in the manifest; temporary placeholders must be labeled.

## Implement, run, inspect, correct

For web apps/browser games, `docs/VISUAL_RUNNER.md` provides an executable capture/journey adapter. Keep its configuration project-owned; preserve the distinction between automatic checks and viewed visual evidence.

1. Build the representative screen/scene using real components and approved assets.
2. Launch the application through available runtime tools. Exercise the primary journey and affected interactions.
3. Capture and **view** screenshots at representative desktop/mobile or target device sizes. Record route/scene, state, viewport, scale, and build/revision. A saved file that was never viewed is not visual review.
4. Check layout, composition, hierarchy, copy, tokens, image crops, motion, focus, touch behavior, loading/empty/error/success states, long text, localization, and reduced motion where applicable.
5. Compare with the relevant reference at matched dimensions. Fix material mismatches, inspect the changed states again, and retain final evidence.

For automated screenshot tests, control fixtures, time, animations, fonts, viewport, and randomness. Pixel diffs detect change, not taste or usability; use them together with human/visual judgment. Update baselines only for an intentional reviewed change. For animation, use recordings and interaction checks; a still image cannot prove timing quality.

If browser/device access is unavailable, deliver the artifact with a clear `visual verification pending` limitation and reproducible inspection steps. Never label static code review as a passed visual gate.

## Accessibility and performance

Use the project's accessibility target; for web work prefer WCAG 2.2 AA as the review baseline. This checklist is not a certification. Check semantics, keyboard interaction, labels, focus visibility/obscuring, contrast, zoom/reflow, modal focus return, and alternatives to drag-only interactions. WCAG 2.2 AA target size (2.5.8) is 24×24 CSS px with specified exceptions; 44×44 is a useful comfort target and relates to enhanced AAA criterion 2.5.5, not a universal AA rule. [W3C target-size guidance](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html).

Measure on the stated target rather than assuming a fast workstation represents mobile performance. Capture load time, input responsiveness, layout shift, memory, asset/network budget, and frame-time distribution as relevant. Establish project-specific limits before declaring a pass. See `docs/GAME_DEVELOPMENT.md` for games.

## Evidence report

For substantial visual work, keep a short review with baseline references, final screenshots/recordings, tested routes/states/devices, measured results, issues fixed, remaining issues, and reviewer identity. Score direction/coherence, composition, craft/detail, interaction, accessibility, and performance separately using a described rubric. Scores are judgments supported by evidence, not objective measurements. A serious usability, accessibility, or performance defect cannot be averaged away by attractive art.
