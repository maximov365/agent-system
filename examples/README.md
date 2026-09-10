# Optional examples

These are development fixtures and teaching examples. They are not part of the
installed framework: sync, bootstrap, and downstream rendering must not copy any
`examples/` source or runtime asset. Projects choose their own application code,
art direction, dependencies, and quality profile.

- `assets/`: minimal source/export provenance and validation fixture.
- `quality/`: a sample browser journey configuration, copied only by an owner.
- `game-slice/`: a standalone browser game exercising the visual and asset tools.
- `unfolda/`: historical configuration and project-document examples.

Optional example dependencies never belong in `requirements-framework.txt`.
Keep generated screenshots, traces, video, catalogs, and local reports under
`.agent/` (ignored). Commit concise reviewed evidence, not a session archive.
