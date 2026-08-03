# Field Report 52 — Figures That Stopped Being True

**Series note.** Fifty-second report of the EYESPIRAL series, and the third of three run in
succession. FR51 concluded the internal evidence base is as examined as it can be made
without new data. This cycle checks something different: whether the *derived* figures the
doctrine quotes still hold. Instrument `eyestale.py`, selftest 7/7 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** The skeleton grew from 47 glyphs to 56 across FR33 and FR34, and
figures derived from the older version do not update themselves. Two are stale. **FR20's
usable adjacent-pair count is 558, not 464** — and it is doubly out of date, since FR39's
cross-message pooling superseded that channel entirely with 6,384 pairs. More
consequentially, **FR27's packing constraint is far tighter than published**: 9 × 10⁷ valid
placements rather than 1.5 × 10¹⁰, a pruning factor of roughly **2.4 × 10⁷ instead of
1.5 × 10⁵** — about 160 times stronger. Larger components pack harder, so the widening
bought considerably more than its relation count alone suggested. The residual curve
correspondingly tightens, reaching 37 completions at nine anchors rather than 44 — though
the *middle* of that curve is estimator-noisy and non-monotonic, for a reason worth stating
rather than hiding: the estimator fixes each anchored component's base at zero, which is
arbitrary and need not be jointly valid. Only the endpoints should be read as reliable.

---

## 1. T1 — the adjacent-pair count

| | value |
|---|---|
| published (47-glyph skeleton) | 464 |
| **current (56-glyph skeleton)** | **558** |

Stale, but the correction hardly matters, because the channel it belonged to was replaced:
FR39 showed that cross-message pairs inside a component are drift-free by the same argument
as within-block pairs, taking the sample to **6,384**. FR20's within-block figure should not
be quoted at all.

## 2. T2 — the packing constraint

| | placements | pruning |
|---|---|---|
| published (47 glyphs, 9 components) | 1.5 × 10¹⁰ | 1.5 × 10⁵ |
| **current (56 glyphs, 9 components)** | **9 × 10⁷** | **2.4 × 10⁷** |

**About 160 times tighter.** This is the least expected result of the three cycles. The
widening was reported in FR33/FR34 in terms of relations (223 → 384) and exposure
(64.6% → 74.1%), and those figures understate what it did to the packing problem: component
1 grew from 19 glyphs to 25, and a component's value-set becomes much harder to place
disjointly as it grows. The constraint FR27 measured as real-but-not-decisive is now four
orders of magnitude short of enumerable rather than five.

## 3. T3 — the residual curve, with its caveat

| anchors | remaining placements | glyphs | corpus |
|---|---|---|---|
| 2 | ~9 × 10⁷ | 25 | 31.2% |
| … | *(noisy — see below)* | | |
| 9 | **37** | 54 | 71.5% |
| 10 | **1** | 56 | 74.1% |

Published: 44 completions at nine anchors. Now 37.

**The middle of this curve should not be read.** The estimator fixes each anchored
component's base at zero, which is an arbitrary choice and need not be jointly valid, so
intermediate counts come out noisy and occasionally non-monotonic — fixing *more*
components appearing to leave *more* placements, which is impossible. Only the endpoints
are trustworthy. Reporting the curve without this caveat would invite exactly the
over-reading the series has spent several cycles correcting.

## 4. T4 — what the doctrine should now carry

| quantity | current value |
|---|---|
| A-vs-B channel sample | **6,384 pooled pairs** (FR39), not FR20's within-block count |
| packing placements | **~9 × 10⁷**, pruning ~2.4 × 10⁷ |
| two anchors in component 1 | 25 glyphs, **31.2%** of the corpus |
| ten anchors | 56 glyphs, **74.1%** |

The acquisition arithmetic is unchanged. The packing figure is simply stronger than
recorded.

## 5. The three cycles together

| cycle | result |
|---|---|
| **FR50** | class #2 audits clean — k = 5, chance 2 × 10⁻⁷ corpus-wide, zero in 2000 shuffles; its standalone instance is not comparable to E1@68 because the skeleton weights differ by four orders of magnitude |
| **FR51** | the strict tier is *implied* by the atlas (158/158 rows redundant, no conflicts) — method-level corroboration of the inherited classes, not waste |
| **FR52** | two derived figures were stale; the packing constraint is ~160× tighter than published |

Between them, both load-bearing pieces are now audited (FR48, FR50), the inherited atlas is
corroborated by an independent scan (FR51), and the derived arithmetic is current (FR52).

## 6. Where the model stands

384 relations over 56 glyphs, components 25/11/7/3 plus five pairs, injectivity clean,
74.1% exposure. Repair A the unique maximal reading (likelihood ratio ~2.8 × 10⁵ over B).
Drift unpinned, H4 the only surviving hypothesis. Plaintext: large effective inventory, no
detected structure. Openings: stamped headers, untestable independently.

## 7. Horizon

(1) **Two external anchors in component 1** remain the only route to the drift — 25 glyphs
and 31.2% of the corpus from the first two alone. (2) **The success criterion** is unchanged
as the most consequential open item, and nothing measurable bears on it. (3) Any figure
derived from the skeleton should be recomputed whenever the skeleton changes; this cycle
found two that were not, and there is no mechanism preventing a third.

## 8. Reproduction

`eyestale.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
7-check gate — the current skeleton confirmed at 56 glyphs, the adjacent-pair counter exact
on a constructed case, both published figures shown stale, the packing estimator finite and
sane, fixing every component leaving exactly one placement, and the baseline guard. The
full run reproduces T1–T4. Failures carry prefix `XD-MBYG04K-URS3LF`.
