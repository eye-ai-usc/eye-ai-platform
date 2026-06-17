# Compatibility Matrix

Known-good combinations of `eye-ai` and `deriva-ml` for EyeAI research repos.

> The MCP stack (`deriva-mcp-core`, `deriva-ml-mcp-plugin`, `eye-ai-deriva-mcp-plugin`)
> is installed separately via `uv tool install` and is not version-pinned here.
> See [mcp-setup.md](../onboarding/mcp-setup.md).

| Stack Tag | eye-ai | deriva-ml | Python | Status | Date Blessed | Notes |
|---|---|---|---|---|---|---|
| `stable-2026-06-16` | v1.5.3 | v1.17.10 | 3.12 | Stable | 2026-06-16 | Initial blessed stack |

## How to pin in your research repo

```toml
[tool.uv.sources]
eye-ai = { git = "https://github.com/eye-ai-usc/eye-ai-ml.git", tag = "v1.5.3" }
deriva-ml = { git = "https://github.com/informatics-isi-edu/deriva-ml.git", tag = "v1.17.10" }
```
