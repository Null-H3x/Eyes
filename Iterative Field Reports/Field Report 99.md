# Field Report 99 — THE GENERATOR SPACE IS EXHAUSTED: 25.8 BILLION CANDIDATES, ZERO SURVIVORS

*Instrument: `eyefast.c` (FR98) via `run_full_sweep.sh`. July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. What this cycle is

FR98 reduced the entire generator sweep from GPU-hours to CPU-minutes. This
cycle spent those minutes. Every seed the project has ever contemplated — both
of the author's generators, both integer mappings, both Fisher-Yates
directions, both q/q⁻¹ orientations, the **full** 2³¹ Park-Miller space and the
**full** 2³² fastrand space — has now been tested against the skeleton filter.

The result is a null, and the point of this report is that it is a **verified**
null, not a silent one. The distinction is the whole FR60 lesson: EyeStat's 34
billion seeds were silence because its filter had no discrimination. This
filter's liveness is proven across all 13.6 billion seeds by the canary count.

---

## 1. The sweep

Run on the Threadripper 9970X, all cores, via `run_full_sweep.sh`. Six
configurations, each `eyefast` gating 18/18 first, each checkpointed:

| configuration | generator | seeds | canaries | hits |
|---|---|---:|---:|---:|
| fastrand full, floor map | `fy_fastrand_floor` | 4,294,967,296 | 429,497/429,497 | 0 |
| fastrand full, modulo map | `fy_fastrand_mod` | 4,294,967,296 | 429,497/429,497 | 0 |
| LGM full 2³¹, descending FY | `fy_lgm` | 2,147,483,647 | 214,748/214,748 | 0 |
| LGM full 2³¹, ascending FY | `fy_lgm_fwd` | 2,147,483,647 | 214,748/214,748 | 0 |
| LGM timestamp 2010–2021, desc | `fy_lgm` | 347,155,200 | 34,715/34,715 | 0 |
| LGM timestamp 2010–2021, asc | `fy_lgm_fwd` | 347,155,200 | 34,715/34,715 | 0 |

Each run also tests q⁻¹ internally, so the candidate count is twice the seed
count. **13,579,212,286 seeds; 27,158,424,572 candidates; zero survivors.**

---

## 2. The null is trustworthy — the integrity check, verified

A clean null is worth exactly what its liveness proof is worth. Every run
reports `canary_integrity: true` with caught == planted, and the planted counts
match `seeds / 10000` (the canary rate) to within one on all six runs:

```
fastrand (4.29e9 seeds)  -> 429,497 canaries   (expected 429,496)   OK
LGM full (2.15e9 seeds)  -> 214,748 canaries   (expected 214,748)   OK
timestamp (3.47e8 seeds) ->  34,715 canaries   (expected  34,715)   OK
```

Known-consistent alphabets were injected into the live stream ~429,000 times in
the largest run and **every one was caught**. A single miss aborts and voids the
run (FR95, verified in C at FR98). The filter was demonstrably firing across the
entire sweep — this is a negative result, not the FR60 failure mode of a filter
that silently could not fire.

---

## 3. What is now closed

**The low-complexity-generator hypothesis for `C` is exhausted.** Not sampled,
not reduced to a natural sub-range — exhausted. The unique seed spaces covered:

- fastrand 2³², floor and modulo mappings, **complete** (including seed 0, the
  state-12 stream `eyerunner.py` skipped, tested by `eyefast` per FR98's P1);
- Park-Miller 2³¹, descending and ascending Fisher-Yates, **complete**.

The two timestamp runs are subsets of the LGM-full runs and served as
corroboration. The generators themselves are not assumptions: both were
verified from the author's source (FR92, `MonteCarlo_NoMoreMoney/random.cpp`),
the fastrand seeding bug (`seed ^ 12`) was found and corrected (FR94), and the
port reproduces the Python stream bit-for-bit (FR98).

**If `C` was produced by running either of the author's generators, under any
seed, either shuffle direction, either integer mapping, in either orientation —
it is not there.** That sentence now has no qualifier.

---

## 4. What this does NOT establish

The same care as every prior null. This does not say `C` is unstructured or
unrecoverable. It says `C` is not the output of a *low-complexity generator in
the swept families*. `C` could still be:

- a generator **outside** his toolkit (a different PRNG, a hash-derived
  ordering, a string seed — FR89's "in-game text as keyword" direction was a
  different attack and is separately closed, but the space of possible
  generators is not finite);
- a **hand-constructed** permutation with no generator at all — the
  arbitrary-`C` reading, which every exclusion in the programme strengthens;
- a multi-stage composition beyond the two-stage sweeps already run.

The filter is necessary-not-sufficient (46 of 56 glyphs) at 83⁻⁴¹ selectivity
(~1e-78, FR96), so a hit would have been `C` almost certainly — but a miss only
removes the swept families. **A faster null is still a null.**

---

## 5. Where this leaves the programme

Every construction the author is known to favour is now excluded over its full
natural range: Mnemonica (FR91), faro and cuts (FR90), Finnish keywords and
in-game text (FR89), and now — completely, not partially — his own two
generators at every seed (FR99). The arbitrary-`C` reading is the last
construction hypothesis standing, and it is not attackable by sweeping.

This closes the sweep programme. It was the last thing the analysis box could
do to the seed space, and it is now done. **The glyph images are the sole
remaining resource for every open vector** — MSB counting (base-5 vs base-7),
MDL segmentation, FR97's encounter-order construction family, and the five
external anchors that would fix the alphabet as numbers. None of these is a
sweep; all of them need the image assets.

---

## 6. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Generator sweep | timestamp window + 2M small-integer + 1.38B cumulative | **FULL 2³¹ LGM and 2³² fastrand EXHAUSTED**, both mappings, both directions, both orientations, integrity-verified |
| Cumulative sweep total | 1.38 billion | **27.16 billion candidates** (13.58 billion seeds ×2), zero survivors |
| Low-complexity-generator hypothesis | partially tested | **closed** — no qualifier remains |
| fastrand seed 0 | untested (eyerunner skipped it) | **tested** (eyefast P1, state 12) |
| Sweep programme | open (G1–G4 in queue) | **complete**; G1, G2, G4 all subsumed |
| The blocking resource | "glyph images or a sweep" | **glyph images only** — the sweep is done |

---

## 7. Model status

Unchanged. 384 relations over 56 glyphs; injectivity clean; exposure 74.1%;
residual 33.59 bits; inventory 82.5 CI [73.0, 93.7]; alphabet [56, 83], floor
56 (FR97). **Cumulative: 27.16 billion candidates, zero survivors.**

---

## 8. Horizon

1. **The sweep is finished.** Do not reopen it without a *new* generator family
   with a real prior — re-running swept space is not evidence.
2. **Acquire the glyph images.** This is now unambiguously the single
   highest-value action: it unblocks MSB counting, MDL segmentation, the
   encounter-order family, and anchor placement simultaneously. The sweep
   reaching zero over its full range is what makes this the clear priority
   rather than one option among several.
3. **A CUDA kernel is no longer worth building** — the CPU sweep already
   exhausted the space it would have accelerated.
4. **The success criterion** (FR82 §7). Unchanged, and now the dominant open
   question: with the generator hypothesis closed and the alphabet size
   internally settled, whether recovering `C` as a token stream counts as
   solving the Eye Messages is the question that governs whether acquiring the
   images is worth it.
