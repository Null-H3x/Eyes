# Field Report 132 — THE CORRECTED READING: 191 POSITIONS, AND FR129/FR130's TARGETS WERE ALL ARTIFACTS

*Instrument: `eyeplain.py` (4/4 gate). Artifact: `PLAINTEXT_RELATIVE.txt`.*
*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. Rebuilt correctly

FR131 withdrew every reading artifact: they were built from `v` alone, with
`A_block` never computed, and the linking edges drew on dot cells that FR7's
doctrine says are variable interior. This rebuilds on `p`.

```
p = A_block + v,  A_block propagated along LETTERED cells only
edges 397   conflicts 0   drift-invariant at 1,2,3,7,11,41,82
```

**Parameter dependencies, per FR131's new standing check:** `p` depends on `Δ`
(determined by the skeleton), `d` (unknown, but the equality structure is
verified drift-invariant), and `A_block` (determined within a group, one free
gauge). Nothing else. Positions in different groups are **not comparable** and
are emitted as undetermined, never as unequal.

---

## 1. The reading

```
positions        : 191 (18.4% of corpus)
messages         : 7 of 9   (West 2 and West 3 absent)
distinct values  : 72
free parameters  : ONE global constant
```

| message | determined |
|---|---:|
| East 1 | 29/99 (29%) |
| West 1 | 38/103 (37%) |
| East 2 | 37/118 (31%) |
| East 3 | 47/137 (34%) |
| East 4 | 12/119 (10%) |
| West 4 | 15/120 (13%) |
| East 5 | 13/114 (11%) |

---

## 2. FR129's and FR130's targets were all artifacts

**Zero within-message equal pairs at distance ≤ 10.** Every one of FR129's
sixteen "robust crib targets", including FR130's four doubled-letter sites,
checks out as **not determined** — in each case one or both positions falls
outside the valid group:

```
East 4  33== 34   not determined (both missing)
East 4  78== 79   not determined
East 4 109==110   not determined (both missing)
East 5  86== 87   not determined
East 3  32== 34   not determined (both missing)
West 3  74== 76   not determined (both missing)
```

**FR130's entire experiment therefore tested nothing** — 46 informative
placements against sites that the corrected reconstruction does not determine.
Its conclusion (zero fits, consistent with chance) is unaffected in substance
because it was already a null, but its *premise* is withdrawn.

---

## 3. What the 232 equal-pairs actually are

```
within one message : 41   -- minimum distance 11, maximum 109
across messages    : 191
   at the SAME offset (shared passages): 15
     East 1 / West 1  12      West 1 / West 4  1
     East 2 / West 4   1      East 4 / East 5  1
```

> **The nearest plaintext repeat within any message is at distance 11.** There
> are no doubled letters, no `X_X`, no short-range structure at all in the
> determined region.

This corroborates FR126 independently: that cycle found no cross-block
short-range coincidence excess under a correct null; this one finds no
short-range repeats *at all*. Two different routes, same answer.

The 12 same-offset East 1 / West 1 pairs are the near-duplicate structure
surviving into the corrected reading — the one piece of FR123's visible
structure that was real.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Reading artifact | `v`-based, invalid off-block | **`PLAINTEXT_RELATIVE.txt`** — 191 positions, `A_block` solved, 0 conflicts |
| FR129's 16 crib targets | "robust" | **all undetermined** — artifacts of `v`-comparison |
| FR130's 4 doubled sites | robust targets | **undetermined**; the experiment tested nothing |
| Short-range plaintext repeats | none detected (FR126) | **none exist** in the determined region; nearest is distance 11 |
| Shared passages in plaintext | 26 "novel" runs (FR131, withdrawn) | **15 same-offset cross-message pairs**, 12 of them East 1 / West 1 |
| Coverage vocabulary | "exposure" used loosely | **exposure 74.1%** (glyphs determined) vs **relative-plaintext 18.4%** — distinct quantities |

---

## 5. Model status

Unchanged structurally. **Relative-plaintext reading: 191 positions (18.4%),
7 of 9 messages, one free constant, drift-invariant, zero propagation
conflicts.** Repair A gives 108. Cumulative: 27.16 billion candidates, zero
survivors.

---

## 6. Horizon

1. **Crib testing must be re-based on this artifact.** `eyehypo.py`,
   `eywordsC.py` and `eyedouble.py` all consume the withdrawn readings and will
   silently test undetermined positions. They need the `p`-based map.
2. **Word cribs are now much weaker than FR121/FR125 suggested.** With 191
   positions and no short-range repeats, almost no word pattern is testable at
   all — the honest power is near zero, and that should be measured rather than
   assumed.
3. **The 41 within-message equal pairs at distance 11–109 are the only
   internal repeat structure that exists.** If anything is a crib target, it is
   those — long-range, which suits repeated *words in a list* far better than
   repeated letters in a word.
