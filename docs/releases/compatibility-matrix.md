# Compatibility Matrix

Known-good combinations of `eye-ai` and `deriva-ml` for EyeAI research repos.

> The MCP stack (`deriva-mcp-core`, `deriva-ml-mcp-plugin`, `eye-ai-deriva-mcp-plugin`)
> is installed separately via `uv tool install` and is not version-pinned here.
> See [mcp-setup.md](../onboarding/mcp-setup.md).

| Stack Tag | eye-ai | deriva-ml | Python | Status | Release Date | Notes |
|---|---|---|---|---|---|---|
| `stable-2026-06-16` | v1.5.3 | 1.51.2 (git main) | 3.12 | Stable | 2026-06-16 | Initial blessed stack. `deriva-ml` resolves transitively via `eye-ai@v1.5.3`; no independent tag pin possible. |

## How to pin in your research repo

```toml
[tool.uv.sources]
# Only pin eye-ai by tag; deriva-ml resolves transitively from it.
eye-ai = { git = "https://github.com/eye-ai-usc/eye-ai-ml.git", tag = "v1.5.3" }
```

Copy `lockfiles/stable/uv.lock` into your repo and run `uv sync --frozen` for a fully reproducible environment.
