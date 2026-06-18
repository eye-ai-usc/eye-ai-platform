# Organizing a Sustainable GitHub Infrastructure for an Interdisciplinary Clinical ML Project: The EyeAI Case

---

## Abstract

Long-running interdisciplinary machine learning projects in clinical research face a class of software infrastructure problems that are distinct from both pure research projects and pure software engineering projects. This document describes the organizational design decisions made for the EyeAI GitHub organization — a multi-year glaucoma detection project involving ophthalmologists, ML engineers, and data managers. We identify eight recurring failure modes in the current structure, propose a repository architecture that addresses each, and describe the role-specific workflows and automation mechanisms that make the system sustainable for a team with heterogeneous technical backgrounds. The design prioritizes low researcher overhead and automated provenance tracking over process enforcement.

---

## 1. Project Background

### 1.1 The EyeAI Project

EyeAI is a clinical ML research project with the primary aim of automated glaucoma detection from ophthalmic imaging data. The project is representative of a broader class of academic clinical ML efforts: it combines domain expertise from practicing clinicians, ML research from academic engineers, and data management from dedicated data staff, all operating against a shared data infrastructure that evolves continuously over the life of the project.

Data is sourced from multiple clinical and open-source origins, including LA County clinic networks, USC Keck Medical School, and publicly available ophthalmic imaging benchmarks. All data is managed through the **Deriva Platform**, a data catalog and asset management system developed by a separate research group that provides schema-defined, structured access to research datasets. The EyeAI Deriva site is the authoritative data store for all project assets.

### 1.2 Team Composition and Roles

The team spans three functional roles with substantially different technical backgrounds and working styles:

**Ophthalmologists and clinical collaborators** contribute clinical knowledge, data access, and medical annotation. They can write basic Python scripts but are not software engineers. They need minimal-friction tooling and cannot be expected to follow complex multi-repo workflows.

**ML engineers (CS professors and PhD students)** are responsible for model development, experiment design, feature engineering, and research infrastructure. They work at varying levels of software engineering rigor — CS professors may write production-quality code while clinical PhD students may write exploratory notebooks.

**Data managers** are responsible for data ingestion from clinical sources, catalog integrity, and data quality. Their work is often entirely orthogonal to any specific modeling task — they may need to add a new data source or restructure a table with no associated model development.

### 1.3 The Software Stack

The project depends on a layered software stack developed by the professor who leads the Deriva project:

```
Deriva              — data catalog platform and asset management
  └── Deriva-ML     — ML experiment tracing layer; links model runs to catalog state
      └── EyeAI     — domain library: ETL utilities, data export, AI-ready formatting
          └── MCP Agent (mcp-eye-ai / deriva-mcp)
                    — LLM agent layer for interpreting catalog data
                      and constructing reproducible experiments
```

Each layer depends on the one below it. The stack is developed incrementally and released every several months without a fully stabilized release process. This creates a recurring pattern: a new release is announced, researchers update at different times, bugs surface independently, and debugging is duplicated across the team.

### 1.4 The Data Catalog as a Moving Target

Unlike projects that train against static benchmarks, EyeAI's data catalog evolves continuously. New imaging data arrives from clinical partners. Researchers compute new features — cup-to-disc ratios, vessel caliber measurements, image quality scores — and add them as columns to existing catalog tables. Human annotations are ingested as they become available. Schema changes happen in response to new clinical requirements or modeling needs.

This dynamic catalog creates a provenance challenge: for any experiment, it must be possible to reconstruct exactly what data and features were available at the time the experiment was run. Deriva-ML addresses part of this by tracing experiment runs back to catalog state. But the catalog modification scripts themselves — the scripts that define when and how the catalog changed — also need a traceable home.

---

## 2. Problems with the Current Structure

The current repository structure has grown organically since the project's early stages. Eight specific failure modes have emerged that motivate the reorganization.

### P1 — Per-researcher repos cause fragmentation

Each researcher maintains their own GitHub repository. Researchers working on the same research question cannot easily share data export configurations or reference each other's feature engineering code. Related work is spread across repositories with no shared structure.

### P2 — No subproject-level organization

There is no single location containing all scripts related to a given research question. Data preparation, feature engineering, model code, and experiment configurations are either spread across multiple repos or mixed without clear separation. The full scope of any subproject is invisible from a single vantage point.

### P3 — Upstream updates are painful and uncoordinated

When any component of the Deriva/EyeAI stack is updated, every researcher must manually update their environment. There is no automated mechanism to validate that a new version works against EyeAI's actual workflows, notify the team, or propagate the update in a coordinated way. Researchers unknowingly run different versions, causing subtle reproducibility failures.

