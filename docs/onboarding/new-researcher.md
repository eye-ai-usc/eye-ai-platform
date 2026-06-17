# New Researcher Guide

Welcome to the EyeAI project. This page gives role-specific entry points.

---

## If you are an ML engineer or PhD student

1. **Start with the quickstart:** [quickstart.md](quickstart.md)
2. **Pick your research repo** (or create one from the template)
   - Glaucoma detection with VGG-19 → [eye-ai-vgg19](https://github.com/eye-ai-usc/eye-ai-vgg19)
   - RETFound foundation model → [eye-ai-retfound](https://github.com/eye-ai-usc/eye-ai-retfound) or [retfound-aireadi](https://github.com/eye-ai-usc/retfound-aireadi)
   - Multimodal analysis → [eye-ai-multimodal-kim](https://github.com/eye-ai-usc/eye-ai-multimodal-kim)
   - New research question → start from the template (see quickstart)
3. **Set up the MCP agent:** [mcp-setup.md](mcp-setup.md)
4. **Learn DerivaML:** `/deriva-ml:help` in Claude Code gives a guided orientation

---

## If you are a clinical collaborator or ophthalmologist

1. You primarily need access to the Deriva catalog UI and annotation tools.
2. Navigate to `https://www.eye-ai.org` and log in with Globus.
3. For running specific analysis scripts, ask the ML engineering team to set up a notebook for you.
4. If you need to compute annotations: open a [Feature Registration Request](https://github.com/eye-ai-usc/data-curation/issues/new?template=feature-registration.md) describing what you want added to the catalog.

---

## If you are a data manager

1. Your primary repo is [data-curation](https://github.com/eye-ai-usc/data-curation).
2. All catalog schema changes go in `data-curation/migrations/` — see the [catalog migration guide](../guides/catalog-migration.md).
3. Data ingestion scripts for each source live in `data-curation/ingestion/`.
4. When a researcher opens a Feature Registration Request, you pick it up, write the migration, and notify the researcher when done.

---

## Key contacts and channels

- **GitHub org:** [github.com/eye-ai-usc](https://github.com/eye-ai-usc)
- **Catalog UI:** [www.eye-ai.org](https://www.eye-ai.org)
- **Issues / catalog changes:** [data-curation issues](https://github.com/eye-ai-usc/data-curation/issues)
