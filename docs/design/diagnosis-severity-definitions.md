# Diagnosis & Severity Vocabularies — Clinical Data Dictionary

- Status: **draft / strawman** — clinical definitions are **provisional**, to be finalized with Dr. Bolo and Dr. Xu
- Date: 2026-06-30
- Catalog: `www.eye-ai.org`, catalog `eye-ai`, schema `eye-ai`
- Scope: clinical reference only — **this document does not modify the catalog** (see §9)

> **Provisional notice.** Every clinical definition, criterion, and threshold in
> this document is a placeholder strawman written to be *argued with*, not a
> settled standard. Nothing here is a clinical authority until reviewed and
> ratified by Dr. Bolo and Dr. Xu.
> Where a definition is unknown, it is marked **TBD — clinical**.

## Summary of conclusions

The short version, for readers who want the outcome before the evidence:

- **Two axes, kept separate.** *Condition* (`Condition_Label`: which glaucoma, or
  none) and *severity* (`Severity_Label`: stage of established disease). Severity
  applies **only when a glaucoma condition is present** — "mild glaucoma" = a
  glaucoma condition **+** a `Mild` severity, not a fused term (§5.1–§5.2).
- **`Severity_Label` needs cleanup.** `GS` and `Normal or No dx` are *conditions*,
  not stages, and should be retired from severity; `Unspecified/Indeterminate`
  should split into `Not Staged` vs `Indeterminate`; `Mild/Moderate/Severe` need
  real clinical criteria (§4, §6.1).
- **`Condition_Label` is grounded in ICD.** Each term *is* an ICD-11 concept
  (`GS`=`9C60`, `POAG`=`9C61.0`, `PACG`=`9C61.1`, `Unspecified`=`9C61.Z`) with the
  WHO URI as its identity. ICD-10 codes move **out of `Synonyms`** (where they are
  mis-stored today) into an `ICD10_Condition_Map` cross-walk table — no custom
  columns are added to the vocabulary (§5.6–§5.7).
- **The hard-coded mapping goes away.** With the cross-walk in the catalog, the
  `icd_mapping` dict in `eye-ai-ml`'s `compute_condition_label()` becomes a join;
  only the multi-code priority tie-break remains in code (§5.7).
- **Nothing here changes the catalog.** This is a clinical reference and design
  proposal; all changes go through `data-curation`. The executable plan — five
  changes, their ordering, and the open clinical questions — is in §8. Clinical
  definitions are provisional pending Dr. Bolo and Dr. Xu.

## 1. Purpose & scope

This document defines the **Condition (diagnosis)** and **Severity** vocabularies
used to label glaucoma in the Eye-AI catalog — their **clinical meaning** and
**intended use**, stated **independently of any algorithm, model, or grading
tool**. A term means what a clinician means by it; whether a CNN, an ICD-derived
rule, or a human grader produced a given label does not change the definition of
the label itself.

What this document is:

- The **clinical reference** for the members of `Condition_Label` and
  `Severity_Label` (and the related `Glaucoma_Diagnosis` image-level vocabulary).
- A **strawman conceptual model** for how *condition* and *severity* relate, to be
  refined in the upcoming meeting with Dr. Bolo and Dr. Xu.
- A **record of the problems** in the current vocabularies, grounded in the actual
  catalog data, so the cleanup is driven by evidence rather than opinion.

What this document is **not**:

- It is **not** an algorithm spec, a model card, or a grading protocol.
- It is **not** a numbered ADR — this is an **evolving clinical reference**, not a
  one-time decision record. Decisions that *result* from this work (e.g. renaming
  a term, removing a value) may be captured separately once made.
- It is **not** a mechanism for changing the catalog. Term/schema changes are
  requested through the `data-curation` process (see §9).

### Where this sits in the project (per the `eye-ai-platform` roadmap)

The `eye-ai-platform` repository is the project's front door and repository index.
Per its layering:

- **Schema and vocabulary *changes*** (adding/renaming terms, altering tables) are
  tracked and executed in **`data-curation`** — the catalog-integrity repo. Its
  *"Feature Registration Request"* issue template is the front door for requesting
  a catalog change.
- The **`eye-ai-ml`** library (the `EyeAI` domain class) **reads and writes** these
  vocabularies — e.g. `compute_condition_label()` / `insert_condition_label()` map
  ICD-10 codes into `Condition_Label` values.
- **This document** (in `eye-ai-platform/docs/design/`) is the **clinical reference
  for what the terms mean.** It informs the `data-curation` requests; it does not
  perform them.

## 2. Current state — every term, exactly as in the catalog

Snapshot taken 2026-06-30 from `www.eye-ai.org` / `eye-ai`. Descriptions and
synonyms are reproduced verbatim; commentary is set off as notes.

### 2.1 `Condition_Label` — 6 terms

> Catalog comment: *"Vocabulary of clinical condition labels used in chart-review
> diagnoses (e.g., glaucoma, diabetic retinopathy)."*

| RID | Name | Description (verbatim) | Synonyms (verbatim) |
|---|---|---|---|
| `2-NKSW` | **GS** | Glaucoma Suspect | `H40.00*`, `H40.01*`, `H40.02*`, `H40.03*`, `H40.04*`, `H40.05*`, `H40.06*` |
| `2-NKSY` | **POAG** | Primary open angle glaucoma | `H40.10*`, `H40.11*`, `H40.12*`, `H40.13*`, `H40.14*`, `H40.15*` |
| `2-NKT0` | **PACG** | Primary angle closure glaucoma | `H40.2*` |
| `2-NKT2` | **Other** | All other conditions (For ICD derived condition label) | — |
| `5-26KY` | **Normal or No dx** | No signs of glaucoma or No diagnosis made | — |
| `6-0A34` | **Unspecified Glaucoma** | Glaucoma present, subtype unspecified (from LAC patient-level chart review). | — |

