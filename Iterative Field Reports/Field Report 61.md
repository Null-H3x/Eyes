# Field Report 61 — THE REPLACEMENT FILTER, BUILT AND SWEPT: EXHAUSTION IS NOW A WEEKEND

*Instrument: `eyesweep` (6/6 selftests, green before sweeping). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. Why this cycle

FR60 ended with an engineering claim — that the skeleton is a language-free
replacement for EyeStat's chi² pre-filter, with effectively nil false-positive rate
at comparable cost. A claim of that shape should be **built and validated**, not
asserted and left on a horizon list. This cycle builds it, proves it end-to-end
against a planted seed, and runs the first PRNG sweep in the project whose filter
can register a hit.

---

## 1. CHALLENGE I — a convention error caught before building

A PRNG produces a permutation, but whether that permutation is `C` (value → glyph)
or `C⁻¹` (glyph → value) is a **convention, not a fact**, and the inverse of a
Fisher-Yates output is not itself a Fisher-Yates output. Sweeping one direction
only would halve the covered space while appearing complete.

**Both directions are swept throughout.** Cheap to fix in advance; expensive to
discover after publishing a null.

---

## 2. The filter

A candidate alphabet `q` must satisfy, for every within-component pair,

```
q[g₂] − q[g₁] = drift · (Δ₂ − Δ₁)      one drift shared by all 379 relations
```

379 equations, one free parameter, **no plaintext assumption of any kind**. First
relation solves for the drift; the remaining 378 must agree. Early exit rejects
roughly 82 of 83 candidates on the first check.

Gate: relation count 379; **Park-Miller KAT verified** (seed 1 → 16807 → 282475249,
Schrage form); planted consistent alphabet accepted; **0 false positives over 20,000
random permutations**; a single corrupted relation detected; acceptance
drift-independent across drifts 1, 2, 41, 82.

---

## 3. END-TO-END CONTROL — the thing chi² could not do

Plant seed **777777**, generate `q` by floor-biased Fisher-Yates over Park-Miller,
build a skeleton consistent with it, then sweep a window around the plant:

```
4,001 seeds swept in 0.2 s  →  seeds found: [777777]
RECOVERED: YES, uniquely, zero false positives
```

The same plant under FR60's chi² filter:

```
chi² of the CORRECT decryption : 0.04431
chi² of a WRONG-key decryption : 0.04459
→ indistinguishable
```

**This is the demonstration FR60 argued for rather than showed.** The old filter
cannot flag a correct seed on a flat plaintext; the new one recovers it uniquely
from its neighbours.

---

## 4. The sweep — a real null, honestly small

Four families reflecting Petri's documented habits, both directions, 250,000 seeds
each:

| family | direction | seeds/s | hits |
|---|---|---:|---:|
| pm-fy-single | q | 32,610 | 0 |
| pm-fy-single | q⁻¹ | 30,132 | 0 |
| pm-fy-double | q | 16,391 | 0 |
| pm-fy-double | q⁻¹ | 15,336 | 0 |
| pm-fy-floorbias | q | 25,456 | 0 |
| pm-fy-floorbias | q⁻¹ | 23,717 | 0 |
| mt19937-shuffle | q | 33,905 | 0 |
| mt19937-shuffle | q⁻¹ | 30,938 | 0 |

**2,000,000 candidates, zero survivors, 83 s single-core Python.**

Stated plainly: this covers about **0.1%** of one family's Park-Miller seed space. It
is a small null. The difference from the 34-billion-seed null is not size but kind
— **within its range this one is informative**, because §3 proves a correct seed
inside the range would have been found.

---

## 5. THE DELIVERABLE — exhaustion is now tractable

The filter is *cheaper* than the pipeline it replaces. chi² requires a full
histogram, a sort, and three language comparisons, then survivors go to Hungarian
assignment and dictionary matching. The skeleton check is one modular inverse plus,
on average, about two subtractions before rejection. **The cost is dominated by
generating the permutation, not by filtering** — so a GPU port inherits EyeStat's
demonstrated generation rate rather than being bounded by scoring.

Complete Park-Miller space, 4 families × 2 directions × 2³¹ seeds ≈ **1.7 × 10¹⁰
candidates**:

| rate | wall time for a COMPLETE sweep |
|---|---|
| 272,000/s (EyeStat's demonstrated rate) | **~17.5 hours** |
| 100,000/s (conservative) | ~47 hours |

Against the original 30–90 day projection **for a run that could not have registered
a hit.** A conclusive result — hit or exhaustive null — is now roughly a weekend of
GPU time. That is the first time in this series that a whole hypothesis class has
moved from intractable to closeable.

---

## 6. What this does not cover

Stated so the null is not over-read later:

- **Seeding conventions.** Covers 32-bit integer seeds. String seeds, multi-word
  state, time-derived seeds, or seeds passed through a hash are not covered.
- **Construction.** Covers direct Fisher-Yates over a PRNG. An alphabet built by any
  other procedure — including the irreducible three-feature construction FR59 left
  open — is invisible to this sweep.
- **Necessary, not sufficient.** The filter uses the 46 glyphs I hold. A hit would be
  a candidate requiring verification against the full 56-glyph skeleton, injectivity
  and packing. Given selectivity of order 83⁻³⁷⁸, a hit would be essentially certain
  to be real, but it is formally a pre-filter.
- **Conditional on repair A**, like everything downstream of FR26.

---

## 7. Model status — unchanged

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity
clean; exposure 768/1036 = 74.1%; repair A the unique maximal reading; drift unpinned
with H4 the only surviving hypothesis.

---

## 8. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Skeleton as candidate filter | recommended (FR60) | **BUILT AND VALIDATED** — 0/20,000 FP, planted seed recovered uniquely |
| PRNG exhaustion | 30–90 day projection, uninformative filter | **~17–47 GPU-hours for a conclusive sweep** |
| Sweep direction | implicit single convention | **both `q` and `q⁻¹` required**; inverse of a FY output is not a FY output |
| PRNG null, current extent | 34B seeds, uninformative | **2M candidates, informative, ~0.1% of one family** |

---

## 9. Horizon

1. **Port `eyesweep`'s filter into EyeStat and run the complete Park-Miller space.**
   It is a weekend, it is conclusive either way, and it closes a hypothesis class
   that has been open since the project began. This is the highest-value action
   available and it needs only hardware you already have.

2. **Widen the seeding conventions** (§6) once the direct sweep is exhausted —
   string seeds and hashed seeds are the natural next tier, and the filter is
   indifferent to how the permutation was produced.

3. **Count the MSB states on the glyph pictures** (FR59 §4). Still the cheapest open
   question, still symmetric, still needs no binary.

4. **Settle the radix** (`GHIDRA.md` base-7 vs corpus base-5). Load-bearing for FR58
   and FR59.

5. **Standing, unchanged:** two external anchors in component 1 (FR54 ordering); and
   the success criterion, which FR57 made decidable and which remains undecided.
