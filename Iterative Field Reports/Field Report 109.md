# Field Report 109 — THE REPAIR FORK REOPENS: FR47'S REFUTATION WAS GAUGE-CONTAMINATED

*Instrument: `eyerefork.py` (5/5 gate, canonical machinery). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. Why repair A was the target

FR107 opened a new error class — **a gauge fixed for one computation, reused
where it does not hold** — and asked for an audit. CHALLENGE I made that audit
finite by giving the error a signature: a quantity is at risk iff it was
computed with a parameter fixed for convenience **and** the conclusion drawn
concerns a situation where that parameter is unknown. Condition one alone is
harmless; FR105's ratio scan fixes `d2 = 1` legitimately.

Applying the signature to the doctrine's load-bearing decisions put **repair A**
at the top, and the reason is sharp:

- FR25 opened the fork — the corpus admits a determining injective reading only
  if one well-supported instance is discarded, and **two** repairs worked:
  **A** (drop East 3@101 + East 1@68) and **B** (drop East 3@101 + East 4@51).
- FR47 closed it **by injectivity**: with the FR32/33 passage included, A gave
  384 relations and 0 violations, B gave 393 and **4**.
- Under one drift that reasoning is airtight, because **FR53's P1 proves
  injectivity is scale-invariant** — one drift settles it.
- **Under two drifts injectivity is not ratio-invariant.** That is exactly what
  FR104/FR105 found: 65 of 82 ratios fail it, 17 pass. Injectivity became a
  discriminator precisely where P1 had proved it useless.

So repair B was refuted by a test now known to be ratio-dependent, evaluated at
a single ratio.

---

## 1. The reconstruction is faithful

Both pre-registered gates pass before any scan:

```
R1  repair A at ratio 1 : 384 relations, 0 violations, 56 glyphs,
                          components (25,11,7,3,2,2,2,2,2)   [canonical]
R2  repair B at ratio 1 : 393 relations, 4 violations, 55 glyphs   [FR47 exactly]
```

R2 matters most: it confirms this cycle rebuilds repair B the way FR47 did, so
any difference downstream is the ratio and not the reconstruction.

---

## 2. THE FINDING — repair B survives at five ratios

Scanning all 82 ratios with the FR32/33 passage included throughout:

| reading | pool pairs | contradictory | injectivity fails | **clean** | clean ratios |
|---|---:|---:|---:|---:|---|
| **A** | 67 | 0 | 65 | **17** | 1, 8, 9, 15, 22, 28, 35, 40, 48, 51, 53, 55, 74, 76, 77, 78, 82 |
| **B** | 74 | 0 | 77 | **5** | **7, 8, 9, 22, 40** |
| AB | 64 | 0 | 55 | 27 | 1, 6, 7, 8, 9, 10, 15, 16, 22, 24, 26, 28, 35, 40, 42, 48, 51, 53, 55, 62, 70, 73, 74, 76, 77, 78, 82 |

Repair B is **injectivity-clean at ratios 7, 8, 9, 22 and 40**, delivering 393
relations over 55 glyphs with components (24, 14, 7, 2, 2, 2, 2, 2).

> **[R3] THE FORK REOPENS.** FR47's refutation of repair B holds at ratio 1 and
> at ratio 1 only. It is not a property of repair B; it is a property of
> evaluating repair B under the assumption of equal drifts.

**FR48's likelihood ratio collapses with it.** FR48 priced repair B as needing
to assert *both* East 4@51 spurious (~1.7e-3) *and* the FR32/33 passage spurious
(~3.6e-6), giving ~2.8e5 in favour of A. That second term existed only because
"passage + B is contradictory". **At ratios 7, 8, 9, 22 and 40 the passage and
repair B are jointly consistent**, so B need not assert the passage spurious and
the 2.8e5 factor evaporates.

---

## 3. The repair and the drift ratio are entangled

A structural relation the series has not seen before:

| ratio | repair A | repair B |
|---|---|---|
| **1** (equal drifts) | clean | **fails** |
| **7** | fails | **clean** |
| 8, 9, 22, 40 | clean | clean |
| 15, 28, 35, 48, 51, 53, 55, 74, 76, 77, 78, 82 | clean | fails |