> **Note — ICD codes in `Synonyms`.** The `Synonyms` field of `GS`, `POAG`, and
> `PACG` is currently being used to store **ICD-10 code patterns** (`H40.*`), not
> human-readable alternate names. This is the lookup key that
> `EyeAI.compute_condition_label()` reverses (its hard-coded `icd_mapping` mirrors
> exactly these patterns: `H40.0x → GS`, `H40.1x → POAG`, `H40.2* → PACG`, else
> `Other`). The codes belong in a defined ICD→condition mapping, not in a
> free-text synonyms list (see §6).

### 2.2 `Severity_Label` — 6 terms

> Catalog comment: *"Vocabulary of severity levels for clinical conditions (e.g.,
> mild, moderate, severe, advanced). Used in chart-review and ICD-derived severity
> classifications."*

| RID | Name | Description (verbatim) | Synonyms |
|---|---|---|---|
| `4-YFWT` | **Mild** | Mild stage | — |
| `4-YFWP` | **Moderate** | Moderate stage | — |
| `4-YFWR` | **Severe** | Severe stage | — |
| `4-YFWW` | **Unspecified/Indeterminate** | Indeterminate stage or stage unspecified | — |
| `4-YFWY` | **GS** | Glaucoma Suspect | — |
| `5-29BJ` | **Normal or No dx** | No signs of glaucoma or No diagnosis made | — |

> **Note.** Three of these six are not severity stages at all: `GS` and
> `Normal or No dx` are *conditions* (they duplicate `Condition_Label` members),
> and `Unspecified/Indeterminate` is a "no stage available" sentinel whose name
> packs a synonym into a slash. Only `Mild`/`Moderate`/`Severe` are genuine
> severity grades. See §3–§4 for the evidence and §6 for proposed fixes.

### 2.3 `Glaucoma_Diagnosis` — 3 terms (consolidated image-level vocabulary)

The image-level diagnostic vocabulary, **created 2026-06-30** as the single
consolidated vocabulary that the three diagnosis levels now share.

> Catalog comment: *"Vocabulary of image-level diagnostic categories for retinal
> images (e.g., referable glaucoma, no glaucoma)."*

| RID | Name | Description (verbatim) | Synonyms (verbatim) |
|---|---|---|---|
| `6-0EQR` | **No Glaucoma** | No Glaucoma | No Referable Glaucoma |
| `6-0EQP` | **Suspected Glaucoma** | Suspected Glaucoma | Referable Glaucoma |
| `6-0EQM` | **Unknown** | Unknown | Ungradable |

**Consumed by** (all foreign-key to `Glaucoma_Diagnosis.Name`, all populated):

| Table | Rows | Level |
|---|---|---|
| `Image_Diagnosis` | 194,204 | image-level (per fundus image) |
| `Observation_Diagnosis` | 7,020 | observation / visit-level |
| `Subject_Diagnosis` | 7,020 | subject-level |

All 194,204 `Image_Diagnosis` rows resolve to exactly these three terms —
**No Glaucoma** 155,279, **Suspected Glaucoma** 38,547, **Unknown** 378 (sum =
194,204) — confirming the 2026-06-30 consolidation is complete with no legacy
values or nulls remaining at the image level.

> **Note.** `Glaucoma_Diagnosis` (image-level: No / Suspected / Unknown, ~a
> referability signal from graders/models) is deliberately kept **separate** from
> `Condition_Label` (the fine-grained chart-review subtype). They differ on
> granularity and source and are not merged; the full distinction and why it holds
> is in §5.

### 2.4 Supporting vocabularies (distinct from diagnosis — do not conflate)

These describe *provenance, status, and context* of a diagnosis, not the
diagnosis itself. Listed so the clinical reader knows they exist and why they are
**not** part of the condition/severity cleanup.

- **`Diagnosis_Tag`** (11 terms) — *provenance / study tags*, not diagnoses.
  Examples: `Initial Diagnosis` (from the original dataset), `CNN_Prediction`,
  `Expert_Consensus` (*"Expert consensus diagnosis from 3 expert graders (Benjamin
  Xu, Brandon Wong, Van Nguyen)"*), `Intragrader_Agreement`,
  `GlaucomaSuspect-Training` / `-Validation`, `UI Annotation`. Answers *"who/what
  produced this label, in what study?"*
- **`Diagnosis_Status`** (3 terms) — `Graded`, `Validated`, `Rejected`. Answers
  *"what is the review state of this diagnosis?"*
- **`ICD10_Eye`** — vocabulary of ICD-10 ophthalmic codes; the standardized source
  feeding the ICD-derived condition and severity labels.
- **`Grading_Condition`** — **exists but is currently empty (0 terms)**. Intended
  (per its catalog comment) to *"record the conditions under which a chart label
  was graded, so that the USC and LAC grading contexts remain distinguishable
  within the shared Chart_Label feature table."* Referenced by
  `Execution_Subject_Chart_Label.Grading_Condition`. Flagged here because it is a
  context axis the cleaned-up model may need to populate.

## 3. How the terms are actually used today (the evidence)

The clinical chart-review label lives in the **`Chart_Label` feature on Subject**
— table `Execution_Subject_Chart_Label`, **2,302 rows** — which carries
`Condition_Label` **and** `Severity_Label` as two columns on the same row. The
distinct `(Condition_Label, Severity_Label)` pairs actually present:

| Count | Condition_Label | Severity_Label |
|---:|---|---|
| 698 | GS | **GS** |
| 392 | POAG | Unspecified/Indeterminate |
| 287 | GS | Unspecified/Indeterminate |
| 219 | POAG | Moderate |
| 215 | POAG | Mild |
| 214 | POAG | Severe |
| 107 | Other | Unspecified/Indeterminate |
| 61 | Normal or No dx | Unspecified/Indeterminate |
| 27 | Normal or No dx | **Normal or No dx** |
| 21 | PACG | Unspecified/Indeterminate |
| 20 | PACG | Mild |
| 17 | PACG | Severe |
| 16 | Unspecified Glaucoma | Unspecified/Indeterminate |
| 8 | PACG | Moderate |

