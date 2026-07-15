# Subject/Observation Diagnosis → Feature Tables

**Status: COMPLETE — executed and verified on both hosts (2026-07-08).**
14,040 feature-value rows written on each of `dev.eye-ai.org` and
`www.eye-ai.org` (7,020 `Subject_Diagnosis` + 7,020 `Observation_Diagnosis`),
verified 1:1 against the legacy source tables on both hosts — matching row
counts, no duplicate or missing anchor RIDs, zero value mismatches on a
spot-check.

The vocabulary fold this migration was originally gated on — see [Diagnosis & Severity Definitions](diagnosis-severity-definitions.md)
§4.3/§5 — was checked directly against the live catalog before running and
confirmed landed, identically, on both hosts: `Glaucoma_Diagnosis` carries the
folded 7-term set (`GS`, `POAG`, `PACG`, `Unspecified Glaucoma`,
`Non-Glaucoma`, `Other`, `No Diagnosis`), `Condition_Label` no longer exists
as a separate table, `Severity_Label` carries the cleaned 6-term set, and
`Severity_Method` exists with its 6 agreed members. Legacy
`Subject_Diagnosis`/`Observation_Diagnosis` rows already referenced the new
term names (e.g. `"Non-Glaucoma"`, not the old `"No Glaucoma"`), so the
backfill needed no value remapping. Two items in the design doc, **Q6**
(disposition of ICD `9C61.2/.3/.4`) and **Q8** (new-scale severity default),
were not verifiable from the vocabulary alone and may still be open — neither
affected this migration.

Two unrelated issues surfaced during the real runs and were fixed (see
`data-curation`'s `tacit-knowledge.md` and this migration's own `README.md`
for full detail): a `Workflow_Type` vocabulary term-name mismatch, and a stale
local DerivaML execution-bookkeeping cache on the operator's machine
(unrelated to any catalog data). Neither required changes to the migration's
backfill logic itself.

**Remaining work:** retire the old `Subject_Diagnosis`/`Observation_Diagnosis`
tables once downstream consumers are confirmed migrated to the new feature
tables (see Out of Scope below).

## What's broken

Of the three levels at which `Glaucoma_Diagnosis` is recorded —
image / observation (visit) / subject — only the image level,
`Image_Diagnosis`, is a proper DerivaML feature table: it has
`Execution`/`Feature_Name` FKs, so every row carries provenance back to the
model, grader, or process that produced it.

`Subject_Diagnosis` (7,020 rows) and `Observation_Diagnosis` (7,020 rows) were
never migrated the same way. Both are plain tables —
`Subject`/`Observation`, `Glaucoma_Diagnosis`, `Diagnosis_Tag`,
`Diagnosis_Status` columns, no `Execution` link at all. `Diagnosis_Tag` (11
terms: `Initial Diagnosis`, `CNN_Prediction`, `Expert_Consensus`,
`GlaucomaSuspect-Training`/`-Validation`, `Intragrader_Agreement`, …) is doing
a poor-man's job of what `Execution` should carry — it names a source, but
there's no execution record, no workflow, no way to trace a value back to
"which run of what code produced this."

This is separate from the `Chart_Label` feature (`Execution_Subject_Chart_Label`,
2,302 rows) — that's the genuine clinical chart-review determination
(condition + severity together) and is already a proper feature. It doesn't
overlap with `Subject_Diagnosis`/`Observation_Diagnosis`, which are
algorithmic/bulk-provenance signals (model predictions, bulk-imported ground
truth, grader annotations).

No live code in `eye-ai-ml` or `data-curation` reads or writes either table —
`compute_condition_label()`/`insert_condition_label()` write to
`Clinical_Records`, not these tables. The only reference is a stale bootstrap
script (`eye-ai/data/setup.py`) whose column definitions no longer match the
live catalog shape; it's flagged but out of scope here.

## What's being fixed

A migration, prepared in `data-curation`, that:

1. Creates two new feature tables — `target_table="Subject"` /
   `feature_name="Subject_Diagnosis"` and `target_table="Observation"` /
   `feature_name="Observation_Diagnosis"` — with the same term columns
   `Image_Diagnosis` already uses (`Glaucoma_Diagnosis`, `Diagnosis_Tag`,
   `Diagnosis_Status`).
2. Backfills every existing row from the legacy tables into the new feature
   tables, grouped by `(Diagnosis_Tag, RCB)`. Each group gets its own
   `Workflow` + `Execution`, on the reasoning that rows sharing a tag and
   original inserter came from the same real-world process — a
   synthetic-but-honest per-group Execution is a more accurate provenance
   anchor than one blanket "unknown" execution for everything.

This directly generalizes the approach already used, historically, to
backfill `Execution` onto `Image_Diagnosis` itself, in
[`eye-ai-exec/notebooks/schema_changes/fix_diag_exec.ipynb`](https://github.com/eye-ai-usc/eye-ai-exec/blob/main/notebooks/schema_changes/fix_diag_exec.ipynb).

**Scope:** both tables together (`Observation_Diagnosis` has the identical
structural gap and is upstream of `Subject_Diagnosis` in the image → visit →
subject hierarchy — fixing one without the other leaves an inconsistent
pattern).

**Location:** `data-curation/migrations/20260703_000000_zhiweiii_subject-observation-diagnosis-feature/`
(`subject_observation_diagnosis_feature_migration.py` + `README.md`), per
[Catalog Migration Guide](../guides/catalog-migration.md). This repo carries no
catalog code, so the script lives in `data-curation`, not here.

**Safety:** the script defaults to `--dry-run` and refuses `--execute` without
`--confirm-post-vocab-fold`. When it does run, it's dev (`dev.eye-ai.org`)
first, verified, then prod (`www.eye-ai.org`) — never the reverse, and never
without a human explicitly requesting that specific run.

## Why it was gated on the vocabulary fold (now verified landed)

The fold (§4.2 change 2/4 in the severity/diagnosis doc) changes what
`Glaucoma_Diagnosis` values mean and resolves how the current coarse
`Suspected Glaucoma`/`No Glaucoma`/`Unknown` terms map onto the proposed
fine-grained vocabulary. The structural change here (add Execution/Feature_Name
provenance) is independent of which vocabulary terms are in play — rows are
copied through as-is — but running the real backfill before the fold risked
migrating the same ~14,000 rows' values twice. Preparing the migration ahead
of the fold and gating only the `--execute` step avoided that without
blocking on the fold to start writing code.

As of 2026-07-07, the fold has been directly verified against the live
catalog on both `dev.eye-ai.org` and `www.eye-ai.org` (see Status above). The
`--confirm-post-vocab-fold` flag remains required with `--execute`, now as an
explicit human sign-off that this has been checked, rather than a block on an
unmet precondition.

## Out of scope

- The vocabulary fold itself — owned by
  [Diagnosis & Severity Definitions](diagnosis-severity-definitions.md).
- Retiring the old `Subject_Diagnosis`/`Observation_Diagnosis` tables — a
  follow-up migration once this backfill is run and verified.
- Fixing the stale `eye-ai/data/setup.py` bootstrap definitions.
