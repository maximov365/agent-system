# Asset library

The optional `.agent-system/assets/assetlib.py` maintains project-owned `assets/manifest.json`. It records immutable asset ID/revision pairs, parent revisions, source/export paths and hashes, provenance, review status, import settings, and runtime size budgets. It inspects files without editing the artwork.

Install `.agent-system/assets/requirements.txt` into an appropriate environment for raster inspection. The framework developer environment uses `requirements-dev.txt`.

```bash
python3 .agent-system/assets/assetlib.py register --entry assets/new-entry.json
python3 .agent-system/assets/assetlib.py validate
python3 .agent-system/assets/assetlib.py catalog
python3 .agent-system/assets/assetlib.py inspect --file assets/runtime/hero.png
```

Each command accepts `--project`; paths in the manifest, `--entry`, and `--output` remain project-relative. JSON output distinguishes passed metadata checks from a required visual/motion review. Catalog defaults to `.agent/assets/index.html` and refuses to overwrite an existing catalog; choose a new output path for each review. Only register mutates the manifest, after validating the complete candidate library. Coordinate writers through normal task ownership.

## Entry contract

Each entry requires `id` (stable lowercase slug), positive integer `revision`, optional `parent` (`id@revision`), `kind`, `source`, `author`, `license`/permitted-use statement, `created_at`, `purpose`, `review_status` (`draft`, `reviewed`, or `placeholder`), and nonempty `exports`. Registration fills SHA-256 hashes. Keep source and export paths separate; originals may be editable art, a project-authored procedural source, or a generated original. Do not replace a prior revision silently.

Each export records `path`, `sha256`, and positive `max_bytes`; images may require width/height and `alpha: required|opaque`. Generated assets also record `generation.provider`, actual `generation.prompt`, and model/version when exposed. References record `source` and `permitted_use`. The validator checks presence/consistency; it does not establish legal ownership or independently verify a provider's claims.

Sprite entries add `sprite.frame_width`, `frame_height`, `frame_count`, `fps`, `pivot: [x,y]`, optional `transparent_padding`, and `ground_line_tolerance`. The complete regular grid must match frame count; each frame must contain pixels, respect requested padding, and fit the ground-line tolerance when applicable. For jumps or non-grid atlases use explicit project-specific validation rather than an inappropriate tolerance.

PCM16 WAV inspection reports duration, channels, sample rate, peak, RMS, and first/last-sample discontinuity. Exports can set `max_peak`, `loop`, and `max_loop_delta`. A smooth sample boundary does not prove an inaudible seam or a well-mixed sound; listen in the running product.

glTF 2.0 JSON inspection checks local buffer/texture references and reports mesh/material/rig/animation counts. Target-engine import, scale, materials, topology, collision, and animation review remain required. GLB/FBX, compressed audio, irregular atlases, and images above 16,777,216 pixels require suitable project-specific adapters; unsupported formats fail explicitly. SVG inspection rejects scripts, embedded HTML, external entities/resources and event handlers.

`examples/assets/` is a minimal usable library; the playable example extends the same contract. Use `docs/VISUAL_QUALITY.md` for art direction and observed acceptance.
