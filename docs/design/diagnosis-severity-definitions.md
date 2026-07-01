# Diagnosis & Severity Vocabularies — Clinical Data Dictionary

- Status: **draft / strawman** — clinical definitions are **provisional**, to be finalized with Dr. Bolo and Dr. Xu
- Date: 2026-06-30
- Catalog: `www.eye-ai.org`, catalog `eye-ai`, schema `eye-ai`
- Scope: clinical reference and design proposal only — **this document does not modify the catalog** (see Appendix C)

> **Provisional notice.** Every clinical definition, criterion, and threshold in
> this document is a placeholder strawman written to be *argued with*, not a
> settled standard. Nothing here is a clinical authority until reviewed and
> ratified by Dr. Bolo and Dr. Xu. Where a definition is unknown, it is marked
> **TBD — clinical**.

**How to read this document.** The body is the narrative: **§1** what we're
doing, **§2** why (the limits of the current vocabularies), **§3** the proposed
design, **§4** the change plan, **§5** the open clinical questions. The reference
material — the *current* catalog contents and the *proposed* vocabulary tables in
full — lives in the appendices:

- **Appendix A** — current-state inventory (every term, verbatim from the catalog) + how the terms are used today.
- **Appendix B** — the proposed vocabulary tables in full (`Glaucoma_Diagnosis`, `Severity_Label`, `Severity_Method`).
- **Appendix C** — references / provenance / process.

---

## 1. Summary — what we are doing

This document defines the **diagnosis** and **severity** vocabularies used to
label glaucoma in the Eye-AI catalog, and proposes a cleanup. In one screen:

- **Diagnosis and severity are two separate axes.** *Diagnosis* = which glaucoma,
  or none. *Severity* = stage of established disease (`Mild`/`Moderate`/`Severe`),
  applicable **only when a glaucoma condition is present** — "mild glaucoma" = a
  glaucoma diagnosis **+** a `Mild` severity, not one fused term (§3.1).
- **One shared diagnosis vocabulary, ICD-grounded.** Fold today's two overlapping
  diagnosis vocabularies (`Condition_Label` + the image/visit/subject
  `Glaucoma_Diagnosis`) into **one vocabulary named `Glaucoma_Diagnosis`**, so a
  model's "Glaucoma" and a clinician's "Glaucoma" are the *same* term (direct
  model-vs-clinical comparison). Each term **is** an ICD-11 concept (`GS`=`9C60`,
  `POAG`=`9C61.0`, `PACG`=`9C61.1`, `Unspecified`=`9C61.Z`) with the WHO URI as its
  identity; legacy ICD-10 codes move out of `Synonyms` into a cross-walk table
  (§3.2–§3.4). Full table: **Appendix B.1**.
- **Three axes separated.** *Diagnosis* (`Glaucoma_Diagnosis`), *gradability*
  (`Ungradable` — could the image be assessed?), and *status* (`Diagnosis_Status`
  — review state) are distinct questions and get distinct homes (§3.3).
- **`Severity_Label` cleaned up.** Retire the values that are really conditions
  (`GS`, `Normal or No dx`); split the `Unspecified/Indeterminate` catch-all; give
  `Mild`/`Moderate`/`Severe` real clinical criteria (§3.5). Full table:
  **Appendix B.2**.
- **Severity records its method of determination.** The grade stays
  `Mild/Moderate/Severe`; a parallel `Severity_Method` vocabulary (HPA, ICD
  7th-char, …) records the staging basis, so each severity is the pair
  `(Severity_Label, Severity_Method)` (§3.6). Full table: **Appendix B.3**.
- **The hard-coded mapping goes away.** With the ICD-10 cross-walk in the catalog,
  the `icd_mapping` dict in `eye-ai-ml`'s `compute_condition_label()` becomes a
  join; only the multi-code priority tie-break stays in code (§3.4).
- **Nothing here changes the catalog.** All changes go through `data-curation`; the
  executable plan (six changes, ordering, open questions) is §4. Clinical
  definitions are provisional pending Dr. Bolo and Dr. Xu.

### Where this sits in the project

The `eye-ai-platform` repository is the project's front door. Per its layering:
schema/vocabulary **changes** are executed in **`data-curation`** (via its
*"Feature Registration Request"* template); the **`eye-ai-ml`** library reads and
writes these vocabularies (`compute_condition_label()` /
`insert_condition_label()`); **this document** is the clinical reference for what
the terms mean — it informs the `data-curation` requests, it does not perform them.

A guiding principle throughout: **define terms clinically, not by how the label
was produced.** A term's definition describes the eye, never the mechanism. The
same term is written by a human chart reviewer and by an automated ICD rule, and
must mean the same thing both ways — so "Moderate POAG" is one clinical concept
regardless of who or what produced it.

> **Note — two senses of "severity."** This document concerns `Severity_Label`
> (the clinical *stage* of disease). It is unrelated to
> `EyeAI.severity_analysis()` in `eye-ai-ml`, which computes *which eye is worse*
> (laterality) from RNFL/HVF/CDR and flags `Severity_Mismatch`. Never conflate the
> two.

## 2. Why — limitations of the current state