### P4 — The template repo requires constant manual maintenance

A model-template repository helps new researchers get started. However, every stack update requires a manual update to the template. The template consistently lags the active stack, meaning new members start with outdated dependencies.

### P5 — Onboarding documentation is scattered

Installation instructions for Deriva-ML, EyeAI, and the MCP agent are distributed across the README files of multiple individual repos. There is no canonical document a new collaborator can follow from zero to running their first experiment.

### P6 — Release announcements rely entirely on Slack

New version announcements go out via a Slack channel. Not all collaborators — particularly clinical partners and part-time contributors — monitor Slack consistently. Version drift goes unnoticed until something breaks.

### P7 — Upstream releases are incremental and often unstable

The upstream developer cannot always provide a fully tested release. Each release is followed by a period of debugging and patching, the cost of which is currently distributed across the team. Without a shared integration testing step, each researcher independently discovers the same bugs.

### P8 — Catalog modification scripts have no centralized home

Catalog schema changes — adding feature columns, creating new tables, restructuring existing tables — currently live wherever the researcher who made the change happened to be working. There is no audit trail. A data manager who needs to make a catalog change with no associated modeling work has no clear repository for their script.

---

## 3. Design Principles

The architecture is governed by five principles chosen specifically for a research team context, where over-engineered processes will be ignored.

**Structure over rules.** The directory layout and repository separation should make the right thing easy without requiring policy enforcement. If following the correct workflow requires significantly more effort than the incorrect one, the correct workflow will not be followed.

**Asymmetric overhead by role.** Friction must be minimized for ML engineers and clinical collaborators, who cannot be expected to maintain complex multi-repo workflows. Data managers, whose job is catalog integrity, absorb the coordination overhead of formal catalog registration. This is an explicit and intentional asymmetry, not a failure of the design.

**One source of truth per concern.** Onboarding documentation lives in one place. Catalog migrations live in one place. The blessed dependency stack lives in one place. Duplication creates drift, and drift in a research context is invisible until it causes a failed experiment.

**Automation over announcements.** Dependency updates should propagate via pull requests and CI, not Slack messages. A researcher who ignores Slack still gets a GitHub notification.

**Research granularity, not person granularity.** Repositories are organized by research question, not by individual. The scientifically meaningful unit of organization is the subproject, and this is reflected in the repository structure.

---

## 4. Repository Architecture

The target architecture consists of three layers: a platform layer, a catalog layer, and a research layer.

### 4.1 The Platform Layer: `eyeai-platform`

`eyeai-platform` is a new repository that serves as the front door for the entire project. It contains no research code and no catalog migration scripts. Its sole purpose is orientation, onboarding, and dependency governance.

**Onboarding documentation** (`docs/onboarding/`) consolidates all installation and setup instructions that are currently scattered across individual repo READMEs. A new collaborator — regardless of role — is sent a single URL. The quickstart document covers the full path from a fresh machine to a running first experiment, including stack installation, MCP agent configuration, and research repo initialization.

**Blessed lockfile registry** (`lockfiles/`) is the mechanism by which dependency updates are coordinated across the team. The `stable/` directory contains a `uv.lock` file representing the current known-good combination of Deriva-ML, EyeAI, and MCP agent versions, along with a `manifest.toml` that records the versions, the date they were blessed, and notes on any breaking changes. An `archive/` directory preserves historical lockfiles by quarter, functioning as a browsable version history of the stack.

**The Cookiecutter template** (`templates/researcher-repo/`) replaces the standalone template repository. When the template is embedded in `eyeai-platform`, updating it means updating one directory rather than maintaining a separate repository. A new researcher initializes their repo with a single command that pulls the template and the current stable lockfile simultaneously.

**Automation** (`.github/workflows/`) handles two processes. A weekly integration test installs the latest upstream versions of all stack components, runs smoke tests against the EyeAI catalog, and opens a draft PR with an updated testing lockfile if tests pass. A release notification workflow fires when a new blessed stack is published, posting to Slack and triggering Renovate PRs in all satellite repos.

### 4.2 The Catalog Layer: `eyeai-catalog`

`eyeai-catalog` — the existing data curation repository — becomes the single source of truth for all catalog schema changes and data ingestion. This repository directly addresses P8 by giving every catalog modification a permanent, traceable home.

