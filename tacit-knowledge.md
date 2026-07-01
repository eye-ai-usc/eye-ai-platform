# Tacit Knowledge — eye-ai-platform

Running journal of the *why* behind decisions. Pairs with the up-front design
docs in `docs/design/`; this file is the after-the-fact rationale.

---

## 2026-06-30 — Consolidated change plan (diagnosis/condition/severity cleanup)

The actionable synthesis of the whole ICD-11 design session. Ordering and repo
split matter — see below.

**The changes:**
1. **Clean up `Severity_Label`** — retire `GS` + `Normal or No dx` (conditions,
   not stages), split `Unspecified/Indeterminate` → `Not Staged` vs
   `Indeterminate`, add real clinical criteria to Mild/Moderate/Severe
   (TBD-clinical). *Independent of 2–5, can run in parallel.*
2. **Re-anchor `Condition_Label` on ICD-11** (NOT "create" — table exists, §2.1):
   add ICD-11 `ID`/`URI` to each term (`GS=9C60`, `POAG=9C61.0`, `PACG=9C61.1`,
   `Unspecified=9C61.Z`), remove `H40.*` from `Synonyms`, put WHO index terms in
   `Synonyms`, reconcile member set to ICD-11 (decide `9C61.2/.3/.4`).
3. **Create `ICD10_Condition_Map`** (`ICD10_Eye → Condition_Label`, exact codes).
   Prereq: `ICD10_Eye` must enumerate every code the data uses.
4. **Migrate `Chart_Label` data** (`Execution_Subject_Chart_Label`) — re-map rows
   to cleaned severity + condition values (counts in doc §6.1). This is DATA
   migration, distinct from schema/vocab changes 1–3.
