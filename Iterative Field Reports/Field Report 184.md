# Field Report 184 — TWO MALFORMED NULLS CORRECTED, AND WHAT SURVIVES IS A CONSISTENT +1.2σ

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. Correction 1 — FR183's null conditioned on a random quantity

FR183 simulated "uniform over K types" with **K = the number of distinct values
observed** (72 at n=191). Wrong twice:

1. the observed distinct count is **itself random** — conditioning on it removes
   the very variation under test
2. the alphabet is **83**, not 72; types absent from a sample still exist

`IC = Σnᵢ(nᵢ−1)/n(n−1)` is an **unbiased estimator of Σpᵢ²**. For a uniform
source over 83 types that is exactly `1/83 = 0.01205` at **every** sample size.
The correct null is fixed, not n-dependent.

**The sign flips:**

```
    n  observed IC  null mean   null sd       z       p
  191      0.01279    0.01206   0.00081   +0.91  0.1722
  435      0.01254    0.01205   0.00036   +1.39  0.0896
  123      0.01453    0.01205   0.00127   +1.96  0.0315
```

FR183's *"the readings are flatter than chance"* was an artifact. **They are
consistently above uniform, not below.**

---

## 1. Correction 2 — my next null was tautological

I then built a null keeping the equality classes and randomising their values,
reporting **zero collisions at z = −5.37**. That is meaningless: **a "class"
*is* a value-group**, so distinct classes carry distinct values by definition.
The null merged classes, which changes the structure it was supposed to hold
fixed.

Two malformed nulls in two cycles, both caught by asking what the statistic
would be if the hypothesis were false.

---

## 2. What survives, tested properly

Non-definitional quantities only, against `n` uniform draws over 83 types —
the exact hypothesis under test:

```
statistic                observed  null mean  null sd       z       p
index of coincidence      0.01244    0.01205  0.00032   +1.22  0.1143
class-size variance       6.96879    5.84894  0.91320   +1.23  0.1220
largest class            12          12.60     1.37     -0.44  0.7920
distinct values          83          82.78     0.47     +0.47  1.0000
```

> **The two informative statistics both sit at +1.2σ, in the direction a
> structured source predicts. Neither is significant. Both point the same way.**

The largest class and distinct-value count are exactly at expectation, which is
what should happen — they are dominated by sample size rather than by
structure.

---

## 3. Reading this honestly

**+1.2σ twice is not a finding.** It is what you would see roughly one time in
nine from pure noise, and the two statistics are not independent — class-size
variance and IC are near-monotone functions of one another, so this is closer to
*one* +1.2σ observation than two.

**But the direction is the one that matters.** A structured source raises both;
a rationed or permutation source lowers both; noise moves them either way.
Across every sample size tested — 108, 123, 144, 191, 435, 491 — **the sign has
never once been negative** once the null was corrected.

That consistency is worth more than any individual z, and it is the first thing
in this project's plaintext work that has pointed the same way twice.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| FR183's "flatter than chance" | observation | **WITHDRAWN** — null conditioned on a random quantity |
| The class-value null | z = −5.37 | **WITHDRAWN** — tautological |
| Correct IC null | n-dependent | **fixed at 1/83**; IC is unbiased at every n |
| Reading vs uniform | below | **above, consistently, at ~+1.2σ** |
| Significance | — | **none individually**; the consistency of sign is the only content |

---

## 5. Model status

Unchanged: one reading, five fragments, 819 positions (79.1%), 794 relations,
61 glyphs. Cumulative: 27.16 billion candidates, zero survivors.

---

## 6. Where to push next

The effect, if real, is **small**: `Σpᵢ² = 0.01244` against `0.01205` uniform —
a **3.2% excess**. For comparison, English letters run **70%** above uniform.
So whatever this is, it is not language and never was.

Three ways to get power, in order of cost:

1. **Use all five fragments, not one.** 819 positions instead of 491 would cut
   the standard error by ~30%. The fragments have independent constants but the
   *class-size distribution* within each is comparable — they can be pooled for
   this statistic even though their symbols cannot be compared.
2. **Test the second fragment separately** (222 positions). If the +1.2σ is
   real it should appear there too, independently. If it is noise it will not.
   **This is the cheapest genuine replication available.**
3. **Pre-register the direction.** The sign has been positive at six sample
   sizes. A one-sided test on fragment 2, declared before looking, would be a
   real test rather than another look at the same data.