The cleanup is driven by concrete problems in today's vocabularies, grounded in
the actual catalog data (full inventory and usage counts in **Appendix A**):

1. **Two overlapping diagnosis vocabularies.** `Condition_Label` (fine
   chart-review subtypes) and `Glaucoma_Diagnosis` (coarse No/Suspected/Unknown,
   used at image/visit/subject levels) both describe glaucoma status and overlap
   at the subject level. A model's label and a clinician's label live in
   *different* vocabularies, so comparing them requires a cross-vocabulary mapping
   instead of a value comparison — the cost lands on the platform's central query.

2. **ICD codes are mis-stored in `Synonyms`.** The `Synonyms` field of `GS`,
   `POAG`, `PACG` holds ICD-10 code patterns (`H40.*`), not human-readable names —
   a machine lookup key masquerading as alternate names, and the key that
   `compute_condition_label()`'s hard-coded `icd_mapping` reverses. The terms have
   no proper external identifier.

3. **`Severity_Label` contains values that are really conditions, not stages.**
   `GS` and `Normal or No dx` duplicate `Condition_Label` members; the data proves
   it (698 `GS`/`GS` rows, 27 `Normal`/`Normal` rows where severity just echoes the
   condition). True severity only meaningfully applies to established glaucoma —
   grading a "suspect" or "normal" eye on a Mild/Moderate/Severe scale is a
   category error.

