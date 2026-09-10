# Tools and media capabilities

The current host's tool list is the source of available capabilities. Framework documents describe possible integrations; they do not install or register tools.

## Capability order

1. Use an appropriate native tool/skill already available in Codex or the current client.
2. Use an installed connector, MCP server, or project CLI when it fits the task.
3. Add a provider integration only when the task needs it and installation/account access is authorized.

For image generation, use native image generation when present; Illustrator does not require a Cursor MCP server. For editing, follow the applicable image tool/skill and inspect references first. For vector/code-native graphics, use the existing asset/component system. For video/audio/3D, verify a capable tool is present; image output is not equivalent to those asset types.

For browser verification, use the host browser tools or the project's established test harness. A screenshot must be viewed to count as visual inspection. For profiling, collect measurements from the actual runtime/target. See `docs/VISUAL_QUALITY.md` and `docs/GAME_DEVELOPMENT.md`.

## Configuration

Codex MCP configuration belongs in the appropriate Codex configuration layer; Cursor and Claude Code have their own mechanisms. Follow the active client's current official documentation and the server's supported schema. Never copy `.cursor/mcp.json` into Codex and assume it is recognized.

Before introducing a server, verify publisher/source, supported operations, authentication method, version, and data destinations. Use environment/credential facilities instead of committing keys. Prefer pinned reviewed versions to unversioned automatic downloads. Request only task-relevant capabilities; respect the runtime sandbox.

When a tool is unavailable, explain what is missing and continue independent work. Never invent calls, results, model access, or API parameters. Optional gateways and third-party reviews follow `docs/MODEL_POLICY.md` and `docs/EXTERNAL_REVIEW_CONTRACT.md`.

## Project capability record

A project may record image generation/edit, browser/preview, engine/editor, audio/video, asset conversion, and profiling tools with a last-verified date. Record exact exposed tool/version, allowed input surfaces, outputs, limits/budget, and a fallback. Keep this in project-owned configuration so framework sync cannot overwrite it.

Old package rankings, price tables, Claude-specific result-size annotations, and claims that servers are already installed were removed from active guidance. Retain a verified project integration when useful; verify its current documentation before reusing historical setup examples.
