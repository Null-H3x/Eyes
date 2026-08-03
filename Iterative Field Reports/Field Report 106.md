# Field Report 106 — THE SEVENTEEN COLLAPSE FOR FREE: 91% OF ANCHOR PAIRS RESOLVE THE RATIO

*Instrument: `eyeresolve.py` (5/5 gate, canonical machinery). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — the nominated framing was wrong

FR105 closed by nominating *"identify which anchors are cross-group"*. That
framing does not survive inspection.

Work in the scale gauge `d2 = 1`. The unknowns are `d1` (17 candidates) and one
free base per component.

- **Two anchors in *different* components** each pin their own component's base
  and produce no cross-constraint — the inter-component offset is free, which is
  exactly FR27's packing freedom. **They discriminate nothing about the ratio.**
- **Two anchors in the *same* component** pin the base and then supply a known
  pair-difference `q[a] − q[b]`, which the model predicts as a function of `d1`.
  Different `d1`, different prediction.

**Discrimination comes from within-component pairs and only from them.** Pool
provenance is what *makes* a component's Δ table ratio-dependent, but the
acquisition-side question is not about provenance at all: it is which
within-component pair separates the seventeen predictions. Tenth horizon item
reframed rather than executed as written.

---

## 1. The measure

For each within-component pair `(a, b)`, the model predicts `q[a] − q[b] =
Δ_a − Δ_b` at each surviving ratio. Counting distinct predictions: **17 distinct
means the pair resolves the ratio outright; 1 means it is blind.**

Gate 5/5, including R1 (the single-drift build reproduces 384/0/56) and a
control confirming a non-survivor ratio is correctly rejected.

| component | glyphs | pairs | fully resolving | blind |
|---|---:|---:|---:|---:|
| 1 | 25 | 300 | **277 (92%)** | 23 |
| 2 | 11 | 55 | **50 (91%)** | 5 |
| 3 | 7 | 21 | **17 (81%)** | 4 |
| 4 | 3 | 3 | 2 (67%) | 1 |
| 5–9 | 2 each | 1 each | **1 (100%) each** | 0 |

> **351 of 384 within-component pairs — 91% — collapse the seventeen candidate
> readings to one.**

---

## 2. HEADLINE — the ambiguity is free

FR54's programme opens with **two anchors in component 1**. Component 1 has 300
pairs, of which **277 fully resolve**. So:

- an *arbitrary* component-1 anchor pair resolves the ratio with probability
  **0.92**;
- an acquirer working from the table in §3 can choose targets and resolve it
  with **certainty**, at no additional acquisition cost.

**This corrects two prior reports in the same direction, both over-charges:**

| claim | source | corrected |
|---|---|---|
| "the programme needs one more independent anchor than FR54 priced" | FR103 §3 | **No.** FR54's existing opening move resolves it. |
| "acquisition yields seventeen candidate alphabets, enumerable by hand" | FR104 §4 | **Only if targets are chosen blindly.** With the blind-pair table, seventeen collapse to one. |

The two-drift discovery (FR102) and the ratio narrowing (FR104/FR105) were real
and load-bearing. What was over-estimated each time was the *cost*, and each
estimate was made before the discriminating structure had been computed.

---

## 3. The 33 blind pairs, and why they cluster

The pairs that cannot resolve the ratio are not scattered. A pair is blind
exactly when `Δ_a − Δ_b` is ratio-independent, which happens when the two
glyphs' relation to each other rests on **single-drift-group evidence** — the
ratio cannot move them relative to one another. They therefore fall into tight
clusters:

**Component 1** — nine clusters:
`{0,1,27}` `{5,50}` `{6,7,47,57}` `{9,10,79,81}` `{17,62,63}` `{20,71}`
`{30,68}` `{34,45}` `{48,64}`

**Component 2** — `{13,44}` `{19,49,66}` `{25,60}`
**Component 3** — `{16,26,73}` `{21,40}`
**Component 4** — `{35,37}`

> **OPERATIONAL RULE FOR ACQUISITION.** Two anchors in the same component
> resolve the drift ratio outright **unless both glyphs come from the same
> blind cluster above.** Any other within-component pair collapses seventeen
> candidates to one. Anchors in *different* components never resolve it,
> however many are acquired.

That rule is worth more than the count: it converts a probabilistic hope into a
target specification.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| "Cross-group anchors resolve the ratio" | FR105 horizon 2 | **wrong frame** — resolution comes from within-component pairs only |
| Cross-component anchor pairs | untested for ratio power | **blind** — inter-component offset is free (FR27 packing) |
| Cost of the 17-way ambiguity | +1 anchor (FR103) / 17-way enumeration (FR104) | **zero** — FR54's opening move resolves it, 92% of pairs arbitrarily, 100% with target selection |
| Within-component pair power | unmeasured | **351 of 384 (91%) fully resolving**; 33 blind |
| Blind pairs | unknown | **enumerated and clustered** — 15 clusters across 4 components |
| Acquisition guidance | component ordering (FR54) | component ordering **plus** the blind-cluster exclusion |

---

## 5. Model status

384 relations over 56 glyphs; injectivity clean; exposure 74.1%; components
[25, 11, 7, 3, 2, 2, 2, 2, 2] — ratio-invariant. Alphabet [56, 83], floor 56.
**Drift: two parameters; ratio confined to 17 values, and resolvable at zero
marginal acquisition cost.** Cumulative: 27.16 billion candidates, zero
survivors.

---

## 6. Horizon

1. **Re-run FR54's ordering on canonical machinery under two drifts.** Still
   owed, and now the only unexecuted piece of the acquisition pricing. This
   cycle proves the partition and the pair-power structure; FR54's *yield*
   numbers were computed under one drift and deserve the direct check rather
   than the inference.
2. **Merge the blind-cluster table into the acquisition specification.** The
   deliverable an acquirer needs is one document: component ordering (FR54),
   which two glyphs to target first, and the blind pairs to avoid. It exists in
   pieces across FR54, FR105 and this report.
3. **Nothing further is owed on the ratio.** FR105 closed arithmetic reduction;
   this cycle closes the acquisition cost. The remaining drift work is
   acquisition, not analysis.
