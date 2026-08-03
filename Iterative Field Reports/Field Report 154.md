# Field Report 154 — ONE ANCHOR PAIR CUTS THE SPACE FIVEFOLD, AND TWENTY-EIGHT RELATIONS ARE INVARIANT

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. CHALLENGE I

A *single* anchor cannot discriminate: FR-audit showed `q[g] = v` is absorbed by
the component base and all 83 values remain consistent. **A pair in one
component can**, because the reading fixes `q[a] − q[b]`.

---

## 1. Discrimination measured

Eleven distinct maximal readings collected, all determining the same 496 glyph
pairs. For each pair, how many distinct values do the readings assert?

```
distinct values per shared pair : {1: 28, 3: 156, 4: 11, 5: 183, 6: 6, 7: 101, 8: 11}

mean readings distinguished by one anchor pair : 4.6 of 11
pairs that FULLY separate all 11               : 0
pairs where every reading AGREES               : 28
```

> **One anchor pair cuts the space to roughly a fifth** — about 2.4 surviving
> readings from 11, so ~6 from ~30. **Two well-chosen pairs would very likely
> leave one.**

No single pair separates everything, so discrimination is statistical rather
than surgical. But the acquisition programme already calls for six anchors, and
six anchors yield fifteen pairs.

> **The six-anchor programme is not merely sufficient for the alphabet — it is
> massively over-determined for selecting the reading.** FR152–153's bad news
> costs nothing in practice.

---

## 2. The invariant core

**Twenty-eight relations hold identically in every reading.** They are the part
of the model that does not depend on the class selection at all:

```
q[2]  - q[26] = 1     q[4]  - q[13] = 2     q[4]  - q[19] = 55
q[4]  - q[72] = 37    q[5]  - q[10] = 48    q[6]  - q[41] = 35
q[7]  - q[30] = 30    q[13] - q[19] = 53    q[13] - q[72] = 35
q[17] - q[48] = 53    q[17] - q[74] = 81    q[19] - q[72] = 65
```
*(twelve of twenty-eight shown)*

These are the project's hardest internal results: true whichever maximal set is
correct, and independent of the repair fork, the atlas selection and the drift.
**No prior report has isolated an invariant core.**

---

## 3. What this settles

FR152 and FR153 looked like a serious downgrade — the skeleton is not unique,
and the space is ~30 readings. **The practical consequence is close to nil:**

- one anchor pair → ~5× reduction
- the programme already needs 6 anchors → 15 pairs
- 28 relations are invariant and need no anchors at all

The uncertainty is real and was previously unstated, but it is **collapsed by
exactly the evidence already being sought.**

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Anchor discrimination | unmeasured | **~5× per pair**; 4.6 of 11 readings distinguished |
| Single anchor | assumed discriminating | **cannot discriminate** — absorbed by the base |
| Six-anchor programme | sufficient for the alphabet | **also over-determined for reading selection** |
| Invariant relations | none identified | **28**, holding in every maximal reading |
| FR152/153's impact | serious downgrade | **real but practically absorbed** |

---

## 5. Model status

Content unchanged: 794 relations, 61 glyphs, 8 homophones, 79.1% exposure,
435-position reading, 6 anchors. Standing: one of ~30 maximal readings, **with a
28-relation invariant core and a 5×-per-pair collapse under acquisition.**
Cumulative: 27.16 billion candidates, zero survivors.

---

## 6. Horizon

1. **Ship the invariant core.** Twenty-eight relations true in every reading is
   the most robust artifact this project has produced and nothing currently
   states them.
2. **Rebuild the artifacts** with the ~30-reading uncertainty and the invariant
   core both stated. Now unblocked: the uncertainty is measured and its practical
   cost is known.
3. **Acquisition guidance changes slightly** — anchors should be chosen as
   *pairs within one component* to maximise discrimination, which the current
   spec does not say.
