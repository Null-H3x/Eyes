# Field Report 64 — THE FIRST ANCHOR IS SPENT ON GAUGE: A CORRECTION TO FR63's ACQUISITION ARITHMETIC

*Instrument: `eyeenum` (5/5 selftests, extended). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — retracting FR63's horizon item 1 as written

FR63 closed with *"rank the 22,550 by any available prior"* and called it the
cheapest path to progress. **That phrasing is wrong and I retract it.**

FR62 established that bulk hypothesis trawling is free *when the filter's
false-positive rate is astronomically small* — at selectivity 83⁻³⁷⁸ a hit cannot be
chance. **There is no such filter here.** The 22,550 are all equally consistent with
every constraint the corpus supplies; that is what it means for them to be the
consistent set. Ranking them by a prior chosen after inspection and taking the top
one is a 1-in-22,550 claim with no validator behind it — precisely the fishing this
project forbids, and the failure mode the MAGICK embedding cycle was retired for.

A prior is admissible only if it was motivated **before** this cycle. Exactly one
qualifies: **H4** (FR43), which implies drift ∈ {1..8, 75..82} if the nine message
labels are consecutive.

That leaves the question FR63 should have asked instead: **what is already
determined across all 22,550, with no anchor at all?**

---

## 1. SELF-CORRECTION — FR63's anchor table is off by one

FR63 reported "1 anchor → 275 survivors, 6.36 bits." That is wrong as a statement
about *real* anchors, and the error is structural rather than arithmetic.

A global rotation of `C` is absorbed into the per-message bases (FR9's gauge
theorem). Verified directly this cycle:

```
rotation preserves all within-component differences and injectivity : TRUE
→ every rotation of a consistent alphabet is itself consistent
→ for ANY (glyph, value) pair there is a rotation of EVERY candidate matching it
```

Therefore **a single absolute anchor discriminates nothing.** It fixes the gauge and
leaves all 22,550 alive. My enumeration fixes `base₁ = 0`, so its "anchors" are
implicitly *relative to glyph 0* — gauge-relative constraints, not real
correspondences. **N real anchors provide N−1 discriminating constraints.**

| real anchors | survivors | bits |
|---:|---:|---:|
| 0 | 22,550 | 0.00 |
| **1 — spent on gauge** | **22,550** | **0.00** |
| 2 | 275 | 6.36 |
| 3 | 37 | 9.25 |
| 4 | 33 | 9.42 |
| 5, random placement | 13 | 10.76 |
| **5 = one per component + gauge** | **1** | **14.46** |

This explains FR54's "two external anchors in component 1" from underneath: the
first is consumed by the rotation, the second supplies the pair-difference that is
bijective in the drift. FR54 stated the *what*; the *why* is that anchor one buys
nothing.

**Consequence: acquisition costs one more anchor than the doctrine implies**, and
FR63's table should be read shifted by one throughout.

**Placement dominates count.** Five randomly placed anchors leave 13 candidates;
five placed one-per-component leave exactly 1. That is a 13× difference at identical
cost, and it sharpens FR54's ordering: after the gauge anchor, put one in each
component before adding a second anywhere.

---

## 2. What packing has already determined, free

Per-glyph entropy over the 22,550 — mean 6.06 bits against 6.38 for uniform over 83.
Nearly flat *on average*, but not uniformly so:

| quantity | possible values | entropy | vs uniform |
|---|---:|---:|---|
| base of component 2 (glyph 13) | **9** of 83 | 3.17 bits | 6.38 |
| base of component 3 (glyph 16) | **14** of 83 | 3.81 bits | 6.38 |
| base of component 4 (glyph 4) | **37** of 83 | 5.21 bits | 6.38 |
| glyphs in component 1 | 82 | 6.36 bits | 6.38 |

**FR27's packing constraint has already done more work than the doctrine credits it
with.** Component 2's base is confined to nine values out of eighty-three before any
external evidence arrives — better than half the uncertainty removed. The smaller
the component, the more the packing of the larger ones pins it.

Actionable consequence: **weak external evidence is worth most where entropy is
highest.** A hint about a component-1 glyph carries up to 6.36 bits; the same hint
about component 2's base carries at most 3.17, because packing already supplied the
rest. FR54 ranked anchors by corpus exposure; this ranks them by information, and
the orderings differ.

*(Glyph 0's zero entropy is my gauge fixing, not a determination — flagged again
because it will otherwise be read as a solved glyph.)*

---

## 3. H4, priced exactly

The one admissible pre-motivated prior:

```
drift ∈ {1..8, 75..82}   →   4,400 survivors   (5.1× reduction, 2.36 bits)
remaining entropy: 12.10 bits   (from 14.46)
mean per-glyph entropy: 4.64 bits (from 6.06)
```

Worth having and not close to sufficient. It also remains conditional on the
consecutive-label premise, which FR43/FR44 established is **not testable from inside
the corpus** — so this is 2.36 bits of *assumption*, not of evidence, and should be
carried as such.

---

## 4. THE ACQUISITION SPECIFICATION

The programme now has a budget rather than a wish:

> **Total to close: 14.46 bits. One anchor of that is unavoidable overhead (gauge).**
> **The remaining 14.46 bits require, at best placement, four further anchors —
> one per component — or any combination of weaker evidence summing to the same.**

Because the set is enumerated, weak evidence composes: a glyph narrowed to ten
values contributes ~3 bits, a probabilistic hint contributes fractionally, and they
add. This is the FR63 §2 reframe, now with the overhead correctly accounted.

What this does **not** license is §0's retracted idea. Ranking without a
pre-motivated prior is not evidence, and 14.46 bits of it cannot be manufactured by
choosing a plausible-looking ordering.

---

## 5. Scope

Covers the 46 determined glyphs (components 25/11/7/3). The five two-glyph
components add five further free bases; the 27 undetermined glyphs remain freely
permutable among leftover values. Conditional on repair A.

---

## 6. Model status — unchanged

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity
clean; exposure 768/1036 = 74.1%; repair A the unique maximal reading; drift
unpinned.

---

## 7. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| "Rank the 22,550 by any prior" (FR63) | my horizon item | **RETRACTED** — fishing without a validator; only pre-motivated priors admissible |
| FR63's anchor table | 1 anchor → 275 survivors | **CORRECTED** — first anchor is gauge; N real anchors = N−1 constraints |
| Why FR54 needs two anchors in component 1 | stated, unexplained | **EXPLAINED** — anchor one is consumed by the global rotation |
| Anchor placement | ranked by corpus exposure (FR54) | **placement dominates count** — 5 spread → 1 candidate, 5 random → 13 |
| Packing's contribution | pruning factor on completions | **already fixes component 2's base to 9 of 83 values**, before any anchor |
| H4 | qualitative 5.1× narrowing | **2.36 bits**, and it is assumption, not evidence |

---

## 8. Horizon

1. **Acquire the gauge anchor plus one per component.** The specification is now
   exact: five real anchors, spread one-per-component, uniquely determine all 46
   glyphs and 61.3% of the corpus. Anything less than five leaves ≥13 candidates
   under random placement.
2. **Target high-entropy glyphs.** Component 1's glyphs carry 6.36 bits each;
   component 2's base carries 3.17. Evidence is not fungible across components.
3. **Count the MSB states on the glyph pictures** (FR59 §4) — still cheap, still
   symmetric, still outstanding.
4. **Settle the radix** (`GHIDRA.md`) — load-bearing for FR58/FR59.
5. **Port the filter into EyeStat** (FR61/FR62) — unchanged.
