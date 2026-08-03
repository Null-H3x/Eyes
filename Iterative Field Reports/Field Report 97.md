# Field Report 97 — THE MERGE SWEEP CANNOT ADD RELATIONS, AND THE SIGNAL IT FOUND WAS AN ARTIFACT

*Instrument: `eyemerge.py` (14-check gate, three screens, negative control). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — V4's mechanism audited before use

Tech-ref §12 V4 proposes resolving the alphabet size within [56, 83] by
"rebuilding the skeleton under each candidate merge of an undetermined glyph
into a determined one; record added relations versus contradictions. A correct
merge adds relations; a wrong merge contradicts or changes nothing."

**That mechanism is near-vacuous, and the reason is definitional.** A glyph is
undetermined precisely because it occupies no cell of any w-anchored pair — no
matched non-dot cell of a pool alignment whose message-pair constant is forced.
A skeleton rebuild under any merge therefore adds **zero** relations and
contradicts **nothing**, for all 1,863 candidates. The census verifies it:

```
undetermined occurrences at lettered cells, pool instances:      4
                              at lettered cells, discarded:      2
                              at dot cells:                    148
```

The prediction was 0 and the observed 4 **refine rather than break** the
argument — all four sit in w-free contexts, the only place they could sit:

- **glyph 58** at #2- East 3@64, offsets 0 and 4 (letter A) — the
  **cross-triplet bridge** instance. Siblings all in T3; no forced base
  difference; the matched cells yield only relative relations.
- **glyph 12** at #4 West 2@18, offsets 3 and 5 (letter B) — **West 2**, the
  message unattested across six channels; its base floats, so its within-T2
  pair constants are free.

FR54's mechanism sharpens accordingly: undetermined ≠ "appears only at dots";
undetermined = "appears at no cell of a **w-anchored** pair."

A corollary logged as structure, not used: merging 12~13 would force
`base[W2]−base[E3]` to a specific value, and 58~60 the cross-triplet
difference — such merges are **consequential, not excluded**. Nothing known
excludes the implied linkages.

---

## 1. What survives: three screens that do not route through the rebuild

| screen | mechanism | conditionality |
|---|---|---|
| **S1 adjacency** | 0 same-value doubles in 1,027 slots (~12.4 expected, chance ~4e-6) reads as mechanism: the plaintext never steps −drift. A merged pair adjacent anywhere would be a symbol double. | the mechanism reading; variant-masking conspiracy priced ≤ ~1e-3 (all ~12 expected doubles independently masked at ≤0.5 each) |
| **S3 same-instance exactness** | two differently-lettered cells of one pool instance are symbol-distinct, else that instance's signature diverges from its siblings' | the class being genuine; perfect isomorphism |
| **S2 indicator distinctness** | the nine position-0 glyphs read as per-message labels; a merge collapses two labels | the distinct-labels reading — weakest; **never floor-bearing** |

New corpus fact en route: all four out-of-skeleton indicators are
undetermined — E2:**36**, W2:**76**, W4:**77**, E5:**33** (E1:50, W1:80,
E3:63, W3:34, E4:27 confirm FR43).

---

## 2. The instrument, and three bugs its own gate caught

`eyemerge.py`, stdlib, 14-check gate green before corpus contact. Three of my
own plants failed and were fixed rather than the tests: a T3 plant in which
the "never adjacent" pair was adjacent; a T4 plant that violated same-letter
equality — which exposed that `s3_pairs` guarded different-letter equality but
not same-letter inequality, so the **guard was added and its own planted
violation test with it**; a T8c plant whose "undetermined" nodes overlapped
the global determined set, letting the solver attach them for free. Gates
that catch their author are working.

---

## 3. The sweep

```
candidates                 1,863   (27×56 det-merges + C(27,2) undet-merges)
S1 adjacency excluded        371   (324 du, 47 uu)
S3 exactness excluded          3   (12,55) (20,58) (30,58)
S1 ∪ S3 (floor-bearing)      374
S2 indicator flagged          26   (not floor-bearing)
det×det S3 consistency       143   pairs re-confirmed distinct, zero anomalies
```

Per-glyph: every undetermined glyph retains 34–51 surviving determined
partners. **No glyph is isolated** (R1 not triggered). Exact minimum
undetermined-only classes: **0** (94 search nodes).

**The conditional floor stays at 56.** The [56, 83] window does not tighten.

---

## 4. SELF-CORRECTION — the pre-registered criterion fired, and the firing is an artifact

R3, frozen before corpus contact: claim evidence for mergeability only if
observed S1 exclusions fall below the null 5th percentile. They did:

```
observed 371    null 402.7 ± 7.75    5th pct 390    z = −4.09
```

**R3 was mis-specified, because it lacked a negative control.** The corpus's
repeated passages — refrains, near-duplicate runs, stamped shared prefixes —
repeat their adjacencies, concentrating adjacency mass on fewer distinct
pairs than any within-message shuffle. Three measurements settle it:

```
det×det pairs (PROVEN non-merged)   obs 419   null 452.4 ± 8.76   z = −3.81
all distinct pairs                  obs 790   null 855.1 ± 9.71   z = −6.70
repeated adjacency tokens           obs 237   null 161.1 ± 9.53   z = +7.96
corrected differential (cand−det²)  obs −0.0729  null −0.0776 ± 0.0080  z = +0.58
```

