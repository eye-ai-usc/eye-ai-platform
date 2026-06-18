# EyeAI GitHub Org Restructuring — Claude Code Implementation Spec

> **Instructions for Claude Code:** This document is a complete, self-contained implementation specification. Execute each task in the order listed. For each task, check the actual state of the EyeAI GitHub org first, then apply only the changes needed. Do not make changes outside the scope of each task. Flag anything ambiguous before proceeding.
>
> GitHub org: `eye-ai-usc`
> Upstream org (read-only reference): `informatics-isi-edu` (Deriva)

---

## Step 0 — Repo Audit (do this first, before any changes)

Query the EyeAI GitHub org and produce a table with the following columns for every repo:

| Repo Name | Last Commit | Primary Language | Has pyproject.toml? | deriva-ml version pinned | eyeai version pinned | Apparent purpose (1 line) |

Then answer each of these questions explicitly before proceeding:

1. Which repos contain catalog migration or schema change scripts outside the data curation repo?
2. Which repos have overlapping ETL or data export scripts?
3. Which researcher repos are working on the same research question (candidates for subproject consolidation)?
4. Is there a template repo? What is its current state and how out of date is it?
5. Where does the MCP agent live — EyeAI org or Deriva org?
6. Are there any repos that don't fit the categories: platform / catalog / research satellite?

Do not proceed past Step 0 until the audit table and answers are complete.

---

## Step 1 — Create `eyeai-platform`

### 1.1 Create the repo
- New public repo in `eye-ai-usc` org named `eyeai-platform`
- Description: "Front door for the EyeAI project — docs, onboarding, templates, and blessed dependency lockfiles"
- Initialize with README

### 1.2 Create directory skeleton
```
eyeai-platform/
├── README.md
├── ECOSYSTEM.md
├── docs/
│   ├── onboarding/
│   │   ├── quickstart.md
│   │   ├── mcp-setup.md
│   │   ├── catalog-overview.md
│   │   └── new-researcher.md
│   ├── guides/
│   │   ├── etl-workflow.md
│   │   ├── experiment-tracing.md
│   │   └── catalog-migration.md
│   └── releases/
│       ├── CHANGELOG.md
│       └── compatibility-matrix.md
├── lockfiles/
│   ├── stable/
│   │   ├── uv.lock
│   │   └── manifest.toml
│   ├── testing/
│   │   └── .gitkeep
│   └── archive/
│       └── .gitkeep
├── templates/
│   └── researcher-repo/
│       ├── cookiecutter.json
│       └── {{project_name}}/
│           ├── pyproject.toml
│           ├── uv.lock
│           ├── README.md
│           ├── .github/
│           │   └── renovate.json
│           ├── data/
│           │   ├── export_config.yaml
│           │   └── prepare.py
│           ├── features/
│           │   └── .gitkeep
│           ├── models/
│           │   └── .gitkeep
│           ├── experiments/
│           │   └── .gitkeep
│           └── catalog_patches/
│               └── README.md
└── .github/
    ├── ISSUE_TEMPLATE/
    │   └── feature-registration.md
    └── workflows/
        ├── integration-test.yml
        └── notify-release.yml
```

### 1.3 Populate README.md
Content: one paragraph describing the EyeAI project, followed by a table listing every repo in the org with its purpose and a link. Use the audit results from Step 0 to fill in the table.

### 1.4 Populate ECOSYSTEM.md
For each repo in the org, write:
- Repo name and link
- Owner/maintainer
- Purpose (2–3 sentences)
- Status (active / maintenance / archived)
- Relationship to other repos

### 1.5 Populate docs/onboarding/quickstart.md
Content must cover, in order:
1. Prerequisites (Python version, uv installation)
2. Installing the blessed stack: `uv sync --frozen` using the stable lockfile from this repo
3. Installing and configuring the MCP agent (point to mcp-setup.md for details)
4. Cloning or creating a research repo from the template
5. Running a first experiment end-to-end

