# Catalog Migration Guide

**Never modify the EyeAI Deriva catalog schema directly from a research repo.**

All schema changes go through `data-curation`.

---

## Researcher workflow (minimal overhead)

1. Develop and stabilize your compute script in your research repo.
2. Open a [Feature Registration Request](https://github.com/eye-ai-usc/data-curation/issues/new?template=feature-registration.md).
3. Fill in: feature name, target table, link to compute script, brief description.
4. A data manager handles the migration and notifies you when done.
5. Your compute script stays in your research repo permanently.

Total researcher time: ~5 minutes.

---

## Data manager workflow

1. Pick up the Feature Registration Request issue.
2. Write a migration in `data-curation/migrations/YYYYMMDD_HHMMSS_{author}_{description}/`.
3. Each directory contains `migration.py` (with required header), frozen `.SNAPSHOT.py` copies, and `README.md`.
4. Open a PR. CI validates migration headers. Merge and run against catalog.
5. Close the issue and notify the researcher.

---

## Migration header format

```python
"""
Migration: {short_name}
Type: {data_management | feature_registration}
Author: {github_handle}
Date: {YYYY-MM-DD}
Catalog table: {schema.TableName}
Description: {What this migration does}
Source computation: {URL to compute script, or N/A}
Reversible: {yes | no}
"""
```

---

## See also

- [data-curation/migrations/README.md](https://github.com/eye-ai-usc/data-curation/blob/main/migrations/README.md)