Read directly off the data:

- **The only rows carrying a genuine severity grade** (Mild/Moderate/Severe) are
  POAG (648 rows) and PACG (45 rows) — i.e. established glaucoma. Everything else
  is `Unspecified/Indeterminate` or a condition-as-severity sentinel.
- **698 rows are `GS` / `GS`** — the condition *and* the severity are both "GS".
  The severity column is restating the condition.
- **27 rows are `Normal or No dx` / `Normal or No dx`** — same pattern at the
  no-disease end.
- **`Unspecified/Indeterminate` is the catch-all** across every condition (≈900
  rows), used wherever no real stage applies.

## 4. Identified problems (what's broken and why)

1. **`Severity_Label` contains values that are really conditions, not stages.**
   `GS` (`4-YFWY`) and `Normal or No dx` (`5-29BJ`) duplicate `Condition_Label`
   members and make the severity column do double duty. The data proves it: 698
   `GS`/`GS` rows and 27 `Normal`/`Normal` rows where severity simply echoes
   condition.
2. **`Unspecified/Indeterminate` packs a synonym into the name via a slash.** It
   conflates two ideas ("indeterminate stage" vs "stage not recorded") in one
   label and functions as a dumping ground for any condition with no graded stage.
3. **Severity descriptions are circular and thin.** "Mild stage", "Moderate
   stage", "Severe stage" restate the name and carry **no clinical criteria** — no
   VF MD thresholds, no structural criteria, nothing a grader could apply
   reproducibly.
4. **Condition descriptions are better but lean on ICD codes stuffed in
   `Synonyms`.** The `H40.*` patterns in `GS`/`POAG`/`PACG` synonyms are a
   machine lookup key masquerading as alternate names; the clinical definition of
   each condition is mostly carried by the (short) Description, not a proper
   criteria statement.
5. **True severity only meaningfully applies to established glaucoma
   (POAG/PACG).** Grading a "suspect" or a "normal" eye on a Mild/Moderate/Severe
   scale is a category error — which is exactly why those rows fall back to
   condition-as-severity or `Unspecified`.

## 5. Proposed conceptual model (the strawman to discuss)

> **Provisional.** This section is the strawman to be confirmed/revised with
> Dr. Bolo and Dr. Xu.

### 5.1 Two separate axes

- **Condition** = *which glaucoma, or none* — the diagnosis. Candidate members
  (from current `Condition_Label`): `Normal or No dx`, `GS` (glaucoma suspect),
  `POAG`, `PACG`, `Unspecified Glaucoma`, `Other`.
- **Severity** = *stage of established glaucomatous disease* —
  `Mild` / `Moderate` / `Severe` — **applicable only when a glaucomatous condition
  is present**. The non-stage values (`GS`, `Normal or No dx`) move **out** of
  severity; the "no stage available" case is represented explicitly (see §6),
  not by smuggling a condition into the severity column.

### 5.2 Intended relationship: separate but conditional

Severity is a **further attribute of an established glaucoma diagnosis**, not an
independent label. You first have a *condition*; *severity* refines it **only**
when that condition is glaucoma (POAG/PACG, and possibly `Unspecified Glaucoma`).

This directly answers **Professor Carl's question** — *"is there such a thing as 'mild
glaucoma', or is it glaucoma + a separate severity attribute?"* — with a proposed
answer: **separate but conditional.** "Mild glaucoma" = condition `POAG` (or
`PACG`) + severity `Mild`; severity is not baked into the condition term.
**Pending clinical confirmation.**

Corollaries to confirm in the meeting:

- A **suspect (`GS`)** has, by definition, no established disease to stage — so
  does a suspect have a severity at all? (Strawman: **no** — severity is
  undefined/not-applicable for `GS`.)
- A **normal** eye has no severity. (Strawman: not-applicable.)

### 5.3 Data-model placement

**Current join (as built):**

- `Condition_Label` and `Severity_Label` are **two independent foreign-key columns
  side by side** on the `Chart_Label` feature on Subject
  (`Execution_Subject_Chart_Label`: `Condition_Label` → `Condition_Label.Name`,
  `Severity_Label` → `Severity_Label.Name`). Nothing in the schema ties the two —
  any condition can pair with any severity, which is how `GS`/`GS` and
  `Normal`/`Normal` arose.
- **Severity also stands alone**, decoupled from the chart condition, in the
  **ICD-derived feature** `Execution_Clinical_Records_Glaucoma_Severity`
  (**3,674 rows**; column `ICD_Severity_Label` → `Severity_Label.Name`), whose
  target `Clinical_Records` carries the condition separately in
  `Clinical_Records.ICD_Condition_Label` → `Condition_Label.Name`.

**Future enforcement (to discuss).** Once severity is defined as conditional on a
glaucoma condition, the schema *could* enforce "severity requires a glaucoma
condition" — e.g. severity is non-null only for glaucomatous conditions and
null/not-applicable otherwise, or a constraint/validation at write time in the
`Chart_Label` and `Glaucoma_Severity` features. This is a `data-curation` change,
out of scope for this document beyond recording the intent.

The **ERD in §5.7 (Figure 1)** shows this whole model — both axes on the
`Chart_Label` row, the conditional severity constraint, and the ICD grounding of
`Condition_Label` — once the ICD pieces (§5.6) are in place.

### 5.4 Define terms clinically, not by how the label was produced

A term's definition must describe **the eye**, never the mechanism that assigned
the label. The same term is written into the catalog two ways — by a **human**
chart reviewer, and by an automated **ICD rule** (see §5.6 for how both reach the
same term) — and its meaning must be identical in both cases.

So: define `POAG` as a clinical condition, **not** as "whatever `H40.1x` maps to"
(only true for the ICD path) or "what the grader circled" (only true for the
human path). "Moderate POAG" must mean the same clinical thing whether a grader
wrote it or an ICD rule produced it.