### 1.6 Populate docs/onboarding/mcp-setup.md
Content: full instructions for installing and configuring the EyeAI MCP stack (`deriva-mcp-core` + `deriva-ml-mcp-plugin` + `eye-ai-deriva-mcp-plugin`) and the Claude Code skills plugins. See Step 1.10 for the detailed content spec. Pull installation commands from the upstream READMEs in `informatics-isi-edu`.

### 1.7 Populate docs/releases/compatibility-matrix.md
Create the initial table with the current known-good stack versions (from audit results):

| Stack Tag | eye-ai | deriva-ml | Python | Status | Date Blessed | Notes |
|---|---|---|---|---|---|---|
| `stable` | v1.5.3 | v1.17.10 | 3.12 | ✅ Stable | 2026-06-16 | Initial blessed stack — git tags, sourced from informatics-isi-edu/deriva-ml and eye-ai-usc/eye-ai-ml |

> **MCP stack** (`deriva-mcp-core`, `deriva-ml-mcp-plugin`, `eye-ai-deriva-mcp-plugin`) is
> installed separately via `uv tool install` and is not version-pinned here. See `docs/onboarding/mcp-setup.md`.

### 1.8 Populate lockfiles/stable/manifest.toml
```toml
[stack]
blessed_date = "2026-06-16"
blessed_by = "eyeai-infra"
python = "3.12"

[versions]
"deriva-ml" = "v1.17.10"
"eye-ai" = "v1.5.3"

[sources]
"deriva-ml" = "git+https://github.com/informatics-isi-edu/deriva-ml.git@v1.17.10"
"eye-ai" = "git+https://github.com/eye-ai-usc/eye-ai-ml.git@v1.5.3"

[notes]
summary = "Initial blessed stack. Baseline from existing active researcher environments."
breaking_changes = "None"
migration_required = false

# MCP stack (deriva-mcp-core, deriva-ml-mcp-plugin, eye-ai-deriva-mcp-plugin) is
# installed separately via 'uv tool install' and is not pinned here.
# See docs/onboarding/mcp-setup.md for the current installation recipe.
```

### 1.9 Generate lockfiles/stable/uv.lock
**This is a manual local step.** Run the following in a terminal, then paste the output
back so it can be committed to the repo:

```bash
cd /tmp && uv init --python 3.12 eyeai-stable && cd eyeai-stable && \
uv add \
  "eye-ai @ git+https://github.com/eye-ai-usc/eye-ai-ml.git@v1.5.3" \
  "deriva-ml @ git+https://github.com/informatics-isi-edu/deriva-ml.git@v1.17.10" && \
cat uv.lock
```

The MCP tool stack is NOT included — it is installed separately via `uv tool install`
and does not belong in the research environment lockfile.

### 1.10 Populate docs/onboarding/mcp-setup.md
Full instructions for installing and configuring the EyeAI MCP agent stack.
The MCP stack consists of three components installed into a single isolated `uv tool` venv:
- `deriva-mcp-core` (`informatics-isi-edu/deriva-mcp-core`) — base MCP server
- `deriva-ml-mcp-plugin` (`informatics-isi-edu/deriva-ml-mcp-plugin`) — DerivaML ML tools
- `eye-ai-deriva-mcp-plugin` (`informatics-isi-edu/eye-ai-deriva-mcp-plugin`) — Eye-AI RAG plugin

The Claude Code skills plugins are installed separately via the `deriva-plugins` marketplace.
Pull exact installation commands from the README files of each upstream repo.

Key steps to cover:
1. Install the MCP tool stack (single `uv tool install` command with `--with` for each plugin)
2. Authenticate: `deriva-globus-auth-utils login --host www.eye-ai.org`
3. Configure Claude Code stdio mode: `claude mcp add -t stdio deriva -- deriva-mcp-core --transport stdio`
4. Enable mutations for ML work: create `~/deriva-mcp.env` with `DERIVA_MCP_DISABLE_MUTATING_TOOLS=false` and `DERIVA_MCP_RAG_ENABLED=true`
5. Install Claude Code skills: `/plugin marketplace add informatics-isi-edu/deriva-plugins`, then `/plugin install deriva` and `/plugin install deriva-ml`

