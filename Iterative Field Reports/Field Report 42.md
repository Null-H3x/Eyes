# Field Report 42 — FR41 Is Withdrawn

**Series note.** Forty-second report of the EYESPIRAL series. FR41 reported the first
structural evidence about the plaintext to survive FR36 and FR39. This cycle finds that
result to be an artifact of the skeleton's own geometry and withdraws it. Instrument
`eyenull.py`, selftest 4/4 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** FR41 claimed local repeat avoidance in the plaintext at
p = 0.0013. The claim is **withdrawn**. A coincidence at distance *d* requires two glyphs
whose Δ values differ by exactly *d*, sitting *d* apart — and the skeleton's Δ set is
heavily depleted in exactly the range where FR41 found its gap: **33 of 384
within-component glyph pairs have a Δ-difference in 9–17, which is 8.6% where uniform
would give 22.0%.** Coincidences at those distances are therefore about 2.6 times rarer
for geometric reasons, before the plaintext is consulted at all. FR41's null could not see
this because it permuted **v-values** freely, which destroys the v = Δ − t construction and
with it the geometry. The correct null permutes which **glyph** occupies each position
*within each (message, component) block*: that preserves block membership, positions and
the Δ multiset exactly — the pair-count profile drifts by **zero** — while randomising only
the plaintext. Under it the null's own mean is **−2.76** against an observed **−3.36**, and
**P = 0.108. Not significant.** The corrected null is not merely insensitive: it detects a
strong planted avoidance at p < 0.005, which the gate asserts. What still stands is FR36,
FR39 and FR40; A-vs-B returns to where FR40 left it.

---

## 1. The artifact

| Δ-difference *d* | glyph pairs |
|---|---|
| 1–8 | 97 |
| **9–17** | **33** |
| 18–25 | 73 |

Across all within-component glyph pairs, differences in 9–17 account for **8.6%** where a
uniform spread would give **22.0%** — a depletion of about 2.6×. Since a coincidence at
distance *d* *requires* a glyph pair with Δ-difference *d*, this suppresses coincidences at
precisely the distances FR41 reported as anomalous, with no involvement from the plaintext
whatsoever.

## 2. The two nulls

| null | mean | 5th pct | P(≤ observed) |
|---|---|---|---|
| FR41's — v-values permuted within blocks | −2.02 | −2.64 | **0.0017** |
| **corrected — glyphs permuted within blocks** | **−2.76** | **−3.55** | **0.108** |

Observed max-deficit z = −3.36 at range (4, 17) in both cases; only the null changes.

The gap between the two null means, −2.02 against −2.76, is the size of the geometry
FR41's null destroyed. Nearly all of the apparent effect lived there.

**The corrected null preserves the geometry exactly.** Permuting glyphs *within* a
(message, component) block leaves block membership, positions and the Δ multiset
untouched, so the pair-count profile by distance drifts by zero — asserted in the gate. An
earlier attempt that permuted glyphs across a whole message failed this check, because it
moved glyphs between components and changed the sampling structure; that version was
discarded.

**And it has power.** A planted arrangement avoiding coincidences within 25 positions is
detected with a null fraction below 0.005. So the withdrawal is not the result of building
a test that cannot see anything.

## 3. What went wrong, stated generally

A permutation null must randomise **only the quantity under test** and preserve everything
else. FR41's null randomised the plaintext and the instrument's geometry together, and the
inflation was large enough to turn a null result into a headline. That the observed
statistic was unchanged between the two analyses makes the point sharply: the entire
difference between "p = 0.0013" and "p = 0.108" is a choice about what the null holds
fixed.

This is the second time in three cycles that a methodological fix has overturned a
result — FR41 corrected FR40's unusable pre-registration, and FR42 now corrects FR41's
null. Both errors were mine, and both were found by asking what the test was actually
holding constant.

## 4. What still stands

- **FR36:** small *contiguous* plaintext alphabets excluded, with planted controls
  recovering the drift at rank 1.
- **FR39:** small *scattered* plaintext alphabets excluded at 3.3σ.
- **FR40:** the channel validated by a positive control — z ≈ +6 on known shared
  plaintext, quiet on a non-near-duplicate pair.
- **The skeleton:** 384 relations over 56 glyphs, components 25/11/7/3 plus five pairs,
  injectivity clean, 74.1% exposure, drift unpinned.

A-vs-B therefore returns to where FR40 left it: **the plaintext has a large effective
inventory and no structure this series has detected.** FR41's brief reopening is closed.

## 5. The doctrine question, unaffected

FR40 raised it and it is untouched by this correction: recovering C yields a token stream,
not a reading; two external anchors would determine 25 glyphs and a quarter of the corpus
as numbers. Whether that constitutes solving the Eye Messages is a question about the
project's success criterion, and it remains the most consequential open item.

## 6. Horizon

(1) **Settle the success criterion** — it governs whether acquisition is worth pursuing,
and nothing measurable now bears on it. (2) **Any future plaintext statistic must be
tested against a geometry-preserving null**; the within-block glyph permutation built here
is the reusable instrument for that. (3) Two external anchors in component 1 remain the
only route to the drift, after which H1's prediction of drift 31 becomes testable.

## 7. Reproduction

`eyenull.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
4-check gate — the Δ-difference depletion measured, the within-block glyph permutation
shown to preserve the pair profile exactly (drift 0), the corrected null shown to detect a
strong planted avoidance, and the baseline guard. The full run reproduces X1–X4. Failures
carry prefix `XD-MBYG04K-URS3LF`.