4. **`Unspecified/Indeterminate` packs two ideas into one label** ("indeterminate
   stage" vs "stage not recorded") via a slash, and is the dumping ground for any
   condition with no graded stage (≈900 rows).

5. **Severity descriptions are circular and carry no criteria.** "Mild stage",
   "Moderate stage", "Severe stage" restate the name — nothing a grader could
   apply reproducibly, and no record of *which staging system* produced a grade.

6. **`Normal or No dx` fuses two opposite states.** "Normal" (assessed, healthy)
   and "No diagnosis" (no determination made) are opposites in information content,
   welded into one term — you cannot tell screened-healthy from never-screened.

## 3. Proposed design

> **Provisional strawman** to be confirmed/revised with Dr. Bolo and Dr. Xu.

### 3.1 Two axes: diagnosis and severity, separate but conditional

- **Diagnosis** = which glaucoma, or none — `GS`, `POAG`, `PACG`,
  `Unspecified Glaucoma`, `Normal`, `Other`, `No Diagnosis`.
- **Severity** = stage of established glaucomatous disease —
  `Mild`/`Moderate`/`Severe` — **applicable only when a glaucomatous condition is
  present.**

Severity is a *further attribute of an established glaucoma diagnosis*, not an
independent label: you first have a diagnosis; severity refines it **only** when
that diagnosis is glaucoma (POAG/PACG, possibly `Unspecified Glaucoma`). This
answers **Professor Carl's question** — *is there such a thing as "mild glaucoma"?*
— with **separate but conditional**: "mild glaucoma" = diagnosis `POAG` (or `PACG`)
+ severity `Mild`; severity is not baked into the diagnosis term. Corollaries
(pending clinical confirmation): a suspect (`GS`) and a normal eye have no severity
(not-applicable).

**Future enforcement (to discuss).** The schema *could* enforce "severity requires
a glaucoma condition" (severity non-null only for glaucomatous diagnoses) via a
write-time constraint on the features — a `data-curation` change, noted here as
intent.

### 3.2 One shared diagnosis vocabulary: `Glaucoma_Diagnosis`

> **⚠️ Proposed change — pending clinical confirmation (Dr. Xu & Dr. Bolo).**
> This fold **reverses** an earlier team-noted position to keep the two
> vocabularies separate, so it needs **explicit sign-off before implementation.**
> In scope: merge the two diagnosis vocabularies into one. Unchanged / not in
> question: the ICD-11 grounding + cross-walk (§3.4), and severity as its own axis.

**Fold `Condition_Label` and the current `Glaucoma_Diagnosis` into one
vocabulary**, named **`Glaucoma_Diagnosis`**, referenced by the image / visit /
subject / chart tables alike. The driving requirement: **a model's "Glaucoma" and
a clinician's "Glaucoma" must be the *same* term**, so that model-vs-ground-truth
is a direct value comparison (`prediction == label`), not a cross-vocabulary
mapping. Storing the same concept in two vocabularies is denormalization of the
concept.

The distinction "a model asserted it" vs "a clinician asserted it" is **provenance
of the assertion** — carried by `Diagnosis_Tag` (`CNN_Prediction`,
`Expert_Consensus`, …), **not** by which vocabulary the value comes from.
Provenance is an attribute of the *assertion*, not of the *concept*.

The merged vocabulary keeps the name `Glaucoma_Diagnosis` (it *is* the glaucoma
diagnosis, and that name is already consumed at all three levels); the old 3-term
`Glaucoma_Diagnosis` is replaced by it and `Condition_Label`'s terms move into it.
**Full proposed table: Appendix B.1.**

### 3.3 Three axes: diagnosis, gradability, status

The current vocabularies conflate three independent questions. Separate them:

| Axis | Question | Home |
|---|---|---|
| **Diagnosis** | which glaucoma, or none? | **`Glaucoma_Diagnosis`** |
| **Gradability** | could the image be assessed? | gradability vocab / flag (`Gradable`, `Ungradable`) |
| **Status** | what is the review state? | `Diagnosis_Status` (`Graded`, `Validated`, `Rejected`) |

The distinctions that drive the placement:

- **`Normal` ≠ `No Diagnosis`.** The old `Normal or No dx` fused two opposites:
  `Normal` = assessed, no glaucoma (a real negative finding — ICD codes the
  encounter, `Z01.00`); `No Diagnosis` = no determination on record. **They split.**
- **`No Diagnosis` stays on the diagnosis axis, as a local term.** "No diagnosis"
  is a legitimate *value* of the diagnosis field (one column, ML-comparable). It
  has no ICD code, so it is a **local term** with an EyeAI URI — *"no ICD code"*
  means *"local term"*, not *"different axis."* Because it lives here,
  `Diagnosis_Status` does **not** also get a `Not assessed` value (that would
  duplicate the concept).
- **`Unknown` ≡ `No Diagnosis`** — the same concept ("no determination"). The old
  `Glaucoma_Diagnosis.Unknown` synonym `Ungradable` was a **mis-synonym** (it
  paired a status concept with an image-quality concept) and is dropped.
- **`Ungradable` is not a diagnosis** — "couldn't assess the image" is an
  image-quality fact → the **gradability** axis. (An image classifier that can
  abstain carries `Ungradable` as one of *its* output classes on the gradability
  axis — the one place image-model output and clinical diagnosis legitimately
  differ.)

### 3.4 ICD grounding and the cross-walk mechanism

**Each `Glaucoma_Diagnosis` term *is* an ICD-11 concept** — the ICD-11 code is the
term's **identity**, held in the vocabulary's standard `ID`/`URI` columns. This
gives one vocabulary reached two ways: a human chart reviewer picks the ICD-11
concept directly (ICD-11-native, not ICD-free), and legacy ICD-10 records are
translated *up* to the same concept. ICD-10 never stands alone as the identity.

**Curated subset, at the category level.** Ground the vocabulary in only the
glaucoma codes, at the category level (`H40.0`/`H40.1`/`H40.2`) — not the granular
per-eye/per-stage sub-codes. This keeps the ICD-10 ↔ ICD-11 crosswalk effectively
**1-to-1 and lossless** and the vocabulary small and auditable. (Of ~27,962
ICD-coded rows / 1,209 distinct codes, only the ~134 H40 glaucoma codes — at
category level just `H40.0/.1/.2` — matter here.)

**The canonical ICD-10 ↔ ICD-11 mapping:**

| `Glaucoma_Diagnosis` | ICD-10-CM category | ICD-11 (MMS) | ICD-11 title | Crosswalk |
|---|---|---|---|---|
| `GS` | `H40.0` (H40.00–.06) | **`9C60`** | Glaucoma suspect | Concept-equivalent, **structurally relocated** — ICD-11 makes suspect its own stem code `9C60`, a *sibling* of `9C61` Glaucoma (reinforces §3.1: a suspect is not staged disease). A few H40.0 sub-codes move under `9C61` (ocular hypertension → `9C61.01`; PAC suspect → `9C61.10`). |
| `POAG` | `H40.1` (H40.10–.15) | **`9C61.0`** | Primary open-angle glaucoma | Equivalent, 1-to-1 |
| `PACG` | `H40.2` | **`9C61.1`** | Primary angle closure / angle closure glaucoma | Equivalent, 1-to-1 |
| `Unspecified Glaucoma` | `H40.9` | **`9C61.Z`** | Glaucoma, unspecified | Equivalent |
| `Normal` | — (no glaucoma code) | *(TBD, §5)* | — | Absence of disease; grounded via encounter code `Z01.00` or a local URI |
| `Other` | — (non-glaucoma) | — | — | Catch-all outside the curated glaucoma subset |
| `No Diagnosis` | — | — | — | No determination on record; local (EyeAI) URI |

> The secondary/developmental ICD-11 subtypes (`9C61.2` secondary OAG, `9C61.3`
> secondary ACG, `9C61.4` developmental) have **no dedicated member** and fall into
> `Other` until added — a clinical decision (§5). ICD-11 codes **verified
> 2026-06-30** against the WHO ICD-11 MMS; the URI *scheme* is settled but exact
> per-term IRIs and the release-version pin are §4/§5 open items.

**How codes are stored — standard vocabulary shape only.** A Deriva controlled
vocabulary has a fixed schema (`RID`, `Name`, `Description`, `Synonyms`, `ID`,
`URI`). **No custom columns are added.** So:

- **ICD-11 → `ID`/`URI`** — the term's one canonical external identity (WHO
  publishes ICD-11 as linked data with official URIs; ICD-10-CM has no single
  official URI scheme, and ICD-11 is forward-looking).
- **ICD-10 → the `ICD10_Condition_Map` cross-walk table**, *not* a column. One
  condition maps from *many* ICD-10 codes (`H40.00`–`H40.06` → `GS`); a
  many-to-one external relation attaches through an association table.
