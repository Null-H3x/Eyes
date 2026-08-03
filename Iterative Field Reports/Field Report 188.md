# Field Report 188 — THE STANDING MODEL SURVIVES THE IC CHALLENGE, BY ABOUT 20×

*July 2026. Cycle: EYESPIRAL-C. Closing the IC line.*

---

## 0. The comparison FR187 set up

Two selections, same 61 glyphs, same 819 exposed positions:

```
standing      : 794 relations, 8 homophones, 19 classes accepted
low-homophone : 685 relations, 3 homophones, 15 accepted, 4 rejected
```

FR128's rule says rank by **what each must assert**. Each asserts that its
accepted classes are genuine and its forced merges are real; the low-homophone
model additionally asserts that **four rejected classes are not co-plaintext.**

---

## 1. The IC prices the merges directly

If the plaintext is uniform over `K = 83 − m`, the observed IC has a likelihood
under each `m`. That is a proper likelihood, not a heuristic:

```
merges    K  log-likelihood   vs best
     0   83          6.100     -1.941
     3   80          7.887     -0.154
     4   79          8.041      0.000   <- ML estimate
     5   78          7.940     -0.100
     8   75          6.089     -1.951

log10 likelihood ratio, 3 merges vs 8 : +0.78   (~6x)
```

**The plaintext's maximum-likelihood merge count is four**, and it favours three
over eight by about sixfold. Real, and small.

---

## 2. A correction to my own pricing

I first priced "reject a class" at its **pattern surprise** — 1.19 to 1.66 each,
5.97 total. **That assumes isomorph implies co-plaintext, which FR151 refuted.**

The correct prior comes from the corpus:

```
P(a strong class IS co-plaintext) = 160/208 = 0.769   -> accept costs 0.114
P(a strong class is NOT)          =  48/208 = 0.231   -> reject costs 0.637
```

Rejecting is only **4.4× more surprising than accepting**, not the 43× the
pattern-surprise implied. The overstated version would have decided the question
by a factor of 150,000.

---

## 3. The verdict

```
model                   accepts  rejects  cost(a,c)   IC gain    TOTAL
standing (19 classes)        19        0       2.16     +0.00    -2.16
low-homophone (cap 3)        15        4       4.26     +0.78    -3.48
```

> **The standing model wins by 1.31 log10 units — about 20×.**

**Both pricings agree on the winner**, differing only in margin: 5.19 under the
overstated cost, **1.31** under the measured one. The IC's preference for fewer
merges is genuine but is outweighed by the cost of asserting that four
well-attested classes are not co-plaintext.

---

## 4. What the IC line produced

Six cycles, and the ledger is worth stating plainly.

**Delivered:**
- the alphabet narrowed from `[56, 82]` to **`[78, 82]`**, the first narrowing in
  eighty reports, from a direction independent of the constraint system
- **K = 56 refuted at −14.2σ** — the proven floor is attainable but not actual
- a **likelihood function over merge counts**, giving ML = 4
- confirmation that `IC` is not useless here: FR175 said it cannot detect
  language in a uniform stream, which is true; it estimates the alphabet size
  instead

**Withdrawn along the way:** FR183's "flatter than chance" (null conditioned on a
random quantity), FR184's class-value null (tautological), FR186's homophone
attribution (first-match search), and this cycle's first pricing (wrong
rejection cost). **Four malformed statistics in six cycles** — every one caught
by asking what the number would be if the hypothesis were false.

**Not delivered:** the standing model is unchanged. The IC challenged it and
lost, which is a result rather than a disappointment.

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Low-homophone selection | a live rival (FR187) | **loses by ~20×** |
| Standing 8-homophone model | challenged | **stands** |
| Rejection cost | pattern surprise | **FR151's measured rate**, 0.637 per class |
| ML merge count | — | **4**, with 3 favoured over 8 by 6× |
| Alphabet | [56, 82] | **[78, 82]**, ML ≈ 79 |
| `IC`'s role | "cannot work" (FR175) | **estimates the alphabet size** |

---

## 6. Model status

Unchanged and now defended: 794 relations, 61 glyphs, 8 homophones, one reading,
five fragments, 819 positions (79.1%), **alphabet [78, 82]**. Cumulative: 27.16
billion candidates, zero survivors.

---

## 7. Horizon

**The IC line is closed.** It narrowed the alphabet, supplied a likelihood over
merge counts, and challenged the model on its own terms without displacing it.

The residual tension is worth keeping visible rather than resolving: the
plaintext mildly prefers four merges, the class evidence more strongly prefers
eight, and **an anchor on any of the six disputed homophone pairs would settle
it outright** — which adds a sixth item to the acquisition target list at no
cost.