> Note: MCP setup instructions may be extended as the upstream stack evolves.
> Always check the upstream READMEs for the most current recipes.

### 1.11 Create .github/ISSUE_TEMPLATE/feature-registration.md
```markdown
---
name: Feature Registration Request
about: Request that a researcher-computed feature be registered as a catalog column
title: "Register feature: [FEATURE NAME]"
labels: catalog-registration
assignees: ''
---

**Feature name:**

**Target catalog table:**

**Compute script location:** [link to file in research repo]

**Ingest script location:** [link to file in research repo, if separate]

**Description of what this feature represents:**

**How values are computed (brief):**

**Are values already computed and stable?** [ ] Yes

**Subproject:**

**Requesting researcher:**
```

### 1.12 Create .github/workflows/integration-test.yml
```yaml
name: Integration Test — Latest Stack

on:
  schedule:
    - cron: '0 8 * * 1'
  workflow_dispatch:

jobs:
  test-latest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - name: Install with latest upstream
        run: |
          uv sync \
            --upgrade-package "eye-ai" \
            --upgrade-package deriva-ml
      - name: Run smoke tests
        run: uv run pytest tests/integration/ -v
      - name: Open PR with updated testing lockfile on success
        if: success()
        uses: peter-evans/create-pull-request@v6
        with:
          title: "chore: update testing lockfile — $(date +%Y-%m-%d)"
          branch: "lockfile/testing-$(date +%Y%m%d)"
          commit-message: "Update testing/uv.lock with latest upstream"
          add-paths: lockfiles/testing/uv.lock
```

### 1.13 Create .github/workflows/notify-release.yml
```yaml
name: Notify on Blessed Release

on:
  release:
    types: [published]

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Post to Slack
        # TODO: add SLACK_WEBHOOK_URL secret in org Settings → Secrets → Actions
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "New EyeAI stack blessed: ${{ github.event.release.tag_name }}\nChangelog: ${{ github.event.release.html_url }}\nTo update: git pull && uv sync --frozen"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### 1.14 Populate templates/researcher-repo/cookiecutter.json
```json
{
  "project_name": "eyeai-research-my-subproject",
  "researcher_name": "your_name",
  "subproject_description": "One sentence describing the research question",
  "eye_ai_version": "v1.5.3",
  "deriva_ml_version": "v1.17.10",
  "python_version": "3.12"
}
```

### 1.15 Populate templates/researcher-repo/{{project_name}}/pyproject.toml
```toml
[project]
name = "{{ project_name }}"
dynamic = ["version"]
description = "{{ subproject_description }}"
requires-python = ">=3.12"
dependencies = [
    "eye-ai",
    "deriva-ml",
]

[tool.uv]
python-preference = "only-managed"
default-groups = ["dev", "jupyter"]
package = true

[tool.uv.sources]
eye-ai = { git = "https://github.com/eye-ai-usc/eye-ai-ml.git", tag = "{{ eye_ai_version }}" }
deriva-ml = { git = "https://github.com/informatics-isi-edu/deriva-ml.git", tag = "{{ deriva_ml_version }}" }

[dependency-groups]
dev = ["pytest", "ruff", "ipython"]
jupyter = ["ipykernel", "jupyter"]
```

### 1.16 Populate templates/researcher-repo/{{project_name}}/.github/renovate.json
```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:base"],
  "packageRules": [
    {
      "matchPackageNames": ["eye-ai", "deriva-ml"],
      "groupName": "EyeAI core stack",
      "prTitle": "chore: update EyeAI core stack",
      "prBody": "Check the [compatibility matrix](https://github.com/eye-ai-usc/eyeai-platform/blob/main/docs/releases/compatibility-matrix.md) before merging.",
      "schedule": ["after 9am on monday"]
    }
  ]
}
```

### 1.17 Populate templates/researcher-repo/{{project_name}}/catalog_patches/README.md
```markdown
# Catalog Patches

