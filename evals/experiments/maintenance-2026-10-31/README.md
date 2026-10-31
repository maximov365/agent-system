# Bounded maintenance experiments

These synthetic fixtures are repository-only evaluation inputs, not application
features or deployed framework files. They do not change model defaults, install
skills, update screenshot baselines or perform an independent review. Run from the
framework root after installing its optional visual dependencies and test browser.

```bash
npm install --prefix .agent/maintenance-comparison --save-exact pixelmatch@8.0.0
node evals/experiments/maintenance-2026-10-31/visual.mjs \
  .agent/maintenance-visual \
  .agent/maintenance-comparison/node_modules/pixelmatch/index.js
python3 evals/experiments/maintenance-2026-10-31/reviews.py \
  --image .agent/maintenance-visual/broken.png --output .agent/maintenance-models
```

The last command only previews case IDs and prompt hashes. Add `--run` to authorize
seven actual Codex calls: one old/new specification-review pair, one structured
adapter check, and two visual repeats per model, with reversed order on repeat 2.
Each call has a 180-second limit. Unavailable models are recorded without fallback
or further calls. Output must be a fresh directory. User configuration is ignored;
host built-in instructions still contribute to context. Only synthetic prompts,
responses and runtime metadata are stored. Read-only mode does not hide the
filesystem, so the prompt requires no tool use; inspect actual events before
claiming isolation or comparability.

Specification expectations, fixed before execution: report unauthorized overwrite,
private-note transmission, out-of-scope cloud/accounts, untestable acceptance, and
missing empty/error/cancel/verification behavior. Visual expectations: clipped
payment button, overlapping total/receipt labels, unreadable pale total. Inspect
the actual screenshot and outputs; do not use a model's self-awarded quality score.
The three visible defects are deliberately explicit in the requirements; this is
a defect-checking smoke test, not a broad design critique benchmark.

Pixelmatch compares identical, near-white tint, one-pixel translation, missing
button, clipped button, low-contrast total and combined-defect screenshots at
640×480, scale 1, threshold 0.1. Version 8's 32×32 window result is a *local maximum
count*, not a full-frame count/ratio. The fixture does not cover sprite alpha,
real-device rendering, complex games or broad raster noise. Source and input hashes,
versions, findings and limitations are recorded in the dated maintenance report.
