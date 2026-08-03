# Field Report 183 — BOTH ATTACKS RUN, BOTH NULL, AND THE READINGS ARE FLATTER THAN CHANCE

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. Attack A — contaminated `q`

**Hypothesis.** Some accepted classes are not co-plaintext; their false
constraints scramble `q`, and a scrambled `q` flattens the recovered `p`.
Removing them should make `p` less flat.

**Fitness.** Chi-square is wrong here — removing classes shrinks the reading,
expected cell counts fall below 5, and the approximation inflates. Used the
**Index of Coincidence** instead: a probability, directly comparable across
sample sizes.

**First run had no power.** Removing any of the 19 non-atlas classes left IC,
positions and distinct count **identical**. They add relations to `q` but the
reading is driven by the atlas pool, so contamination would have to be there.

**Redirected to the 13 atlas classes:**

```
      dIC       IC  pos  dist  class
 +0.00174  0.01453  123    58  #3+ / #3
 +0.00101  0.01379  144    65  #2-
 +0.00071  0.01350  108    56  #M- / #M
 -0.00105  0.01174   90    54  #2+ / #2
```

Removing #3 raises IC by the most — and cuts the reading from 191 positions to
123. **IC rises mechanically as a sample shrinks.** Simulating uniform draws at
each `(n, K)`:

```
    n    K  expected IC     sd   observed       z
  191   72      0.01390  0.00090   0.01279   -1.24   baseline
  123   58      0.01727  0.00153   0.01453   -1.79   remove #3
  108   56      0.01788  0.00174   0.01350   -2.51   remove #M
   90   54      0.01851  0.00218   0.01174   -3.10   remove #2
```

> **Every observed IC sits at or below what uniform sampling gives at that
> sample size. The #3 "signal" is the shrinkage confound, exactly as
> pre-registered. Attack A returns null.**

---

## 1. An unexpected result inside the null

Look at the sign of every z: **−1.24, −1.79, −1.31, −2.51, −3.10.** All negative.

**The readings are consistently *flatter* than uniform sampling predicts** — and
increasingly so as they shrink. That is not what a contaminated `q` produces,
and it is not what a natural source produces either.

It is what you get when the value-classes are **more evenly sized than chance**
— which is what an equality structure derived from *constraints* rather than
from *data* would look like. Logged as an observation; it is a hint about the
reconstruction's own geometry rather than about the plaintext, and it deserves
its own cycle.

---

## 2. Attack B — flat but structured source

**Hypothesis.** A flat distribution does not imply a flat sequence. Key streams,
indices, coordinate lists and counters are all uniform in distribution and
highly structured in order.

**And one family of sequence tests survives FR36**: since
`p[t+1] − p[t] = d·(v[t+1] − v[t])`, "the first difference is constant over a
run" holds at every drift — the constant just scales. **Arithmetic runs are
drift-independent.**

Null: permute `p` within the reading, preserving the distribution exactly and
destroying only the order.

```
test                          observed  null mean  null sd       z
arithmetic runs, longest             2       1.54     0.51   +0.90
arithmetic runs, mass                0       0.02     0.24   -0.08
quadratic runs, longest              1       1.32     0.47   -0.68
repeated diff-pair, max              1       1.21     0.41   -0.52
```

**Null across the board.** But the power is thin and should be stated: only
**97 positions** sit in contiguous determined runs of length ≥ 4, the longest
being 8. A sequence structure with a period longer than 8 could not be seen at
all.

---

## 3. Where this leaves the two hypotheses

| hypothesis | status after this cycle |
|---|---|
| contaminated `q` | **no evidence** — no class removal beats the shrinkage confound |
| flat structured source | **no evidence**, but the test has 97 positions of power |
| flat unstructured source | **still the residual**, still unfalsifiable |

**Neither is refuted.** Attack A found nothing where it had power; attack B had
little power to find anything.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Contaminated `q` | the testable survivor (FR182) | **tested, null** |
| IC as a fitness function | proposed | **works, but the shrinkage confound must be simulated** |
| The 19 non-atlas classes | add relations (FR146) | **inert for the READING** — the atlas drives it |
| Sequence structure in `p` | untested | **null at 97 positions of power** |
| Reading flatness vs chance | unexamined | **consistently BELOW uniform expectation**, z = −1.2 to −3.1 |

---

## 5. Model status

Unchanged: one reading, five fragments, 819 positions (79.1%), 794 relations,
61 glyphs, Quagmire II with a progressive key. Cumulative: 27.16 billion
candidates, zero survivors.

---

## 6. Horizon

1. **The negative-z observation is the live thread.** The readings are flatter
   than chance at every sample size, monotonically increasing as they shrink.
   That is a property of how the equality structure is *built*, not of the
   plaintext, and it has never been characterised.
2. **Attack B deserves a re-run if coverage ever rises.** At 97 positions it
   could not have detected anything with a period above 8.
3. **Attack A is closed at the single-class level.** A subset search would need
   a fitness immune to shrinkage, which the simulation above now provides.
