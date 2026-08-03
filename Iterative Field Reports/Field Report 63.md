# Field Report 63 — THE ANSWER IS ONE OF 22,550: THE ACQUISITION PROBLEM IS 14.5 BITS

*Instrument: `eyeenum` (5/5 selftests). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — against my own last five cycles

FR58 through FR62 were all C-hunting nulls: 27.75 million candidates, zero
survivors. That programme has a structural weakness I had not examined —
**generate-and-filter can only cover constructions someone thought to generate.**
Five nulls say nothing about the constructions nobody enumerated.

The inverse question was never asked: **how large is the set of alphabets the
skeleton actually permits?** If that set is small, enumerating it dominates guessing
at generators, because it covers every construction at once — including ones nobody
will ever think of.

Inside a component `q[g] = base_c + drift·Δ_g`, so a partial alphabet over the 46
determined glyphs is fixed entirely by `(drift, base₁…base₄)` with one base a gauge
freedom (FR9: a global rotation of `C` is absorbed into the per-message bases).
Injectivity across components is FR27's packing constraint.

---

## 1. The exact size of the answer space

FR53 proved the packing count is drift-invariant and reported 275 on the four
largest components. Verified independently here rather than inherited:

```
packings at drift 1, 2, 3, 5, 7, 17, 31, 41, 82  →  275, identical at every drift
```

Therefore:

| quantity | value |
|---|---|
| packings per drift | **275** |
| non-degenerate drifts | 82 |
| **total consistent alphabets over 46 glyphs** | **22,550** |
| **residual entropy** | **14.46 bits** |

Every selftest passes: all enumerated packings are genuinely injective over the 46
glyphs, and the degenerate all-zero base assignment is correctly excluded.

**This is the headline.** After sixty-two cycles the determined portion of `C` is
not "unknown" — it is one of twenty-two thousand five hundred explicitly
enumerable possibilities. That is a smaller object than the doctrine's language
around it suggests.

---

## 2. THE STRATEGIC REFRAME

The acquisition programme has been framed throughout as *acquire external anchors* —
certain, verified (glyph, value) correspondences. That framing was correct when the
alternative was 83! orderings. It is the wrong framing now.

> **The problem is not acquiring certainty. It is acquiring 14.46 bits.**

Because the set is enumerable, **any evidence that discriminates among 22,550
hypotheses is usable**, including evidence far too weak to constitute an anchor:

- a single glyph's value narrowed to a range of ten → ~3 bits
- a probabilistic hint over any glyph → fractional bits, and they **add**
- a plausibility ordering over candidate alphabets → usable as a ranking, no
  certainty required
- partial or noisy information from the binary, the pictures, or dev statements —
  none of which needs to be conclusive

This matters because FR60's discussion of anchors emphasised that a single anchor is
*unfalsifiable in isolation* — you cannot check it, because FR57 removed the "does
it read as language" validator. **Enumerability dissolves that objection.** You no
longer need a correspondence you can verify; you need evidence that reweights an
enumerated list, which is a far weaker and far more available thing.

---

## 3. Exact anchor arithmetic

Replacing FR27/FR52's estimates with exact counts over the enumerated set:

| evidence | survivors (mean / median) |
|---|---|
| none | 22,550 |
| 1 anchor, random glyph | 390 / 275 |
| 2 anchors, random glyphs | 106 / 39 |
| 3 anchors, random glyphs | 85 / 29 |
| **2 anchors both in component 1** | **275 / 275** |
| **1 anchor in each of the 4 components** | **1 / 1** |

Two results deserve attention.

**Two anchors inside component 1 leave 275 survivors.** They do exactly what FR54
said — fix the drift (a pair-difference is bijective in it) and `base₁`, determining
all 25 glyphs of component 1 — but the other three component bases remain free,
and 275 packings survive. FR54's exposure figure (31.2%) is correct; what it did not
state is that **the remaining ambiguity after those two anchors is still 275-fold**.

**Four anchors, one per component, determine everything uniquely.** Four equations
against four unknowns (drift plus three non-gauge bases) is exactly determined, and
the measurement confirms a single survivor — all 46 glyphs, **61.3%** of the corpus.
Under FR54's ordering four anchors yield 58.5%. **Spreading anchors one-per-component
reaches full determination of the held components at the same anchor count**, which
is a refinement of FR54's ordering rather than a contradiction of it: FR54 optimises
exposure at two and three anchors, but at four the spread placement dominates.

---

## 4. Per-glyph uncertainty is not uniform

| glyph | distinct values across the set |
|---|---|
| glyph 0 | **1** — *gauge artifact, see below* |
| glyph 4 (component 4, size 3) | 37 |
| glyphs 1, 5, 6, 7 (component 1) | 82 |
| range across all 46 | 1 – 83 |

**Glyph 0's single value is an artifact of my gauge fixing** (`base₁ = 0`), not a
determination. Flagged explicitly because it would otherwise read as a solved glyph.

The real content is that **glyphs in small components are more constrained by
packing** — component 4's glyph 4 admits 37 values against component 1's 82. So
external evidence is worth *more bits* when it concerns a large-component glyph, and
weak evidence about a small-component glyph is correspondingly cheaper to obtain but
less informative. FR54's ordering ranked anchors by corpus exposure; this ranks them
by information, and the two orderings are not the same.

---

## 5. Scope

- Covers the **46 determined glyphs** I hold (components 25/11/7/3). The five
  two-glyph components add five more free bases; FR54's full-skeleton figures remain
  the reference for the 56-glyph case.
- The **27 undetermined glyphs are untouched** — they remain freely permutable among
  the leftover values, so this is not 14.46 bits for the whole alphabet, only for
  its determined portion.
- Conditional on repair A, like everything downstream of FR26.
- The gauge freedom is genuine (FR9), so 22,550 counts physically distinct
  alphabets, not labelings.

---

## 6. Model status — unchanged

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity
clean; exposure 768/1036 = 74.1%; repair A the unique maximal reading; drift
unpinned.

---

## 7. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Size of the answer space | qualitative ("drift unpinned", packing estimates) | **EXACTLY 22,550**, 14.46 bits, enumerated |
| FR53's 275 packings | published | **independently reproduced**, drift-invariance verified at 9 drifts |
| Acquisition framing | acquire certain anchors | **acquire 14.46 bits** — weak/probabilistic evidence is usable |
| "A single anchor is unfalsifiable" (FR60) | a real objection | **dissolved by enumerability** — evidence reweights a list, no verification needed |
| 2 anchors in component 1 | 31.2% exposure (FR54) | correct, **but 275-fold ambiguity remains** |
| 4 anchors | 58.5% under FR54's ordering | **one-per-component → unique, 61.3%** |
| Anchor value ranking | by corpus exposure (FR54) | **by information**, which ranks differently |

---

## 8. Horizon

1. **Rank the 22,550 by any available prior.** This is now the cheapest path to
   progress and it needs no new evidence at all: plausibility over drift values,
   over base offsets, or over the resulting glyph-value patterns produces an ordered
   list to test. The top candidates can be checked against the full 56-glyph
   skeleton, injectivity and packing directly.
2. **Reframe the external hunt around bits, not anchors** (§2). Weak evidence from
   the binary, the pictures, or dev statements now has a well-defined value.
3. **Count the MSB states on the glyph pictures** (FR59 §4) — still cheap, still
   symmetric.
4. **Settle the radix** (`GHIDRA.md`) — load-bearing for FR58/FR59.
5. **Port the filter into EyeStat** (FR61/FR62) — unchanged, though §2 makes it less
   urgent relative to enumeration.
