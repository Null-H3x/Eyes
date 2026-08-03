# Field Report 175 — `eyemult.py`: THE COMMUNITY'S LEADING CANDIDATE, REFUTED WITHOUT BRUTE FORCE

*Instrument: `eyemult.py` (4/4 gate). July 2026. Cycle: EYESPIRAL-C.*

---

## 0. What the community documents leave outstanding

From *"Cipher model definition and Brute force guidelines"* (Dykoine):

```
Polynomial with modulo : Failure, Under tests for design improvement
N-time-pad             : Failure
Alberti                : Failure
```

with the stated blocker on the surviving candidate:

> *"Candidate 2: c[i] = (k[i] * p[i] + phi) % 83 — Status: Require more
> efficient reverse IoC. Can't brute force it without a significant way to
> simplify it, requiring millenia of computation."*

and, under **Contributing**, an explicit request: *"We need to reverse the Index
of Coincidence formula with great efficiency."*

**That is the outstanding item, and it is the one thing this project is
positioned to answer** — because the IoC is not needed at all.

---

## 1. The isomorphs collapse the family algebraically

Their model is `c[i] = r^(i+1) · p[i] + phi (mod 83)`, `r` a primitive root.

If two positions `a` and `b` carry the same plaintext token:

```
c[a] - phi = r^(a+1) · p        c[b] - phi = r^(b+1) · p
=>  (c[a] - phi) = r^(a-b) · (c[b] - phi)
```

**One equation per co-plaintext cell, in two unknowns.** The whole space is
40 primitive roots × 83 values of `phi` = **3,320 candidates**, evaluated
against 413 co-plaintext cell pairs from the atlas. It runs in seconds.

No key brute force. No Index of Coincidence. No language assumption.

---

## 2. Gated, then run

```
G1 planted multiplicative corpus recovered : r=8, phi=37 at 100%   PASS
G2 shuffled control not recovered          : best 5.3%             PASS
```

The test can find a true positive and rejects a scrambled one — so a null
result means something.

```
rank   r  phi  cells satisfied       %
   1  47   62           55/413   13.3%
   2  79   60           53/413   12.8%
   3   2   10           53/413   12.8%

best 13.3%   mean 5.7%   chance ~1.2%
```

> **REFUTED. The best of 3,320 candidates explains 13.3% of co-plaintext cells.
> A correct one explains 100%, as the planted control demonstrates.**

---

## 3. What this gives the community

**The multiplicative family is dead, and the millennia of computation are
unnecessary.** More usefully, the *method* generalises: any proposed cipher
family that is linear in the unknowns given a shared passage collapses the same
way. The isomorph alignments are a far stronger constraint than the IoC and cost
nothing to apply.

**And the IoC route cannot work regardless.** FR173 measured the inner layer's
token distribution as uniform (χ² = 93.4 on 81 df, z = +0.97) against a Zipf
prediction of 20% for the top type versus 2.5% observed. The Index of
Coincidence measures exactly the departure from uniformity that is absent. **The
tool they asked for would return noise even if it were built.**

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Multiplicative family `k[i]·p[i]+phi` | untested by this project | **REFUTED** — 13.3% vs 100% for a planted control |
| The community's IoC request | unaddressed | **the IoC cannot work** — the inner layer is uniform |
| Their stated blocker | "millenia of computation" | **3,320 candidates, seconds** |
| Isomorphs as a discriminator | used internally | **generalises to any family linear in the unknowns** |

---

## 5. Model status

Unchanged: 794 relations, 61 glyphs, 79.1% exposure, 435-position reading, 68
maximal readings, two invariant cores, base-5 verified first-hand, plaintext
inventory 83 uniform. Cumulative: 27.16 billion candidates, zero survivors —
**plus 3,320 multiplicative candidates, zero survivors.**

---

## 6. What is left to build

The community's remaining named candidates are **N-time-pad** and **Alberti**,
both already marked "Failure" in their document but without a stated method.
`eyemult.py` generalises to both: each is linear in its unknowns given a shared
passage, so each collapses to a small candidate set the same way.

**That is the tool worth extending** — a family tester driven by the isomorph
alignments, into which anyone can drop a proposed cipher and get a verdict in
seconds instead of a brute force they cannot afford.
