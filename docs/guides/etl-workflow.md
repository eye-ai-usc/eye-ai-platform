# ETL Workflow Guide

This guide covers the standard pattern for exporting data from the EyeAI Deriva catalog
into a format suitable for model training.

---

## Overview

```
Deriva catalog
  └── Dataset definition (deriva-ml:Dataset)
      └── BDBag export (eye_ai.export_dataset)
          └── Local asset directory
              └── DataLoader / model input
```

---

## Step 1 — Define or select a dataset

Datasets are defined in the catalog via the DerivaML dataset lifecycle.
See `/deriva-ml:dataset-lifecycle` in Claude Code for guided dataset creation.

```python
from eye_ai import EyeAI

ea = EyeAI(hostname='www.eye-ai.org', catalog_id=1)
datasets = ea.list_datasets()
```

---

## Step 2 — Export to a BDBag

```python
bag_path = ea.export_dataset(
    dataset_rid='<dataset-RID>',
    output_dir='./data/bags/'
)
```

---

## Step 3 — Prepare for training

Use the `data/prepare.py` script in your research repo to convert the BDBag into
the format expected by your model.

---

## Data source notes

- **LA County / USC Keck:** Clinical data with de-identification requirements.
- **AI-READI:** Public dataset. See [docs.aireadi.org](https://docs.aireadi.org).
- **Open-source benchmarks:** No special handling required.