The key structural addition is `migrations/`, a directory of timestamped Python scripts that record every change to the catalog schema. Migrations follow a naming convention (`YYYYMMDD_HHMMSS_{author}_{description}.py`) and a required header block that records the author, date, affected table, description, and — critically — a pointer to any external computation script if the migration registers a researcher-derived feature.

Two classes of migrations are explicitly distinguished. **Data management migrations** are authored directly by data managers and have no external pointer — they represent pure catalog work such as adding a new data source's table or restructuring a vocabulary. **Feature registration migrations** are authored by data managers on behalf of researchers and contain a `Source computation` field pointing to the compute script in the researcher's own repository. This pointer is the provenance link: it records not just that a column exists, but exactly how its values were computed and where that code lives.

Ingestion scripts for each data source (LA County, USC Keck, open-source datasets) are organized under `ingestion/` as subdirectories. This co-location with migrations reflects that ingestion and schema management share the same concern — they both modify the catalog state — and should be owned by the same people.

### 4.3 The Research Layer: `eyeai-research-{subproject}`

One repository per research subproject replaces the current one-repository-per-researcher structure. A subproject is defined by a distinct research question, not by team membership. Researchers working on the same question share a repository and work in named subdirectories.

The internal structure separates data export configuration, feature engineering, model code, and experiment configuration into top-level directories. Within each directory, researcher-named subdirectories minimize the surface area for merge conflicts: researchers rarely touch each other's subdirectories, and the shared `data/` directory is mostly declarative configuration rather than imperative code.

Each subproject repo carries its own `uv.lock` file, initialized from the stable lockfile in `eyeai-platform` at creation time and updated via Renovate PRs when a new blessed stack is published.

---

## 5. Key Workflow: Feature Engineering to Catalog Registration

The feature engineering workflow is the most operationally important workflow in the system because it sits at the intersection of all three roles and all three repository layers. It is also the workflow where the tension between researcher autonomy and catalog provenance is most acute.

### 5.1 The Design Tension

A researcher computing a new feature faces two competing requirements. Their compute script is research code: it iterates rapidly, it depends on their model and pipeline, it may be refactored multiple times before stabilizing, and forcing it into a formal repository during development would add friction that slows research. At the same time, once the feature is stable and ingested into the catalog, there must be a permanent record of how it was computed — a record robust enough to survive the researcher leaving the project or their repository being restructured.

The naive solutions both fail. Keeping the script only in the researcher's repo creates pointer rot and discoverability problems. Copying the script into `eyeai-catalog` creates duplication drift and places research code in a repository owned by data managers.

### 5.2 The Solution: Frozen Snapshots with Explicit Ownership

