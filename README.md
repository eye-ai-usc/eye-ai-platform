# eye-ai-platform

Front door for the [EyeAI](https://www.eye-ai.org) project — onboarding documentation,
dependency lockfiles, and the Cookiecutter researcher template.

EyeAI is a clinical ML research project for automated glaucoma detection from ophthalmic
imaging data. The project combines ophthalmology domain expertise, ML engineering, and data
management over a shared [Deriva](https://deriva.isi.edu) catalog.

## Getting Started

- **New researcher?** → [docs/onboarding/quickstart.md](docs/onboarding/quickstart.md)
- **Setting up the MCP agent?** → [docs/onboarding/mcp-setup.md](docs/onboarding/mcp-setup.md)
- **Updating MCP or skills?** → [docs/onboarding/mcp-setup.md#updating-the-mcp-stack](docs/onboarding/mcp-setup.md#updating-the-mcp-stack)
- **Starting a new research repo?** → [templates/researcher-repo/](templates/researcher-repo/)
- **Requesting catalog changes?** → [Open a Feature Registration Request](https://github.com/eye-ai-usc/data-curation/issues/new?template=feature-registration.md)
- **Maintaining this repo?** → [docs/MAINTENANCE.md](docs/MAINTENANCE.md)

## Repository Index

| Repository | Visibility | Layer | Status | Purpose |
|---|---|---|---|---|
| [eye-ai-platform](https://github.com/eye-ai-usc/eye-ai-platform) | Public | Platform | ✅ Active | This repo — front door, docs, templates, lockfiles |
| [eye-ai-ml](https://github.com/eye-ai-usc/eye-ai-ml) | Public | Platform / Library | ✅ Active | Core `eye-ai` Python library (EyeAI layer atop Deriva-ML); latest: `v1.5.3` |
| [data-curation](https://github.com/eye-ai-usc/data-curation) | Private | Catalog | ✅ Active | Data ingestion, schema migrations, and catalog integrity |
| [eye-ai-vgg19](https://github.com/eye-ai-usc/eye-ai-vgg19) | Private | Research | ✅ Active | VGG-19 glaucoma classification with TensorFlow + DerivaML |
| [eye-ai-multimodal-kim](https://github.com/eye-ai-usc/eye-ai-multimodal-kim) | Private | Research | ✅ Active | Multimodal glaucoma detection — Dr. Kim's 3-expert reference standard |
| [eye-ai-multimodal](https://github.com/eye-ai-usc/eye-ai-multimodal) | Private | Research | ✅ Active | RETFound multimodal experiments on AI-READI data |
| [retfound-aireadi](https://github.com/eye-ai-usc/retfound-aireadi) | Private | Research | ✅ Active | RETFound foundation model on AI-READI retinal imaging |
| [eye-ai-retfound](https://github.com/eye-ai-usc/eye-ai-retfound) | Private | Research | ✅ Active | RETFound model implementation |
| [retfound-severity](https://github.com/eye-ai-usc/retfound-severity) | Private | Research | ✅ Active | RETFound severity grading vs glaucoma specialists |
| [eye-ai-aireadi](https://github.com/eye-ai-usc/eye-ai-aireadi) | Private | Research | 🔶 Maintenance | AI-READI dataset experiments (earlier iteration) |
| [kim-glaucoma-computable-definitions](https://github.com/eye-ai-usc/kim-glaucoma-computable-definitions) | Private | Research | ✅ Active | Computable glaucoma definitions using Eye-AI datasets |
| [eye-ai-privacyML](https://github.com/eye-ai-usc/eye-ai-privacyML) | Private | Research | 🔶 Early | Privacy-preserving ML experiments |
| [eye-ai-privacy](https://github.com/eye-ai-usc/eye-ai-privacy) | Private | Research | ⬜ Placeholder | Empty placeholder for privacy ML work |
| [eye-ai-compute-platform](https://github.com/eye-ai-usc/eye-ai-compute-platform) | Public | Infrastructure | 🔶 Maintenance | Containerized JupyterHub for GPU compute |
| [eye-ai-rag-docs](https://github.com/eye-ai-usc/eye-ai-rag-docs) | Public | MCP Content | ✅ Active | RAG content (PDFs + Markdown) for the eye-ai-deriva-mcp-plugin |
| [eye-ai-model-template](https://github.com/eye-ai-usc/eye-ai-model-template) | Public | Template | ⚠️ Deprecated | Old researcher template — use [templates/researcher-repo/](templates/researcher-repo/) instead |
| [eye-ai-exec](https://github.com/eye-ai-usc/eye-ai-exec) | Public | Legacy | 🗄️ Stale | Old execution catch-all; schema changes migrated to data-curation |
| [eye-ai](https://github.com/eye-ai-usc/eye-ai) | Private | Legacy | 🗄️ Legacy | Pre-ML era webapp and clinical interface |
| [eye-ai-tools](https://github.com/eye-ai-usc/eye-ai-tools) | Public | Legacy | 🗄️ Stale | Misc utilities; last active 2024 |

## Software Stack

```
Deriva                       — data catalog platform and asset management
  └── Deriva-ML              — ML experiment tracing layer
      └── eye-ai (eye-ai-ml) — domain library: ETL, data export, AI-ready formatting
          └── MCP Agent      — LLM agent for catalog interpretation and reproducible experiments
                               (deriva-mcp-core + deriva-ml-mcp-plugin + eye-ai-deriva-mcp-plugin)
```

## Dependency Management

The blessed research stack is governed by [`lockfiles/stable/manifest.toml`](lockfiles/stable/manifest.toml).
See [`docs/releases/compatibility-matrix.md`](docs/releases/compatibility-matrix.md) for version history
and [`docs/onboarding/quickstart.md`](docs/onboarding/quickstart.md) for installation instructions.
