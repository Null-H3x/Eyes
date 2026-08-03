# Field Report 166 — TWO OF FOUR ASSUMPTIONS DIE ON SCALE-INVARIANCE; THE "ANOMALY" WAS A RESTATEMENT

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The pattern that looked like a crack

FR165 closed the last item that could change the cipher. Looking for what
remained, an apparent anomaly surfaced in the hardest result:

```
14 of 19 invariant relations have |signed value| <= 2
expected if uniform : 1.14      binomial p = 7.2e-14
```

My first explanation — small same-message alignment shifts — **failed**: there
are zero same-message alignments at shift ≤ 2. Affine `C` was also refuted, 18
distinct multipliers over 19 relations. So it stood as unexplained, and I
nominated "the drift is small" as the assumption to test.

---

## 1. It is a restatement, not an anomaly

Under the model, a plaintext token at positions `t` and `t+k` encodes to glyphs
whose q-values differ by `k·d`. So

```
q[a] - q[b] = k*d   <=>   a and b carry the SAME token, k positions apart
```

At drift 1 the values **are** the `k`s. Dividing out `d`:

```
  d   values in units of d
  1   [-30,-30,-28,-2,-1,-1,-1,-1,-1,0,0,1,1,2,2,2,2,30,30]
  2   [-30,-30,-28,-2,-1,-1,-1,-1,-1,0,0,1,1,2,2,2,2,30,30]
 41   [-30,-30,-28,-2,-1,-1,-1,-1,-1,0,0,1,1,2,2,2,2,30,30]
 82   [-30,-30,-28,-2,-1,-1,-1,-1,-1,0,0,1,1,2,2,2,2,30,30]
```

**Identical at every drift** — necessarily, since dividing out `d` is what makes
it scale-invariant.

> **"14 of 19 relations are small" means "14 of 19 invariant relations link
> glyphs carrying the same token within two positions of each other." That is
> true at every drift and carries no information about `d`.**

The `p = 7.2e-14` is real and the statement is true; it is simply a fact about
the alignment geometry restated in q-space, not a discovery.

---

## 2. Assumption 1 retired — and my CHALLENGE I was right for the wrong reason

I first rejected it as circular (d=1 maximises small values because the table is
solved at drift 1). **That reasoning was wrong** — the solver does not optimise
for small values, and d=1 tying with d=82 is just negation.

The correct reason is **FR36**: every scale-invariant test is guaranteed to fail
on the drift. Stated properly, the pattern is scale-invariant, so it cannot
discriminate `d`.

---

## 3. Assumption 2 dies the same way

"`C` preserves local order" requires ordering 29 glyphs from mod-83 differences.
That ordering depends on `d`, and requiring the values to pack distinctly into
0..82 **is exactly FR53's packing test, proven scale-invariant.**

---

## 4. What survives

| assumption | status |
|---|---|
| 1. The drift is small | **RETIRED** — scale-invariant, FR36 |
| 2. `C` preserves local order | **RETIRED** — reduces to FR53's packing |
| **3. The ±29 base differences** | **survives** — about specific values, not scaled away |
| **4. Mnemonica as a construction family** | **survives** — proposes a specific `C`, testable against the 19 invariants |

**Assumption 4 is now the only live internal lead**, and it is testable at zero
cost: any candidate `C` either satisfies all nineteen invariant relations or is
refuted, whichever of the 68 readings is correct.

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| "14 of 19 small" | unexplained anomaly | **restatement of alignment geometry** in q-space |
| "The drift is small" | nominated assumption | **retired** — FR36 applies once stated correctly |
| "`C` preserves local order" | nominated assumption | **retired** — reduces to FR53's packing |
| FR166's first CHALLENGE I | circularity argument | **wrong reason, right verdict** |
| Live internal leads | four | **one** — Mnemonica |

---

## 6. Model status

Unchanged: 794 relations, 61 glyphs, 8 homophones, alphabet [56, 75], 79.1%
exposure, 435-position reading, 6 anchors, 68 maximal readings, 19 invariant
relations, stamped header proven forced. Cumulative: 27.16 billion candidates,
zero survivors.

---

## 7. Horizon

1. **Test Mnemonica-derived permutations against the invariant core.** Petri's
   own repo carries the stack; the 27.16B sweep covered Park-Miller/Fisher-Yates
   only, so this is an un-swept family with a real prior. The 19 relations make
   the test cheap and decisive.
2. **The ±29 observation** is worth stating in the record but is not a test
   until something predicts it.
3. **FR36 and FR53 are stronger than they have been given credit for.** Between
   them they have now retired four separate drift-pinning proposals. Any future
   one should be checked against them *first*.
