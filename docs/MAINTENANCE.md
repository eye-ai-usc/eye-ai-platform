# Maintenance Guide

This document explains how to keep `eye-ai-platform` up to date as the upstream stack evolves.
It covers what is automated, what requires manual action, and the full procedure for blessing a new stack version.

---

## Repo responsibilities at a glance

`eye-ai-platform` owns three things:

1. **Onboarding documentation** — `docs/onboarding/`, `docs/guides/`
2. **Blessed dependency stack** — `lockfiles/stable/uv.lock`, `lockfiles/stable/manifest.toml`
3. **Researcher repo template** — `templates/researcher-repo/`

None of these change on their own. Every update is triggered by one of two events: an upstream package release, or a change in team practice (new tool, new workflow, new onboarding step).

---

## What is automated

| Trigger | What happens automatically |
|---|---|
| Every Monday 08:00 UTC | `integration-test.yml` installs the latest `eye-ai` and `deriva-ml`, runs `tests/integration/`, and opens a draft PR to `lockfile/testing` if tests pass |
| A GitHub Release is published on this repo | `notify-release.yml` posts a Slack message with the tag and changelog link |

**Nothing else is automated.** Promoting a lockfile from `testing` to `stable`, updating version numbers in docs, and archiving old lockfiles are all manual steps.

---

## Procedure: blessing a new stack version

This is the main recurring task. It happens when a new `eye-ai` release is ready for the team to adopt.

### Step 1 — Wait for the integration test to pass

The weekly CI run (`integration-test.yml`) tests the latest upstream and opens a PR to `lockfile/testing` if it passes.

- If the PR is open and green: proceed to Step 2.
- If tests are failing: open an issue upstream (or ping the Deriva maintainer) and stay on the current blessed stack. Do not bless a broken stack.
- To trigger the test manually before Monday: go to **Actions → Integration Test - Latest Stack → Run workflow**.

### Step 2 — Soak period (1–2 weeks)

Before blessing, let one or two active research repos test against `lockfiles/testing/uv.lock`:

1. In a research repo, temporarily replace `uv.lock` with the testing lockfile.
2. Ask a researcher to run their usual workflow and confirm nothing is broken.
3. One week is enough for minor updates; two weeks for major version bumps.

### Step 3 — Generate the new stable lockfile locally

```bash
cd /tmp && uv init --python 3.12 eyeai-newstack && cd eyeai-newstack
uv add "eye-ai @ git+https://github.com/eye-ai-usc/eye-ai-ml.git@<NEW_TAG>"
```

Replace `<NEW_TAG>` with the new `eye-ai` release tag (e.g. `v1.6.0`). Do **not** add a separate `deriva-ml` pin — it resolves transitively.

After the command completes, check the resolved `deriva-ml` version:

```bash
grep -A 4 '"deriva-ml"' uv.lock | head -5
```

Note down the resolved `version` and `source` commit SHA — you'll need them for `manifest.toml`.

### Step 4 — Update files in this repo

Copy the new lockfile:

```bash
cp /tmp/eyeai-newstack/uv.lock /path/to/eye-ai-platform/lockfiles/stable/uv.lock
```

Archive the old lockfile (use the date it was blessed, e.g. `2026-Q2`):

```bash
cp lockfiles/stable/uv.lock lockfiles/archive/uv.lock-2026-Q2
```

Update `lockfiles/stable/manifest.toml`:

- `blessed_date` → today's date
- `[versions] "eye-ai"` → new tag
- `[versions] "deriva-ml"` → resolved version from Step 3
- `[sources] "deriva-ml"` → resolved commit SHA from Step 3
- `[notes] summary` → brief description of what changed

Update `docs/releases/compatibility-matrix.md`:

- Add a new row at the top of the table with the new stack tag, versions, today's date, and status `Stable`.
- Change the previous row's status to `Superseded`.

Update `templates/researcher-repo/cookiecutter.json`:

- `eye_ai_version` → new tag

Update `templates/researcher-repo/{{cookiecutter.project_name}}/pyproject.toml`:

- The `eye-ai` source tag in `[tool.uv.sources]`.

### Step 5 — Commit and publish a GitHub Release

