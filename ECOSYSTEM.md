# EyeAI Ecosystem

Per-repository details for the `eye-ai-usc` GitHub organization.

---

## Platform Layer

### [eye-ai-platform](https://github.com/eye-ai-usc/eye-ai-platform)
- **Maintainer:** Infrastructure / all senior MLEs
- **Purpose:** Front door for the EyeAI project. Contains onboarding documentation, the stable dependency lockfile registry, the Cookiecutter researcher repo template, and GitHub Actions for integration testing and release notification. No research code, no catalog scripts.
- **Status:** Active
- **Depends on:** Nothing (documentation references all other repos)

### [eye-ai-ml](https://github.com/eye-ai-usc/eye-ai-ml)
- **Maintainer:** Carl Kesselman / senior MLEs
- **Purpose:** Core `eye-ai` Python library. Provides the EyeAI domain class that inherits from Deriva-ML, plus ETL utilities, data export helpers, and AI-ready dataset formatting for the EyeAI Deriva catalog. This is the layer every research repo depends on.
- **Status:** Active — latest release `v1.5.3`
- **Depends on:** `informatics-isi-edu/deriva-ml`
- **Used by:** All research repos

---

## Catalog Layer

### [data-curation](https://github.com/eye-ai-usc/data-curation)
- **Maintainer:** Data managers
- **Purpose:** Single source of truth for all catalog schema changes and data ingestion. Contains timestamped migration scripts, ingestion pipelines for each data source (LA County, USC Keck, open-source), and CI to validate migration headers. Feature registration requests from researchers are handled here.
- **Status:** Active
- **Depends on:** `eye-ai-ml`, `deriva-ml`
- **Relationship:** Downstream research repos open Feature Registration Request issues here when they need new catalog columns.

---

## Research Layer

### [eye-ai-vgg19](https://github.com/eye-ai-usc/eye-ai-vgg19)
- **Maintainer:** Kyle / ISRD
- **Purpose:** VGG-19 convolutional network for glaucoma diagnosis using EyeAI imaging data. Integrates with DerivaML for experiment tracking and TensorFlow/Keras for model training.
- **Status:** Active — most recently pushed repo in the org
- **Depends on:** `eye-ai-ml` (git main), `deriva-ml` (git main)

