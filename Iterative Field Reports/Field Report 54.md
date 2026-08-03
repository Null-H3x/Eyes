# Field Report 54 — What the Ceiling Is Made Of

**Series note.** Fifty-fourth report of the EYESPIRAL series. Fifty-three reports have
quoted the 74.1% exposure figure without once asking what the *other* 25.9% consists of.
Instrument `eyetarget.py`, selftest 7/7 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** The model determines 56 glyphs and leaves **27 outside every
component**, covering 268 corpus positions. Those 27 are **systematically rarer** — mean
corpus frequency 9.93 against 13.71, z = **+4.32**, where a random split of the same sizes
gives z = +0.29 — so the ceiling is largely a **sampling limit** rather than anything
structural: rare glyphs co-occur in fewer isomorph windows and so never get linked. The
separation is real but not clean; the most common undetermined glyph appears 17 times, more
often than a third of the determined ones. The consequence for acquisition is the
substantive result. **A component anchor buys the whole component; a singleton anchor buys
only its own positions.** One anchor in component 2 buys 179 positions; the best singleton
buys 17 — more than a tenfold difference in yield. That gives a strict priority ordering
which the standing summary ("ten anchors reach 74.1%") obscures: **the first two anchors are
worth more than the next eight combined.**

---

## 1. G1–G2 — the partition

| | glyphs | positions | corpus |
|---|---|---|---|
| determined | 56 | 768 | 74.1% |
| **undetermined** | **27** | **268** | **25.9%** |

| | mean freq | median | range |
|---|---|---|---|
| determined | 13.71 | 13.0 | 3–26 |
| **undetermined** | **9.93** | 10.0 | 5–17 |

**z = +4.32.** The gate checks this is not an artefact of the group sizes: a random split
into 56 and 27 gives z = +0.29.

So the undetermined glyphs are genuinely the rarer ones — which is what a sampling
explanation predicts, since a glyph enters a component only by appearing in a certified
isomorph window alongside another. It is *not* a clean separation, though: the most common
undetermined glyph (2, appearing 17 times) is commoner than 19 of the 56 determined ones.
The ceiling is therefore mostly about co-occurrence luck, not about those glyphs being
special.

## 2. G4 — anchor yield

| target | glyphs | positions | corpus | anchors needed |
|---|---|---|---|---|
| **component 1** | 25 | **323** | **31.2%** | 2 |
| **component 2** | 11 | **179** | 17.3% | 1 |
| component 3 | 7 | 104 | 10.0% | 1 |
| components 4–9 | 2–3 each | 24–29 | 2.3–2.8% | 1 each |
| glyph 2 (best singleton) | 1 | 17 | 1.6% | 1 |
| glyph 11 | 1 | 16 | 1.5% | 1 |
| … 25 more singletons | 1 | 5–15 | ≤1.4% | 1 each |

**Every component anchor outyields every singleton anchor.** The gap between the worst
component (24 positions) and the best singleton (17) is narrow, but the gap at the top is
not: component 2 is worth ten and a half singletons.

## 3. G5 — the acquisition priority

| step | cumulative anchors | cumulative corpus |
|---|---|---|
| **component 1** (base + drift) | **2** | **31.2%** |
| component 2 | 3 | 48.5% |
| component 3 | 4 | 58.5% |
| component 4 | 5 | 61.3% |
| components 5–9 | 6–10 | 63.6% → **74.1%** |
| glyph 2 | 11 | 75.8% |
| glyphs 11, 43, 29, 8 | 12–15 | 81.3% |

The first two anchors deliver 31.2%; the next eight deliver 42.9% between them. And the
*second* anchor is doing something the others cannot: it supplies a known pair-difference,
which is bijective in the drift (FR26), and therefore pins the drift for the **entire
system** at once — not just for component 1.

**A programme acquiring anchors opportunistically rather than by this ordering will spend
considerably more for the same exposure.** That is a practical result and it has not been
stated before: the standing summary treats the ten anchors as interchangeable, and they are
not.

## 4. What this changes

**Changes.** The acquisition target is now ordered rather than merely counted. Prior
reports said "two anchors in component 1, then one per component"; this adds *which*
components are worth most, that all component anchors beat all singletons, and that the
ceiling above 74.1% costs roughly one anchor per 1.5 points of exposure.

**Does not change.** The model: 384 relations over 56 glyphs, components 25/11/7/3 plus
five pairs, injectivity clean, 74.1% exposure, repair A the unique maximal reading, drift
unpinned with H4 the only surviving hypothesis.

## 5. A caveat on the whole exercise

None of this changes what the anchors would deliver, which FR46 and FR39/FR40 settled:
plaintext **values** in 0…82 drawn from an inventory exceeding ~60, not a reading. This
cycle sharpens *how to get there most cheaply*, not *whether arriving is worth it*. The
success criterion remains the more consequential question and nothing measurable bears on
it.

## 6. Horizon

(1) **Two external anchors in component 1**, and the ordering above for anything beyond
them. (2) **The success criterion** — unchanged, and now the only item of consequence that
this series can neither compute nor close. (3) Re-run the canonical derivation (FR53)
whenever the skeleton changes; this cycle's tables inherit from it and would go stale the
same way.

## 7. Reproduction

`eyetarget.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
7-check gate — the skeleton confirmed, glyphs and positions partitioning exactly, the
rarity statistic with a random-split calibration, component anchors shown to outyield
singletons by more than fivefold, and the baseline guard. The full run reproduces G1–G5.
Failures carry prefix `XD-MBYG04K-URS3LF`.
