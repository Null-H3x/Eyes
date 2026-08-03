# Field Report 94 — HIS ACTUAL SEEDING PRACTICE IS A SMALL EXPLICIT INTEGER

*Instrument: `eyepetri` (corrected), `CardBackGenerator` archival. July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — FR93's caveat was the likely case, not the alternative

FR93 built the timestamp sweep on `CRandomSeedSetter`, which seeds from `time(NULL)`,
and logged a caveat: *"random.h exposes `SetRandomSeeds(int)` for reproducible runs, and
an author wanting a fixed alphabet has good reason to use it with a hand-chosen
integer."*

`gummikana/CardBackGenerator` — a **procedural art generator**, which is precisely what
producing a fixed cipher alphabet is — settles which reading is his practice:

```cpp
list_(double, seed, 1234, MetaData( 0, 10000 ) )
...
ceng::CLGMRandom randomizer;
randomizer.SetSeed( config.seed );
```

**Not `time(NULL)`. An explicit config seed, default 1234, exposed on a UI slider with
range 0 to 10000.**

When this author generates reproducible procedural output, he uses a **small
hand-chosen integer**. That is direct primary-source evidence about the seed space, and
it inverts FR93's ordering: the timestamp window is the *alternative*, not the primary.

---

## 1. SELF-CORRECTION — a bug in my own instrument

Reading `SetSeed` raised an alarm:

```cpp
void Global_LGMRandom::SetSeed( double s ) { seed = s; iseed = 0; }
```

`iseed = 0` would degenerate the Schrage step. Checking `Next()`:

```cpp
double Global_LGMRandom::Next() {
    long iseed = (long)seed;        // LOCAL, shadows the member
    ...
    seed = (double)iseed; return seed*4.656612875e-10;
}
```

The member `iseed` is written once and **never read** — the state lives entirely in the
double `seed`. My LGM implementation was correct after all, and the KAT confirms it.

**But `fastrand` was wrong:**

```cpp
void set_fastrand_seed( int seed ) { g_seed = seed ^ 13 - 1;
```

C precedence binds `-` tighter than `^`, so this is **`g_seed = seed ^ 12`**. My
`fy_fastrand` seeded with the raw value. Every fastrand result in FR92 and FR93 —
including the 400,000-seed rate measurement — tested the **wrong stream**.

Corrected in `eyepetri.py` and re-run.

---

## 2. Sweeps

| generator | seed range | result |
|---|---|---|
| `fy_lgm` (default) | 0 … 1,000,000 | NONE |
| `fy_lgm_fwd` | 0 … 1,000,000 | NONE |
| `fy_fastrand` floor *(pre-fix)* | 0 … 1,000,000 | void — wrong seeding |
| `fy_fastrand` mod *(pre-fix)* | 0 … 1,000,000 | void — wrong seeding |
| **`fy_fastrand` floor** *(corrected)* | **0 … 2,000,000** | **NONE** |
| **`fy_fastrand` mod** *(corrected)* | **0 … 2,000,000** | **NONE** |

Both directions throughout. The UI range that motivated this (0–10,000) is covered two
hundred times over, and the LGM sweep covers a hundred times over.

**Zero survivors.**

---

## 3. What this settles and what it does not

**Settles:** if the alphabet came from his own generator seeded the way he seeds
procedural art — a small explicit integer, LGM or fastrand, either Fisher-Yates
direction — **it is not in the first million seeds.** The natural range is exhausted
several orders beyond the slider bound.

**Does not settle:** the timestamp hypothesis (G1 in the GPU queue), the full 2³¹/2³²
spaces, or generation outside his own toolkit entirely.

**Sharpens the picture from FR89.** Every construction the author is known to favour is
now excluded over its natural parameter range: Mnemonica (FR91), faro (FR91), cuts
(FR90), Finnish keywords (FR89), in-game text (FR89), and now his own RNG at his own
seeding practice. The arbitrary-`C` reading strengthens with each.

---

## 4. Model status

384 relations over 56 glyphs; injectivity clean; exposure 74.1%; residual 33.59 bits;
inventory 82.5 CI [73.0, 93.7]; no periodic component 2–90; no cut signature; PRNG,
integer mapping and **fastrand seeding** now verified from source.

**Cumulative sweep total: 1.38 billion candidates, zero survivors.**

---

## 5. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| His seeding practice | assumed `time(NULL)` (FR93) | **small explicit integer**, default 1234, UI range 0–10000 |
| Seed-space priority | timestamp window primary | **small-integer primary**, timestamp secondary |
| `set_fastrand_seed` | assumed raw seed | **`seed ^ 12`** — FR92/FR93 fastrand results **VOID** |
| `Global_LGMRandom` state | ambiguous (`iseed = 0`) | **state is the double `seed`**; member `iseed` never read |
| Small-integer seed space | untested | **exhausted to 1–2 million**, all generators, both directions |

---

## 6. Horizon

1. **GPU queue G1 is demoted, not cancelled.** The timestamp window is now the
   secondary hypothesis. Still worth its 25 minutes, but after G2.
2. **Promote fastrand full-space** (G2) — it was swept with the wrong seeding
   throughout, so it is effectively untested.
3. **Read `procedural_triangles.cpp` in full.** 704 lines of his procedural-generation
   idiom; this cycle read only the seeding. If he has a characteristic
   shuffle-then-transform pattern, it is there.
4. **The success criterion** (FR82 §7). Unchanged.
