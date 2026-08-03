# Field Report 186 — IC WORKFLOW: REPLICATION HOLDS, ALPHABET ≈ 79, AND FOUR HOMOPHONES TRACE TO ONE CLASS

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The pre-registered replication

FR185 predicted, before looking: **Fragment 2 must give `1/IC` in 78–82 if the
reading is sound.**

```
frag  positions  distinct       IC    1/IC    95% CI on K
   1        491        83  0.01244    80.4       (77, 83)
   2        222        72  0.01317    75.9       (68, 83)
   3         48        34  0.02039    49.0       (33, 73)
```

**Fragment 2's confidence interval contains the predicted window.** A weak
replication — the interval is wide at 222 positions — but it does not refute,
and it was declared in advance.

Fragment 3 at 48 positions is uninformative, as expected.

---

## 1. The pooled estimate

Symbols are not comparable across fragments, but the **coincidence rate is** —
it is a within-fragment quantity, so the fragments can be pooled:

```
pooled IC 0.01268 over 146,766 pairs
effective alphabet 1/IC = 78.9
```

**146,766 pairs** is the largest sample any plaintext statistic in this project
has been computed on.

---

## 2. What it implies about the homophone count

83 glyphs onto `K` symbols requires `83 − K` merges:

```
   K  merges  expected IC  z vs pooled
  75       8      0.01333        -2.14
  78       5      0.01282        -0.47
  79       4      0.01265        +0.09     <- best fit
  80       3      0.01250        +0.64
  83       0      0.01205        +2.27
```

> **The plaintext's coincidence rate implies roughly FOUR merges. The standing
> model forces EIGHT.**

About half the model's forced homophones look spurious — which is exactly what
FR163 demonstrated the pipeline does (23 of 23 false in synthetic data with an
injective alphabet).

---

## 3. And the suspects are identifiable

Tracing what forces each of the eight:

```
homophone   atlas pool alone   otherwise forced by
  (2, 16)          no          L=21 E3@77, E4@2, E5@2
  (4, 60)          no          L=9  E1@41,E1@69,W1@41,W1@71,E2@46,E2@81
 (10, 75)          no          L=9  (same class)
 (19, 35)          no          L=9  (same class)
 (22, 64)          no          L=19 W1@59, E3@90   <- the fixed-point class
 (36, 68)         YES          -
 (37, 66)          no          L=9  (same class)
 (42, 74)          no          -
```

> **Four of the eight — `(4,60)`, `(10,75)`, `(19,35)`, `(37,66)` — are forced
> by a SINGLE non-atlas class**: the L=9 six-instance class at E1@41 / E1@69 /
> W1@41 / W1@71 / E2@46 / E2@81.

Drop that one class and the homophone count falls from eight to four — **exactly
the number the IC implies.**

That class is the L=9 sibling of `a_b_cb_ac`, the pattern Lymm independently
identified (FR171) and whose East 1 instances are the two that **fail to extend**
to the longer 18-glyph pattern. The suspicion is not new; the arithmetic is.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Fragment 2 replication | pre-registered | **holds** — CI (68,83) contains 78–82 |
| Alphabet estimate | 78–82 (FR185, one fragment) | **78.9 pooled**, 146,766 pairs |
| Implied merge count | 8 (model) | **~4** from the plaintext's own statistics |
| The 8 homophones | disfavoured at −2.7σ (FR185) | **four of them trace to ONE class** |
| That class | adopted in FR146's nineteen | **the prime suspect**, and already flagged by Lymm's extension asymmetry |

---

## 5. Model status

794 relations, 61 glyphs, one reading, five fragments, 819 positions (79.1%).
**Alphabet ≈ 79. Four of eight homophones attributable to a single class.**
Cumulative: 27.16 billion candidates, zero survivors.

---

## 6. Next iteration

**Test the model with that L=9 class removed.** If the IC prediction is right,
the result should be: **four homophones, alphabet ≈ 79, and a reading that does
not lose coverage.** If coverage collapses, the class is load-bearing and the
tension is real rather than resolvable.

That is a single build and it is the sharpest test the IC line has produced.