- **`Synonyms` stays human-only** — the `H40.*` patterns move out to the
  cross-walk; lookup **by code** uses `ID`/`URI`, **by name** uses `Synonyms`.
- **Grounded-vs-local** is the **URI namespace** (`id.who.int/…` = ICD-11 authority;
  `eye-ai.org/…` = EyeAI-local), never a null test. Local terms (`Other`,
  `No Diagnosis`, possibly `Normal`) get EyeAI-routed resolvable URIs.

**The cross-walk turns `compute_condition_label` into a join.** Its input is the
`Clinical_Records_ICD10_Eye` association table already in the catalog (confirmed
via deriva MCP 2026-06-30 — 27,962 rows). Two bridges represent all the codes as
data: `Clinical_Records_ICD10_Eye` (observed data: which codes a record carries)
and `ICD10_Condition_Map` (the classification rule: what a code means). With both,
the code→condition step is a pure join —
`Clinical_Records ─ ICD10_Eye ─ ICD10_Condition_Map ─ Glaucoma_Diagnosis` — and the
Python dict disappears.

**What this retires in `eye-ai-ml`** (verified against `eye_ai.py:268`).
`compute_condition_label()` does two things: (1) ICD-10 → condition mapping via an
inline `icd_mapping` dict — **the cross-walk table replaces this** (delete the
dict, read from the table); (2) multi-code priority resolution
(`PACG>POAG>GS>Other` tie-break) — **not** replaced (a per-record reconciliation
policy that still needs a home). So the dict is no longer needed; the function
shrinks to the priority step. `insert_condition_label()` is unaffected. Retiring
the dict is an `eye-ai-ml` change, contingent on `ICD10_Condition_Map` existing
first (§4). Map **exact codes** (FKs to real `ICD10_Eye` terms), not wildcard
patterns, so no wildcard-matching logic is needed.

![ERD — the Chart_Label feature carries the diagnosis and severity axes side by side; the diagnosis term is the ICD-11 concept (chart review picks it directly, legacy ICD-10 cross-walks up), and severity is valid only when the diagnosis is glaucoma.](img/icd11-condition-erd.png)

*Figure 1 — the full Chart_Label model: the two axes (§3.1), the ICD-11 grounding
(§3.4), and the ICD-10→ICD-11 cross-walk. The figure uses the current name
`Condition_Label`; under the fold read it as the folded `Glaucoma_Diagnosis`.
Source: [`img/icd11-condition-erd.svg`](img/icd11-condition-erd.svg).*

### 3.5 Severity cleanup

- **Keep `Mild`/`Moderate`/`Severe`**, add real clinical criteria (VF MD / RNFL /
  CDR thresholds — **TBD — clinical**); today's descriptions are circular.
- **Split & rename `Unspecified/Indeterminate`** → `Not Staged` ("glaucoma present,
  stage not recorded") vs an optional `Indeterminate` ("stage genuinely
  indeterminate"); removes the slash.
- **Retire `GS` and `Normal or No dx` from severity** — they are diagnoses, not
  stages; represent them via `Glaucoma_Diagnosis`. Retiring them requires
  re-mapping existing `Chart_Label` rows so the condition is preserved and severity
  becomes not-applicable/not-staged (data migration — §4 change 4; counts in
  Appendix A).

The stage set `Mild`/`Moderate`/`Severe`/`Indeterminate` mirrors the ICD-10
7th-character glaucoma staging convention, so severity aligns with how stage is
already coded in the source data. **Full proposed table: Appendix B.2.**

### 3.6 Severity method of determination — the `(Severity, Method)` pair

`Mild`/`Moderate`/`Severe` are ambiguous without a named **basis** — the same
grade means different things under different staging systems, and two systems must
never be silently mixed in one column. Resolution: **record the method of
determination as a first-class value alongside the grade**, so each severity is
the pair **`(Severity_Label, Severity_Method)`**.

Method is a *semantic property of the severity value* — "this `Mild` was determined
by HPA staging" — not a fact about which code ran, and not part of the grade. So:

- It is **not** encoded into the severity term (`HPA_Mild`, …) — that repeats the
  pack-two-axes-into-one-label anti-pattern this cleanup removes elsewhere, and
  destroys the clean three-value scale.
- It is **not** left implicit in the producing `Workflow`/`Execution` — method
  varies **per row** (a grader may use HPA on one subject, another system on the
  next), applies to human chart-review values that have no workflow, and would
  otherwise need a provenance walk to read. Provenance (which code ran) and method
  (which clinical basis) are complementary and both kept.

**Where the method is recorded.** Severity lives **only in features**, never as a
raw column (confirmed from the live catalog — `Clinical_Records` has no severity
column, only the raw measurements `IOP`/`CDR`/`CCT`/… that *feed* severity). So
`Severity_Method` is added as a **feature column beside the severity column**, on
each severity-bearing feature:

| Feature (target) | Severity column | New method column |
|---|---|---|
| `Execution_Subject_Chart_Label` (Chart_Label on Subject) | `Severity_Label` | `Severity_Method` |
| `Execution_Clinical_Records_Glaucoma_Severity` (ICD-derived) | `ICD_Severity_Label` | `ICD_Severity_Method` |

Each goes in as part of the feature definition (features are multi-column), so the
method inherits the feature machinery — including the provenance link to the
producing Execution. The method column is **NOT-NULL whenever the severity is a
graded value**; not-applicable for the `Not Staged` / `Indeterminate` sentinels.
**Full proposed `Severity_Method` vocabulary: Appendix B.3.**

### 3.7 GAMMA / GLEAM band mapping (open)

Dr. Kyle's **GAMMA** mapping needs a **"Moderate-to-Severe"** band (GAMMA's
"Progressive" category maps to it, per Dr. Bolo). Open question: does a
`Moderate-to-Severe` band become an additional `Severity_Label` member, or should
cross-dataset band collapses (GAMMA/GLEAM) be a **mapping layer** on top of
canonical `Mild`/`Moderate`/`Severe` rather than new vocabulary terms? Flagged so
the cleanup doesn't lock GAMMA/GLEAM out (§5 Q6).