**Equal drifts force repair A. Ratio 7 forces repair B.** Four ratios admit
both. The repair choice and the drift ratio are not independent unknowns — they
constrain one another, and neither is settled.

This also means the drift-equality question (FR102, unresolved) and the repair
question (FR25, reopened here) are **the same question viewed twice**: evidence
for either constrains the other.

---

## 4. What this costs — including a document shipped this session

**The acquisition specification is conditional on repair A**, and this was not
stated when it was written. Under repair B the components differ materially:

```
repair A : 56 glyphs, components (25, 11, 7, 3, 2, 2, 2, 2, 2), 74.1% exposure
repair B : 55 glyphs, components (24, 14, 7, 2, 2, 2, 2, 2)
```

Component 2 grows from 11 glyphs to 14, component 4 shrinks from 3 to 2. Every
per-component yield, the ordering, the blind clusters and the witness triples
are repair-A objects. **The spec has been amended to say so rather than
withdrawn** — it remains correct conditional on A, which is still the
best-supported reading (§5).

**What does not change:** the mechanism (progressive, linear, two drifts), the
three-anchor opening (an algebraic consequence of three unknowns, not of the
repair), and the acquisition arithmetic's *shape*.

---

## 5. What still favours repair A — and what no longer does

**Still standing, because it is drift-independent:**

- **FR2 / FR27 embeddedness.** East 1@68 is the *only* instance in either class
  with no parent passage; every other candidate sits inside a larger certified
  passage. This is a structural fact about the atlas and no gauge touches it.
- **FR25's minimal cores.** Every minimal core of the six false equalities
  contained East 3@101 — common to both repairs, so it discriminates nothing,
  but it is unaffected.
- **Ratio 1.** If drift equality is ever re-established, repair A follows
  immediately and uniquely.

**No longer standing, being gauge-contaminated:**

- **FR47's injectivity refutation** — holds only at ratio 1.
- **FR48's 2.8e5 likelihood ratio** — its dominant term was the passage
  incompatibility, which does not hold at B's clean ratios.

Per **R4, this cycle does not adjudicate.** Reopening is the finding;
adjudication needs evidence that discriminates the two readings without
assuming a ratio, and identifying such evidence is the next cycle's work.

---

## 6. Doctrine changes

| item | prior status | status now |
|---|---|---|
| **Repair fork** | closed (FR47), A unique | **REOPENED** — B clean at ratios 7, 8, 9, 22, 40 |
| FR47's refutation of B | decisive | **holds at ratio 1 only**; gauge-contaminated |
| FR48's likelihood ratio ~2.8e5 | favours A | **collapses** — the passage term does not apply at B's clean ratios |
| Repair / drift independence | assumed | **entangled**: ratio 1 ⇒ A; ratio 7 ⇒ B; 8, 9, 22, 40 ⇒ either |
| Acquisition specification | unconditional | **conditional on repair A**, now stated |
| The 17 clean ratios | property of the corpus | property of **corpus + repair A**; B has its own 5 |
| Evidence for A | FR2, FR27, FR47, FR48 | **FR2 and FR27 only** — the drift-independent ones |

---

## 7. Model status

Under repair A (the standing reading): 384 relations over 56 glyphs, injectivity
clean at 17 ratios, exposure 74.1%, components (25, 11, 7, 3, 2, 2, 2, 2, 2).
**Now explicitly conditional**, with repair B a live alternative at 5 ratios
giving 393 relations over 55 glyphs. Cumulative: 27.16 billion candidates, zero
survivors.

---

## 8. Horizon

1. **Find evidence that discriminates A from B without assuming a ratio.**
   FR27's embeddedness is the surviving candidate and was priced as "soft"; it
   deserves the quantitative treatment FR48 gave the (now collapsed) passage
   argument. This is the cycle's own successor and the most consequential open
   item in the project.
2. **The drift-equality and repair questions should be worked together.** §3
   shows they constrain one another; separate cycles on each will keep
   rediscovering the same entanglement.
3. **Continue the gauge audit.** Repair A was the highest-value target and it
   broke. The remaining candidates — FR27's packing residual curve, the gauge
   ladder (0/82, 0/82, 82/82), FR21's injectivity census — have not been
   checked, and this cycle is evidence the class is not hypothetical.
