# Updating Your Environment

Run through this guide whenever a new stack release is announced, or whenever MCP or
skills updates are posted. You do not need to do all three sections every time — each
section is independent.

Check the [compatibility matrix](../releases/compatibility-matrix.md) first to see
what changed in the new release and whether any breaking changes require action.

---

## 1. Update Python packages (eye-ai, deriva-ml)

Run this inside your research repo:

```bash
uv sync --frozen
```

`--frozen` installs exactly what is pinned in your repo's `uv.lock` with no changes.
Use this for day-to-day work to keep your environment consistent.

To adopt a newly released stack, copy the updated lockfile from this repo into yours
and then sync:

```bash
cp /path/to/eye-ai-platform/lockfiles/stable/uv.lock ./uv.lock
uv sync --frozen
```

Or if your repo has Renovate configured, merge the Renovate PR that was opened
automatically when the new lockfile was published.

To check what is currently installed:

```bash
uv pip show eye-ai deriva-ml
```

---

## 2. Update the MCP server

### Local machine (browser available)

**[Claude session]** Ask Claude: `"delete the mcp-eye-ai-org MCP server"`

**[Claude session]** Verify with `/mcp` — confirm `mcp-eye-ai-org` is no longer listed

**[Terminal]** Re-add the server:

```bash
claude mcp add -t http mcp-eye-ai-org https://mcp.eye-ai.org/mcp \
  --client-id deriva-mcp --callback-port 8080 -s user
```

**[Claude session]** Authenticate: `/mcp` → choose `mcp-eye-ai-org` → Authenticate →
complete the web login in your browser

### Compute node (no browser available)

**[Claude session]** Ask Claude: `"delete the www-eye-ai-org MCP server"`

**[Claude session]** Verify with `/mcp` — confirm `www-eye-ai-org` is no longer listed

**[Terminal]** Obtain a bearer token (run from inside an eye-ai project repo):

```bash
uv sync
uv run deriva-credenza-auth-utils --host www.eye-ai.org login \
  --resource https://mcp.eye-ai.org/mcp --refresh --show-token
```

Copy the token printed to stdout.

**[Terminal]** Add the server with the token:

```bash
claude mcp add --transport http www-eye-ai-org https://mcp.eye-ai.org/mcp \
  --header "Authorization: Bearer <TOKEN VALUE>"
```

**[Terminal]** Verify:

```bash
claude mcp list
```

You should see the server listed with `✓ Connected`.

---

## 3. Update skills

**[Claude session]** Ask Claude:
`"delete all old deriva-related skills and marketplace"`

Claude will clean up `installed_plugins.json`, `settings.json`,
`known_marketplaces.json`, and the plugin cache.

**[Claude session]** Re-add the marketplace:

```
/plugin marketplace add informatics-isi-edu/deriva-plugins
```

**[Claude session]** Reinstall the plugins:

```
/plugin install deriva@deriva-plugins
/plugin install deriva-ml@deriva-plugins
```

**[Claude session]** Reload:

```
/reload-plugins
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Import errors after `uv sync` | Delete `.venv/` and re-run `uv sync --frozen` |
| `✗ Not connected` after MCP update | Restart Claude Code; re-run the authenticate step |
| Bearer token rejected on compute node | Token may have expired — re-run `deriva-credenza-auth-utils ... --refresh --show-token` |
| Skills commands missing after reinstall | Run `/reload-plugins`; if still missing, restart Claude Code |
| Not sure what version you have | `uv pip show eye-ai deriva-ml` for packages; `/mcp` in Claude for MCP status |