```bash
git add lockfiles/stable/ lockfiles/archive/ docs/releases/compatibility-matrix.md \
        templates/researcher-repo/
git commit -m "chore: bless eye-ai <NEW_TAG> as stable stack"
git push
```

Then on GitHub: **Releases → Draft a new release**

- Tag: `stack-<NEW_TAG>` (e.g. `stack-v1.6.0`)
- Title: `Blessed stack: eye-ai <NEW_TAG>`
- Body: copy the `[notes]` from `manifest.toml` plus any breaking changes

Publishing the release triggers `notify-release.yml`, which posts to Slack automatically.

### Step 6 — Notify researcher repos (optional but recommended)

If your research repos use Renovate, they will receive automatic PRs once the lockfile is updated.
If not, post in the team channel pointing to the new release and the `uv sync --frozen` command.

---

## Procedure: updating documentation

No automation here — docs are updated manually whenever onboarding steps change, new tools are added, or team practices evolve.

Common triggers:

- **MCP stack update** (`docs/onboarding/mcp-setup.md`) — when `deriva-mcp-core`, `deriva-ml-mcp-plugin`, or `eye-ai-deriva-mcp-plugin` changes its install command or adds a new configuration step.
- **New researcher role or workflow** (`docs/onboarding/new-researcher.md`, `docs/guides/`) — when a new subproject type or data source is introduced.
- **Catalog schema process change** (`docs/guides/catalog-migration.md`) — when the migration naming convention or header format changes.

Edit the relevant file directly on GitHub or locally and push. No CI runs on doc changes.

---

## What to do when CI is broken

**Integration test fails week-over-week:**

1. Check the Actions log for which test failed.
2. If it's a test infrastructure issue (e.g. `setup-uv` version, GitHub runner change), fix the workflow file.
3. If it's an upstream package breakage, open an issue in the upstream repo and leave a comment on the failing PR summarizing the error.
4. Do not merge the `lockfile/testing` PR until tests are green.

**`notify-release.yml` fails (Slack post not sent):**

- Most likely cause: `SLACK_WEBHOOK_URL` secret is missing or expired.
- Go to: **org Settings → Secrets and variables → Actions → SLACK_WEBHOOK_URL**
- Update the webhook URL from your Slack workspace app settings.

---

## One-time setup tasks (if starting from scratch)

These were done during initial setup but are listed here for handover purposes.

| Task | Where | Status |
|---|---|---|
| Create `SLACK_WEBHOOK_URL` org secret | GitHub org Settings → Secrets → Actions | Must be done manually |
| Enable Actions on the repo | Repo Settings → Actions → General | Should already be on |
| Protect `main` branch (require PR + CI) | Repo Settings → Branches | Recommended but optional |
| Restrict `lockfiles/stable/` write to infra team | Via CODEOWNERS file | Not yet configured |

To add a `CODEOWNERS` rule for the lockfiles:

```
# Only the infra team can merge changes to the blessed lockfile
lockfiles/stable/ @eye-ai-usc/eyeai-infra
```

Create `.github/CODEOWNERS` with that content when the `eyeai-infra` team exists in the org.

---

## Key files reference

| File | Purpose | Update frequency |
|---|---|---|
| `lockfiles/stable/uv.lock` | Blessed dependency lockfile | Per stack release (~quarterly) |
| `lockfiles/stable/manifest.toml` | Versions, commit SHAs, blessing metadata | Per stack release |
| `lockfiles/archive/` | Historical lockfiles by quarter | Per stack release |
| `docs/releases/compatibility-matrix.md` | Human-readable version history | Per stack release |
| `templates/researcher-repo/cookiecutter.json` | Default versions for new repos | Per stack release |
| `docs/onboarding/mcp-setup.md` | MCP install recipe | When MCP stack changes |
| `.github/workflows/integration-test.yml` | Weekly upstream freshness check | Rarely |
| `.github/workflows/notify-release.yml` | Slack notification on release | Rarely |
| `docs/design/architecture.md` | Design rationale (why things are structured this way) | Rarely |
| `docs/design/implementation-spec.md` | Step-by-step implementation record | Rarely |
