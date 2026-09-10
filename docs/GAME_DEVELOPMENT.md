# Game development production contract

Load for game work. Reuse the existing game-market/game-design Discovery methods when useful, but carry their conclusions through a playable build and measured validation.

## Start with a playable vertical slice

Specify player fantasy, core loop, controls, camera, session length, target platform/device, intended art quality, and what makes the moment-to-moment interaction satisfying. Implement one representative playable encounter/level with final-quality direction, UI, animation, effects, and audio before scaling content. A market report or concept image is not a validated game.

Use a concrete loop: input → anticipation/action → readable consequence → audiovisual feedback → recovery/reward → next meaningful choice. Tune movement, acceleration/deceleration, collision, camera, aim or navigation assistance, anticipation, hit feedback, and failure/retry speed. Use genre-appropriate techniques; screenshake, hit-stop, particles, and haptics are optional and need comfort controls.

## Separate simulation from presentation

Keep rules/simulation, input mapping, rendering, assets, audio, and persistence decoupled where practical. Use a fixed simulation step for systems that need stable physics and interpolate presentation as appropriate; do not multiply a variable timestep everywhere and assume deterministic behavior. Use explicit random seeds for reproducible tests, not as a guarantee of cross-platform floating-point determinism.

Test start, play, pause, resume, death/win, retry, save/load, scene changes, background/foreground, and input disconnect when applicable. Cover simultaneous input, frame spikes, collisions at boundaries, missing assets, and corrupted/migrated saves. Multiplayer requires explicit authority, reconciliation, latency and abuse tests; do not add it as a cosmetic extension.

## Art, animation, audio

Follow `docs/VISUAL_QUALITY.md`. Maintain a style guide and reference sheets with silhouettes, scale, palette, lighting, and materials. Validate sprites in motion for frame jitter, consistent pivots/ground line, missing directions, clipping, and loop seams. Validate tilemaps for seams and readable navigation. Validate 3D assets in-engine for materials, scale, rigging, clipping, LOD, and collision.

Generated raster/video assets do not replace a skeletal rig, shader, 3D asset, or controllable animation. Build those with the engine/content tools actually available. Audio needs consistent levels, layering, event timing, loop seams, mixing priorities, pause behavior, and mute/volume controls. Record provenance and permitted use for sound/music as for art.

## Performance budgets

Record the target refresh/FPS and representative device before profiling. A 60 FPS target gives roughly 16.7 ms per frame; 30 FPS gives 33.3 ms. Measure p50/p95/p99 frame time and stalls, CPU/GPU bottlenecks where tools allow, memory/VRAM, loading/scene transition times, draw calls, shader compilation, texture/atlas sizes, and download budget. Label unavailable measurements instead of estimating them as facts.

Stress-test a representative worst-case scene and a longer session for leaks or thermal degradation where device access permits. Test on the actual target or clearly state emulator/desktop limitations. Optimize measured bottlenecks: batching/atlases, object reuse where warranted, culling/LOD, texture compression and load scheduling. Do not trade away the art direction before locating the bottleneck.

## Playtest and release evidence

Run a deterministic scripted smoke path for regression and a separate exploratory play session for feel. Record build, device, inputs, duration, objective, observations, and defects. Ask representative players to attempt the first session without coaching when feasible; report confusion, retries, control errors, and time to first meaningful interaction. Do not invent retention/revenue metrics or treat a simulated persona as real user research.

Acceptance requires: core loop works, state/save flows survive, visual/audio direction is coherent in motion, no known blocking defects, target budgets are met or exceptions explicit, and the limits of playtesting are recorded. Automated tests and agent judgment help, but “fun” and commercial polish require player evidence and iteration.