### 5.5 Do not conflate the two senses of "severity"

There are **two unrelated meanings of "severity"** in this codebase; the
vocabulary concerns only the first:

- **Severity grade (this document)** — `Severity_Label`: the clinical stage of
  disease (Mild/Moderate/Severe).
- **Laterality severity (different concept)** — `EyeAI.severity_analysis()` in the
  `eye-ai-ml` library computes *which eye is worse* (left vs right) from RNFL
  thickness, HVF MD, and CDR, and flags `Severity_Mismatch`. This is **not** the
  `Severity_Label` vocabulary and must never be confused with it.

The doc states this explicitly so the two are never merged in code or
conversation.

### 5.6 Grounding `Condition_Label` in ICD (the "what" and "why")

> **Settled design direction** (provisional only on the clinical *wording*). How
> `Condition_Label` is grounded in an external standard. The *implementation
> mechanism* (cross-walk table, compute join, `eye-ai-ml` impact) is §5.7.

**Each `Condition_Label` term *is* an ICD-11 concept.** The condition vocabulary
is not a local scheme that ICD-11 merely tags; each term **is** an ICD-11 concept,
with the short name as its display label — `GS` = ICD-11 `9C60`, `POAG` = `9C61.0`,
and so on. The ICD-11 code is the term's **identity**. This gives **one vocabulary
(ICD-11 concepts) reached two ways** — a human chart reviewer picks the ICD-11
concept directly (ICD-11-native, not ICD-free), and legacy ICD-10 records are
translated *up* to the same concept (§5.7). Both arrive at the same term; ICD-10
never stands alone as the identity.

**Curated subset, at the category level.** Ground the vocabulary in a curated
subset of **only the glaucoma codes**, at the **category level**
(`H40.0` / `H40.1` / `H40.2`) — not the granular per-eye / per-stage sub-codes.
Working at the category level keeps the ICD-10 ↔ ICD-11 crosswalk effectively
**1-to-1 and lossless**. *Rationale (Carl):* a small curated subset keeps the
vocabulary tables small and the crosswalk easy to maintain and audit. (Scale: the
live data holds ~27,962 ICD-coded rows / 1,209 distinct codes, of which only the
~134 H40 glaucoma codes — at category level just `H40.0/.1/.2` — matter here.)

**The ICD-10 ↔ ICD-11 mapping (the canonical table — referenced throughout).**

| `Condition_Label` | ICD-10-CM category | ICD-11 (MMS) code | ICD-11 title | Crosswalk |
|---|---|---|---|---|
| `GS` (Glaucoma Suspect) | `H40.0` (H40.00–H40.06) | **`9C60`** | Glaucoma suspect | Concept-equivalent but **structurally relocated** — ICD-11 breaks "glaucoma suspect" out as its **own stem code `9C60`**, a *sibling* of `9C61` Glaucoma (in ICD-10 it sits *inside* the H40 block). This **reinforces §5.2**: a suspect is not staged disease. A few H40.0 sub-codes move under `9C61` in ICD-11 (ocular hypertension → `9C61.01`; primary angle-closure suspect → `9C61.10`). |
| `POAG` | `H40.1` (H40.10–H40.15) | **`9C61.0`** | Primary open-angle glaucoma | Equivalent, 1-to-1 |
| `PACG` | `H40.2` | **`9C61.1`** | Primary angle closure or angle closure glaucoma | Equivalent, 1-to-1 |
| `Unspecified Glaucoma` | `H40.9` | **`9C61.Z`** | Glaucoma, unspecified | Equivalent |
| `Normal or No dx` | — (no glaucoma code) | — | — | Absence of disease |
| `Other` | — (non-glaucoma; default) | — | — | Catch-all for codes outside the curated glaucoma subset |

At this coarse category level the mapping is **1-to-1 and lossless** for
`POAG` / `PACG` / `Unspecified Glaucoma`, with the single `GS` caveat above
(concept-equivalent, structurally relocated). The secondary/developmental
ICD-11 subtypes (`9C61.2` secondary OAG, `9C61.3` secondary ACG, `9C61.4`
developmental) have **no dedicated `Condition_Label` member** and currently fall
into `Other` — a disposition to decide clinically (§6.2, §7).

**How the codes and identifier are stored — using the vocabulary's standard shape
only.** A Deriva controlled vocabulary has a fixed schema — `RID`, `Name`,
`Description`, `Synonyms`, `ID`, `URI` (plus system columns). **We do not add
custom columns** (no `ICD10_code` / `ICD11_code` fields on the term). That
uniformity is the contract Chaise and the deriva-ml APIs depend on; external
grounding belongs in the slots the vocabulary already provides. So:

- **ICD-11 → the `ID` / `URI` identifier.** The term's `ID` / `URI` holds the real,
  authoritative **ICD-11 WHO URI** (`http://id.who.int/icd/...`), not a
  locally-minted id. This is the term's one canonical external identity. *Why
  ICD-11 for the identifier:* WHO publishes ICD-11 as linked data with official
  canonical URIs, so authoritative identifiers come for free; ICD-10-CM has no
  single official URI scheme (CDC/NCHS code lists), and ICD-11 is forward-looking
  as international data moves to it.
- **ICD-10 → the `ICD10_Condition_Map` association table**, *not* a column on the
  term. The live data is natively ICD-10-CM (~27,962 stored codes, and US EHRs
  keep sending it), and one condition maps from *many* ICD-10 codes
  (`H40.00`–`H40.06` → `GS`). A many-to-one external relation attaches to a
  vocabulary through an **association table** (§5.7), which is also what lets the
  exact per-code data resolve to a condition. It is never modelled as extra
  columns on the vocabulary.
