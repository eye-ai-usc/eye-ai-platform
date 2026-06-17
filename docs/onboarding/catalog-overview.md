# EyeAI Catalog Overview

The EyeAI Deriva catalog at `www.eye-ai.org` is the authoritative data store for all
project assets. This document gives a practical orientation for new researchers.

---

## What is Deriva?

[Deriva](https://deriva.isi.edu) is a scientific data management platform developed at ISI.
It provides:

- **ERMrest** — a schema-defined REST API for structured tabular data
- **Hatrac** — an object store for large binary assets (images, model weights, etc.)
- **Chaise** — a browser-based UI for browsing and editing catalog data

The EyeAI catalog is a Deriva instance hosted at `www.eye-ai.org`.

---

## Data Sources

The catalog aggregates imaging data from multiple clinical and research sources:

| Source | Description |
|---|---|
| LA County DHS | Ophthalmic images from Los Angeles County clinic networks |
| USC Keck Medical | Images from USC Keck School of Medicine |
| AI-READI | Public multimodal diabetic eye disease dataset |
| Open-source benchmarks | Publicly available ophthalmic imaging benchmarks |

Data ingestion is managed by the data team via scripts in `eye-ai-usc/data-curation`.

---

## Key Catalog Tables

| Table | Description |
|---|---|
| `eye-ai:Subject` | Patient/subject records |
| `eye-ai:Image` | Individual ophthalmic images (fundus, OCT, etc.) |
| `eye-ai:Observation` | Clinical observations and diagnoses |
| `eye-ai:Annotation` | Human expert annotations |
| `deriva-ml:Dataset` | ML dataset definitions (groups of subjects/images) |
| `deriva-ml:Workflow` | Model workflow definitions |
| `deriva-ml:Execution` | Individual experiment runs with provenance |

The full schema is browsable at `https://www.eye-ai.org` via Chaise.

---

## Accessing the Catalog

### Python (research code)

```python
from eye_ai import EyeAI

ea = EyeAI(hostname='www.eye-ai.org', catalog_id=1)
```

### MCP agent (Claude Code)

With the MCP agent configured (see [mcp-setup.md](mcp-setup.md)), you can ask Claude
to query the catalog in natural language:

```
How many glaucoma-positive subjects are in dataset X?
What features are available for the fundus images?
```

### Chaise browser UI

Navigate to `https://www.eye-ai.org` and log in with your Globus credentials.

---

## Modifying the Catalog

Schema changes (new tables, new columns, new features) must go through `data-curation`.
Do not modify catalog schema directly from research repos.

See [catalog-migration.md](../guides/catalog-migration.md) for the full workflow.
