# Field Report 170 — 92% RECOVERED, AND WHY NO ORACLE CAN EXIST

*July 2026. Cycle: EYESPIRAL-C. Strategic assessment.*

---

## 0. The question

In-game findings are exhausted, the code is datamined out, and external pins are
not functionally obtainable. **Where does that leave the effort?**

Answering it required two measurements neither of which had been made.

---

## 1. How much is actually recovered

```
                     a priori         now
cipher FORM          unknown          SETTLED
modulus              ?                83 (certain)
C (the map)          83! ~ 10^124     68 readings, 61 of 83 glyphs determined
drift d              82               82        <- UNMOVED
kappa_g              83^3             absorbed into base_m
base_m               83^9             83^5 / gauge

a priori search space : 2^478
remaining             : 2^38
```

> **440 of 478 bits recovered — 92.1%.** The remaining space is
> 68 readings × 82 drifts × 83⁴ bases = **2.6 × 10¹¹**, which is a few CPU-hours.

**The blocker has never been the search.** It is that nothing scores a candidate.

---

## 2. Why nothing can score one

Under any candidate the reading gives `p = d·v − b`. Any test depending only on
the **equality structure** of `v` is scale-invariant and dies (FR36) — which is
what killed distinct-value counts, packing, coincidence statistics, repeat
structure and every language statistic tried.

The one natural test that survives scale-invariance is **contiguity**: if the
designer numbered symbols `0..k−1`, the true `(d, b)` puts every plaintext value
in a window of width `k`. FR53's proof does **not** cover this — multiplication
by `d` preserves distinctness but not ranges.

Running it produced the number that answers everything:

```
reading: 435 positions, 82 DISTINCT plaintext values
gap to fill if contiguous: 1 residue  ->  every drift qualifies, no discrimination
```

**82 distinct values.** Against expectation:

```
435 draws uniform over 83 tokens -> expected distinct 82.6, observed 82
if the alphabet were 26 -> expect 26     56 -> expect 56
                    29 -> expect 29     75 -> expect 74.8
                    83 -> expect 82.6   <-- MATCHES
```

> **The plaintext token inventory is ~83. The corpus uses essentially the
> entire ring, at exactly the rate uniform sampling predicts.**

---

## 3. Two consequences, and they are the answer

**(a) No oracle can exist.** A plaintext uniform over its full alphabet has no
structure to detect. The seven independent null results (FR39, FR41/42, FR115,
FR126, FR132, FR133, FR134) were not seven failures — they were seven correct
measurements of the same fact. **Enumerating the remaining 2³⁸ is pointless not
because it is large but because nothing can rank the output.**

**(b) The alphabet question is retired, and was mis-stated.** `[56, 75]` was
never the token inventory; it is the **image size of the glyph map** `q = C⁻¹`.
Two different quantities have been called "the alphabet" since FR97. The token
inventory is 83.

---

## 4. Where this leaves the effort

**The cipher is substantially solved.** Form, modulus, keystream shape, per-
message bases, 61 of 83 glyph relations, two invariant cores, a 435-position
relative reading, and a 92.1% reduction of the parameter space.

**The inner layer is unrecoverable by analysis.** Not "hard" — unrecoverable.
A uniform payload cannot be distinguished from noise by any statistic, so the
last 8% requires information from outside the ciphertext, and that is precisely
what is unavailable.

**This is a coherent end state, not a stall.** FR101 settled the success
criterion as recovering the mechanism, with the inner layer explicitly out of
scope. By that criterion the project is near-complete, and the measurement above
explains *why* the out-of-scope part was correctly placed out of scope.

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Fraction recovered | unquantified | **92.1% of 478 bits** |
| Remaining space | "needs anchors" | **2^38, enumerable in CPU-hours** |
| The blocker | search | **scoring — no oracle can exist** |
| Plaintext inventory | [56, 75] | **~83; uses the entire ring** |
| "Alphabet" | one quantity | **two** — token inventory (83) vs glyph-map image (≤75) |
| The seven null results | seven failures | **seven measurements of one fact** |
| Contiguity test | untried | **tried; cannot discriminate** because the inventory is full |

---

## 6. Model status

Extended skeleton: 794 relations, 61 glyphs, 8 glyph-map collisions, 79.1%
exposure, 435-position reading, 68 maximal readings, two invariant cores
(13 atlas / 19 extended), stamped header forced, **plaintext inventory ~83**.
Cumulative: 27.16 billion candidates, zero survivors.

---

## 7. What can still progress

1. **Publish for collective attack.** `eyeverify.py` + `INVARIANT_CORE.md` let
   anyone test a construction in seconds without accepting a single choice this
   project made. That is the highest-yield remaining action and it costs nothing.
2. **Rank the 68 readings empirically.** They are not equally probable; FR164
   supplies the chance-isomorph rate needed to price them. This would not prove
   one but would give a defensible best estimate — the one internal item with
   real value left.
3. **Do not enumerate the 2³⁸.** It is affordable and useless.
4. **If a new eye message is ever found**, everything changes: more corpus is
   the only thing that adds information without an external pin.