5. **Update `compute_condition_label`** (`eye-ai-ml`) — replace `icd_mapping`
   dict with the JOIN (step 1 → the map); KEEP the priority tie-break (step 2 —
   it already exists, don't re-add). `insert_condition_label` unaffected.

**Dependency ordering (getting it wrong = half-built states):**
`ICD10_Eye enumerated → (2)+(3) → (5) → (4)`; (1) parallel. The map (3) needs
both endpoints ready; the code (5) needs the map (3); the migration (4) needs the
cleaned vocabularies (1,2).

**Repo split:** 1,2,3,4 = catalog/schema/data → `data-curation` (Feature
Registration Request). 5 = code → `eye-ai-ml`, contingent on 3 landing first (its
PR can't merge until the catalog side exists).

**Open clinical/verification gates:** severity criteria (Bolo, §7 Q1); whether
`9C61.2/.3/.4` are members or fold into `Other` (affects 2 + the priority list);
GAMMA `Moderate-to-Severe` band (§6.4, may add a severity member in step 1);
verify `ICD10_Eye` is a vocab + name the `Clinical_Records ⇄ ICD10_Eye` table
(deriva MCP not connected this session).

---

## 2026-06-30 — What the ICD10_Condition_Map retires in eye-ai-ml (code-verified)

**Verified against `eye-ai-ml/eye_ai/eye_ai.py` (not the doc's secondhand
description).** `EyeAI.compute_condition_label()` (`eye_ai.py:268`) does TWO
things, and the cross-walk table only replaces one:

1. **ICD-10→condition mapping** — an inline `icd_mapping` dict (`H40.0x→GS`,
   `H40.1x→POAG`, `H40.2*→PACG`, else `Other`) applied by `startswith` prefix
   match. **This is what `ICD10_Condition_Map` replaces.** Delete the dict, read
   the mapping from the table. It is the ONLY copy in the library (one site +
   `test_eye_ai_units.py:139`; no duplicates).
2. **Multi-code priority resolution** — when one `Clinical_Records` has several
   ICD codes, keep the highest-priority condition (`PACG>POAG>GS>Other`) via
   priority sort + `drop_duplicates`. **NOT replaced by the table** — it's a
   per-record reconciliation policy that still needs a home.

**Why this matters / the catch:** the naive claim "the mapping function is no
longer needed" is only *half* right. The `icd_mapping` **dict** is obsolete once
the table exists; the **priority-dedup logic is not** and would be silently lost
if the whole function were deleted. `insert_condition_label()` (`eye_ai.py:302`)
is unaffected (just writes to `Clinical_Records`). Doc note added to §5.6. Also
corrected a doc inaccuracy: code uses `H40.2*` (prefix), not `H40.2`. Retiring
the dict is an `eye-ai-ml` change, contingent on the table existing first.

**The map IS step 1 of compute_condition_label, as a join.** Confirmed framing:
the table replaces the ENTIRE first step (code→condition) — join
`Clinical_Records⇄ICD10_Eye` (record's codes) ⋈ `ICD10_Condition_Map`
(code→ICD-11 concept) = every code labeled with its Condition_Label. No dict, no
`startswith`, no `map_icd_to_category`. Only step 2 (collapse to one per record
by priority `PACG>POAG>GS>Other`) remains, and even that can become data (priority
column on Condition_Label + sort). CAVEAT that makes the join valid: the map must
enumerate EXACT codes as `ICD10_Eye` rows (`H40.10…H40.15` each → POAG), so the
join is equality — NOT prefix/wildcard like today's `startswith` on `H40.1*`. If
`ICD10_Eye` doesn't already enumerate every code the data uses, populating it is a
prerequisite. (This is the concrete "what the table buys": step 1 goes from
hard-coded Python to catalog data.)

**End-to-end resolution: many ICD-10 codes → ONE ICD-11 Condition_Label.** A
`Clinical_Records` carries several ICD-10 codes. The function does NOT "pick one
code" — it maps EVERY code to its ICD-11 concept, then picks the highest-priority
CONCEPT by clinical severity `PACG>POAG>GS>Other` (`eye_ai.py:295`). Ex: record
with `H40.11`+`H40.00` → candidates {POAG=9C61.0, GS=9C60} → POAG wins → stored
`Condition_Label = POAG (ICD-11 9C61.0)`. Under the new structure the stored
label IS an ICD-11 concept (codes = input, winning ICD-11 term = output).
Consequence: the priority tie-break now orders ICD-11 *concepts* (belongs on
Condition_Label, could be a priority column); adding `9C61.2/.3/.4` as members
means slotting them into that ordering (clinical, §7).

**"The ICD-10 source is already in the catalog — why link it to the ICD-11
term?"** (Recurring challenge.) Because *presence ≠ meaning*. The data bridge
(`Clinical_Records ⇄ ICD10_Eye`) tells you WHICH codes a record carries; it does
NOT tell you what they mean. Nothing in it connects `H40.11` → `POAG`. The whole
system's output is the *condition*, and computing it requires the code→concept
lookup — that IS the knowledge bridge (`ICD10_Condition_Map`) / the hard-coded
dict it replaces. Analogy: a list of ZIP codes present in a table doesn't tell
you which city each belongs to. The only case you could "skip" it: if
`Clinical_Records.ICD_Condition_Label` is already populated — but that column was
itself produced by running the mapping once; it's a cached result that goes stale
on any new record or re-derivation (corrected mapping, ICD-11 added), and
skipping the bridge leaves the mapping trapped in Python (the dict we're
removing). So the link is what makes the mapping *data not code* and
*reproducible not a one-time cached run*. Do not drop it on "the source is
already there" grounds.

**Input source = a catalog bridge → the mapping becomes a join (TWO bridges).**
`compute_condition_label()`'s input is a DataFrame `RID, Clinical_Records,
ICD10_Eye` (verified: `eye_ai.py:293` + fixture `test_eye_ai_units.py:131`) —
i.e. a read of a **`Clinical_Records ⇄ ICD10_Eye` association table** already in
the catalog. So the full ICD side is representable as two DISTINCT bridges:
(1) `Clinical_Records ⇄ ICD10_Eye` = *observed data* (which codes a record
carries) — already exists; (2) `ICD10_Condition_Map` (`ICD10_Eye ⇄
Condition_Label`) = *classification rule* (what a code means) — proposed. With
both, the mapping step is a pure JOIN
(`Clinical_Records─ICD10_Eye─Condition_Label`); the inline dict vanishes; only
the priority tie-break remains (and could become a priority column on
Condition_Label). Keep the two bridges separate — one records facts, the other
records the rule; they evolve on different schedules. UNVERIFIED: exact name of
the `Clinical_Records ⇄ ICD10_Eye` table (notebook that builds the input not
in-repo; deriva MCP not connected) — existence implied by column shape +
confirmed endpoints; name is a catalog-verification TODO.

---

## 2026-06-30 — REVISION: Condition_Label IS the ICD-11 concept (supersedes Option A)

**Decision (Prof. Carl):** A `Condition_Label` term **is** an ICD-11 concept, not
a local label that ICD-11 merely identifies. `GS` = display name for ICD-11
`9C60`; `POAG=9C61.0`; `PACG=9C61.1`; `Unspecified Glaucoma=9C61.Z`. The ICD-11
code is the term's identity (`ID`/`URI`). **This supersedes the earlier "Option A
/ ICD-11 identifies a local term" framing** in the entry below — it is the strong
form (formerly "Option B"): ICD-11's taxonomy *drives* the vocabulary.

**Consequences for the data model:**
- **One vocabulary (ICD-11 concepts) reached two ways**, not two label kinds
  sharing a vocab. Chart review picks the ICD-11 term **directly** (ICD-11-native
  — NOT "ICD-free"; my earlier ERD calling the chart path "no ICD" was wrong).
  Legacy ICD-10 records **cross-walk up** to the same ICD-11 term.
- The map (`ICD10_Condition_Map`) is now precisely an **ICD-10 → ICD-11
  cross-walk**, not an "ICD → local-label" mapper. Still needed (legacy records
  carry ICD-10; vocab is ICD-11), still upstream of Condition_Label, still the
  data-driven replacement for `compute_condition_label()`.
- ICD-10's finer suspect codes (`H40.00`–`H40.06`) **collapse** into the single
  ICD-11 suspect `9C60` on the way up — correct, because ICD-11 collapses them.

**Synonym question — answered.** Q: "do the codes appear as synonyms in the
ICD-11 table, for semantic lookup by code?" A: **No — lookup by code is `ID`'s
job, not `Synonyms`.** Each ICD-11 term's code IS its `ID`/`URI`, so
`lookup_by_id("ICD11:9C60") → term` is a typed, indexed, one-hop by-code lookup
needing NO duplication into `Synonyms`. `Synonyms` carry the WHO index/
subcategory terms (human names: "borderline glaucoma", "ocular hypertension",
"narrow angle glaucoma suspect", …) → semantic lookup BY NAME. Putting the code
into its own row's `Synonyms` just duplicates `ID` and reintroduces the
code-vs-name ambiguity. (A code only belongs in `Synonyms` as a *secondary/
deprecated alias code*; the primary code is always `ID`.) One `resolve(token)`
view can offer both: by-code via `ID`, by-name via `Synonyms`.

**Still to confirm:** member-set reconciliation to ICD-11 (e.g. `9C61.2/.3/.4`
secondary/developmental have no current Condition_Label member) — clinical,
Dr. Bolo / Dr. Xu. Also still unverified: `ICD10_Eye` is structurally a vocab
table (deriva MCP not connected this session).

> The entry below records the *prior* framing (Option A, "ICD-11 identifies a
> local term"). Kept for history; superseded by the above.

---

## 2026-06-30 — ICD-11 is the definitive code (ICD-10 demoted to legacy/source)

**Decision (Prof. Carl):** ICD-11 is the **definitive/canonical** code for each
condition. ICD-10 is demoted to a **legacy source code** that maps *up* to the
ICD-11-anchored term. Authority hierarchy: ICD-11 = definitive identity (in the
term's `ID`/`URI`); ICD-10 = legacy input that resolves via the map;
`Condition_Label.Name` (`GS`) = the local working label, identified by ICD-11.

**Concretely:** `Condition_Label.ID`/`URI` holds the ICD-11 code
(`GS → ID=ICD11:9C60`). `ICD10_Eye` rows are inputs to the map, not standalone
answers. The map sharpens from a symmetric cross-walk to a directional
**ICD-10 → ICD-11-definitive term**:
`ICD10_Eye(H40.02) ──map──▶ Condition_Label(GS, ID=ICD11:9C60)`. ICD-10 never
stands alone as the identity; it is always a path to the ICD-11 identity.

**The ICD-11 code numbers (VERIFIED 2026-06-30 vs WHO ICD-11 MMS).** Glaucoma
suspect = **`9C60`**, a standalone stem code *outside* the `9C61` Glaucoma block.
Established glaucoma is under `9C61`: `POAG=9C61.0`, `PACG=9C61.1`,
unspecified=`9C61.Z` (`.2`/`.3`/`.4` = secondary OAG / secondary ACG /
developmental — no dedicated Condition_Label member yet). That suspect is a
*sibling* of glaucoma, not a child, reinforces the §5.2 "suspect is not staged
disease" model. URI form: `http://id.who.int/icd/release/11/mms/{code}`.

> **CORRECTION — earlier in this very session I used `9C61.3` for glaucoma
> suspect. WRONG.** `9C61.3` is *secondary angle closure glaucoma*. The correct
> suspect code is `9C60`. Root cause: I asserted it from model memory; the `9C61`
> block reorganization across ICD-11 draft releases is a known trap. Lesson:
> never enshrine an ICD-11 code from memory — verify against
> https://icd.who.int/browse11 (or findacode.com mirror) FIRST. All docs/SVG/PNG
> were corrected to `9C60`.

**Granularity choice — Option A chosen (recommended):** ICD-11 is the definitive
*identifier* of each EXISTING condition; `Condition_Label`'s working granularity
is unchanged. NOT Option B (restructure conditions to mirror ICD-11's taxonomy).
Why A: ICD-11 and ICD-10 don't carve identically (`H40.00`–`H40.06` are several
distinct suspect situations ICD-11 collapses into the single code `9C60`); A
gives "ICD-11 is authoritative" with minimal disruption and lets ICD-10 map up
cleanly. Revisit only if we later want ICD-11's tree to drive the vocabulary.

**Still to confirm.** (1) condition→code map for `9C61.2/.3/.4`
(secondary/developmental — clinical, Dr. Bolo / Dr. Xu); (2) that `ICD10_Eye` is
structurally a controlled-vocabulary table (asserted from data dictionary §2.4,
NOT yet verified against the live catalog — deriva MCP not connected this
session).

---

## 2026-06-30 — ICD codes do not belong in vocabulary `Synonyms`

**Decision:** For the diagnosis vocabularies (`Condition_Label`, etc.), external
coding-system identifiers (ICD-11, ICD-10) must **not** be stored in the Deriva
`Synonyms` column.

- **ICD-11** → the canonical vocabulary `ID` / `URI` columns
  (e.g. `ID = ICD11:9C60`, `URI = http://id.who.int/icd/release/11/mms/9C60`
  for glaucoma suspect). These columns exist precisely to hold a single stable
  external identity for the concept.
- **ICD-10** → a dedicated `ICD10_Eye → Condition_Label` mapping table, not a
  column or synonym. ICD-10 for one condition is a *family* of patterns
  (e.g. `H40.00`–`H40.06` for GS), i.e. a many-to-one relation, which is a
  mapping table by nature. This also makes `compute_condition_label()`'s
  currently hard-coded `H40.0x → GS` logic data-driven.

**Why:** `Synonyms` has a specific semantic — alternate *human-readable names*
for the same concept, used so a search for "Suspected glaucoma" resolves to
`GS`. ICD codes are identifiers, not names; putting them in `Synonyms` is a
category error. The catalog today *does* stuff `H40.*` patterns into the
`Synonyms` of `GS`/`POAG`/`PACG`, and the data dictionary
(`docs/design/diagnosis-severity-definitions.md`, §4 item 4 and §6.2) explicitly
flags this as a defect to undo. Adding ICD-11 to `Synonyms` would repeat and
compound that mistake.

**How to apply:** When proposing the glaucoma-suspect (and sibling) vocabulary
entries, put ICD-11 in `ID`/`URI`, route ICD-10 to the mapping table, and keep
`Synonyms` for human alternates only. This is a clinical-reference proposal;
actual catalog changes go through the `data-curation` Feature Registration
Request process, and clinical definitions remain provisional pending Dr. Bolo
and Dr. Xu.

**Why not put codes in `Synonyms` to get one-column code-OR-name lookup?**
(Recurring challenge — the convenience is real: one `Synonyms` column gives
`lookup("H40.02")→GS` *and* `lookup("Glaucoma Suspect")→GS` with no join, which
is why the catalog already does it.) The goal — a single lookup accepting a code
*or* a name — is legitimate; `Synonyms` is just a poor implementation of it.
Arguments against codes-in-`Synonyms`: (1) **one-directional** — resolves
code→term but cannot answer term→family without string-parsing the free-text
list; (2) **collides the two coding systems** — `H40.02` and `9C60` in one
bag lose their system (no ICD-10 vs ICD-11 typing, can't query "all ICD-10 for
GS" without shape-matching); (3) **can't carry per-code info** — `H40.00`
vs `H40.02` vs `H40.05` are clinically distinct rollups, opaque strings as
synonyms, own rows in a vocab/map; (4) **re-creates the §4-item-4/§6.2 defect** the
cleanup is undoing — self-contradicting; (5) **no referential integrity** — free
text admits typos/stale/nonexistent codes; an FK to `ICD10_Eye` validates every
code. **Resolution:** keep the unified *interface*, not a unified storage bucket
— expose a thin `resolve(token)` view/function that tries the typed code path
(`ICD10_Eye`/`ID`-`URI` → term, one hop) then the name path (`Synonyms` → term).
Same code-OR-name ergonomics, with direction, system-typing, per-code data, and
integrity preserved.

**Code on its OWN term, in its OWN system's table (the converging design).**
Better proposal: don't put codes on `Condition_Label` at all — give each coding
system its own vocabulary (ICD-10 = `ICD10_Eye`, one term per code `H40.00`…;
plus an ICD-11 vocabulary, term = the ICD-11 concept `9C60`), and the code
identifies *its own* term. This is correct placement. **One refinement:** a code
identifying its own term is the term's *identifier*, so it belongs in that row's
`ID`/`URI`, NOT `Synonyms` (e.g. `ICD10_Eye` row: `Name=H40.02`,
`ID=ICD10:H40.02`, `Description="primary angle closure suspect"`, `Synonyms`=
human names for that code). This cleanly fixes system-typing, per-code data,
integrity, and the §4-item-4 defect — all the things codes-on-`Condition_Label`
broke. **But it does not replace the mapping table:** three independent
vocabularies (ICD-10, ICD-11, `Condition_Label`) have no relationships between
them — nothing says `H40.02→GS` or `9C60≈H40.0*`. Classification (ICD-10
family→condition) and cross-walk (ICD-10↔ICD-11) are *relationships*, and
relationships live in association tables, not in any one vocab's columns. So the
two are complementary: this proposal makes the map's *endpoints* clean typed
terms; the map ties them together:
`ICD10_Eye(H40.02) ──map──▶ Condition_Label(GS) ◀──ID/URI── ICD-11(9C60)`.
Strongest version of the whole design = three typed vocabularies + one mapping
table.

**The mapping table — from/to and why.** Maps **from `ICD10_Eye`** (the existing
vocabulary of ICD-10 ophthalmic codes, one row per code) **to `Condition_Label`**
(the term). Standard many-to-one association table, grain = one ICD-10 code per
row; the family for a term falls out as "all rows where `Condition_Label = GS`".
Map **exact codes** (`H40.00`, `H40.01`, … as FKs to real `ICD10_Eye` terms),
**not patterns** (`H40.0*`) — patterns reintroduce the wildcard-matching logic
we're trying to remove. Two distinct jobs justify the table's existence:
*identity* ("what is this concept canonically?" → single-valued `ID`/`URI` =
one ICD-11 code) vs *classification* ("which raw codes fall into this concept?"
→ many ICD-10 codes). `ID`/`URI` can't hold a 7-member family and `Synonyms` is
the wrong type, so a table is the only structure that fits, and the relation
evolves independently (ICD-10 revisions, re-mapping) without touching the
vocabulary terms. Payoff: the table is the data-driven, catalog-queryable
replacement for `compute_condition_label()`'s hard-coded `icd_mapping`
(`H40.0x→GS`, `H40.1x→POAG`, `H40.2→PACG`, else `Other`), moving that logic out
of Python and into `data-curation`-managed data.

**Model-label and clinical-label should share ONE vocabulary (normalization).**
(Prof. Carl's framing.) Key distinction: *agreement* (do the values match — they
need NOT) is separate from *shared domain* (should a model's "Glaucoma" and the
chart's "Glaucoma" be the SAME term — yes). Storing the same concept in two
vocabularies (`Glaucoma_Diagnosis` vs `Condition_Label`) is denormalization of the
concept; the cost lands on the platform's most important query — model prediction
vs clinical ground truth — which becomes a cross-vocabulary mapping instead of a
value equality (`prediction == label`). DB-designer position: provenance ("a model
said it" vs "a clinician said it") is an attribute of the ASSERTION, not the
CONCEPT — model it via `Diagnosis_Tag` (already exists: CNN_Prediction,
Expert_Consensus, …) and/or which table, NOT via a duplicate vocabulary. Normalized
target: ONE `Condition_Label` (ICD-11-grounded) referenced by image/visit/subject/
chart tables alike; provenance via `Diagnosis_Tag`; gradability via
`Diagnosis_Status`; `Glaucoma_Diagnosis` retired or demoted to a coarse view. Two
real obstacles, both resolvable: (1) GRANULARITY — one vocab holds both coarse and
fine terms with a defined coarse↔fine relation; a producer asserts at the
resolution it supports (model→GS/coarse, clinician→POAG). (2) `Unknown`/`Ungradable`
is an image-QUALITY state, not a diagnosis — move it onto the gradability/status
axis (`Diagnosis_Status`), don't put it in the condition vocab. COUNTERWEIGHT:
bigger change, ~194K image rows repoint to Condition_Label; worth it IF
model-vs-clinical comparison is central to the platform (likely yes for Eye-AI),
not if Glaucoma_Diagnosis is a throwaway per-image screen. NOT YET DECIDED / not
in the doc — discussion only; needs live-catalog check of what populates each.

**Doc restructured (2026-07-01) — proposal-first, reference to appendices.** (Prof.
Carl.) The doc had grown table-heavy and buried the proposal behind the current-
state inventory. New arc: §1 Summary (what we're doing) → §2 Why/limitations
(brief, distilled from the old §4 problems) → §3 Proposed design (narrative core:
axes, fold, ICD grounding, severity cleanup, method) → §4 Change plan → §5 Open
questions. Reference material moved to appendices: **App. A** = current-state
verbatim inventory + usage counts (old §2/§3); **App. B** = full proposed vocab
tables (B.1 Glaucoma_Diagnosis, B.2 Severity_Label, B.3 Severity_Method); **App. C**
= references (old §9). Load-bearing decision tables (ICD-10↔ICD-11 crosswalk, the
3-axis table, the change plan) kept INLINE per Prof. Carl's choice; only
reference/sample tables moved. Also fixed a duplicate §6.4 GAMMA heading. 942→607
lines, no content lost, all cross-refs renumbered and verified.

**WRITTEN TO DOC (2026-07-01):** §6.3 rewritten from the open "naming precision"
question into the `Severity_Method` decision (with a sample vocabulary table +
the two feature method-columns); §7 Q3 resolved → points to §6.3; §8 change plan
gained change **6** (create Severity_Method vocab + add method columns), gates
gained "confirm Severity_Method member set"; Summary + §9 references updated.
Catalog-verified that Clinical_Records has no severity column, so no table-column
variant is needed — method is a feature column on both severity features only.

**Severity method-of-determination → separate `Severity_Method` CV + (Severity,
Method) pair (recommended B).** (Prof. Carl.) Severity scale stays Mild/Moderate/
Severe; the *method* (HPA / CMS / ICD-7th-char / …) is recorded too. Three
options examined through 3 lenses:
- **A — method = Workflow_Type / execution provenance** (infer method from the
  Workflow that produced the value). ML: bad — reading method needs a lineage
  walk (value→Execution→Workflow→type), can't `groupby`. Chaise: bad — method
  invisible on the record without cross-FK visible-columns, no native facet. DB:
  layering violation — conflates "what code ran" (Workflow's job) with "what
  staging system the value uses" (a semantic property of the VALUE); breaks when
  method ≠ code (human chart review has no workflow; ICD-derived; configurable
  graders); pollutes the built-in system vocab Workflow_Type with domain
  semantics; can't NOT-NULL-enforce "severity needs a method".
- **B — separate `Severity_Method` domain CV; feature carries Severity_Label +
  Severity_Method columns; unit = the (Severity, Method) pair.** ML: winner —
  both are df columns, trivial filter/groupby, method-vs-method confusion matrix
  is a self-join. Chaise: winner — two native FK dropdowns, independent facets,
  at-a-glance + editable. DB: winner — method modeled as what it is (attribute of
  the value), FK-validated, NOT-NULL-able, source-independent (works for chart
  review AND ICD-derived without an Execution), composes with the existing
  "severity only when glaucoma" rule, and directly resolves §6.3 (Dr. Xu's
  caution about silently mixing staging systems).
- **C — encode method in the term (`HPA_Mild`…).** Rejected: the exact
  pack-two-axes-into-one-label anti-pattern this whole doc removes (cf.
  Unspecified/Indeterminate, Normal or No dx); corrupts the clean 3-value scale.

**Where Severity_Method is recorded (two layers).** (1) *Vocabulary table* — a new
domain vocab `Severity_Method` (via `deriva_ml_create_vocabulary`), one row per
staging system (HPA, ICD_7th_char, CMS…), defining the allowed methods — parallel
to how `Severity_Label` defines the allowed stages. (2) *Value* — a new
`Severity_Method` FK column ADDED TO EACH FEATURE that carries a severity, beside
the severity column, so the (Severity, Method) pair is co-located on the same row:
`Execution_Subject_Chart_Label` (Chart_Label feature: Condition_Label +
Severity_Label + Severity_Method) and `Execution_Clinical_Records_Glaucoma_Severity`
(ICD_Severity_Label + ICD_Severity_Method). Add it as PART OF THE FEATURE
DEFINITION (features are multi-column — Chart_Label already carries condition +
severity) so it keeps the feature machinery (Execution provenance link,
Feature_Name). This realizes "keep both": method column on the row (semantic) +
feature→Execution link (provenance). RESOLVED (Prof. Carl): method VARIES PER ROW (a grader can use HPA vs CMS on
different subjects) → it IS a genuine per-row FK column on the feature, beside
Severity_Label. No fixed-per-source shortcut; full Option B. NOT-NULL when severity
is present.

**Placement invariant across features AND plain table columns.** The rule is:
*method goes wherever the severity value goes, on the same row; and a given
severity should live in exactly ONE place per source.* Mechanism adapts to where
severity already is:
- Severity as a **Feature** (e.g. `Execution_Subject_Chart_Label` Chart_Label;
  `Execution_Clinical_Records_Glaucoma_Severity` ICD-derived) → add the method as
  a **feature column** (`Severity_Method` / `ICD_Severity_Method`) in the feature
  definition — keeps the Execution provenance link.
- Severity as a **plain FK column** directly on a table (the way
  `Clinical_Records.ICD_Condition_Label` is a plain column) → add a **plain
  `Severity_Method` FK column** beside it. Same co-located-pair principle.
RESOLVED via live catalog (get_table www.eye-ai.org/eye-ai Clinical_Records,
2026-07-01): `Clinical_Records` has NO severity column. Its columns are RID +
system, Date_of_Encounter, LogMAR_VA, Visual_Acuity_Numerator, IOP,
Refractive_Error, CCT, CDR, Gonioscopy, Condition_Display, Provider, Clinical_ID,
**ICD_Condition_Label** (FK→Condition_Label), Powerform_Laterality (FK→Image_Side).
So condition IS a raw column (ICD_Condition_Label) but SEVERITY is not — the only
severity-ish data are raw numerics (IOP/CDR/CCT/…), the *inputs* to severity, not
a grade. ICD-derived severity lives ONLY in the feature
`Execution_Clinical_Records_Glaucoma_Severity`. CONSEQUENCE: do NOT add a severity-
method column to `Clinical_Records` (no severity there to qualify).
`Severity_Method` goes only on the two FEATURES where severity lives —
`Execution_Subject_Chart_Label` (Severity_Method) and
`Execution_Clinical_Records_Glaucoma_Severity` (ICD_Severity_Method) — both as
feature columns. Cleanest case: severity is consistently a feature (never a raw
column), so method is consistently a feature column; no feature-vs-column
duplication risk, no Clinical_Records schema change. (Aside: ICD_Condition_Label
FK→Condition_Label becomes FK→Glaucoma_Diagnosis under the §5.8 fold — migration
covered by change 2/4.)

**Verdict: B — all three lenses converge** (rare), because method IS a semantic
attribute of the severity value, not a fact about the code. Keep BOTH provenance
(Workflow = which code ran) and Severity_Method (which clinical basis) — they are
complementary, not substitutes. Honest caveat for A: if method were *always* a
deterministic function of the workflow it'd be redundant with provenance — but
that assumption fails for human/ICD/configurable sources, and even when it holds
the read-cost makes A worse. Implementation: `Severity_Method` = new domain vocab
(`deriva_ml_create_vocabulary`); add `Severity_Method` FK column to the
Chart_Label / Glaucoma_Severity features beside `Severity_Label`, NOT-NULL when
severity present. NOT yet written to the doc (offered).

**§5.8.3 and §6.0 diagnosis tables were duplicative — deduped.** (Prof. Carl.)
The prior "defer §6.0 to §5.8.3" half-fix left BOTH tables present, and §6.0's
still said `Condition_Label`. Resolved: §5.8.3 is now the SINGLE diagnosis table
(enriched with a Synonyms column + fuller descriptions merged from §6.0, named
`Glaucoma_Diagnosis`); §6.0's condition table is DELETED and §6.0 is retitled to
severity-only. §6.2 worked example kept but re-scoped to "illustrates the column
layout" (defers values to §5.8.3). Rule going forward: diagnosis term definitions
live ONLY in §5.8.3; severity term definitions ONLY in §6.0; §6.1/§6.2 are
actions that reference those, not restatements.

**Tech-writer re-review (2026-06-30, Claude + Codex) — fold left a
"which-vocab-is-the-target" inconsistency.** After §5.8 made `Glaucoma_Diagnosis`
the folded target, §5.6/§5.7/§6/§9 still framed `Condition_Label` as the future
grounded vocab — doc described two end-states. Root cause: `Condition_Label` was
used for BOTH current-state and proposed-state. Fix applied: a naming-convention
note at the top of §5.6 (`Condition_Label` = current/pre-fold; `Glaucoma_Diagnosis`
= folded target; read the former as the latter under §5.8), then relabeled the
pre-fold spots (§5.6 table `Normal or No dx` row, §6.0 defers diagnosis source-of-
truth to §5.8.3, §6.2 retitled to migration current→folded with the split
decided, Figure 1 caption, §9 ICD10_Condition_Map note). Also fixed: "see §6"→
§5.6-5.7 (line 115) and §6.1 (line 278); "image-level Glaucoma_Diagnosis" leaks →
"current 3-term image/visit/subject" (Summary, §5.8 banner, §8 change 2) — kept
the legitimate image-level uses (verbatim catalog comment, Image_Diagnosis row,
194K-rows count). Judged NOT worth changing: the 5× "no catalog edits" caveat
(Codex #9) — each instance is scoped to a different reader entry-point, defensible
for a strawman; and the §5.6-before-§5.8 ordering (Codex #4) — addressed with the
transition note rather than a large section move.

**DECIDED (Prof. Carl): the merged vocabulary is named `Glaucoma_Diagnosis`, not
`Condition_Label`.** The fold of Condition_Label + the old image-level
Glaucoma_Diagnosis into ONE shared vocabulary takes the name `Glaucoma_Diagnosis`
(the merged thing IS the glaucoma diagnosis, and that name was already consumed at
image/visit/subject). So: the old 3-term `Glaucoma_Diagnosis` (No/Suspected/
Unknown) is REPLACED by the 7-term merged vocab; `Condition_Label` as a table name
goes away (its terms move into `Glaucoma_Diagnosis`). All the design points
(ICD-11 identity, local EyeAI terms, No dx local condition term, cross-walk table)
now attach to `Glaucoma_Diagnosis`. Captured in the doc (§5.8 + revised §2.3).

**DECIDED (Prof. Carl): `No dx` is a LOCAL term in `Condition_Label`;
`Diagnosis_Status` does NOT get `Not assessed`.** Supersedes the status-axis lean
below. Rationale: "no diagnosis" is a legitimate VALUE of the diagnosis field —
one column, in-domain, ML-comparable (a model/query asking "what's the condition?"
gets a direct answer incl. "none made"). Key reconciliation with the ICD-code
argument: "no ICD code" forces `No dx` to be a LOCAL term (EyeAI URI), it does NOT
force it onto a different axis — local-ness and axis are independent choices. So
`No dx` = local condition term (`EYEAI:No_dx`, `eye-ai.org/id/condition/No_dx`).
CONSEQUENCE: because the concept now lives in Condition_Label, `Diagnosis_Status`
must NOT also carry `Not assessed` (would duplicate the concept — the thing we've
been avoiding). Status stays Graded/Validated/Rejected. `Unknown` ≡ `No dx` (per
earlier decision) → represented by this one term. `Ungradable` still off this
table (gradability axis). Updated Condition_Label = 7 terms: GS, POAG, PACG,
Unspecified Glaucoma (ICD); Normal (ICD-Z `Z01.00`? or local — sub-choice); Other,
No dx (local).

**[SUPERSEDED by the decision above] ICD-codeability is the discriminator: `No dx`
has NO ICD code → status axis; `Normal` DOES (`Z01.00`) → condition.** (Resolves the prior "unsettled" note.)
Verified against ICD-10-CM: `Z01.00` = "Encounter for examination of eyes and
vision WITHOUT abnormal findings" (real billable code) and `Z13.5` = screening —
both code an encounter that HAPPENED, i.e. they map to **Normal** (examined, no
disease), NOT to "no dx". "No dx" = no determination ever made = no encounter, no
finding → nothing for ICD to code (ICD codes clinical events; absence of one isn't
codeable). Apply the design rule (Condition_Label terms are ICD-groundable):
Normal → groundable (Z01.00) → belongs in Condition_Label; No dx → not groundable
because it isn't a clinical event → belongs on the STATUS axis (Diagnosis_Status.
Not assessed). So the answer to "why can't No dx go in the diagnosis table" is
principled, not just purist: it has no ICD grounding because it's the absence of
an assessment, not a diagnosis. TIPS the earlier-unsettled axis choice toward
`Not assessed` on the status axis. Hedge: Normal's grounding is a Z "reason-for-
visit" encounter code, not a disease code — so whether Normal's ID is Z01.00 or an
EyeAI-local URI is a sub-choice; but the CONTRAST holds (Normal has a candidate
code, No dx has none). Sources: icd10data.com Z01.00, Z13.5. (Prof. Carl pushed back — earlier note
over-stated "No dx → status" as forced. Correction.) "No dx" literally = no
diagnosis = the Not-assessed/Unknown concept, so `Normal or No dx` still clearly
fuses two things (Normal = negative diagnosis; No dx = no diagnosis) and should
split. BUT the split TARGET for "No dx" is a real choice, not a given:
- **In `Condition_Label`** (as a `No dx` term): "no diagnosis" is a legitimate
  VALUE of the diagnosis field ("none made" answers "what's the diagnosis?").
  Keeps one column, keeps model-vs-clinical a single-domain comparison with "no
  dx" as a comparable value — the SAME argument we used for the ML reject class.
  Consistent with already putting Normal/Other/Unspecified (non-pure-ICD) in the
  vocab. Simpler.
- **In `Diagnosis_Status`** (as `Not assessed`): purist view — "no determination"
  is a workflow state, not an eye-fact; keeps condition = eye-facts only.
The DECIDING question: does `Diagnosis_Status` already track an ORTHOGONAL
"assessed?" axis (Graded/Validated/Rejected) that "Not assessed" naturally
extends, AND does "assessed?" need to vary independently of the condition value?
If YES → status axis (else you duplicate the axis). If NO — if "no diagnosis" is
purely one possible answer to the diagnosis question and never coexists with an
actual diagnosis → `No dx` in Condition_Label is simpler and correct; shipping it
to a status table is over-engineering. This is a catalog/workflow fact (how
Diagnosis_Status is actually used vs condition), NOT resolvable by reasoning.
UNSETTLED. Data split of the 88 rows also still needs the catalog.

**OPEN DATA Q: are there subjects with unknown / no-determination glaucoma status?**
Can't answer from the doc snapshot — needs a live catalog query (deriva MCP not
connected). What the snapshot shows: all 2,302 `Chart_Label` rows carry a REAL
condition (GS/POAG/PACG/Other/Normal or No dx/Unspecified) — no explicit
`Unknown`. BUT two catches: (1) `Normal or No dx` (61+27=88 rows) conflates
"assessed-healthy" vs "no determination" — some of those 88 may BE
no-determination subjects, unresolvable from the label (exactly what the split
fixes); (2) Subject_Diagnosis/Observation_Diagnosis cover ~7,020 each vs only
2,302 chart-labeled subjects — subjects with an image diagnosis but NO Chart_Label
row are effectively "not assessed" clinically, and Glaucoma_Diagnosis has an
`Unknown` value (378 image rows). To answer, query: Subject_Diagnosis where
Glaucoma_Diagnosis=Unknown; subjects in imaging but absent from Chart_Label; and
disambiguate the Normal-or-No-dx rows. Meta-point: that this is HARD to count today
is itself evidence for the proposal — with a clean status axis + Normal split it'd
be a one-line query.

**`Unknown` is not dropped — it relocates to `Diagnosis_Status` as `Not assessed`.**
(Prof. Carl check.) Removing `Unknown`/`Not assessed` from `Condition_Label` does
NOT delete the concept — it still needs a home, on the STATUS axis. `Diagnosis_Status`
today = Graded/Validated/Rejected (§2.4), with NO "no determination" value, so we
must ADD `Not assessed` (≡ Unknown) there. Modeling sub-choice: represent "no
determination" either (1) as an explicit `Not assessed` status term (first-class,
queryable — better for a screening worklist; "we know it's unassessed" is
actionable and unambiguous), or (2) as absence-of-row (null/missing carries it —
ambiguous: unassessed vs record-lost). Lean explicit for a screening platform.
Full three-axis term counts: Condition (Condition_Label) = GS, POAG, PACG,
Unspecified Glaucoma, Normal, Other; Gradability = Gradable, Ungradable; Status
(Diagnosis_Status) = Graded, Validated, Rejected, + Not assessed(≡Unknown, NEW).
Discussion-only; not in the doc.

**Proposed `Condition_Label` shape (concept-complete draft).** Standard vocab
columns only (RID, Name, Description, Synonyms, ID, URI). Terms: GS→ICD11:9C60,
POAG→9C61.0, PACG→9C61.1, Unspecified Glaucoma→9C61.Z (all WHO URIs; H40.* leaves
Synonyms for ICD10_Condition_Map); Normal→EyeAI URI (split out of the old
`Normal or No dx`, keeps only the assessed-healthy meaning); Other→EyeAI URI.
NOT in this table: Ungradable (gradability axis), Unknown/Not-assessed (status
axis — the "or No diagnosis made" half of the old Normal-or-No-dx). Grounded vs
local = URI namespace (id.who.int vs eye-ai.org). Open sub-decisions: (a) does
`Normal` get a WHO ICD-11 URI or an EyeAI one (is "no glaucoma" ICD-representable,
or modeled as absence?) — TBD; (b) 9C61.2/.3/.4 still have no member → Other
unless added (§7); (c) RID handling when splitting the old 5-26KY `Normal or No
dx` row is a data-curation mechanic; (d) exact per-term IRIs + EyeAI URI scheme
still TBD-verify. Discussion-only; not in the doc.

**RESOLVED: `Unknown` ≡ `Not assessed` (one concept); `Ungradable` is separate.**
(Prof. Carl decision.) Do NOT conflate `Unknown` with `Ungradable`. `Unknown` and
`Not assessed` ARE the same concept = "no diagnostic determination on record" →
one STATUS value (`Diagnosis_Status`). `Ungradable` = "image couldn't be assessed"
→ separate GRADABILITY axis. So the three distinct concepts land cleanly: `Normal`
= assessed-healthy → CONDITION; `Unknown`/`Not assessed` = no determination →
STATUS (single value, not two); `Ungradable` → GRADABILITY. IMPORTANT catalog
implication: `Glaucoma_Diagnosis.Unknown` currently has synonym `Ungradable`
(§2.3) — under this ruling that is a MIS-SYNONYM (it pairs a status concept with a
gradability concept, two different axes) and must be broken when Glaucoma_Diagnosis
is decomposed. Discussion-only; not in the doc.

**`Normal` ≠ `Unknown` — `Normal or No dx` packs opposites and must split.**
(Prof. Carl.) The term's verbatim description "No signs of glaucoma OR No diagnosis
made" fuses two OPPOSITE information states: **Normal** = assessed, eye is healthy
(a positive negative finding — "we know it's negative") vs **No dx / Not assessed**
= no determination exists ("we don't know"). For a screening platform this is
critical: screened-healthy (done) vs never-screened (still needs a visit). They
scatter across axes: **Normal** stays a real CONDITION value (arguably
ICD-groundable as absence-of-glaucoma); **Unknown/No dx/Not assessed** leaves the
condition axis for STATUS (`Diagnosis_Status`, = absence of a Graded state). So
`Normal or No dx` should SPLIT (as §6.0 already tentatively flags). Consequence for
the Glaucoma_Diagnosis fold: its 3 terms do NOT map to 3 condition terms — they
scatter across ALL THREE axes (`No Glaucoma`→Normal[condition];
`Suspected`→GS[condition]; `Unknown`→Ungradable[gradability] OR Not-assessed
[status] depending on meaning). That Glaucoma_Diagnosis mixes condition + condition
+ not-a-condition in one vocab is the strongest argument yet that it was a
mixed-axis vocabulary all along and should be DECOMPOSED, not preserved.
Discussion-only; not in the doc.

**Condition_Label needs NO NEW local terms — the gaps belong on other axes.**
(Prof. Carl.) Checked §2.1: the 6 terms are GS, POAG, PACG, Other, Normal or No
dx, Unspecified Glaucoma. There is NO `Unknown`/`Ungradable` term (those live in
`Glaucoma_Diagnosis`, not here). Coverage: "glaucoma present, subtype unknown" =
`Unspecified Glaucoma` ✅; "no disease / no dx" = `Normal or No dx` ✅ (note: its
description already bundles "No signs of glaucoma OR No diagnosis made" — the
"not assessed" idea is already (sloppily) folded in, which is the §6.0 split flag).
So the earlier "add local terms to Condition_Label" step largely DISSOLVES: the
condition axis needs no new local terms. `Ungradable` correctly has no home here
(it's gradability, not a condition → gradability axis). `Unknown/Not assessed` is
already (mis-)covered by `Normal or No dx`'s "or No diagnosis made" clause → if
split, it moves to the STATUS axis (`Diagnosis_Status`), not a new condition term.
The only non-ICD (EyeAI-URI) condition terms — `Normal or No dx`, `Other` —
ALREADY EXIST; they are not new. Net: reinforces the three-axis model and
simplifies the proposal (no new condition terms to mint).

**`Unknown` and `Ungradable` are DIFFERENT concepts (and maybe different axes).**
(Prof. Carl.) The catalog conflates them today — §2.3 has one term `Unknown` with
synonym `Ungradable`. Pull apart: **Ungradable** = the input couldn't be assessed
(artifact failure — blurry/dark/media opacity; a judgment is impossible).
**Unknown / Not assessed** = no judgment was made or recorded (process gap — image
may be fine, just not graded). Independent states: an image can be
gradable-but-not-graded OR ungradable-but-someone-tried; collapsing loses the
action difference (re-image the patient vs just grade it). Sharper: they may not
share an axis — **Ungradable** is about image quality/assessability (gradability
axis, property of the artifact); **Unknown/Not assessed** is about whether a
determination exists (status/completeness axis — arguably just the absence of a
`Graded` `Diagnosis_Status`). Clean model = THREE axes: Condition
(`Condition_Label`, ICD-grounded) / Gradability (Gradable|Ungradable) / Status
(`Diagnosis_Status`: Graded|Validated|Not assessed).

TENSION with the prior note: (prior) ML reject/abstain belongs IN the prediction
domain → put Ungradable in the shared vocab; (this) Ungradable/Unknown are
assessability/status, not diagnosis → separate axes. Resolution depends on WHOSE
output: an image-classifier that can abstain legitimately has `Ungradable` as one
of ITS output classes (same domain as its other outputs), but the CLINICAL
condition vocab should not. That is itself evidence the image-classifier output
vocab and the clinical condition vocab are NOT the same thing — the reject class is
exactly where the two domains legitimately diverge. So this PARTIALLY WALKS BACK
"just add local terms to one shared Condition_Label": the abstain class is a reason
the image-model domain and clinical domain may stay distinct after all. Unresolved;
feeds the keep-vs-fold decision. Discussion-only; not in the doc.

**Handling `Unknown`/`Ungradable` under one shared vocab: local terms with
EyeAI-routed URIs (NOT null).** (Prof. Carl's option + correction.) Rather than
move gradability to `Diagnosis_Status`, add `Ungradable`/`Unknown` as LOCAL terms
IN the shared `Condition_Label` vocab. CORRECTION to an earlier note: local terms
must get an **EyeAI-routed, resolvable URI** (e.g. `https://www.eye-ai.org/id/
condition/Ungradable`), NOT a null URI. Reasons: (1) every term deserves a
first-class resolvable identity — null makes local terms second-class; (2) the
grounded-vs-local distinction is the URI's NAMESPACE/authority
(`id.who.int/...` = ICD-11, `eye-ai.org/...` = EyeAI-local), a queryable explicit
signal — do NOT overload URI-nullness to mean "local" (fragile, semantically
wrong); the filter for ICD-grounded is `WHERE URI LIKE '%id.who.int%'`, not `URI
IS NOT NULL`; (3) FAIR/linked-data correct — if EyeAI mints a concept the world
has no standard for, EyeAI mints the URI in its own namespace (standard ontology
extension-term practice); (4) URI authority encodes who DEFINED the concept (WHO
vs EyeAI), a distinct axis from `Diagnosis_Tag` which records who ASSERTED a value.

DB-designer verdict (unchanged): for an ML platform the shared-vocab-with-local-
terms option is the better pragmatic choice — abstain/reject is a legitimate VALUE
of a prediction and belongs in the SAME domain (one FK, one comparison, reject
class included). Alternative (Unknown→`Diagnosis_Status`) forces a two-column
"condition null + status why" state and drops the reject class out of model-vs-
clinical comparison. Refinements: don't fuse `Ungradable` (image quality) with
`Not assessed`/`Unknown` (no determination) if both needed (§4 slash-packing);
mark local terms via their eye-ai.org URI + a "local / non-ICD" description.
OPEN: exact EyeAI URI scheme/route (eye-ai.org/id/... vs catalog ermrest URL vs
minted PURL) — pin against how EyeAI already mints identifiers. Discussion-only;
not in the doc.

**Glaucoma_Diagnosis is NOT image-only — it spans image/visit/subject.** (Prof.
Carl caught this.) The doc's §2.3 heading and §1 call it the "image-level
vocabulary", but its own "Consumed by" table shows three consumers:
`Image_Diagnosis` (194,204, per image), `Observation_Diagnosis` (7,020, visit),
`Subject_Diagnosis` (7,020, subject). So at the SUBJECT level it labels the same
entity `Condition_Label` does. This demolishes the "different entity/grain"
argument for keeping the two vocabularies separate. Surviving distinctions:
(1) resolution — coarse No/Suspected/Unknown vs fine subtypes (a mapping, not a
merge reason); (2) provenance — Glaucoma_Diagnosis is a grader/model signal that
runs consistently across image→visit→subject, Condition_Label is a subject-level
chart-review clinical determination; (3) `Unknown` is an image-quality/gradability
state with no clinical-diagnosis equivalent. NET: at the subject level the two
genuinely overlap; the keep-separate case now rests on provenance + the
multi-level signal, not entity. NEEDS LIVE-CATALOG VERIFICATION (deriva MCP not
connected): what populates Subject_Diagnosis vs the Chart_Label feature, and
whether they agree per subject. Also fix the "image-level" mislabel in §1/§2.3.

**Do NOT add custom columns to a Deriva vocabulary table.** (Prof. Carl,
correcting merged content.) A controlled-vocabulary table has a fixed standard
shape — `RID, Name, Description, Synonyms, ID, URI` (+ system cols). That
uniformity is the contract Chaise and the deriva-ml APIs rely on. A term's
external grounding goes in the **`ID`/`URI`** slot (one canonical identifier);
bespoke columns like `ICD10_code` / `ICD11_code` violate the contract and must
not be added. Consequence: the "dual ICD-10 + ICD-11 code columns on each term"
idea (mechanism (a), which entered via a merged colleague draft) is **wrong and
removed** — it is NOT a live option. This collapses the former (a)/(b) fork: there
is only ONE design — ICD-11 identity in `ID`/`URI`; ICD-10 codes in the
`ICD10_Condition_Map` association table (many exact codes → one term). Many-to-one
external relations attach to a vocabulary via an association table, never via
added columns. Fixed §5.6 accordingly (removed the dual-column subsection and the
(a)/(b) open-decision box).

**ERD scope — must show BOTH axes, not just condition.** (Prof. Carl caught this.)
The first ERD drew only the condition/ICD side and omitted `Severity_Label`
entirely — but the doc's core model (§5.1–§5.3) is that Condition and Severity are
two side-by-side FK axes on the `Chart_Label` feature row
(`Execution_Subject_Chart_Label`), with severity conditional on the condition
being glaucoma. A figure sitting after that model that shows only one axis reads as
incomplete. Fix: the ERD now shows the Chart_Label feature carrying BOTH
`Condition_Label` and `Severity_Label` FKs, `Severity_Label` as its own vocab, and
the orange "severity valid only if condition = glaucoma" constraint (§5.2). There
is NO `Condition_Severity` table — severity is a second column on the feature row,
not a separate association. Figure lives in §5.7 (after ICD grounding is
explained) with a forward pointer from §5.3, to avoid showing ICD-11 codes before
§5.6 introduces them.

**Placement — the map is upstream of `Condition_Label`, not a hop off the
Subject.** Two paths populate `Condition_Label`, and the map is only on one of
them. (1) *Chart-review path*: Subject → `Chart_Label` feature
(`Execution_Subject_Chart_Label`) → `Condition_Label` FK — a human grader picks
the term directly; **no ICD code, no map involved.** (2) *ICD-derived path*:
`ICD10_Eye` code → `ICD10_Condition_Map` → `Condition_Label`, with
`Clinical_Records.ICD_Condition_Label` then referencing the produced term. The
map's sole job is to *derive/produce* the term from raw ICD-10 codes on the
ICD path; once the term exists, every consumer (Subject, Clinical_Records)
references the **term**, never the map. So "Subject has a Condition_Label, then
the map" is right in spirit but the map is not a second hop off the Subject — it
is how the ICD path fills in the Condition_Label in the first place. Why this
matters: prevents anyone wiring the map between Subject and Condition_Label
(which would be wrong — the chart path has no ICD code to map from).

**Corollary — synonyms can *index* an ICD-10 family, not *store* it.** A
human-readable synonym can serve as the entry point for a deterministic two-hop
lookup: synonym → term (`GS`) → ICD-10 family (`H40.00`–`H40.06`) via the
mapping table. What a synonym cannot do is identify a *single* code (the
term→code step is one-to-many, and ICD-11 vs ICD-10 are different codes for the
same concept). The lookup you actually want is the family, so synonym-as-key is
fine — but it is only reliable if **synonym uniqueness is an invariant** of the
vocabulary (no synonym shared across terms, no collision with another term's
`Name`). If synonyms are used as a family-lookup key, that uniqueness becomes
load-bearing and should be enforced/validated. Codes still live in the mapping
table + `ID`/`URI`; the synonym only indexes, never stores them.
