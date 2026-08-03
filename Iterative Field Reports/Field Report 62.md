# Field Report 62 — WHEN THE FILTER IS SAVAGE ENOUGH, FISHING IS FREE

*Instrument: `eyeorder` (6/6 selftests, green before sweeping). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — correcting FR59

FR59 left "irreducible three-feature construction" as the sole survivor in
`eyeforward`'s labeling-frame hiding place and called it *"untested and probably
untestable without a specific candidate."* **That was too pessimistic, and FR61 is
the reason.**

The usual objection to trawling many hypotheses is multiple comparisons: test enough
things and something fires. That objection has force only when the false-positive
rate is non-negligible. The skeleton filter's selectivity is of order **83⁻³⁷⁸**, and
FR61 measured 0 false positives over 20,000 random permutations. At that rate,
**bulk hypothesis trawling carries no multiple-comparison cost at all** — a hit
cannot be chance, so there is no penalty for having looked.

The correct statement is not that structured construction is untestable. It is that
it is testable **one specific candidate at a time**, and the filter makes generating
candidates in bulk the only cost. That is a different, and much more tractable,
problem.

---

## 1. A structural result that halves all future sweeps

While designing the sweep: if `q` satisfies the skeleton with drift `d`, then for any
`a ≠ 0`,

```
(a·q + b)[g₂] − (a·q + b)[g₁] = a·(q[g₂] − q[g₁]) = (a·d)·(Δ₂ − Δ₁)
```

so `a·q + b` satisfies it with drift `a·d`. **The filter is invariant under affine
post-composition** — verified in the gate across 15 (a,b) combinations.

Consequence: the 6,806-member family `{a·q + b}` is covered automatically for every
candidate, at zero cost. Only affine **pre**-composition on glyph labels,
`q[(a·g+b) mod 83]`, needs explicit sweeping. Any future sweep that enumerates both
is doing 6,806× redundant work.

---

## 2. What was swept

**Mathematical / structural orderings (22):** identity, reverse, base-5 digit
reverse, digit-sum, digit-product, digit-max, digit-min, digit-sort, reflected Gray
code base 5, 7-bit bit-reversal, quadratic-residue ordering, multiplicative inverse,
and **discrete exponentiation** `g ↦ aᵍ mod 83` for ten primitive-root bases.

The discrete-exponentiation family is worth naming: it is **neither affine nor a
power map**, so it lies outside everything FR28 and FR58 excluded. It is the natural
"multiplicative" construction and had never been tested.

**In-game orderings (21), harvested from the Noita `data/` dump:** `materials.xml`
name order, `ui_gfx/gun_actions`, `ui_gfx/perk_icons`, `items_gfx/perks`,
`items_gfx/wands`, `generated/material_icons`, `generated/sprite_uv_maps` — each in
three truncations to 83 (head, tail, alphabetical). This closes the thread the
builds-data dump opened: if Petri had numbered the glyphs off an existing in-game
list, these are the lists.

**Two-stage compositions:** all 1,849 ordered pairs `π₁ ∘ π₂`, generalising the
documented double-back-to-back-shuffle idiom to structured orderings.

All of the above × 6,806 affine pre-compositions × 2 directions (`q` and `q⁻¹`).

---

## 3. Results

| sweep | candidates | survivors |
|---|---:|---:|
| FR61 — PRNG, 4 families × 2 directions | 2,000,000 | 0 |
| FR62a — structured × affine × 2 | 585,316 | 0 |
| FR62b — two-stage × affine × 2 | 25,168,588 | 0 |
| **cumulative under an informative filter** | **27,753,904** | **0** |

Gate throughout: random ordering gives 0 hits over its full 6,806-variant affine
family; a planted affine pre-composition of a valid alphabet is recovered.

---

## 4. THE COST MODEL, CORROBORATED AND SHARPENED

FR61 estimated a complete Park-Miller sweep at 17–47 GPU-hours on the argument that
filtering is cheaper than permutation generation. This cycle measures it directly:

```
FR61 (PRNG generation + filter) :  15,000 – 34,000 candidates/s
FR62 (indexing + filter)        : 173,000 – 178,000 candidates/s
```

**A 5–11× speedup from removing permutation generation alone**, in the same
interpreter on the same core. The filter is nearly free; generation is the whole
cost. FR61's estimate stands, and the corollary matters for how effort is spent:

> Investment should go into **candidate generation breadth**, not filter throughput.
> The filter will not be the bottleneck at any realistic scale.

---

## 5. What this does not cover

- **Non-structured `C`.** A hand-built arbitrary permutation is invisible to any
  generator-based sweep and only anchors reach it.
- **Seeding and construction conventions** outside §2 — string seeds, hashed seeds,
  time-derived seeds, three-stage compositions, keyed alphabets over 83 symbols.
- **Necessary, not sufficient.** The filter uses the 46 glyphs I hold; a hit would
  require verification against the full 56-glyph skeleton, injectivity and packing.
- **Conditional on repair A**, like everything downstream of FR26.
- **In-game orderings are excluded only in the truncations tested** (head / tail /
  alphabetical). A filtered subset chosen on some other criterion is not covered.

---

## 6. Model status — unchanged

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity
clean; exposure 768/1036 = 74.1%; repair A the unique maximal reading; drift unpinned
with H4 the only surviving hypothesis.

---

## 7. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Structured `C` "probably untestable" (FR59) | my assessment | **CORRECTED** — savage filter removes the multiple-comparison cost; testable in bulk |
| Affine post-composition | swept explicitly | **PROVED INVARIANT** — 6,806× redundant work in any sweep that enumerates it |
| Discrete exponentiation `g ↦ aᵍ` | never tested (outside FR28/FR58 families) | **EXCLUDED** |
| In-game list orderings as `C` | raised by the builds-data dump | **EXCLUDED** in head/tail/alphabetical truncations |
| Two-stage structured composition | untested | **EXCLUDED** across 1,849 pairs |
| Filter throughput | assumed comparable to chi² | **measured 173–178k/s single-core Python**; generation is the bottleneck |

---

## 8. Horizon

1. **Port the filter into EyeStat and run the complete Park-Miller space.** Unchanged
   as the top item, and this cycle strengthens the case: the filter is provably not
   the bottleneck, so the port is straightforward and the 17–47 hour estimate is if
   anything conservative.

2. **Broaden candidate generation, not filter speed** (§4). The natural next tiers
   are string/hashed seeds, three-stage compositions, and keyed alphabets over 83
   symbols.

3. **Count the MSB states on the glyph pictures** (FR59 §4). Still the cheapest open
   question, still symmetric, still needs no binary.

4. **Settle the radix** (`GHIDRA.md` base-7 vs corpus base-5). Load-bearing for FR58
   and FR59.

5. **Standing, unchanged:** two external anchors in component 1 (FR54 ordering); and
   the success criterion, which FR57 made decidable and which remains undecided.
