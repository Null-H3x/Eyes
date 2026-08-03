# Field Report 129 — TWO SERIOUS READINGS, 98.76% AGREED, AND SIXTEEN ROBUST CRIB TARGETS

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. CHALLENGE I — "32 readings" overstates the ambiguity

FR127 reported 62 viable repairs giving 32 distinct readings, and FR128 ranked
them by evidential cost. Reading the ranking's *shape* rather than its length:

```
cost   x worse than best
 5.8                   1     drop East 1@68        (repair C)
 7.7                  79     drop East 4@51
 9.6                6310
11.5              501187
```

```
readings within  100x of the best : 2
readings within 1000x of the best : 2
```

> **There are TWO serious candidates, not 32.** The gap after the runner-up is
> ~4,000×. Everything from rank 3 down asserts something at least six thousand
> times less probable than repair C.

---

## 1. The two readings, and how much they differ

| | drops | cost | relations | glyphs | eq | positions |
|---|---|---:|---:|---:|---:|---:|
| **R1** | East 1@68 | **5.8** | 409 | 57 | 1 | 686 |
| R2 | East 4@51 | 7.7 | 417 | 56 | 5 | 683 |

On their 659 common positions:

```
position pairs            : 216,811
AGREED EQUAL (both say =) :   1,499
agreed unequal            : 212,628
DISPUTED                  :   2,684  (1.24%)
```

> **98.76% of the equality relation is agreed by both serious readings.**

Every position participates in *some* disputed pair, so there is no clean
consensus *subset of positions*. **The consensus is at the pair level**, and
that is the object worth having: a hypothesis resting only on agreed pairs is
**robust to the repair choice**.

---

## 2. The deliverable: sixteen robust crib targets

Agreed-equal pairs within one message at distance ≤ 10 — the shapes a word
hypothesis actually uses:

| distance | count | targets |
|---:|---:|---|
| **1** (doubled letter) | 4 | East 4 33=34, East 4 78=79, East 4 109=110, East 5 86=87 |
| **2** (X_X) | 7 | East 2 102=104, East 3 32=34, East 3 56=58, East 3 121=123, West 3 74=76, West 4 31=33, West 4 74=76 |
| 3 | 2 | West 4 84=87, … |
| 4, 5, 7 | 3 | |

**These sixteen are supported whichever repair is right.** A Finnish word with
a doubled letter placed at East 4 33, East 4 78, East 4 109 or East 5 86 tests
a claim the model makes robustly, not one contingent on an unresolved fork.

The four distance-1 targets are the same shape FR126 flagged sub-threshold
(d = 1 at z = +2.73) and that FR121's vocabulary was hunting — Finnish doubles
`AA UU II KK LL MM NN SS TT`.

---

## 3. What this changes

**The repair ambiguity is a 1.24% uncertainty, not a 32-way fork.** FR127
framed it as the latter and FR128 ranked it; this cycle measures its actual
size. Practically the project has **one reading with a small, localised
uncertainty** — not thirty-two competing ones.

That also retro-justifies FR122–FR125, which built on repair C alone: the
artifacts they produced are ~99% correct even if repair C is the wrong choice
between the two survivors.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Repair ambiguity | 32 distinct readings (FR127) | **2 serious candidates**; rank 3 is 6,310× worse |
| Reading agreement | unmeasured | **98.76% of the equality relation agreed** |
| Consensus object | assumed position-level | **pair-level** — every position touches a disputed pair |
| Robust crib targets | none identified | **16 agreed-equal pairs at distance ≤10**, listed |
| FR122–125 artifacts | repair-C-conditional | **~99% robust** to the surviving fork |

---

## 5. Model status

**R1** (repair C, cost 5.8): 409 relations, 57 glyphs, 1 homophone, 686
positions, drift forced, unique across drifts. **R2** (cost 7.7): 417
relations, 56 glyphs, 5 homophones, 683 positions. Agreement 98.76%.
**Repair A** remains the bijective alternative at 44.5% coverage with 17
ratios. Cumulative: 27.16 billion candidates, zero survivors.

---

## 6. Horizon

1. **Target the four distance-1 sites with Finnish doubles.** They are robust,
   they are the shape the language predicts, and `eyehypo.py` consumes them
   directly. This is the narrowest, best-supported crib target the project has
   produced.
2. **A crib on a DISPUTED pair discriminates R1 from R2** — 2,684 such pairs
   exist, so the fork is decidable by exactly the same machinery.
3. **`q[36] = q[68]` remains the sharpest external lever**, forced by every
   high-coverage repair including both survivors.