- **`Synonyms` stays human-only.** With ICD-11 in `ID`/`URI` and ICD-10 in the
  cross-walk table, `Synonyms` holds **human-readable alternate names only**
  (e.g. "Primary Open-Angle Glaucoma", WHO index terms). The `H40.*` patterns
  currently mis-stored in `Condition_Label.Synonyms` (§2.1) move out. Lookup **by
  code** uses `ID`/`URI` (and the cross-walk for ICD-10); lookup **by name** uses
  `Synonyms` — see §5.7 for why a code never goes in `Synonyms`.

The vocabulary term is unchanged in shape; all ICD-10 breadth lives in the
association table described next.

> **Status & verification (single source — referenced elsewhere as "the §5.6
> status").** ICD-11 codes **verified 2026-06-30** against the WHO ICD-11 MMS
> (`9C60` suspect; `9C61.0/.1/.Z` established glaucoma). The URI **scheme** is
> settled — `http://id.who.int/icd/release/11/{version}/mms/{code}` — but the
> **exact per-term IRIs must be confirmed against the WHO API/browser**
> (`icd.who.int`) before catalog work; they are not minted here. Still
> **unverified**: (1) disposition of `9C61.2/.3/.4` (clinical — Dr. Bolo / Dr. Xu);
> (2) that `ICD10_Eye` is structurally a controlled vocabulary and the name of the
> existing `Clinical_Records ⇄ ICD10_Eye` association table (§5.7) — the deriva
> MCP surface was not connected when this was written. Primary clinical reference:
> the **AAO Glaucoma ICD-10 Quick Reference Guide** (§9).

### 5.7 Implementation mechanism (the "how" — for `eye-ai-ml` / `data-curation`)

This section details the `ICD10_Condition_Map` cross-walk **table** introduced in
§5.6: how it turns `compute_condition_label` into a join, and what that retires.
Codes and the crosswalk itself are in the §5.6 mapping table; this section does
not restate them.

**Tables involved.**

| Object | Role | Code / keys |
|---|---|---|
| `Condition_Label` | the ICD-11 concept (display name `GS`, `POAG`, …) | `ID`/`URI` = its ICD-11 code (identity) |
| `ICD10_Eye` | one term per legacy ICD-10 code | `ID`/`URI` = that ICD-10 code |
| `ICD10_Condition_Map` *(new, association)* | **ICD-10 → ICD-11 cross-walk** | FKs: `ICD10_Eye` → `Condition_Label` |

![ERD — the Chart_Label feature carries Condition_Label and Severity_Label as two side-by-side axes on one row; Condition_Label is the ICD-11 concept (chart review picks it directly, legacy ICD-10 cross-walks up), and severity is valid only when the condition is glaucoma.](img/icd11-condition-erd.png)

*Figure 1 — the full Chart_Label model: the two axes (condition + severity, §5.1–§5.3),
the ICD-11 grounding of `Condition_Label` (§5.6), and the ICD-10→ICD-11 cross-walk
(this section). Source: [`img/icd11-condition-erd.svg`](img/icd11-condition-erd.svg).*

**Why a cross-walk table (not more columns).** The ICD-10 side at exact-code
granularity is *many* codes per concept (`H40.00`–`H40.06` all → `GS`) — a
many-to-one relation. A single-valued `ID`/`URI` cannot hold a family, and
`Synonyms` is for human names, not codes. Only an association table fits. Map
**exact codes** (FKs to real `ICD10_Eye` terms), not wildcard patterns (`H40.0*`),
so no wildcard-matching logic is needed.

**Lookup by code uses `ID`, never `Synonyms`.** A term's code IS its `ID`/`URI`,
so `lookup_by_id("ICD11:9C60") → term` is a typed, indexed, one-hop lookup — that
*is* semantic lookup by code, needing no duplication of the code into `Synonyms`.
`Synonyms` hold WHO index terms (human names) for lookup by name. Putting a code
in its own row's `Synonyms` would merely shadow `ID` and re-blur code-vs-name.
(A code belongs in `Synonyms` only as a deprecated *alias* code; the primary code
is always `ID`.)

**The two bridges — and the compute join.** `compute_condition_label()`'s input
is a DataFrame `RID, Clinical_Records, ICD10_Eye` — one row per (record, code) —
i.e. a read of a **`Clinical_Records ⇄ ICD10_Eye` association table already in the
catalog** (verified from `eye_ai.py:293` + fixture `test_eye_ai_units.py:131`).
So two distinct bridges represent all the codes as data:

| Bridge | Relates | Kind | Status |
|---|---|---|---|
| `Clinical_Records ⇄ ICD10_Eye` | record ↔ the codes it carries | **observed data** | exists (the input) |
| `ICD10_Condition_Map` | ICD-10 code ↔ its ICD-11 concept | **classification rule** | proposed |

With both, the code→condition step is a pure join —
`Clinical_Records ─ ICD10_Eye ─ ICD10_Condition_Map ─ Condition_Label` — and the
Python dict disappears. Keep the two bridges distinct: one records *facts* (this
record's codes), the other the *rule* (what a code means); they evolve on
different schedules.

**End-to-end: many ICD-10 codes → one ICD-11 `Condition_Label`.** A record
typically carries several codes. Resolution: (1) **map every code** to its ICD-11
concept via the join — e.g. `H40.11`+`H40.00` → {`POAG`, `GS`}; (2) **pick the
highest-priority concept** by clinical severity `PACG > POAG > GS > Other`
(`eye_ai.py:295`) — here POAG wins → `Condition_Label = POAG`. The stored label
is thus an ICD-11 concept; the codes are input, the winning term is output. (The
priority tie-break now orders ICD-11 *concepts*, which is where it belongs. If it
should become catalog data rather than code, it belongs in its own ranking table
keyed to `Condition_Label` — **not** as an added column on the vocabulary, whose
standard shape stays fixed per §5.6.)

**What this retires in `eye-ai-ml`** (verified against `eye_ai/eye_ai.py`,
2026-06-30). `compute_condition_label()` (`eye_ai.py:268`) does two things:

1. **ICD-10 → condition mapping** via an inline `icd_mapping` dict + `startswith`.
   **The cross-walk table replaces this** — delete the dict, read the mapping from
   the table. (It is the only copy in the library — one site + test
   `test_eye_ai_units.py:139`.)
2. **Multi-code priority resolution** (the `PACG>POAG>GS>Other` tie-break). **Not
   replaced** by the table — it is a per-record reconciliation policy that still
   needs a home (library, or a documented rule on the join's output).

So the **`icd_mapping` dict is no longer needed**; the function shrinks to the
priority step (or is removed if that moves elsewhere). `insert_condition_label()`
(`eye_ai.py:302`) is unaffected. **Placement:** the cross-walk is upstream of
`Condition_Label`, *not* a hop off the Subject — the chart-review path references
the term directly, the ICD-10 path reaches it through the cross-walk. **Retiring
the dict is an `eye-ai-ml` change**, contingent on `ICD10_Condition_Map` existing
first (§8).

## 6. Naming cleanup proposals

§6.0 gives the **proposed descriptions and synonyms** for every term; §6.1–§6.2
give the **action** per term (keep / rename / split / retire) and the rationale;
§6.3–§6.4 cover severity-naming precision and the GAMMA band. The **ICD grounding**
is §5.6. §6.1–§6.2 reference §6.0 for wording rather than restating it.

> **Provisional.** Everything below is for discussion; clinical criteria are
> **TBD — clinical**, pending Dr. Bolo and Dr. Xu.

### 6.0 Proposed term definitions (descriptions & synonyms — source of truth)

The **single source** for each term's proposed **description** and
**human-readable synonyms**. Items marked **(confirm clinically)** need Dr. Bolo /
Dr. Xu sign-off; severity staging *thresholds* are deliberately **TBD — clinical**.
Current catalog state is §2.1–§2.2 (unchanged); ICD grounding is §5.6.

**`Condition_Label` — proposed descriptions & synonyms:**

| Term | Proposed description | Proposed synonyms (human-readable) |
|---|---|---|
| `GS` | Glaucoma suspect — findings suspicious for glaucoma (e.g. ocular hypertension / elevated IOP, suspicious optic disc, anatomical narrow angle) **without** established glaucomatous damage. *(confirm clinically)* | "Glaucoma Suspect" |
| `POAG` | Primary open-angle glaucoma — chronic glaucomatous optic neuropathy with an **open** anterior chamber angle and no secondary cause. *(confirm clinically)* | "Primary Open-Angle Glaucoma" |
| `PACG` | Primary angle-closure glaucoma — glaucoma associated with appositional/synechial **closure** of the anterior chamber angle. *(confirm clinically)* | "Primary Angle-Closure Glaucoma" |
| `Unspecified Glaucoma` | Glaucoma is present but the **subtype is not specified** (e.g. LAC patient-level chart review without a subtype). *(confirm clinically)* | "Glaucoma, unspecified"; "Glaucoma NOS" |
| `Normal or No dx` | **No glaucoma diagnosis** — no signs of glaucoma, or no diagnosis recorded. *(confirm whether to split "Normal/no disease" from "not assessed / no dx")* | "No Glaucoma"; "Normal" |
| `Other` | **Catch-all** for non-glaucoma conditions — used when the ICD-derived condition falls **outside** the curated glaucoma subset (§5.6). | "Non-glaucoma"; "Other condition" |

**`Severity_Label` — proposed descriptions & synonyms.** Applies **only to
established glaucoma** (§5.1–§5.2). `GS` and `Normal or No dx` are proposed for
removal (they are conditions, not stages — §4, §6.1).

| Term | Proposed description | Proposed synonyms |
|---|---|---|
| `Mild` | Mild-stage glaucomatous damage. **Criteria TBD — clinical** (e.g. VF MD / RNFL / CDR). | "Early" |
| `Moderate` | Moderate-stage glaucomatous damage. **Criteria TBD — clinical**. | — |
| `Severe` | Severe / advanced-stage glaucomatous damage. **Criteria TBD — clinical**. | "Advanced" |
| `Not Staged` (+ optional `Indeterminate`) | Separate *"glaucoma present, stage **not recorded**"* from *"stage genuinely **indeterminate**"*; replaces `Unspecified/Indeterminate` (removes the slash). | "Stage unspecified"; "Indeterminate stage" |

> **Note.** The stage set `Mild` / `Moderate` / `Severe` / `Indeterminate` mirrors
> the **ICD-10 7th-character glaucoma staging** convention, per the AAO guide (§9)
> — so severity aligns with how stage is already coded in the source data.
> Thresholds remain **TBD — Dr. Bolo / Dr. Xu**.

### 6.1 `Severity_Label` — actions

| Current term | Action | Rationale |
|---|---|---|
| `Mild` / `Moderate` / `Severe` | **Keep**, add real criteria | Genuine stages; today's descriptions are circular (§4 item 3). Add reproducible criteria — **TBD — clinical** (VF MD / RNFL / CDR). |
| `Unspecified/Indeterminate` (`4-YFWW`) | **Split & rename** → `Not Staged` (+ optional `Indeterminate`) | One label conflates "stage not recorded" vs "genuinely indeterminate", and the slash packs a synonym (§4 item 2). |
| `GS` (`4-YFWY`) | **Retire from severity** | A condition, not a stage — represent via `Condition_Label` (§4 item 1). Requires data migration (below). |
| `Normal or No dx` (`5-29BJ`) | **Retire from severity** | Absence of disease, not a stage — represent via `Condition_Label` (§4 item 1). Requires data migration (below). |

(Proposed descriptions & synonyms for the kept terms: §6.0.)

> **Migration note (data migration — §8 change 4, not this doc):** retiring
> severity `GS` and `Normal or No dx` requires re-mapping existing `Chart_Label`
> rows (698 `GS`/`GS`, 287 `GS`/`Unspecified`, 61+27 Normal rows; §3) so the
> condition is preserved and severity becomes not-applicable / not-staged.

### 6.2 `Condition_Label` — actions

| Current term | Action | Rationale |
|---|---|---|
| `GS`, `POAG`, `PACG` | **Keep** names as display labels; ground in ICD-11 | Each term *is* its ICD-11 concept with the WHO URI as identity, and `H40.*` codes move out of `Synonyms` — full design in §5.6/§5.7. |
| `Normal or No dx` | **Consider split** | "Normal" (no disease) vs "No dx" (not assessed) may warrant separation — **TBD — clinical**. |
| `Unspecified Glaucoma` | **Keep** | Subtype unspecified (LAC patient-level). Confirm eligibility for severity grading (§5.2). |
| `Other` | **Keep — reconcile scope** | Catch-all for non-glaucoma. Tension: §5.6 tentatively routes ICD-11 `9C61.2/.3/.4` (secondary/developmental **glaucoma**) here for lack of a member — so `Other` would hold some glaucoma. Decide whether to add those members instead (clinical — §7). |

**Worked example — a grounded `Condition_Label` row (`GS`).** Illustrates the
§5.6 model concretely: `Name` = display label, `ID`/`URI` = the ICD-11 identity
(lookup by code), `Synonyms` = WHO index terms (lookup by name). Description and
synonyms are provisional (§6.0); the `9C60` code is verified (§5.6 status).

| Column | Value |
|---|---|
| `RID` | `2-NKSW` *(the existing GS row, §2.1)* |
| `Name` | `GS` |
| `Description` | Glaucoma suspect — risk factors for glaucoma (elevated IOP / ocular hypertension, suspicious optic disc or RNFL, narrow/occludable angle, or steroid response) **without** definite glaucomatous optic neuropathy or field loss. *(confirm clinically)* |
| `Synonyms` | `Glaucoma Suspect`, `Borderline glaucoma`, `Ocular hypertension`, `Narrow angle glaucoma suspect`, … *(WHO `9C60` index terms — human names, not codes; copy the authoritative set from icd.who.int)* |
| `ID` / `URI` | `ICD11:9C60` / `http://id.who.int/icd/release/11/mms/9C60` |

Siblings follow the same shape: `POAG` = `9C61.0`, `PACG` = `9C61.1`,
`Unspecified Glaucoma` = `9C61.Z`. ICD-10 equivalents (`GS`: `H40.00`–`H40.06`)
are **not** in the row — they live in the `ICD10_Condition_Map` cross-walk table
(§5.6, §5.7), not in columns on the term.

### 6.3 Severity naming precision

Per Dr. Xu's caution (§7), `Mild/Moderate/Severe` may be ambiguous without a named
basis. Options to decide in the meeting: a neutral name vs. a basis-qualified name
(e.g. `HPA_severity` vs `CMS_severity`). The vocabulary name should make the
**basis of staging unambiguous** so two different staging systems are never
silently mixed in one column.

### 6.4 New term needed for the GAMMA mapping

Dr. Kyle's **GAMMA** mapping will require a severity term **"Moderate-to-Severe"**
(per Dr. Bolo's mapping, GAMMA's **"Progressive"** category maps to a
**Moderate-to-Severe** severity band, which needs to be added to the
vocabulary). Open question for the
meeting: does a `Moderate-to-Severe` band fit the cleaned-up Mild/Moderate/Severe
scheme as an additional member, or should cross-dataset band collapses
(GAMMA/GLEAM) be handled as a **mapping layer** on top of canonical
Mild/Moderate/Severe rather than as new vocabulary terms? Flagged so the cleanup
doesn't lock GAMMA/GLEAM out.

## 7. Open clinical questions for Dr. Bolo & Dr. Xu (for the meeting)

1. **Severity criteria.** What clinical criteria define `Mild` / `Moderate` /
   `Severe`? HPA (Hodapp-Parrish-Anderson) staging? VF MD thresholds? Structural
   (RNFL/CDR) criteria, or a combination? (Dr. Bolo.)
2. **Separate but conditional?** Confirm severity should be a separate attribute
   that applies **only** when an established glaucoma condition is present
   (Professor Carl's question; strawman in §5.2).
3. **Naming basis.** How to name severity so its meaning is unambiguous — neutral
   name vs. basis-qualified (`HPA_severity` vs `CMS_severity` vs a neutral label)
   — per Dr. Xu's caution about silently mixing staging systems.
4. **Remove non-stage values?** Confirm retiring `GS` and `Normal or No dx` from
   `Severity_Label` (they are conditions, not stages).
5. **Suspects and severity.** Does a glaucoma suspect (`GS`) have a severity at
   all? (Strawman: no — not applicable.)
6. **GLEAM / GAMMA.** What, if anything, must the cleaned-up vocabulary provide so
   the GLEAM and GAMMA mappings land cleanly — notably GAMMA's `Moderate-to-Severe`
   band (§6.4) — without distorting the canonical clinical definitions?

## 8. Change plan (consolidated)

The actionable synthesis of §§5–7. **Dependency ordering and repo split matter** —
executing these in the wrong order leaves half-built states.

### 8.1 The changes

| # | Change | What it entails | Where |
|---|---|---|---|
| **1** | **Clean up `Severity_Label`** | Retire `GS` and `Normal or No dx` (conditions, not stages); split `Unspecified/Indeterminate` → `Not Staged` vs `Indeterminate`; add real clinical criteria to Mild/Moderate/Severe. (§6.1) | `data-curation` |
| **2** | **Re-anchor `Condition_Label` on ICD-11** | *Not a new table — it exists (§2.1).* Add ICD-11 `ID`/`URI` to each term (`GS=9C60`, `POAG=9C61.0`, `PACG=9C61.1`, `Unspecified Glaucoma=9C61.Z`); remove `H40.*` codes from `Synonyms`, replace with WHO index terms; reconcile member set to ICD-11 (decide `9C61.2/.3/.4`). (§5.6, §6.2) | `data-curation` |
| **3** | **Create `ICD10_Condition_Map`** | New association table `ICD10_Eye → Condition_Label`, **exact codes** (not wildcards). Prereq: `ICD10_Eye` must enumerate every ICD-10 code the data uses. (§5.7) | `data-curation` |
| **4** | **Migrate `Chart_Label` data** | Re-map existing `Execution_Subject_Chart_Label` rows to the cleaned severity + condition values (counts in §6.1). This is **data migration**, distinct from the schema/vocab changes 1–3. | `data-curation` |
| **5** | **Update `compute_condition_label`** | Replace the `icd_mapping` dict with a **join through `ICD10_Condition_Map`**; **keep** the multi-code priority tie-break (it already exists, do not re-add). `insert_condition_label` unaffected. (§5.7) | `eye-ai-ml` |

### 8.2 Dependency ordering

```
ICD10_Eye enumerated ──▶ (2) re-anchor Condition_Label ──┐
                     └──▶ (3) create ICD10_Condition_Map ─┴─▶ (5) update code ──▶ (4) migrate Chart_Label data
(1) Severity cleanup ── independent, can run in parallel
```

- The map (3) needs both endpoints ready: `Condition_Label` re-anchored (2) **and** `ICD10_Eye` populated with exact codes.
- The code change (5) needs the map (3) to exist.
- The data migration (4) needs the cleaned vocabularies (1, 2).
- **Repo split:** 1–4 are catalog/schema/data → `data-curation` (Feature Registration Request); 5 is code → `eye-ai-ml`, and its PR **cannot merge until 3 lands** in the catalog.

### 8.3 Gates (must resolve before the clinical parts land)

- **Severity criteria** for Mild/Moderate/Severe — clinical (Dr. Bolo, §7 Q1).
- **`9C61.2/.3/.4` disposition** — become `Condition_Label` members or fold into `Other`? Affects change 2 and the priority ordering in change 5 (§6.2, §7).
- **GAMMA `Moderate-to-Severe` band** (§6.4) — may add a `Severity_Label` member in change 1.
- **ICD-11 release-version pin** — pin a **specific ICD-11 release** in the term
  URIs (e.g. `…/release/11/2025-01/mms/…`) rather than the bare `{version}`
  placeholder, since ICD-11 codes/titles can shift between releases. Confirm the
  current WHO release at implementation time and **record it in this spec** (keep
  the release-independent foundation `…/icd/entity/{id}` URI as the stable anchor).
- **Catalog verification** — ✅ **resolved (confirmed via deriva MCP, 2026-06-30):**
  `ICD10_Eye` **is** a controlled vocabulary (1,209 terms), and the
  `Clinical_Records ⇄ ICD10_Eye` association is **`Clinical_Records_ICD10_Eye`**
  (27,962 rows — the input to `compute_condition_label`).

## 9. References / provenance

- This document consolidates the read-only investigation from the 2026-06-30
  review of the diagnosis/condition/severity landscape.
- **Catalog objects referenced** (schema `eye-ai`): vocabularies `Condition_Label`,
  `Severity_Label`, `Glaucoma_Diagnosis`, `Diagnosis_Tag`, `Diagnosis_Status`,
  `ICD10_Eye`, `Grading_Condition`; feature/association tables
  `Execution_Subject_Chart_Label` (Chart_Label feature on Subject),
  `Execution_Clinical_Records_Glaucoma_Severity` (Glaucoma_Severity feature on
  Clinical_Records), `Clinical_Records`, `Image_Diagnosis`, `Observation_Diagnosis`,
  `Subject_Diagnosis`.
- **Proposed new object (not yet in catalog)**: `ICD10_Condition_Map` — an
  association table that **cross-walks legacy ICD-10 → the ICD-11 concept**
  (`ICD10_Eye → Condition_Label`, §5.7), the data-driven replacement for the
  hard-coded `icd_mapping` in `compute_condition_label()`. Name is a placeholder;
  creation is a `data-curation` change.
- **Library code referenced** (`eye-ai-ml/eye_ai/eye_ai.py`):
  `compute_condition_label()`, `insert_condition_label()`, `severity_analysis()`
  (laterality — see §5.5).
- **Roadmap context:** repository layering per `eye-ai-usc/eye-ai-platform`
  (front door / repository index).
- **Clinical & coding references** (for the `Condition_Label` ICD grounding, §5.6):
  - AAO *Glaucoma ICD-10 Quick Reference Guide* — **primary** clinical reference
    for the H40 glaucoma codes:
    <https://www.aao.org/Assets/5adb14a6-7e5d-42ea-af51-3db772c4b0c2/636713219263270000/bc-2568-update-icd-10-quick-reference-guides-glaucoma-final-v2-color-pdf?inline=1>
  - icd10data.com — ICD-10-CM H40 glaucoma codes:
    <https://www.icd10data.com/ICD10CM/Codes/H00-H59/H40-H42/H40->
  - WHO **ICD-11 (MMS)** — authoritative ICD-11 glaucoma codes and canonical URIs
    (`http://id.who.int/icd/...`): glaucoma block `9C61`, glaucoma suspect `9C60`;
    browse at <https://icd.who.int/browse11>. (ICD-10-CM has no single official URI
    scheme — CDC/NCHS code lists — which is why the identifier URI uses ICD-11.)
- **Process note — no catalog edits from this document.** Any term rename,
  removal, description change, or new term (§6) is a catalog change and must be
  requested through **`data-curation`** via its *"Feature Registration Request"*
  issue template. This document is the clinical rationale that such requests cite;
  it does not itself mutate the catalog.

---

*Draft for review. All clinical definitions provisional pending Dr. Bolo and
Dr. Xu. Counts and term contents reflect the catalog state on 2026-06-30.*
