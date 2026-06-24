# EyeAI Platform

EyeAI is a clinical ML research platform for automated glaucoma detection from ophthalmic
imaging data. The platform combines ophthalmology domain expertise, ML engineering, and
data management over a shared [Deriva](https://deriva.isi.edu) catalog hosted at
[www.eye-ai.org](https://www.eye-ai.org).

This site is the front door for researchers, clinical collaborators, and contributors.
It consolidates onboarding documentation, dependency governance, and research tooling
for the [eye-ai-usc](https://github.com/eye-ai-usc) GitHub organization.

---

## Latest Release

[![Latest stack release](https://img.shields.io/github/v/release/eye-ai-usc/eye-ai-platform?label=latest%20stack&color=indigo)](https://github.com/eye-ai-usc/eye-ai-platform/releases/latest)

See the full [release list](https://github.com/eye-ai-usc/eye-ai-platform/releases) and
[compatibility matrix](releases/compatibility-matrix.md) for version history.

---

## Getting Started

| I want to… | Go to |
|---|---|
| Set up my environment for the first time | [Quickstart](onboarding/quickstart.md) |
| Update packages, MCP, or skills | [Update Your Environment](onboarding/update-env.md) |
| Set up the MCP agent | [MCP Setup](onboarding/mcp-setup.md) |
| Start a new research repo | [Quickstart → Option B](onboarding/quickstart.md#option-b-start-a-new-research-repo-from-the-template) |
| Understand the Deriva catalog | [Catalog Overview](onboarding/catalog-overview.md) |
| Know what I should work on as a new researcher | [New Researcher Guide](onboarding/new-researcher.md) |
| Request catalog changes | [Feature Registration Request](https://github.com/eye-ai-usc/data-curation/issues/new?template=feature-registration.md) |

---

## Software Stack

```
Deriva                       — data catalog platform and asset management
  └── Deriva-ML              — ML experiment tracing layer
      └── eye-ai (eye-ai-ml) — domain library: ETL, data export, AI-ready formatting
          └── MCP Agent      — LLM agent for catalog interpretation and reproducible experiments
                               (deriva-mcp-core + deriva-ml-mcp-plugin + eye-ai-deriva-mcp-plugin)
```

The current blessed stack is pinned in [`lockfiles/stable/`](https://github.com/eye-ai-usc/eye-ai-platform/tree/main/lockfiles/stable).
Use `uv sync --frozen` in any research repo to install the exact pinned versions.

---

## Repository Index

| Repository | Layer | Status | Purpose |
|---|---|---|---|
| [eye-ai-platform](https://github.com/eye-ai-usc/eye-ai-platform) | Platform | ✅ Active | This repo — docs, templates, lockfiles |
| [eye-ai-ml](https://github.com/eye-ai-usc/eye-ai-ml) | Library | ✅ Active | Core `eye-ai` Python library |
| [data-curation](https://github.com/eye-ai-usc/data-curation) | Catalog | ✅ Active | Data ingestion and catalog migrations |
| [eye-ai-vgg19](https://github.com/eye-ai-usc/eye-ai-vgg19) | Research | ✅ Active | VGG-19 glaucoma classification |
| [eye-ai-multimodal-kim](https://github.com/eye-ai-usc/eye-ai-multimodal-kim) | Research | ✅ Active | Multimodal detection — Dr. Kim's reference standard |
| [eye-ai-multimodal](https://github.com/eye-ai-usc/eye-ai-multimodal) | Research | ✅ Active | RETFound multimodal on AI-READI data |
| [retfound-aireadi](https://github.com/eye-ai-usc/retfound-aireadi) | Research | ✅ Active | RETFound on AI-READI retinal imaging |
| [eye-ai-retfound](https://github.com/eye-ai-usc/eye-ai-retfound) | Research | ✅ Active | RETFound model implementation |
| [retfound-severity](https://github.com/eye-ai-usc/retfound-severity) | Research | ✅ Active | RETFound severity grading |
| [kim-glaucoma-computable-definitions](https://github.com/eye-ai-usc/kim-glaucoma-computable-definitions) | Research | ✅ Active | Computable glaucoma definitions |
| [eye-ai-aireadi](https://github.com/eye-ai-usc/eye-ai-aireadi) | Research | 🔶 Maintenance | AI-READI experiments (earlier iteration) |
| [eye-ai-privacyML](https://github.com/eye-ai-usc/eye-ai-privacyML) | Research | 🔶 Early | Privacy-preserving ML experiments |
| [eye-ai-privacy](https://github.com/eye-ai-usc/eye-ai-privacy) | Research | ⬜ Placeholder | Empty placeholder |
| [eye-ai-compute-platform](https://github.com/eye-ai-usc/eye-ai-compute-platform) | Infrastructure | 🔶 Maintenance | Containerized JupyterHub for GPU compute |
| [eye-ai-rag-docs](https://github.com/eye-ai-usc/eye-ai-rag-docs) | MCP Content | ✅ Active | RAG content for the MCP plugin |
| [eye-ai-model-template](https://github.com/eye-ai-usc/eye-ai-model-template) | Template | ⚠️ Deprecated | Use [templates/researcher-repo/](https://github.com/eye-ai-usc/eye-ai-platform/tree/main/templates/researcher-repo) instead |
| [eye-ai-exec](https://github.com/eye-ai-usc/eye-ai-exec) | Legacy | 🗄️ Stale | Old execution catch-all |
| [eye-ai](https://github.com/eye-ai-usc/eye-ai) | Legacy | 🗄️ Legacy | Pre-ML era webapp |
| [eye-ai-tools](https://github.com/eye-ai-usc/eye-ai-tools) | Legacy | 🗄️ Stale | Misc utilities |