## 4. Change plan

The actionable synthesis of §3. **Dependency ordering and repo split matter** —
executing these in the wrong order leaves half-built states.

### 4.1 The changes

| # | Change | What it entails | Where |
|---|---|---|---|
| **1** | **Clean up `Severity_Label`** | Retire `GS` and `Normal or No dx` (conditions, not stages); split `Unspecified/Indeterminate` → `Not Staged` vs `Indeterminate`; add real clinical criteria to Mild/Moderate/Severe. (§3.5, App. B.2) | `data-curation` |
| **2** | **Fold into one `Glaucoma_Diagnosis` vocabulary** | Merge `Condition_Label` + the current 3-term image/visit/subject `Glaucoma_Diagnosis` into one shared vocab named **`Glaucoma_Diagnosis`** (§3.2). Terms + identities per App. B.1: ICD-11 `ID`/`URI` for `GS/POAG/PACG/Unspecified Glaucoma`; split `Normal or No dx` → `Normal` + `No Diagnosis`; `Other`, `No Diagnosis` as EyeAI-local; `H40.*` out of `Synonyms`. Separate `Ungradable` (gradability axis) and drop the `Unknown`↔`Ungradable` mis-synonym. | `data-curation` |
| **3** | **Create the ICD-10 cross-walk table** | New association table `ICD10_Eye → Glaucoma_Diagnosis` (`ICD10_Condition_Map`), **exact codes** (not wildcards). Prereq: `ICD10_Eye` must enumerate every ICD-10 code the data uses. (§3.4) | `data-curation` |
| **4** | **Migrate diagnosis data onto the folded vocab** | Repoint the `Chart_Label` feature rows and the image/visit/subject `*_Diagnosis` rows to the merged `Glaucoma_Diagnosis` terms; re-map cleaned severity values (counts in App. A). **Data migration**, distinct from the schema/vocab changes 1–3. | `data-curation` |
| **5** | **Update `compute_condition_label`** | Replace the `icd_mapping` dict with a **join through the cross-walk**; **keep** the multi-code priority tie-break (do not re-add). `insert_condition_label` unaffected. (§3.4) | `eye-ai-ml` |
| **6** | **Add severity method of determination** | Create the `Severity_Method` vocabulary (App. B.3), then add a method column to each severity-bearing feature — `Severity_Method` on `Execution_Subject_Chart_Label` and `ICD_Severity_Method` on `Execution_Clinical_Records_Glaucoma_Severity` — NOT-NULL when severity is graded. Records severity as the `(Severity_Label, Severity_Method)` pair. (§3.6) | `data-curation` |

### 4.2 Dependency ordering

```
ICD10_Eye enumerated ──▶ (2) fold into Glaucoma_Diagnosis ──┐
                     └──▶ (3) create cross-walk table ───────┴─▶ (5) update code ──▶ (4) migrate diagnosis data
(1) Severity cleanup ──┐
(6) Severity_Method ───┴─ severity axis; independent of the diagnosis fold, can run in parallel
```

- The cross-walk (3) needs both endpoints ready: the folded `Glaucoma_Diagnosis` (2) **and** `ICD10_Eye` populated with exact codes.
- The code change (5) needs the cross-walk (3) to exist.
- The data migration (4) needs the folded vocabulary (2) and the cleaned severity (1).
- Severity work (1) and the method vocab/columns (6) are on the severity axis, independent of the diagnosis fold; (6) needs the `Severity_Method` member set confirmed (§5) and the severity features (they exist).
- **Repo split:** 1–4 and 6 are catalog/schema/data → `data-curation`; 5 is code → `eye-ai-ml`, and its PR **cannot merge until 3 lands** in the catalog.

### 4.3 Gates (resolve before the clinical parts land)

