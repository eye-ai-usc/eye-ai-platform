# MCP Agent Setup

The EyeAI MCP agent gives Claude Code tools to interact with the Deriva catalog,
run DerivaML experiments, and search Eye-AI research papers — all from natural language.

The stack has three components:

| Component | Repo | Role |
|---|---|---|
| `deriva-mcp-core` | [informatics-isi-edu/deriva-mcp-core](https://github.com/informatics-isi-edu/deriva-mcp-core) | Base MCP server — Deriva catalog CRUD, schema, vocabulary |
| `deriva-ml-mcp-plugin` | [informatics-isi-edu/deriva-ml-mcp-plugin](https://github.com/informatics-isi-edu/deriva-ml-mcp-plugin) | DerivaML plugin — datasets, workflows, executions, features |
| `eye-ai-deriva-mcp-plugin` | [informatics-isi-edu/eye-ai-deriva-mcp-plugin](https://github.com/informatics-isi-edu/eye-ai-deriva-mcp-plugin) | Eye-AI plugin — RAG indexing of catalog tables and research papers |

The Claude Code skills plugins (`deriva-ml-skills`, `deriva-skills`) are installed separately.

---

## Step 1 — Install the MCP server

Install all three components into a single isolated `uv tool` environment:

```bash
uv tool install \
  --from git+https://github.com/informatics-isi-edu/deriva-mcp-core.git \
  --with 'deriva-ml-mcp-plugin @ git+https://github.com/informatics-isi-edu/deriva-ml-mcp-plugin.git' \
  --with 'eye-ai-deriva-mcp-plugin @ git+https://github.com/informatics-isi-edu/eye-ai-deriva-mcp-plugin.git' \
  --with 'deriva-ml @ git+https://github.com/informatics-isi-edu/deriva-ml.git' \
  deriva-mcp-core
```

Verify:
```bash
deriva-mcp-core --version
```

> **Note:** This is a separate `uv tool` installation, isolated from your research project
> environment. Do not add these packages to your research repo's `pyproject.toml`.

---

## Step 2 — Authenticate to the catalog

```bash
deriva-globus-auth-utils login --host www.eye-ai.org
```

This caches credentials in `~/.deriva/credential.json`, which the MCP server reads in stdio mode.

---

## Step 3 — Register with Claude Code

```bash
claude mcp add -t stdio deriva -- deriva-mcp-core --transport stdio
```

Verify the server appears in the tool list:
```bash
claude mcp list
```

You should see `deriva: deriva-mcp-core --transport stdio (stdio) - ✓ Connected`.

---

## Step 4 — Enable mutations and RAG (recommended)

By default the MCP server is read-only and RAG is disabled. For ML work you need both.

Create or edit `~/deriva-mcp.env`:

```ini
DERIVA_MCP_DISABLE_MUTATING_TOOLS=false
DERIVA_MCP_RAG_ENABLED=true
DERIVA_MCP_RAG_AUTO_ENRICH=true
```

Restart Claude Code for the settings to take effect.

> **What these do:**
> - `DISABLE_MUTATING_TOOLS=false` — enables write tools (create dataset, start execution, etc.)
> - `RAG_ENABLED=true` — enables semantic search over catalog schemas and docs
> - `RAG_AUTO_ENRICH=true` — automatically indexes Eye-AI catalog tables on first connect

---

## Step 5 — Install Claude Code skills plugins

The skills plugins provide slash commands (`/deriva-ml:*`) for guided DerivaML workflows.

```
/plugin marketplace add informatics-isi-edu/deriva-plugins
/plugin install deriva
/plugin install deriva-ml
```

Restart Claude Code. You should now have access to commands like:
- `/deriva-ml:dataset-lifecycle`
- `/deriva-ml:execution-lifecycle`
- `/deriva-ml:create-feature`
- `/deriva-ml:help`

---

## Updating the MCP stack

```bash
uv tool upgrade deriva-mcp-core
```

This upgrades all three components in the same tool venv.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `deriva-mcp-core: command not found` | Run the `uv tool install` command from Step 1 |
| `✗ Not connected` in `claude mcp list` | Restart Claude Code; check `~/.deriva/credential.json` exists |
| Read-only errors when running experiments | Add `DERIVA_MCP_DISABLE_MUTATING_TOOLS=false` to `~/deriva-mcp.env` |
| RAG search returns nothing | Add `DERIVA_MCP_RAG_ENABLED=true` to `~/deriva-mcp.env` and reconnect |
| Auth errors | Re-run `deriva-globus-auth-utils login --host www.eye-ai.org` |

For further details see the upstream READMEs:
- [deriva-mcp-core](https://github.com/informatics-isi-edu/deriva-mcp-core)
- [deriva-ml-mcp-plugin](https://github.com/informatics-isi-edu/deriva-ml-mcp-plugin)
- [eye-ai-deriva-mcp-plugin](https://github.com/informatics-isi-edu/eye-ai-deriva-mcp-plugin)
- [deriva-ml-skills](https://github.com/informatics-isi-edu/deriva-ml-skills)
