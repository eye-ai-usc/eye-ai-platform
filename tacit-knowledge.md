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
