# Field Report 187 — THE ATTRIBUTION WAS WRONG, BUT THE PREDICTION WAS RIGHT

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. Self-correction first

FR186 reported that **four of the eight homophones trace to a single L=9 class**
(E1@41, E1@69, W1@41, W1@71, E2@46, E2@81), and predicted that removing it would
drop the count to four.

**Removing it changes nothing.**

```
WITH the class    : 794 rel, 61 gly, 8 eq, IC 0.01268
WITHOUT it        : 794 rel, 61 gly, 8 eq, IC 0.01268
```

Identical in every figure. **My attribution method was a first-match search** —
"the first class in iteration order that forces this equality" — which finds
iteration order, not causation. The homophones are forced redundantly by several
classes, so no single removal touches them.

---

## 1. The right question, and it vindicates the prediction

The correct question is not *which class causes each homophone* but **is there a
class selection with fewer homophones that keeps the relations and coverage?**

Greedily accepting classes subject to an equality cap:

```
cap 1: 424 rel, 58 gly, 1 eq,  6 classes
cap 2: 450 rel, 59 gly, 2 eq, 11 classes
cap 3: 685 rel, 61 gly, 3 eq, 15 classes
cap 4: 685 rel, 61 gly, 3 eq, 15 classes   <- saturates at 3
cap 6: 685 rel, 61 gly, 3 eq, 15 classes
```

**The greedy saturates at three.** Caps of 4, 5 and 6 accept nothing further —
there is a natural selection at three homophones and the model does not need
eight.

---

## 2. The comparison

```
model                   rel  gly  eq  largest  exposed  frag       IC   1/IC
standing (19 classes)   794   61   8      491      819     5  0.01268   78.9
low-homophone (cap 3)   685   61   3      464      819     7  0.01258   79.5
```

**Same 61 glyphs. Same 819 exposed positions.** The low-homophone selection
gives up 109 relations and 27 positions in the largest fragment, and in exchange
drops **five homophones**.

```
IC PREDICTION (FR186) : ~4 merges, alphabet ~79
low-homophone model   :  3 merges, alphabet 79.5
```

> **The prediction was right even though the attribution was wrong. The
> plaintext's coincidence rate said the model carries about four merges too
> many, and a selection exists with exactly that many fewer.**

Its equalities are `(2,16)`, `(22,64)`, `(36,68)` — the last two being the
**invariant homophones** forced by the fixed-point alignment (FR158/FR168), and
therefore not optional. Only `(2,16)` is discretionary.

---

## 3. What this means

**The eight homophones were never load-bearing.** Five of them are consequences
of a class selection that FR146 adopted on mutual-prediction grounds without
ever asking what they cost in coincidence.

**The alphabet ceiling moves.** `83 − 3 = 80`, against the standing `83 − 8 = 75`
— and the IC's independent estimate is **79.5**. Three measurements converge:
the coincidence rate, the merge count, and the ceiling.

**The tension FR185 opened is resolved in the IC's favour.** It did not require
discarding the model; it required noticing that the model had more homophones
than the plaintext supports, and that a cheaper selection was available.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| FR186's four-homophone attribution | claimed | **WITHDRAWN** — first-match search, removal changes nothing |
| Homophones forced redundantly | unknown | **yes** — no single class removal affects any |
| Minimum homophones with full glyph coverage | 8 (standing) | **3**, at 685 relations and the same 61 glyphs |
| Alphabet ceiling | ≤ 75 | **≤ 80**, and the IC estimate is 79.5 |
| Which homophones are optional | unknown | **only `(2,16)`** — the other two are the invariant pair |
| FR185's tension | open | **resolved**: the model carried more merges than the plaintext supports |

---

## 5. Model status

**Two selections now stand**, and the choice is a real one:

- **standing**: 794 relations, 8 homophones, largest fragment 491
- **low-homophone**: 685 relations, 3 homophones, largest fragment 464

Both give 61 glyphs and 819 exposed positions. The second agrees with the
plaintext's own statistics; the first buys 109 relations by asserting five
merges the coincidence rate does not support.

Cumulative: 27.16 billion candidates, zero survivors.

---

## 6. Next iteration

**Price the two selections against each other on the FR128 scale** — what does
each assert, and at what cost? The low-homophone model asserts fewer merges but
accepts fewer classes; the standing model asserts more of both. That is exactly
the comparison FR128 was built for, and it has never been run on this axis.
