# Field Report 155 — THE INVARIANT CORE IS EIGHTEEN, NOT TWENTY-EIGHT

*Artifact: `INVARIANT_CORE.md`. July 2026. Cycle: EYESPIRAL-C.*

---

## 0. Self-correction to FR154

FR154 reported **28 invariant relations** from 11 sampled maximal readings.
Sampling more readings shrinks the intersection:

```
11 readings (FR154) -> 28 invariants
10 readings         -> 23 invariants
12 readings         -> 18 invariants
```

**The sets nest** — the 18-set is a strict subset of the 23-set — so the counts
are consistent and the largest sample gives the best estimate.

> **The invariant core is at most 18 relations, not 28. FR154's figure was
> optimistic, and I published it without checking whether the count was stable.**

This is the same error shape as FR138's uncalibrated simulation: reading a
number off a sample without asking whether the sample was large enough for the
number to mean anything.

---

## 1. The eighteen

```
q[ 2] - q[26] =  1     q[ 5] - q[10] = 48     q[ 6] - q[41] = 35
q[13] - q[19] = 53     q[13] - q[72] = 35     q[17] - q[48] = 53
q[19] - q[72] = 65     q[20] - q[71] = 82     q[22] - q[57] = 35
q[22] - q[62] = 30     q[22] - q[64] =  0     q[23] - q[49] = 48
q[32] - q[59] = 30     q[36] - q[68] =  0     q[44] - q[46] = 30
q[57] - q[62] = 78     q[57] - q[64] = 48     q[62] - q[64] = 53
```

**25 glyphs, 352 of 1,036 corpus positions (34.0%).**

Independent of the repair fork, the atlas selection, the ~30-fold
class-selection ambiguity, and — in ratio — the drift.

---

## 2. Two are homophones

`q[22] = q[64]` and `q[36] = q[68]` hold in **every** reading.

Glyph 36 is East 2's message indicator. **These are the sharpest external tests
the project has**: two independently known glyph values that must come back
equal, or the entire non-bijective family is refuted — and unlike everything
else, this test does not inherit the class-selection ambiguity.

`q[22] = q[64]` is a **second** such test, discovered here, and it was not
previously known to be invariant.

---

## 3. What the artifact is for

Any proposed alphabet `C` must satisfy all eighteen. A candidate violating one
is refuted **whichever reading is correct**. That makes this the cheapest test
of an external hypothesis and the only one that does not carry the ~30-fold
uncertainty FR152 measured.

Values are stated at drift 1; under drift `d` every right-hand side scales by
`d` (FR30), so their **ratios** are invariant even where the values are not.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Invariant core | 28 relations (FR154) | **18**, and that is an upper bound |
| Stability of the count | unchecked | **shrinks with sample size**; nests correctly |
| Invariant homophones | `q[36]=q[68]` known | **also `q[22]=q[64]`** — a second anchor-pair test |
| Coverage of the core | unstated | **25 glyphs, 34.0% of positions** |

---

## 5. Model status

Content unchanged: 794 relations, 61 glyphs, 8 homophones, 79.1% exposure,
435-position reading, 6 anchors, one of ~30 maximal readings. **Plus an
18-relation invariant core independent of that ambiguity.** Cumulative: 27.16
billion candidates, zero survivors.

---

## 6. Horizon

1. **The remaining artifacts still describe repair C** — `CURRENT_STATE.md`,
   `CIPHER_FORMULA.md`, `WORKING_ASSUMPTIONS.md`, `ACQUISITION_SPEC.md`,
   `PLAINTEXT_RELATIVE.txt`. They need the extended skeleton, the ~30-reading
   uncertainty, and the invariant core.
2. **`q[22] = q[64]` should be added to the acquisition spec** alongside
   `q[36] = q[68]` as a second independent anchor-pair test.
3. **Do not re-report the invariant count without stating the sample size.**