If your work requires a new column or table in the EyeAI Deriva catalog:

1. Do **not** modify the catalog directly from this repo.
2. When your feature computation is stable, open a **Feature Registration Request** issue in:
   https://github.com/eye-ai-usc/data-curation/issues/new?template=feature-registration.md
3. A data manager will handle the schema migration and contact you if more information is needed.
4. Your compute and ingest scripts stay here permanently — do not move them.
```

---

## Step 2 — Restructure `eyeai-catalog`

### 2.1 Audit current state
- List all existing directories and files
- Identify: does a `migrations/` directory already exist?
- Identify: where are ingestion scripts currently organized?

### 2.2 Create migrations/ directory structure if not present
```
eyeai-catalog/
├── migrations/
│   └── README.md
├── schema/
│   └── current/
│       ├── tables/
│       └── vocabularies/
├── ingestion/
│   ├── la-county/
│   ├── usc-keck/
│   └── open-source/
└── tests/
    └── validate_migrations.py
```

### 2.3 Populate migrations/README.md
Content must include:
- Two migration types: data management migrations (no external pointer) and feature registration migrations (with pointer to research repo)
- Naming convention: `YYYYMMDD_HHMMSS_{author}_{description}.py`
- Required header block template (see below)
- Rule: migrations are for stable, production-ready changes only — not exploratory work
- How to run a migration against the catalog

**Migration header template:**
```python
"""
Migration: {short_name}
Type: {data_management | feature_registration}
Author: {github_handle}
Date: {YYYY-MM-DD}
Catalog table: {EyeAI.TableName}
Description: {What this migration does}
Source computation: {URL to compute script in research repo, or N/A}
Reversible: {yes | no}
"""
```

### 2.4 Create .github/ISSUE_TEMPLATE/feature-registration.md
Same content as the template created in Step 1.10. This is the issue template researchers use to request catalog registration.

### 2.5 Register legacy eye-ai-exec schema changes (compact bulk approach)
`eye-ai-exec/notebooks/schema_changes/` contains 15 historical schema-change notebooks
(last modified 2025-09, repo is stale and will not be modified further).

Rather than copying 15 notebooks, create ONE bulk retroactive registration entry:

```
migrations/
└── 20240101_000000_legacy_eyeai-exec_schema-changes/
    ├── migration.py
    └── README.md
```

**`migration.py`** — header only, no executable code:
```python
"""
Migration: legacy_eyeai-exec_schema-changes
Type: feature_registration
Author: legacy (pre-migration)
Date: 2024-01-01
Catalog table: multiple (see README.md)
Description: Retroactive registration of historical catalog schema changes
             made via notebooks in eye-ai-exec/notebooks/schema_changes/.
             These changes were made before the migrations/ convention was established.
Source computation: https://github.com/eye-ai-usc/eye-ai-exec/tree/main/notebooks/schema_changes/
Reversible: unknown (historical)
"""
# This migration is an archival record only. No code to execute.
# All schema changes were applied directly to the catalog before this system existed.
```

**`README.md`** — list all 15 notebooks as historical record:
```markdown
# Legacy Schema Changes — eye-ai-exec

These schema changes were made before the migrations/ convention was established.
The canonical source is the eye-ai-exec repo (archived/stale as of 2025-09).

Source: https://github.com/eye-ai-usc/eye-ai-exec/tree/main/notebooks/schema_changes/

## Notebooks registered here

- add_filetable.ipynb
- asset_table_reorg.ipynb
- change_diag_image_annot.ipynb
- change_image_annotation.ipynb
- check_lac_clinic.ipynb
- compute_age.ipynb
- cv_table_change.ipynb
- fix_diag_exec.ipynb
- increase_version_number.ipynb
- observation_datasets.ipynb
- setup_feature_angle_laterality.ipynb
- test_eye-ai_changes.ipynb
- test_schema_separation.ipynb
- update_annotation.ipynb

