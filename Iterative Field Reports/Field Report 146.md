# Field Report 146 — THE NINETEEN ARE GENUINE: MUTUAL PREDICTION AT 100% AGAINST A 2.8% CONTROL

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The decision, made by test rather than preference

FR145 produced a materially better skeleton by adding nineteen non-atlas
isomorph classes, and left the adoption decision open. **FR38's machinery
settles it.**

Remove a class entirely, rebuild from the others, then predict its own held-out
cells. Nothing from that class survives, so any prediction must arrive from
elsewhere through shared glyphs.

---

## 1. The result

```
[1] the 19 non-atlas classes predicting ATLAS classes : 85/85   (100%)
[2] the ATLAS predicting the 19 non-atlas classes     : 32/32   (100%)
[3] NEGATIVE CONTROL, 400 fabricated classes          :  5/178  (2.8%)
```

**Prediction is perfect in both directions.** The classes the atlas omits
predict the classes it contains, and vice versa, out-of-sample.

**The control is not vacuous.** 400 fabricated classes with matching length and
instance profiles score 2.8%. At that chance rate, the probability all 32 real
cells agree is **2.3 × 10⁻⁵⁰**.

> **The nineteen carry the same signal as the atlas. They are genuine.**

---

## 2. What is adopted

| | relations | glyphs | eq | components | exposure | reading |
|---|---:|---:|---:|---|---:|---|
| repair A | 384 | 56 | 0 | [25,11,7,3,2×5] | 74.1% | 108 pos, 3 msgs |
| repair C | 409 | 57 | 1 | [26,11,7,3,2×5] | 75.0% | 191 pos, 7 msgs |
| **EXTENDED** | **794** | **61** | 8 | **[37,16,4,2,2]** | **79.1%** | **435 pos, 8 msgs** |

Zero propagation conflicts. Stable partition and identical relation count at
every one of the 82 drifts.

Homophones: `(2,16) (4,60) (10,75) (19,35) (22,64) (36,68) (37,66) (42,74)` —
**eight pairs, so the alphabet is ≤ 75.**

**`q[36] = q[68]` survives** into the extended reading, so the FR144 anchor-pair
test is unaffected.

---

## 3. What this costs, stated plainly

**Eight homophones instead of one.** A much larger departure from bijectivity,
and the alphabet ceiling falls from 82 to 75.

**Nineteen classes the community excluded are now load-bearing.** FR136 showed
the atlas's selection principle is unknown; the mutual-prediction result says
the exclusions were not made on coherence grounds, but it does not say why they
were made.

**The reading more than doubles but is still 42% of the corpus.** 435 of 1,036
positions, 8 of 9 messages (West 2 remains dark).

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| The 19 non-atlas classes | consistent, unpriced | **GENUINE** — 100% mutual prediction vs 2.8% control |
| Standing skeleton | repair C, 409/57 | **EXTENDED, 794/61**, exposure 79.1% |
| Standing reading | 191 positions, 7 msgs | **435 positions, 8 msgs**, 0 conflicts |
| Alphabet ceiling | ≤ 82 | **≤ 75** (eight forced homophones) |
| Atlas completeness | matters (FR144) | **and the omissions are recoverable by test** |
| `q[36]=q[68]` | forced under repair C | **still forced** — the anchor-pair test is unaffected |

---

## 5. Model status

**ADOPTED: the extended skeleton.** 794 relations over 61 glyphs, eight
homophones, components [37,16,4,2,2], 79.1% exposure, 435-position reading
across 8 of 9 messages with zero propagation conflicts, drift-stable at all 82
values. Cumulative: 27.16 billion candidates, zero survivors.

---

## 6. Horizon

1. **Rebuild the artifacts on the extended skeleton** — `PLAINTEXT_RELATIVE.txt`,
   `WORKING_ASSUMPTIONS.md`, `CURRENT_STATE.md`, `CIPHER_FORMULA.md`,
   `ACQUISITION_SPEC.md`. All currently describe repair C.
2. **Re-run the acquisition arithmetic.** Five components instead of nine means
   fewer anchors: the 11-anchor figure is stale and almost certainly falls.
3. **Re-run the word-crib power measurement.** 0.32% was computed on 191
   positions; 435 positions with larger components should raise it materially.
4. **The 48 contradictory non-atlas classes remain unexamined.**
