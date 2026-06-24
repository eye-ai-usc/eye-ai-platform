# Quickstart Guide

This guide takes you from a fresh machine to running your first EyeAI experiment.

---

## Prerequisites

- **Python 3.12** (managed via `uv` — see below)
- **uv** package manager ([installation](https://docs.astral.sh/uv/getting-started/installation/))
- **git**
- **GitHub account** with access to `eye-ai-usc` org (request from a project admin)
- **Globus account** for authenticating to the EyeAI Deriva catalog

---

## Step 1 — Install uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# or via Homebrew
brew install uv
```

Verify:
```bash
uv --version  # should print 0.5+ 
```

---

## Step 2 — Clone and install a research repo

You will work in an existing research repo or create a new one from the template.

### Option A: Clone an existing research repo

```bash
git clone https://github.com/eye-ai-usc/<repo-name>.git
cd <repo-name>
uv sync
```

`uv sync` installs all dependencies (including `eye-ai` and `deriva-ml`) into an isolated
virtual environment in `.venv/`. Python 3.12 is managed automatically by uv.

### Option B: Start a new research repo from the template

```bash
uvx cookiecutter gh:eye-ai-usc/eye-ai-platform --directory templates/researcher-repo
```

Answer the prompts (project name, researcher name, description), then:

```bash
cd <your-project-name>
uv sync
```

---

## Step 3 — Authenticate to the EyeAI Deriva catalog

```bash
# Install the Globus auth utility (one-time)
uv tool install deriva-globus-auth-utils

# Authenticate (opens a browser)
deriva-globus-auth-utils login --host www.eye-ai.org
```

Your credentials are cached in `~/.deriva/credential.json` and are reused across sessions.
Re-run this command when your session expires.

---

## Step 4 — Set up the MCP agent (optional but recommended)

The MCP agent lets you interact with the EyeAI catalog and run DerivaML experiments
through Claude Code's natural language interface.

See **[docs/onboarding/mcp-setup.md](mcp-setup.md)** for the full installation recipe.

---

## Step 5 — Run your first experiment

Open the Jupyter environment:

```bash
uv run jupyter lab
```

Then open a notebook in `notebooks/` or `experiments/` and follow the experiment tracing
pattern documented in [docs/guides/experiment-tracing.md](../guides/experiment-tracing.md).

---

## Keeping dependencies up to date

When a new stack release is published, a Renovate PR will be opened in your research repo
automatically. Before merging, check the
[compatibility matrix](../releases/compatibility-matrix.md) for any breaking changes.

To update manually:

```bash
uv sync --upgrade-package eye-ai
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `uv: command not found` | Re-run the uv install command and restart your shell |
| `deriva-globus-auth-utils: command not found` | Run `uv tool install deriva-globus-auth-utils` |
| Auth errors connecting to catalog | Run `deriva-globus-auth-utils login --host www.eye-ai.org` again |
| Import errors for `eye_ai` or `deriva_ml` | Run `uv sync` in your project directory |
| Python version mismatch | Run `uv python install 3.12` then `uv sync` |