Also in eye-ai-exec/notebooks/feature/:
- create_chart_label.ipynb
- create_condition_label_feature.ipynb
```

Do not delete the originals from eye-ai-exec.

### 2.6 Add tests/validate_migrations.py
A CI script that:
- Checks every file in `migrations/` has a valid header block
- Checks naming convention is followed
- Does not execute migrations (that is a manual step)

### 2.7 Add GitHub Actions CI for migrations/
```yaml
# .github/workflows/validate-migrations.yml
name: Validate Migrations
on:
  pull_request:
    paths:
      - 'migrations/**'
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv run python tests/validate_migrations.py
```

---

## Step 3 — Create Research Satellite Repos

> ⚠️ **DEFERRED** — Subproject satellite repo consolidation is not in scope for the initial
> restructuring. Execute when individual subprojects reach a natural pause point and their
> owners confirm they're ready to consolidate. The step text below is preserved for future use.

### 3.1 Define subproject list
Using audit results from Step 0, propose a mapping of existing researcher repos to subprojects. Present this mapping and wait for confirmation before creating any repos.

Expected format:
| Subproject repo name | Existing repos to consolidate | Research question |
|---|---|---|
| eyeai-research-{name} | repo-a, repo-b | ... |

### 3.2 For each confirmed subproject: create repo
- New repo in `eye-ai-usc` org: `eyeai-research-{subproject}`
- Initialize from the Cookiecutter template created in Step 1.13
- Description: the research question in one sentence

### 3.3 For each subproject repo: migrate researcher code
For each existing researcher repo being consolidated:
- Create a subdirectory `features/{researcher_name}/`, `models/{researcher_name}/`, `experiments/{researcher_name}/`
- Use `git subtree` to migrate code with history preserved where possible; otherwise copy with a commit message attributing the source repo and original author
- Do NOT squash history

### 3.4 For each retired researcher repo: add archive notice
Add to the top of the existing README.md:
```markdown
> ⚠️ **This repo has been archived.** Active development continues in
> [eyeai-research-{subproject}](https://github.com/eye-ai-usc/eyeai-research-{subproject}).
> This repo is preserved for historical reference.
```
Then archive the repo (Settings → Archive repository).

---

## Step 4 — Deprecate Old Template Repo

### 4.1 Add banner to old template repo README
```markdown
> ⚠️ **This template repo is deprecated.** The new template is maintained in
> [eyeai-platform](https://github.com/eye-ai-usc/eyeai-platform/tree/main/templates/researcher-repo).
> To start a new research repo: `uvx cookiecutter gh:eye-ai-usc/eyeai-platform --directory templates/researcher-repo`
```

### 4.2 Archive the old template repo

---

## Step 5 — Verification Checklist

After all steps are complete, verify:

- [ ] `eyeai-platform` exists in `eye-ai-usc` org and README lists all repos
- [ ] `docs/onboarding/quickstart.md` covers install → first experiment end-to-end
- [ ] `docs/onboarding/mcp-setup.md` covers full MCP + skills install
- [ ] `lockfiles/stable/manifest.toml` has eye-ai=v1.5.3 and deriva-ml=v1.17.10
- [ ] `lockfiles/stable/uv.lock` exists (generated locally and committed)
- [ ] `compatibility-matrix.md` has at least one `stable` row
- [ ] Integration test GitHub Action is valid YAML (can be triggered manually via workflow_dispatch)
- [ ] `data-curation/migrations/` exists with README and naming convention documented
- [ ] Bulk legacy migration entry for eye-ai-exec schema_changes exists
- [ ] Feature registration issue template exists in both `eyeai-platform` and `data-curation`
- [ ] `data-curation` CI validates migration headers on PR
- [ ] `eye-ai-model-template` has deprecation banner pointing to eyeai-platform
- [ ] `ECOSYSTEM.md` in `eyeai-platform` lists every repo with current status
- [ ] (Step 3 DEFERRED) Subproject satellite repos — execute per-subproject at natural pause points