- **Severity criteria** for Mild/Moderate/Severe — clinical (Dr. Bolo, §5 Q1).
- **`Severity_Method` member set** — confirm the staging systems (HPA, ICD 7th-char, structural, …) before creating the vocabulary in change 6 (§3.6, clinical).
- **`9C61.2/.3/.4` disposition** — become `Glaucoma_Diagnosis` members or fold into `Other`? Affects change 2 and the priority ordering in change 5 (§3.4, §5).
- **`Normal`'s identifier** — ICD-Z encounter code (`Z01.00`) vs an EyeAI-local URI (Appendix B.1 note).
- **EyeAI URI scheme** for local terms (`Other`, `No Diagnosis`, maybe `Normal`).
- **GAMMA `Moderate-to-Severe` band** (§3.7) — may add a `Severity_Label` member in change 1.
- **ICD-11 release-version pin** — pin a specific ICD-11 release in the term URIs (e.g. `…/release/11/2025-01/mms/…`) rather than the bare `{version}` placeholder; confirm the current WHO release at implementation time and record it (keep the release-independent foundation `…/icd/entity/{id}` URI as the stable anchor).
- **Catalog verification** — ✅ **resolved (deriva MCP, 2026-06-30):** `ICD10_Eye` **is** a controlled vocabulary (1,209 terms); the `Clinical_Records ⇄ ICD10_Eye` association is **`Clinical_Records_ICD10_Eye`** (27,962 rows); `Clinical_Records` has **no** severity column (so severity-method is a feature column only).
- **Fold verification (open)** — before the fold (change 2/4), confirm what populates `Subject_Diagnosis` vs the `Chart_Label` feature and how the image/visit/subject `*_Diagnosis` rows reconcile with the chart rows onto the merged vocabulary.

## 5. Open clinical questions (for the Dr. Bolo & Dr. Xu meeting)

1. **Severity criteria.** What clinical criteria define `Mild`/`Moderate`/`Severe`? HPA staging? VF MD thresholds? Structural (RNFL/CDR)? A combination? (Dr. Bolo.)
2. **Separate but conditional?** Confirm severity is a separate attribute that applies **only** when an established glaucoma condition is present (§3.1).
3. **`Severity_Method` member set.** Confirm the staging systems to enumerate (HPA, ICD 7th-char, structural, …) — the method design is settled (§3.6); the member list is the clinical input.
4. **Fold sign-off.** Approve (or reject) merging `Condition_Label` + `Glaucoma_Diagnosis` into one vocabulary (§3.2) — this reverses the earlier keep-separate position.
5. **Remove non-stage values?** Confirm retiring `GS` and `Normal or No dx` from `Severity_Label`.
6. **Suspects and severity.** Does a glaucoma suspect (`GS`) have a severity at all? (Strawman: no — not applicable.)
7. **`9C61.2/.3/.4` disposition.** Add secondary/developmental glaucoma as `Glaucoma_Diagnosis` members, or leave them in `Other`?
8. **GLEAM / GAMMA.** What must the cleaned-up vocabulary provide so the GLEAM/GAMMA mappings land cleanly — notably GAMMA's `Moderate-to-Severe` band (§3.7) — without distorting the canonical definitions?

---

## Appendix A — Current state (as in the catalog, 2026-06-30)

Snapshot from `www.eye-ai.org` / `eye-ai`. Descriptions and synonyms are
reproduced **verbatim**; commentary is set off as notes. These are the **pre-fold**
vocabularies; the proposed replacements are in Appendix B.

### A.1 `Condition_Label` — 6 terms

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

> **Note.** The `Synonyms` of `GS`/`POAG`/`PACG` store ICD-10 code patterns
> (`H40.*`), not names — the key `compute_condition_label()`'s `icd_mapping`
> reverses (`H40.0x → GS`, `H40.1x → POAG`, `H40.2* → PACG`, else `Other`). §2
> item 2 / §3.4 address this.

### A.2 `Severity_Label` — 6 terms

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

> **Note.** Three of these six are not stages: `GS` and `Normal or No dx` are
> conditions (duplicating `Condition_Label`), and `Unspecified/Indeterminate` packs
> a synonym into a slash. Only `Mild`/`Moderate`/`Severe` are genuine grades (§2
> items 3–4).

### A.3 `Glaucoma_Diagnosis` — 3 terms (image/visit/subject diagnostic vocabulary)

Created 2026-06-30 as the single consolidated vocabulary the three diagnosis levels
(image / observation / subject) share. **Not image-only**, despite the catalog
comment.

> Catalog comment: *"Vocabulary of image-level diagnostic categories for retinal
> images (e.g., referable glaucoma, no glaucoma)."*

| RID | Name | Description (verbatim) | Synonyms (verbatim) |
|---|---|---|---|
| `6-0EQR` | **No Glaucoma** | No Glaucoma | No Referable Glaucoma |
| `6-0EQP` | **Suspected Glaucoma** | Suspected Glaucoma | Referable Glaucoma |
| `6-0EQM` | **Unknown** | Unknown | Ungradable |

**Consumed by** (all FK to `Glaucoma_Diagnosis.Name`, all populated):

| Table | Rows | Level |
|---|---|---|
| `Image_Diagnosis` | 194,204 | image-level (per fundus image) |
| `Observation_Diagnosis` | 7,020 | observation / visit-level |
| `Subject_Diagnosis` | 7,020 | subject-level |

All 194,204 `Image_Diagnosis` rows resolve to exactly three terms — **No Glaucoma**
155,279, **Suspected Glaucoma** 38,547, **Unknown** 378 (sum = 194,204).

