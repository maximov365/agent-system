# Lantern Market — optional integration example

A small original browser game used to test framework guidance and tools. No game
file is installed into downstream projects. This is a test and reference example,
not a framework runtime feature or a claim of production game readiness.

Run `node server.mjs` here and open `http://127.0.0.1:4321`. The application uses
native browser APIs and has no package dependencies. Pack three-item orders with
the pointer or keys 1–4; Escape pauses. A regular session lasts 60 seconds.

From the framework root:

```sh
node --test examples/game-slice/test/model.test.mjs
node examples/game-slice/quality/playthrough.mjs
python tools/assets/assetlib.py validate --project examples/game-slice
node tools/visual/run.mjs --project examples/game-slice
```

The last two commands use optional tooling dependencies documented in
`docs/ASSET_LIBRARY.md` and `docs/VISUAL_RUNNER.md`. Browser journeys explicitly
use an 8-second seeded fixture. Normal play and animation require their own
observations. See `ART_DIRECTION.md` and the framework review report.

Source artwork, exports, generation provenance, and original procedural audio
are under `assets/`. Evidence output stays in the ignored `.agent/` directory.
No example CI, package, asset, server, or test is added to downstream projects.
