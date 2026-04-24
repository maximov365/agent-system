# MCP Tools Configuration

This document describes external MCP (Model Context Protocol) tools used by tool-agents in the system.

MCP tools extend agent capabilities beyond text generation — enabling image generation, code execution, browser automation, and other external model integrations.

For optional methodological augmentation via Claude skills (prompt templates, not external services), see `docs/CLAUDE_SKILLS.md`.

---

## Image Generation (Illustrator agent)

The Illustrator agent requires an MCP server for AI image generation. Configure one of the following in your project's `.cursor/mcp.json`.

### Option A: nanobanana-mcp (recommended)

Google Nano Banana 2 / Nano Banana Pro via `@ycse/nanobanana-mcp`.

**Prerequisites:** Node.js 18+, Google AI API Key from [Google AI Studio](https://aistudio.google.com/apikey)

```json
{
  "mcpServers": {
    "nanobanana": {
      "command": "npx",
      "args": ["-y", "@ycse/nanobanana-mcp"],
      "env": {
        "GOOGLE_AI_API_KEY": "<your-api-key>"
      }
    }
  }
}
```

**Models available:** `nano-banana-2` (Flash, fast), `nano-banana-pro` (higher quality)

### Option B: mcp-image

Nano Banana 2 with automatic prompt optimization.

```json
{
  "mcpServers": {
    "mcp-image": {
      "command": "npx",
      "args": ["-y", "mcp-image"],
      "env": {
        "GEMINI_API_KEY": "<your-api-key>"
      }
    }
  }
}
```

**Features:** Auto-enhances simple prompts using Subject–Context–Style framework. Three quality tiers.

### Option C: Multi-provider (mcp-imagenate)

Supports Google Gemini, OpenAI, and FLUX models.

```json
{
  "mcpServers": {
    "mcp-imagenate": {
      "command": "npx",
      "args": ["-y", "mcp-imagenate"],
      "env": {
        "GOOGLE_AI_API_KEY": "<your-google-key>",
        "OPENAI_API_KEY": "<your-openai-key>"
      }
    }
  }
}
```

**Models available:** `nano-banana-2`, `nano-banana-pro`, `gpt-image-1.5`, `flux-2-klein`, `flux-2-pro`

---

## Setup instructions

1. Choose an MCP server option above
2. Get the required API key(s)
3. Create or edit `.cursor/mcp.json` in your project root
4. Restart Cursor to activate the MCP server
5. Verify by asking Illustrator to generate a test image

**Security:**
- Never commit API keys to the repository
- `.cursor/mcp.json` should be added to `.gitignore` if it contains secrets
- Use environment variables or a secrets manager for team setups

---

## Adding new MCP tools

When a new tool-agent requires an external MCP tool:

1. Document the MCP server configuration in this file
2. Reference this file from the agent definition
3. Add the MCP server name to the agent's "MCP tool dependency" section
4. Ensure the agent handles the "tool unavailable" case gracefully