### A.4 Supporting vocabularies (distinct from diagnosis — do not conflate)

Provenance / status / context of a diagnosis, not the diagnosis itself:

- **`Diagnosis_Tag`** (11 terms) — provenance / study tags (`Initial Diagnosis`,
  `CNN_Prediction`, `Expert_Consensus`, `Intragrader_Agreement`,
  `GlaucomaSuspect-Training`/`-Validation`, `UI Annotation`, …). "Who/what produced
  this label, in what study?" — the provenance carrier the fold (§3.2) relies on.
- **`Diagnosis_Status`** (3 terms) — `Graded`, `Validated`, `Rejected`. "Review
  state of this diagnosis?" — the status axis (§3.3).
- **`ICD10_Eye`** — vocabulary of ICD-10 ophthalmic codes (1,209 terms); the source
  feeding ICD-derived labels; source side of the cross-walk (§3.4).
- **`Grading_Condition`** — **empty (0 terms)**. Intended to record USC vs LAC
  grading context on the shared `Chart_Label` feature; a context axis the cleaned
  model may need to populate.

### A.5 How the terms are used today (the evidence)

The clinical chart-review label lives in the **`Chart_Label` feature on Subject**
(`Execution_Subject_Chart_Label`, **2,302 rows**), carrying `Condition_Label`
**and** `Severity_Label` as two columns on the same row. Distinct
`(Condition_Label, Severity_Label)` pairs present:

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

Read off the data: genuine severity grades (Mild/Moderate/Severe) appear only on
POAG (648 rows) and PACG (45 rows) — established glaucoma; everything else is
`Unspecified/Indeterminate` or a condition-as-severity sentinel (698 `GS`/`GS`, 27
`Normal`/`Normal`). ICD-derived severity stands alone in
`Execution_Clinical_Records_Glaucoma_Severity` (**3,674 rows**;
`ICD_Severity_Label`), whose target `Clinical_Records` carries the condition
separately in `Clinical_Records.ICD_Condition_Label`.

## Appendix B — Proposed vocabulary tables (full)

> **Provisional.** Descriptions marked **(confirm clinically)** need Dr. Bolo /
> Dr. Xu sign-off; severity staging *thresholds* are **TBD — clinical**. Standard
> Deriva vocabulary shape only (`RID`, `Name`, `Description`, `Synonyms`, `ID`,
> `URI` + system columns) — no custom columns. Grounded-vs-local is the URI
> namespace (`id.who.int/…` = ICD-11; `eye-ai.org/…` = EyeAI-local).

### B.1 `Glaucoma_Diagnosis` (folded diagnosis vocabulary)

The single source of truth for the proposed diagnosis terms. `ID`/`URI` is the
identity (lookup by code); `Synonyms` are human-readable names (lookup by name).
ICD-10 codes are **not** in these rows — they live in the `ICD10_Condition_Map`
cross-walk (§3.4). Full ICD-11 URIs follow
`http://id.who.int/icd/release/11/{version}/mms/{code}` (abbreviated below).

| Name | Description | Synonyms (human-readable) | `ID` / `URI` |
|---|---|---|---|
| `GS` | Glaucoma suspect — findings suspicious for glaucoma (ocular hypertension / elevated IOP, suspicious optic disc or RNFL, narrow/occludable angle, or steroid response) **without** established glaucomatous damage. *(confirm clinically)* | "Glaucoma Suspect"; WHO `9C60` index terms (e.g. "Borderline glaucoma", "Ocular hypertension") | `ICD11:9C60` / `…/mms/9C60` |
| `POAG` | Primary open-angle glaucoma — chronic glaucomatous optic neuropathy with an **open** angle, no secondary cause. *(confirm clinically)* | "Primary Open-Angle Glaucoma" | `ICD11:9C61.0` / `…/mms/9C61.0` |
| `PACG` | Primary angle-closure glaucoma — glaucoma with appositional/synechial **closure** of the angle. *(confirm clinically)* | "Primary Angle-Closure Glaucoma" | `ICD11:9C61.1` / `…/mms/9C61.1` |
| `Unspecified Glaucoma` | Glaucoma present, **subtype not specified**. *(confirm clinically)* | "Glaucoma, unspecified"; "Glaucoma NOS" | `ICD11:9C61.Z` / `…/mms/9C61.Z` |
| `Normal` | Assessed; **no glaucoma** present (a genuine negative finding). *(confirm clinically)* | "No Glaucoma"; "Normal" | `ICD10:Z01.00` *or* `EYEAI:Normal` **(TBD)** |
| `Other` | A **non-glaucoma** condition (outside the curated glaucoma subset). | "Non-glaucoma"; "Other condition" | `EYEAI:Other` / `eye-ai.org/id/condition/Other` |
| `No Diagnosis` | **No diagnosis made** — no glaucoma determination on record (≡ the former `Unknown`). *(confirm whether "not assessed" needs its own wording)* | "No dx"; "Not assessed" | `EYEAI:No_Diagnosis` / `eye-ai.org/id/condition/No_Diagnosis` |

