# Field Report 147 — SIX ANCHORS, NOT ELEVEN

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The consequential number

The extended skeleton (FR146) collapses nine components into five. That changes
the acquisition arithmetic, which is the figure deciding whether this is
finishable.

```
components : [37, 16, 4, 2, 2]   61 glyphs   exposure 819/1036 = 79.1%

  comp  glyphs  positions  % corpus
     1      37        491     47.4%
     2      16        222     21.4%
     3       4         48      4.6%
     4       2         29      2.8%
     5       2         29      2.8%
```

**Unknowns after the skeleton:** 5 component bases + 1 drift − 1 gauge = **5
independent unknowns.**

---

## 1. The yield curve

```
 2 anchors ->  491 positions (47.4%)   [component 1]
 3 anchors ->  713 positions (68.8%)   [+ component 2]
 4 anchors ->  761 positions (73.5%)
 5 anchors ->  790 positions (76.3%)
 6 anchors ->  819 positions (79.1%)   [all]
```

| | old (repair A/C) | **extended** |
|---|---|---|
| anchors for a full solve | 11 | **6** |
| first-tranche yield | 3 anchors → 31.2% | **2 anchors → 47.4%** |
| final exposure | 75.0% | **79.1%** |

> **The programme is now six anchors, and the first two buy nearly half the
> corpus.** The two-anchor opening works because the first fixes component 1's
> base and the second supplies a pair-difference, which is bijective in the
> drift (FR26) and therefore pins it for the whole system.

That is a 45% reduction in what has to be acquired, and it comes entirely from
classes that were sitting in the corpus unexamined.

---

## 2. Word-crib power: better, still not usable

```
EXTENDED READING: 435 positions, 8 messages, 0 conflicts

  marjatta   k=3   17/847   2.01%
  kysymys    k=3   17/855   1.99%
  kaikki     k=3   16/863   1.85%
  maailma    k=3   12/855   1.40%

  words with any testable placement : 18 of 18   (was 16 of 18)
  MEAN POWER: 0.84%    (FR134 on 191 positions: 0.32%)   improvement 2.6x
```

**Every word is now testable somewhere**, where two had zero placements before.
But 0.84% mean power means a word that *is* in the corpus would still be
detected roughly one time in 120.

**FR134's closure of the word-crib route stands.** The improvement is real and
the conclusion is unchanged: the route needs the coverage that solving
provides.

---

## 3. Doctrine changes

| item | prior status | status now |
|---|---|---|
| **Anchors for a full solve** | **11** | **6** |
| First-tranche yield | 3 anchors → 31.2% | **2 anchors → 47.4%** |
| Final exposure | 75.0% | **79.1%** |
| Independent unknowns | 9 bases + drift | **5 bases + drift**, one gauge |
| Word-crib power | 0.32% | **0.84%**, 18 of 18 words testable |
| Word-crib route | closed (FR134) | **still closed** — 2.6× is not enough |

---

## 4. Model status

Extended skeleton: 794 relations over 61 glyphs, eight homophones, components
[37,16,4,2,2], 79.1% exposure, **435-position reading across 8 of 9 messages
with zero conflicts**, drift-stable at all 82 values. Alphabet ≤ 75.
**Acquisition: 6 anchors.** Cumulative: 27.16 billion candidates, zero
survivors.

---

## 5. Horizon

1. **Rebuild the shipped artifacts.** `PLAINTEXT_RELATIVE.txt`,
   `CURRENT_STATE.md`, `WORKING_ASSUMPTIONS.md`, `CIPHER_FORMULA.md` and
   `ACQUISITION_SPEC.md` all describe repair C and are now stale on the
   headline figures.
2. **The 48 contradictory non-atlas classes remain unexamined**, and under an
   eight-homophone reading some may now be admissible.
3. **West 2 is still dark** — the one message absent from the 435-position
   reading, and the obvious next target for a bridge search.