A population of pairs **proven pairwise distinct** shows the same suppression
the candidates do; the differential — the statistic R3 should have been — is
null. FR32's lesson generalizes: **registering a test does not make it sound,
and a pre-registration without a negative control can misfire on schedule.**
Fifth methodological catch of this shape in the series (FR39, FR42, FR45,
FR48, FR97).

---

## 5. The survivors, priced

1,489 merges survive S1∪S3 — against an expected 1,460.4 if **no** merge is
real. Survivors with null-survival probability under 0.5 ("informative"):
**8 observed, 7.4 expected.** Chance, exactly. For the record, the only eight
pairs whose survival means anything: (13,43) (11,49) (29,66) (11,19) (2,5)
(2,13) (13,70) (2,63) — null-survival 0.42–0.50, no claim attached.

**Verdict: the internal routes to the alphabet size are exhausted.** The two
exact regularities touching undetermined glyphs (no-doubles; instance
exactness) exclude 374 merges deductively and cannot confirm any. Tightening
[56, 83] now requires external data — MDL over candidate segmentations needs
the glyph images (§4.5).

---

## 6. Archival — `procedural_triangles.cpp` read in full (FR95 horizon 3 discharged)

704 lines, all read. **There is no shuffle anywhere in this file.** The
randomizer draws jitter and palette picks; nothing is ever permuted. The
shuffle-then-transform hypothesis finds no support in his procedural-art
idiom.

What the file does supply:

- **`VectorAddUnique` palettes** — `LoadColors` raster-scans a PNG and
  dedups **in encounter order**. His ordered-list idiom is *first-occurrence
  order of a scanned asset*. A candidate construction family for `C`:
  encounter-order dedup of a raster-scanned source. **Blocked on assets**
  (glyph sheet, in-game textures); logged for the external-data ledger.
- **`CycleColors`** — `palette[(index + offset + Random(0,3)) % size]`:
  deterministic index, small jitter, modular reduction. His "orderly
  variation" shape; an echo of progressive structure, logged only.
- **Three more `seed, 1234, MetaData(0, 10000)` config blocks** — the
  third, fourth and fifth confirmations of FR94's small-explicit-integer
  seeding practice.
- `offset_x = 82.f` — observed, priced as numerology-grade noise, dismissed
  (the "83 guns" discipline).

**R2 curiosity, pre-registered:** the one in-environment member of the
encounter-order family — the corpus's own derived orderings
(first-occurrence, reversals, inverses, frequency ranks; 7 candidates) —
through `skeleton_ok` at ~1e-78: **0/7 pass**, as expected; the corpus-derived
version is self-referential and was tested only for completeness.

---

## 7. Errata executed (FR96 horizon 3)

`83^-378` patched to `83^-41 (~1e-78)` in the living documents: tech ref ×3
(§4.4, §14, §15 glossary), `eyeorder.py` docstring. §12 V4 rewritten with
this cycle's result. Historical reports left as written; `CORRECTIONS.md`
created as the standing errata ledger (E1 selectivity, E2 V4 mechanism).

---

## 8. Doctrine changes

| item | prior status | status now |
|---|---|---|
| V4 mechanism | "rebuild adds relations or contradicts" | **near-vacuous**; undetermined = no cell of any w-anchored pair |
| Undetermined mechanism (FR54) | "rare glyphs co-occur less" | sharpened: **4 lettered occurrences exist, all w-free** (#2- bridge; West 2) |
| Alphabet size [56, 83] | 1,512-merge sweep pending | **executed over 1,863**; floor 56 stands; 374 excluded; no merge confirmable internally |
| Indicators | 5 of 9 known in-skeleton | all 9 extracted; **the four out-of-skeleton indicators are exactly undetermined glyphs** 36/76/77/33 |
| Adjacency-diversity suppression | unknown | global repetition artifact (z −6.7 all-pairs, +8.0 repeated tokens); **not** merge evidence |
| Pre-registration discipline | "declare thresholds first" | **and give every criterion a negative control** |
| Shuffle-then-transform prior | plausible (FR94) | no shuffle in 704 lines of his procedural-art code |
| Selectivity figure propagation | FR96 horizon item | executed; `CORRECTIONS.md` standing |

---

## 9. Model status

Unchanged. 384 relations over 56 glyphs; injectivity clean; exposure 74.1%;
residual 33.59 bits; inventory 82.5 CI [73.0, 93.7]; alphabet size in
[56, 83] with the floor now re-derived on the repaired skeleton and the
ceiling untouched. **Cumulative sweep total: 1.38 billion candidates plus
this cycle's 1,863 merges and 7 orderings, zero survivors.**

---

## 10. Horizon

1. **G2 then G1** on the 5080 with `eyerunner.py` — unchanged, in flight.
   Read `canary_integrity` first.
2. **The encounter-order construction family** (VectorAddUnique idiom) joins
   the external-data ledger alongside MSB counting and MDL segmentation:
   all three now wait on the glyph images / assets, which have become the
   single blocking resource for three independent vectors.
3. **The success criterion** (FR82 §7). Unchanged, and now sharpened by §5:
   the alphabet-size question, like the drift, is internally exhausted —
   every remaining question routes through external evidence.