The solution separates the compute script (which remains in the researcher's repo and may continue to evolve) from a frozen snapshot (which is copied into `eyeai-catalog` at the moment of catalog registration and explicitly marked as an archival record, not a maintained codebase).

The migration directory in `eyeai-catalog` for a feature registration looks like:

```
migrations/
└── 20250312_jsmith_add_cdrnr_feature/
    ├── migration.py                    ← schema change only
    ├── compute_cdrnr.SNAPSHOT.py       ← frozen copy, never edited here
    ├── ingest_cdrnr.SNAPSHOT.py        ← frozen copy, never edited here
    └── README.md                       ← points to canonical source in research repo
```

The `.SNAPSHOT` suffix communicates unambiguously that these files are archival records. Anyone who needs to re-run or modify the computation is directed to the canonical source in the research repo. Anyone auditing the catalog history can reconstruct exactly what was computed and how without following any external links.

### 5.3 Role-Specific Workflows

**Researcher workflow (minimal overhead):**
The researcher develops their compute script entirely within their own research repository, at whatever level of formality suits their working style. When the feature is stable and ready for catalog ingestion, they open a Feature Registration Request issue in `eyeai-catalog` — a GitHub issue template that takes roughly two minutes to fill out. They provide the feature name, the target catalog table, links to their compute and ingest scripts, a brief description, and confirmation that the values are stable. They then return to their research work.

**Data manager workflow (absorbs coordination overhead):**
The data manager picks up the Feature Registration Request issue. They review the linked scripts, write the schema migration (`migration.py`), copy frozen snapshots of the compute and ingest scripts with the `.SNAPSHOT` suffix, and open a PR to `eyeai-catalog/migrations/`. After review and merge, they run the migration against the catalog and notify the researcher. The issue is closed.

This asymmetry is deliberate. Data managers are the appropriate owners of catalog integrity. Requiring researchers to navigate two repositories and follow formal migration conventions would introduce friction that would either slow research or, more likely, result in catalog changes being made informally without any record.

---

## 6. Dependency Management

### 6.1 The Blessed Lockfile Pattern

The `uv` package manager's lockfile format (`uv.lock`) provides deterministic, cross-platform environment specification. The blessed lockfile pattern uses this capability to decouple "upstream releases a new version" from "the team adopts a new version."

The flow is as follows. When a new upstream version is released, a GitHub Action in `eyeai-platform` automatically installs it in a clean environment and runs integration smoke tests. If tests fail, an issue is opened and the team stays on the current blessed stack. If tests pass, the updated lockfile is committed to `lockfiles/testing/` as a draft PR, available for one or two active research repos to validate against real workflows during a soak period of one to two weeks. After the soak period, the PR is promoted to `lockfiles/stable/`, a new GitHub Release is published, and Renovate automatically opens update PRs in all satellite repos.

### 6.2 The Compatibility Matrix

`docs/releases/compatibility-matrix.md` in `eyeai-platform` maintains a human-readable table of known-good version combinations, their blessing dates, and any notes on breaking changes or required migrations. This table serves two purposes: it gives researchers a quick reference for what is known to work, and it provides a historical record that makes it possible to reproduce the environment of any past experiment.

### 6.3 Why This Matters for Research Reproducibility

In a project where experiments are traced back to catalog state via Deriva-ML, environment reproducibility is a first-class concern. A model trained against catalog version N using stack version X may produce different results than the same model trained against the same catalog version using stack version Y. The blessed lockfile archive, combined with the catalog migration audit trail in `eyeai-catalog`, provides the two components needed to fully reconstruct the conditions of any past experiment.

---

## 7. Migration Strategy

The migration from the current structure to the target architecture is phased to avoid disrupting active research.

**Phase 1** establishes `eyeai-platform` and consolidates documentation. No existing repositories are touched. This phase has zero risk and immediately addresses P5 and P6.

**Phase 2** formalizes `eyeai-catalog` by introducing the `migrations/` structure and communicating the new policy for catalog changes. Existing catalog scripts in researcher repos are registered retroactively as migrations with appropriate headers.

**Phase 3** establishes the lockfile infrastructure and automation. The current working stack is documented as the first blessed stack. The integration test workflow is set up, even if initial smoke tests are minimal.

**Phase 4** migrates the template to `eyeai-platform` as a Cookiecutter template and deprecates the standalone template repository.

**Phase 5** consolidates researcher repositories into subproject satellites. This phase is not time-bounded — each consolidation happens when the relevant subproject reaches a natural pause point. Researcher repos are not archived until their owners confirm the migration is complete.

---

## 8. Governance

Governance is intentionally minimal. Research teams abandon processes that require sustained active enforcement.

Merge rights to `eyeai-catalog/migrations/` are restricted to data managers and senior MLEs. This is the one hard access control in the system, and it is justified: catalog migrations are irreversible changes to shared infrastructure that affect all researchers.

Merge rights to `lockfiles/stable/` in `eyeai-platform` are restricted to the infrastructure maintainer, and merges require passing CI. This protects the team from a broken blessed stack.

Research satellite repos have no mandatory review policy. Researchers own their subdirectories and merge their own code. This reflects the reality that imposing code review on exploratory research code creates friction without proportionate benefit.

An integration tester rotation is recommended: one MLE per month takes responsibility for monitoring the weekly integration test results and shepherding any new upstream release through the soak period. This distributes the infrastructure maintenance burden and builds stack knowledge across the team.

---

## 9. Summary

The eight failure modes identified in the current structure map directly to the architectural decisions described above.

| Problem | Solution |
|---|---|
| P1: Per-researcher repo fragmentation | Subproject satellite repos with researcher subdirectories |
| P2: No subproject-level organization | Standardized internal structure per subproject repo |
| P3: Upstream updates uncoordinated | Blessed lockfile pattern with automated integration testing |
| P4: Template repo maintenance burden | Cookiecutter template embedded in eyeai-platform |
| P5: Scattered onboarding docs | Consolidated docs/onboarding/ in eyeai-platform |
| P6: Slack-only release announcements | GitHub Releases + Renovate PRs + automated Slack post |
| P7: Team absorbs upstream instability | Soak period between upstream release and team adoption |
| P8: No home for catalog modifications | eyeai-catalog/migrations/ with formal registration workflow |

The design is not intended to be permanent. As the project grows and the team's practices mature, specific components — the soak period duration, the integration test coverage, the subproject boundaries — should be revisited. The goal is a structure that is sustainable under current team conditions, not one that is optimal in the abstract.
