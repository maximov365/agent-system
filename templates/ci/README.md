# CI/CD Templates

Reference GitHub Actions workflows for common project stacks. Copy to your project's `.github/workflows/` and customize.

## Available templates

| Template | Stack | Pipeline |
|---|---|---|
| `web-api.yml` | Next.js + FastAPI/Express + PostgreSQL + Redis | lint → test → build → deploy staging → smoke test → deploy prod |
| `macos-app.yml` | Swift/SwiftUI + SPM + Sparkle + DMG | test → build → sign → notarize → DMG → release → appcast |

## Usage

1. Copy the template that matches your stack
2. Search for `<-- customize` comments and replace placeholder values
3. Uncomment deploy sections when ready
4. Add required secrets to your GitHub repository settings
5. Update `docs/DEPLOY_CONTRACTS.md` with your CI/CD pipeline stages

These templates are **not auto-synced** to downstream projects. Each project maintains its own CI configuration.
