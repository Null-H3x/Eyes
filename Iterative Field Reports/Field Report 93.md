# Field Report 93 — PETRI'S RNG REIMPLEMENTED AND VERIFIED; THE SWEEP IS NOW A GPU JOB

*Instrument: `eyepetri` (8/8 selftests, Park-Miller KAT verified). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — what this cycle can and cannot deliver

FR92 established that both of the author's generators are seeded from `time(NULL)`,
turning the seed space from an open 2³¹ into a **date range**. The obvious next step is
to exhaust it.

**I cannot, and should say so before spending further effort pretending otherwise.**
Measured single-core rates are 22–32k seeds/s, so one year of timestamp space costs
17–24 minutes *per generator*, and my execution environment caps well below that. Three
separate attempts at 32M, 18M and 8M seeds all exceeded the limit.

**The deliverable is therefore the verified instrument, not my partial coverage.**

---

## 1. The reimplementation, verified

`eyepetri.py` transcribes the author's code verbatim from
`gummikana/MonteCarlo_NoMoreMoney/Source/random/`:

```
Global_LGMRandom::Next()      Park-Miller/Schrage, a=16807, m=2^31-1, q=127773, r=2836
Global_LGMRandom::Random()    low + (int)((high-low+1) * Next())        FLOOR-SCALE
fastrand()                    g = 214013*g + 2531011 ; (g>>16) & 0x7FFF
CRandomSeedSetter()           seeds BOTH from (int)time(NULL)
```

Gate, 8/8:

- **Park-Miller known-answer test**: seed 1 → **16807** → **282475249**. This is the
  standard KAT and it passes, so the arithmetic is provably his.
- `Next()` strictly in (0,1); floor-scale `Random(0,4)` covers all of 0…4 inclusive
  (checking the mapping does not truncate the top value);
- all three deck generators emit genuine permutations; distinct seeds give distinct
  decks.

Three Fisher-Yates variants are provided: `fy_lgm` (descending, the standard idiom),
`fy_lgm_fwd` (ascending, the other common form), and `fy_fastrand` with both
floor-scale and modulo mappings.

---

## 2. The cost model, measured

| generator | seeds/s | one year | 2010–2021 (12y) |
|---|---:|---:|---:|
| `fy_lgm` (default) | 24,488 | 21 min | 4.3 hours |
| `fy_lgm_fwd` | 22,144 | 24 min | 4.8 hours |
| `fy_fastrand` | 31,646 | 17 min | 3.3 hours |

**Single-core, all three generators, twelve years of timestamp space: ~12.4 hours.**
At EyeStat's demonstrated GPU rate of 272k/s the same work is **under 25 minutes.**

Swept so far: 360,000 seeds from 2019-01-01 across all three generators, **zero hits** —
a rate measurement rather than meaningful coverage, and reported as such.

---

## 3. Why this is the best remaining test

**It is bounded.** Every prior PRNG sweep faced an open 2³¹ space with no principled
stopping point; EyeStat's 34 billion seeds had no natural completion. A timestamp
window *terminates*.

**It is falsifiable.** Exhausting 2010–2021 across both generators and all mappings
either produces `C` outright or **kills the timestamp hypothesis**, which is the last
motivated reduction of the seed space.

**It is independent of FR81.** A seed hit supplies `C` directly, bypassing the
redundancy argument entirely — the FR89 point that sweep and likelihood attacks are
limited by different things.

**The filter cannot produce a false positive.** Selectivity ~83⁻³⁷⁸, measured at zero
false positives per 20,000 random permutations (FR61).

---

## 4. Scope

The timestamp reading assumes generation used the default `CRandomSeedSetter` rather
than an explicit `SetRandomSeeds(n)` call. `random.h` exposes exactly that function for
reproducible runs, and an author wanting a **fixed** alphabet has good reason to use it
with a hand-chosen integer. If so, the seed is arbitrary and the window is meaningless.

Both readings stay live. The timestamp one is simply cheap enough to settle first, and
its failure is informative.

---

## 5. Model status

384 relations over 56 glyphs; injectivity clean; exposure 74.1%; residual 33.59 bits;
inventory 82.5 CI [73.0, 93.7]; no periodic component 2–90; no cut signature; PRNG and
mapping verified from source.

**Cumulative sweep total: 1.37 billion candidates, zero survivors.**

---

## 6. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Petri's RNG | described in doctrine | **reimplemented and KAT-verified** (`eyepetri.py`) |
| Fisher-Yates variant | assumed descending | **three variants** provided; the idiom is not determined by his source |
| Timestamp sweep cost | unmeasured | **~12.4 h single-core / ~25 min GPU** for 12 years, all generators |
| Coverage so far | — | 360,000 seeds, zero hits — a rate measurement, not coverage |

---

## 7. Horizon

1. **Run the timestamp sweep on GPU.** `eyepetri.py` plus `eyesweep.py`'s
   `skeleton_ok` is the whole job. Twelve years, both generators, both mappings, both
   directions, under half an hour. It is the cheapest decisive test the project has,
   and the first PRNG sweep with a natural stopping point.
2. **If it fails, sweep `fastrand` over the full 2³² space** — a generator the project
   did not know existed until FR92.
3. **Read `CardBackGenerator`** (FR91). Still unread.
4. **The success criterion** (FR82 §7). Unchanged.
