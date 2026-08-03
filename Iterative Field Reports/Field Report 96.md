# Field Report 96 — THE SELECTIVITY FIGURE WAS WRONG BY 10^649

*Instrument: `eyerunner.py` v1.1 (14-check gate, hit verification, reference vectors). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — audit the arithmetic, not the plumbing

FR95 hardened the runner against a **false negative** — a filter that cannot fire.
The remaining exposure is the other side: **if it produces a hit, is the hit right?**
That question turns on arithmetic that has never been checked.

It does not survive checking.

---

## 1. THE SELECTIVITY CLAIM IS WRONG

Since FR61 every report has quoted the skeleton filter's selectivity as **83⁻³⁷⁸**,
reasoning from 379 relations with one consumed to determine the drift.

**The relations are not independent.** Within a component, the drift plus a single
glyph determines every other glyph in it. A component of size *k* therefore supplies
*k−1* independent constraints, not *C(k,2)*.

```
component sizes            25, 11, 7, 3
independent constraints    24 + 10 + 6 + 2 = 42
minus 1 consumed by drift  = 41
```

```
correct   P(random permutation passes) ~ 83^-41  = 1e-78.7
claimed   83^-378                                = 1e-727
error factor                                       1e649
```

**Validated empirically rather than asserted.** Building reduced filters from
component subsets and measuring the pass rate where it is measurable:

| filter | independent constraints | predicted hits | observed |
|---|---:|---:|---:|
| C4 only (3 glyphs) | 1 | 36,144.6 | **37,163** (ratio 1.03) |
| C3 only (7 glyphs) | 5 | 1 in 3.9e9 | unmeasurable |
| C4+C3 (10 glyphs) | 7 | 1 in 2.7e13 | unmeasurable |

The model predicts the measurable case correctly, so 83⁻⁴¹ is sound.

**No conclusion changes.** 1e-78 is still far beyond any sweep conducted — 1.38
billion candidates against a 1e-78 false-positive rate leaves an expected 1e-69 false
hits. Every null in the programme stands. But the number was wrong by 649 orders of
magnitude and appeared in a dozen reports.

---

## 2. Arithmetic that checks out

**The scale constant.** His `4.656612875e-10` differs from `1/(2³¹−1)` by 2.5e-20.
Maximum `Next()` is 0.99999999994721556, and `int(83 × that) = 82` — the top index is
never exceeded, so the assertion added in FR95 provably never fires. A port that
substituted the mathematically exact reciprocal would diverge on roughly **1 draw in
5e17**, which is safe, but only because we use his constant verbatim.

**Schrage overflow.** `16807 × lo` with `lo < 127773` gives at most 2,147,479,011,
just inside 2³¹−1 = 2,147,483,647. That margin of 4,636 is the entire point of the
Schrage decomposition, and it holds.

**The Δ tables**, reproduced from the corpus against FR53:

```
C1  25 glyphs  323 positions (31.2%)   FR53: 323  MATCH
C2  11 glyphs  179 positions (17.3%)   FR53: 179  MATCH
C3   7 glyphs  104 positions (10.0%)   FR53: 104  MATCH
C4   3 glyphs   29 positions ( 2.8%)   FR53:  29  MATCH
```

Components disjoint, Δ values distinct within each, all indices in range.

---

## 3. Bulletproofing a hit

The filter uses 46 of 83 glyphs, so a pass is **necessary but not sufficient**. Four
independent checks exist; only two were being applied.

| check | status before | status now |
|---|---|---|
| drift nonzero | enforced | enforced |
| 46 values pairwise distinct | automatic (permutation) | automatic |
| **membership in the 22,550 consistent set** | **not checked** | **`verify_hit()`** |
| full 56-glyph skeleton + packing | not possible here | flagged for downstream |

`verify_hit()` extracts the drift and all four component bases, confirms every glyph
sits exactly where `base + drift·Δ` predicts, and confirms the four component
value-sets are **pairwise disjoint** — FR27's packing constraint. A hit failing this is
a bug, not a discovery, and the runner now says so in the output.

Gated both ways: `verify_hit_on_canary` passes, `verify_hit_rejects_bad` rejects a
permutation perturbed by a single transposition.

---

## 4. Reference vectors

Any C or GPU port must reproduce the Python stream **exactly**, and there was no way to
check that. The gate now emits the first twelve entries of the deck at seed 1234 for
all four generators:

```
fy_lgm             21 20  5 53  3 76 40 47 39  6 23 41
fy_lgm_fwd          0 27 35 80 38 20 10 61 26 39  1  3
fy_fastrand_floor  21 14 67  4 32 23 73 58 17  2 19 16
fy_fastrand_mod     8 64 43 65 16 82 15 71 11 26 14 54
```

**A port that does not reproduce these is not testing the same thing.** They are
written into every JSON report, so any result carries its own provenance.

---

## 5. Runner status

Gate is now **14 checks**: Park-Miller KAT ×2, relation count, permutation validity ×4,
positive control, negative control (0/20,000), drift recovery, `verify_hit` accept,
`verify_hit` reject, independent-constraint count, reference vectors. Verified at
19,711 seeds/s with 200/200 canaries and clean JSON.

---

## 6. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Filter selectivity | 83⁻³⁷⁸ since FR61 | **83⁻⁴¹ (~1e-78)** — wrong by 1e649, empirically validated |
| Independent constraints | conflated with 379 relations | **41** — within a component, drift + 1 glyph fixes the rest |
| Scale constant risk | unexamined | 2.5e-20 offset, divergence ~1 in 5e17 if a port substitutes 1/(2³¹−1) |
| Schrage overflow margin | unexamined | 4,636 inside 2³¹−1 — holds |
| Hit verification | relations only | **+ packing membership** via `verify_hit()` |
| Port verification | impossible | **reference vectors** in every report |

---

## 7. Horizon

1. **Run G2 then G1** with `eyerunner.py`. Check `canary_integrity`, then
   `reference_vectors` if a port was used, then `hit_count`.
2. **Any hit: read `verification.packing_ok` before believing it.** False means bug.
3. **The 83⁻³⁷⁸ figure should be corrected wherever it appears** in prior reports and
   in the technical reference.
4. **The success criterion** (FR82 §7). Unchanged.
