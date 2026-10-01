# Lantern Market — optional integration example

A small original browser game used to test framework guidance and tools. No game
file is installed into downstream projects. This is a test and reference example,
not a framework runtime feature or a claim of production game readiness.

From this directory, run `node server.mjs` and open `http://127.0.0.1:4321`.
Keep the server running while playing. Do not open `index.html` directly or use a
static file preview: browser ES modules need the served page. A direct file view
can display the artwork while leaving the game code and buttons inactive.

Click **Открыть лавку** to start the 60-second session and enable the product
buttons. Read the three-item shopping list, then click those products on the lower
shelf or press keys 1–4. The first order is bread, oranges and fish; completing it
awards 125 points and advances to the next customer. A wrong or repeated item costs
two seconds. Escape or **Пауза** pauses the session; resume continues it, and the
result screen offers another evening when time runs out.

The application uses native browser APIs and has no package dependencies.

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

## Launch diagnostics

From the framework root, `python3 tools/profiles/profile.py doctor --project examples/game-slice`
inspects prerequisites without starting anything. Add `--verify-launch` to run the
existing browser journeys with an owned local server. The default port 4321 must
be free; keep an already open user session separate. This optional example and its
profile are never installed as downstream application code.
