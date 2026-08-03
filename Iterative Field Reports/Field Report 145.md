# Field Report 145 — THE EXTENDED SKELETON: 794 RELATIONS, 435-POSITION READING

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. CHALLENGE I reframes the pricing question

FR144 ended by asking for the new T1 bridge to be priced on FR128's cost scale.
That scale prices what a repair asserts is **spurious**:
`drop cost = k · log₁₀(83)`. Adding a class asserts the opposite — that it is
**genuine** — and for a class with surprise `s` the odds genuine:chance are
about `10^s : 1`:

```
surprise 1.70 -> add cost ~ 0.0086
surprise 3.14 -> add cost ~ 0.0003
surprise 7.20 -> add cost ~ 0.0000
```

**Adding any positive-surprise class is essentially free.** So the question is
not what one bridge costs, but whether the nineteen informative non-atlas
classes are **jointly consistent** — a computation, not a judgement.

---

## 1. They are, and the result is large

Added greedily in surprise order to repair A's pool:

```
added      : 19 of 19
skipped    :  0
conflicts  :  0 at every one of the 82 drifts
partitions :  1 (stable)
```

| | relations | glyphs | equalities | components | exposure |
|---|---:|---:|---:|---|---:|
| repair A | 384 | 56 | 0 | [25,11,7,3,2,2,2,2,2] | 74.1% |
| repair C | 409 | 57 | 1 | [26,11,7,3,2,2,2,2,2] | 75.0% |
| **A + 19 classes** | **794** | **61** | 8 | **[37,16,4,2,2]** | **79.1%** |

Equalities: `(2,16) (4,60) (10,75) (19,35) (22,64) (36,68) (37,66) (42,74)` —
eight homophone pairs, so the alphabet is ≤ 75.

---

## 2. SELF-CORRECTION — a bug that inverted the reading

My first reading computation gave **72 positions in one message**, far worse
than repair C's 191. That is backwards for a richer skeleton, which is what
made it worth chasing.

**The bug:** I gated `A_block` linking edges on *component* difference
(`cm[g1] != cm[g2]`) instead of *block* difference (`blk[A] != blk[B]`). Two
blocks in the **same component but different messages** are still different
blocks and must be linked. Merging components — which the extra classes do —
therefore destroyed the edges instead of adding them.

`eyeplain.py` has this right; my ad-hoc rebuild did not. Corrected:

```
repair A (baseline)      384 rel 56 gly 0 eq | reading 108 pos, 3 msgs, 0 conflicts
repair C (adopted)       409 rel 57 gly 1 eq | reading 191 pos, 7 msgs, 0 conflicts
repair A + 19 classes    794 rel 61 gly 8 eq | reading 435 pos, 8 msgs, 0 conflicts
```

> **435 positions across 8 of 9 messages, zero propagation conflicts — 2.3x
> repair C's reading.**

---

## 3. What is being assumed

**Nineteen classes the atlas omits are being treated as genuine.** Their
surprises run from 3.14 down to ~1.38. For comparison, **#M⁻ — an atlas member,
and until FR144 the sole T1 bridge — has surprise 1.70.** So the strongest
additions are better attested than an atlas class the model already relies on,
and the weakest are slightly worse.

**This is not FR35's error.** That warned against adding cells because they fail
to contradict. These are added because they are *statistically well-attested
isomorph classes*, and consistency is checked afterwards rather than used as the
criterion.

**But it is a real assumption**, and it is new. The atlas's selection principle
remains unknown (FR136); these nineteen may have been excluded for a reason
nobody recorded.

**Eight homophones** is a larger departure from bijectivity than repair C's one.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Cost of adding a class | unpriced | **~0 for any positive surprise**; the question is joint consistency |
| The 19 informative classes | individually tested (FR144) | **jointly consistent**, 0 conflicts at all 82 drifts |
| Best skeleton | repair C, 409/57 | **repair A + 19, 794/61**, exposure 79.1% |
| Best reading | 191 positions, 7 messages | **435 positions, 8 messages**, 0 conflicts |
| Alphabet ceiling | ≤ 82 (one homophone) | **≤ 75** on this reading (eight homophones) |
| Block linking | — | edges gate on **block**, not component; merging components destroys edges if gated wrongly |

---

## 5. Model status

**A materially better reading now exists and has not been adopted.** Repair C
remains the standing position pending a decision on whether nineteen non-atlas
classes should be trusted. Cumulative: 27.16 billion candidates, zero survivors.

---

## 6. Horizon

1. **Decide on the nineteen.** The evidence is: surprises 1.38–3.14 against
   #M⁻'s 1.70, joint consistency at every drift, zero reading conflicts, and
   2.3× the coverage. Against: the atlas excluded them for unknown reasons and
   eight homophones is a large departure.
2. **If adopted, everything downstream needs rebuilding** — the reading, the
   working assumptions, the repair ranking, the acquisition spec.
3. **The 48 contradictory non-atlas classes are still unexamined**, and under a
   non-bijective reading some may be admissible.