### [eye-ai-multimodal-kim](https://github.com/eye-ai-usc/eye-ai-multimodal-kim)
- **Maintainer:** Kimberley Yu, Jayanth Kumar Mallapu
- **Purpose:** Multimodal glaucoma vs. glaucoma-suspect analysis using a 3-expert reference standard (Dr. Kim's reference standard). Combines fundus imaging and clinical metadata.
- **Status:** Active
- **Depends on:** `eye-ai-ml` (git@commit 949c686, `>=1.4.0`), `deriva-ml` (git main)

### [eye-ai-multimodal](https://github.com/eye-ai-usc/eye-ai-multimodal)
- **Maintainer:** ISRD
- **Purpose:** RETFound multimodal experiments applied to AI-READI retinal imaging data with DerivaML integration. Sister repo to `retfound-aireadi`.
- **Status:** Active
- **Depends on:** `deriva-ml` (git main), `retfound` (via RETFoundMultimodal)

### [retfound-aireadi](https://github.com/eye-ai-usc/retfound-aireadi)
- **Maintainer:** ISRD
- **Purpose:** RETFound foundation model applied to AI-READI retinal imaging data (including OCT) with full DerivaML experiment provenance.
- **Status:** Active
- **Depends on:** `deriva-ml` (git main), `retfound` (via RETFoundMultimodal)

### [eye-ai-retfound](https://github.com/eye-ai-usc/eye-ai-retfound)
- **Maintainer:** ISRD
- **Purpose:** EyeAI implementation of the RETFound foundation model. Earlier implementation that uses the `informatics-isi-edu` fork of `eye-ai-ml`.
- **Status:** Active (note: uses older `informatics-isi-edu/eye-ai-ml` source, not `eye-ai-usc/eye-ai-ml`)
- **Depends on:** `eye-ai-ml` (informatics-isi-edu fork, untagged git)

### [retfound-severity](https://github.com/eye-ai-usc/retfound-severity)
- **Maintainer:** ISRD
- **Purpose:** Evaluating RETFound's ability to grade glaucoma severity compared to glaucoma specialists.
- **Status:** Active (last push Dec 2025)
- **Depends on:** `eye-ai-ml` (git tag `v1.4.9`), `retfound`

### [eye-ai-aireadi](https://github.com/eye-ai-usc/eye-ai-aireadi)
- **Maintainer:** ISRD
- **Purpose:** Earlier iteration of AI-READI dataset experiments. Largely superseded by `retfound-aireadi` for foundation model work.
- **Status:** Maintenance
- **Depends on:** `eye-ai-ml` (`>=1.3.0`, git main), `deriva-ml` (git main)

### [kim-glaucoma-computable-definitions](https://github.com/eye-ai-usc/kim-glaucoma-computable-definitions)
- **Maintainer:** ISRD / Dr. Kim
- **Purpose:** Computable glaucoma definitions model — code and configuration for reproducing Dr. Kim's analysis using EyeAI datasets with Hydra-zen configuration.
- **Status:** Active (last push Mar 2026)
- **Depends on:** `eye-ai-ml` (git tag `v1.4.9`), `hydra-zen`

### [eye-ai-privacyML](https://github.com/eye-ai-usc/eye-ai-privacyML)
- **Maintainer:** TBD
- **Purpose:** Privacy-preserving ML experiments using EyeAI data.
- **Status:** Early — created Jun 2026
- **Depends on:** `deriva-ml` (git main), `retfound`

### [eye-ai-privacy](https://github.com/eye-ai-usc/eye-ai-privacy)
- **Maintainer:** TBD
- **Purpose:** Placeholder for privacy ML work.
- **Status:** Empty repo

---

## Infrastructure

### [eye-ai-compute-platform](https://github.com/eye-ai-usc/eye-ai-compute-platform)
- **Maintainer:** Infrastructure
- **Purpose:** Containerized JupyterHub deployment for GPU-enabled collaborative compute workloads. Docker Compose configuration for the shared compute environment.
- **Status:** Maintenance (last push Feb 2026)

---

## MCP Content

### [eye-ai-rag-docs](https://github.com/eye-ai-usc/eye-ai-rag-docs)
- **Maintainer:** ISRD
- **Purpose:** RAG source documents for the `eye-ai-deriva-mcp-plugin`. Contains section-aware Markdown derived from EyeAI research papers, indexed by the plugin for semantic search via `rag_search`.
- **Status:** Active
- **Used by:** `informatics-isi-edu/eye-ai-deriva-mcp-plugin`

---

## Legacy / Stale

### [eye-ai-model-template](https://github.com/eye-ai-usc/eye-ai-model-template)
- **Status:** ⚠️ Deprecated — superseded by [templates/researcher-repo/](https://github.com/eye-ai-usc/eye-ai-platform/tree/main/templates/researcher-repo) in this repo.

### [eye-ai-exec](https://github.com/eye-ai-usc/eye-ai-exec)
- **Status:** 🗄️ Stale (last push Sep 2025) — old catch-all for scripts and notebooks. Historical schema change notebooks are registered in `data-curation/migrations/`. No new work should go here.

### [eye-ai](https://github.com/eye-ai-usc/eye-ai)
- **Status:** 🗄️ Legacy — pre-ML era webapp and clinical interface. Preserved for historical reference.

### [eye-ai-tools](https://github.com/eye-ai-usc/eye-ai-tools)
- **Status:** 🗄️ Stale (last push Apr 2024) — miscellaneous utilities with no Deriva-ML dependency. Preserved for historical reference.

---

## Upstream Dependencies (informatics-isi-edu)

| Repo | Purpose | Used by EyeAI as |
|---|---|---|
| [deriva-ml](https://github.com/informatics-isi-edu/deriva-ml) | ML experiment tracing layer | Core dependency of `eye-ai-ml` and all research repos |
| [deriva-mcp-core](https://github.com/informatics-isi-edu/deriva-mcp-core) | Base MCP server | MCP agent runtime |
| [deriva-ml-mcp-plugin](https://github.com/informatics-isi-edu/deriva-ml-mcp-plugin) | DerivaML MCP plugin | ML tools in Claude Code |
| [eye-ai-deriva-mcp-plugin](https://github.com/informatics-isi-edu/eye-ai-deriva-mcp-plugin) | Eye-AI RAG indexing plugin | Eye-AI domain search in Claude Code |
| [deriva-ml-skills](https://github.com/informatics-isi-edu/deriva-ml-skills) | Claude Code skills | `/deriva-ml:*` slash commands |
| [deriva-mcp-ui](https://github.com/informatics-isi-edu/deriva-mcp-ui) | Browser chatbot for Deriva | Web UI for catalog interaction |