- **`Ungradable` and `Not assessed` are deliberately absent** — gradability axis and (former) status idea respectively; the latter is covered by `No Diagnosis`.
- **`Normal`'s identifier** is an open item: `Z01.00` is a *reason-for-visit* encounter code, not a disease code, so ICD-Z-vs-local is a genuine sub-choice (§4.3).

### B.2 `Severity_Label` (cleaned)

Applies **only to established glaucoma** (§3.1). `GS` and `Normal or No dx` are
retired (they are diagnoses, not stages — Appendix A.2, §3.5). Staging *thresholds*
are **TBD — clinical**.

| Term | Proposed description | Proposed synonyms |
|---|---|---|
| `Mild` | Mild-stage glaucomatous damage. **Criteria TBD — clinical** (e.g. VF MD / RNFL / CDR). | "Early" |
| `Moderate` | Moderate-stage glaucomatous damage. **Criteria TBD — clinical**. | — |
| `Severe` | Severe / advanced-stage glaucomatous damage. **Criteria TBD — clinical**. | "Advanced" |
| `Not Staged` (+ optional `Indeterminate`) | Separate *"glaucoma present, stage **not recorded**"* from *"stage genuinely **indeterminate**"*; replaces `Unspecified/Indeterminate` (removes the slash). | "Stage unspecified"; "Indeterminate stage" |

### B.3 `Severity_Method` (new — the staging basis)

New domain vocabulary; recorded per-row as a feature column beside the severity
value (§3.6). Local vocabulary → EyeAI-routed URIs. Member set is **TBD — clinical**
(at minimum `HPA` and `ICD_7th_char`, the two populated severity sources today).

| Name | Description | `ID` / `URI` |
|---|---|---|
| `HPA` | Hodapp-Parrish-Anderson visual-field staging (VF mean-deviation thresholds + defect location/depth). | `EYEAI:HPA` / `eye-ai.org/id/severity-method/HPA` |
| `ICD_7th_char` | Stage taken from the ICD-10 7th-character glaucoma-stage code (mild / moderate / severe / indeterminate). | `EYEAI:ICD_7th_char` / `…/severity-method/ICD_7th_char` |
| `Structural` | Stage from structural criteria (RNFL thickness / CDR) rather than VF. *(confirm clinically)* | `EYEAI:Structural` / `…/severity-method/Structural` |
| `Clinician_Global` | Clinician's overall global staging judgment, basis not otherwise specified. *(confirm clinically)* | `EYEAI:Clinician_Global` / `…/severity-method/Clinician_Global` |

## Appendix C — References / provenance

- Consolidates the read-only investigation from the 2026-06-30 review of the
  diagnosis/condition/severity landscape.
- **Catalog objects referenced** (schema `eye-ai`): vocabularies `Condition_Label`,
  `Severity_Label`, `Glaucoma_Diagnosis`, `Diagnosis_Tag`, `Diagnosis_Status`,
  `ICD10_Eye`, `Grading_Condition`; feature/association tables
  `Execution_Subject_Chart_Label` (Chart_Label on Subject),
  `Execution_Clinical_Records_Glaucoma_Severity` (Glaucoma_Severity on
  Clinical_Records), `Clinical_Records`, `Clinical_Records_ICD10_Eye`,
  `Image_Diagnosis`, `Observation_Diagnosis`, `Subject_Diagnosis`.
- **Proposed new objects (not yet in catalog)**:
  - `ICD10_Condition_Map` — association table cross-walking legacy ICD-10 → the
    ICD-11 concept (`ICD10_Eye → Glaucoma_Diagnosis`, §3.4); data-driven
    replacement for the hard-coded `icd_mapping` in `compute_condition_label()`.
  - `Severity_Method` — domain vocabulary of severity staging systems (App. B.3),
    referenced by a method column on each severity-bearing feature (§3.6).
- **Library code referenced** (`eye-ai-ml/eye_ai/eye_ai.py`):
  `compute_condition_label()`, `insert_condition_label()`, `severity_analysis()`
  (laterality — see the §1 note).
- **Clinical & coding references:**
  - AAO *Glaucoma ICD-10 Quick Reference Guide* — primary clinical reference for
    the H40 glaucoma codes:
    <https://www.aao.org/Assets/5adb14a6-7e5d-42ea-af51-3db772c4b0c2/636713219263270000/bc-2568-update-icd-10-quick-reference-guides-glaucoma-final-v2-color-pdf?inline=1>
  - icd10data.com — ICD-10-CM H40 glaucoma codes:
    <https://www.icd10data.com/ICD10CM/Codes/H00-H59/H40-H42/H40->
  - WHO **ICD-11 (MMS)** — authoritative ICD-11 glaucoma codes and canonical URIs:
    glaucoma block `9C61`, glaucoma suspect `9C60`; <https://icd.who.int/browse11>.
- **Process note — no catalog edits from this document.** Any term rename,
  removal, description change, or new term (§3–§4) is a catalog change requested
  through **`data-curation`** via its *"Feature Registration Request"* template.
  This document is the clinical rationale such requests cite; it does not mutate
  the catalog.

---

*Draft for review. All clinical definitions provisional pending Dr. Bolo and
Dr. Xu. Counts and term contents reflect the catalog state on 2026-06-30.*
