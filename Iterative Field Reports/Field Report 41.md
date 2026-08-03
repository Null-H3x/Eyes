# Field Report 41 — Structure of a Kind the Other Tests Could Not See

**Series note.** Forty-first report of the EYESPIRAL series. FR40 logged a coincidence
deficit as watch-grade and pre-registered a test for a later cycle. This cycle finds that
registration defective, replaces it with a statistic that can actually be run, and gets a
result. Instrument `eyedist.py`, selftest 5/5 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** FR40's pre-registration cannot be honoured, and saying so is
the first order of business: a pre-registration protects against choosing the analysis
after seeing the data, and buys **nothing** when the same data are re-analysed. The corpus
is fixed and the channel already uses every non-circular position, so re-running bin
(6, 15) reproduces z = −2.85 by construction. There is no held-out sample and there never
will be. The legitimate fix addresses the actual problem, which is multiplicity: a
**max-statistic test** computes the most extreme deficit over *all* contiguous distance
ranges and subjects every null draw to the same search. That can be run on the same data,
because multiplicity is what it corrects for rather than something it assumes away.
Observed **max-deficit z = −3.36 at range (4, 17)**; against a null that permutes v-values
*within* blocks — preserving block sizes, positions and each block's multiset of values,
hence the dependence that generates coincidences — **P = 0.0013**. The anomaly is
one-sided: the same statistic on the excess side gives +1.87 observed against a null mean
of +2.44, so the corpus is unremarkable there. **The plaintext avoids repeating a token at
short range.** That is a *correlation* effect, not an inventory-size effect, which is
exactly why FR36 (how the alphabet is spread) and FR39 (how large it is) could not see it
— and it is the first structural evidence about the plaintext to survive both.

---

## 1. D1 — the correction

FR40 wrote: "PRE-REGISTERED for a future cycle: distance bin (6,15), both channels pooled,
one-sided deficit, α = 0.01." That instruction cannot be carried out in any way that
means something. Pre-registration works by fixing the analysis before the data are seen;
here the data are fixed and already seen, so re-running the specified test returns the
number that motivated it. For the record, re-running gives 2/968, z = −2.85 — the same
figure, which is precisely the point.

This is worth stating plainly rather than quietly dropping, because the error is easy to
repeat: with a fixed corpus and a finite set of usable positions, "pre-register and retest"
is not available as a discipline. What is available is correcting for the search.

## 2. D2 — the distance profile

| d | pairs | hits | expected |
|---|---|---|---|
| 1–3 | 380 | 6 | 4.6 |
| **4** | 142 | **0** | 1.71 |
| 5–8 | 407 | 3 | 4.9 |
| **9–17** | **827** | **0** | **9.95** |
| 18–19 | 179 | 3 | 2.16 |
| 20–25 | 410 | 6 | 4.94 |

Nine consecutive distances with no coincidence at all, against ten expected.

## 3. D3–D4 — the max-statistic test

| quantity | value |
|---|---|
| observed max-deficit | **z = −3.36 at range (4, 17)** |
| null (within-block permutation, 1500 draws) | mean −2.03, 5th pct −2.64, min −3.41 |
| **P(null ≤ observed)** | **0.0013** |
| observed max-excess (sanity) | +1.87 at (2, 2) |
| null max-excess | mean +2.44, 95th pct +3.54 |

Two features of this design matter. The null is **biased strongly negative by
construction** — its mean is −2.03, because taking the most extreme of many ranges will
find something even in random data. That bias is exactly why a raw z is untrustworthy here
and why the null is required rather than optional; the selftest asserts it. And the
one-sidedness check is a genuine discriminator: a modelling error or a broken
reconstruction would be expected to perturb both tails, while local repeat-avoidance
predicts a deficit only. The corpus shows a deficit only.

## 4. D5 — what this establishes, and what it does not

**Establishes.** The plaintext, as the validated reconstruction recovers it, avoids
repeating a token at short range — roughly 4 to 17 positions — at p ≈ 0.001 after
correcting for the range search.

**Does not establish** what the plaintext is. Repeat avoidance is consistent with a varied
text over a large inventory, with a list of distinct items, with an enumeration, and with
other sources. It also remains conditional on repair A and on the reconstruction FR40
validated with its positive control.

**Bearing on A-vs-B.** FR36 excluded small contiguous alphabets, FR39 excluded small
scattered ones, and FR40 confirmed the instrument behind that null was working. The
running conclusion was that the fork was closing against the readable branch. This result
complicates that, in the direction the evidence actually points: branch B predicts
*structure*, and FR36 and FR39 found none **of the kind they were built to measure**. One
measures how the alphabet is spread, the other how large it is; neither measures how
repeats are *placed*. This does, and finds structure.

The honest summary is therefore narrower than FR39's: **the plaintext has a large token
inventory and non-random local placement.** Those are compatible — a text can draw from
many tokens and still avoid repeating them nearby — and the combination is more
informative than either alone.

## 5. Where the programme stands

- **384 relations over 56 glyphs**, components 25/11/7/3 plus five pairs, injectivity
  clean, 74.1% exposure, drift unpinned.
- **Plaintext:** effective alphabet > ~60 (FR36, FR39, validated FR40); **local repeat
  avoidance at distances 4–17** (this cycle).
- **A-vs-B: reopened**, not resolved. The readable branch is not excluded; it is
  constrained to a large-inventory, locally-varied source.
- **Acquisition remains the only lever on the drift.**

## 6. Horizon

(1) **Characterise the avoidance.** Is it a hard constraint (no repeat within a window) or
a soft one? A hard constraint would show as an exact minimum gap between equal tokens and
is directly checkable on the reconstructed stream. (2) **Re-price the doctrine question**
(FR40 §4) in light of this: a stream with a large inventory and enforced local variety is
a more interesting object than the flat token stream FR39 implied, and may be more
tractable to characterise directly. (3) Two external anchors in component 1 remain the
only route to the drift.

## 7. Reproduction

`eyedist.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
5-check gate — a planted deficit located, a flat profile producing none, the channel
totals reproduced, the null's negative bias asserted (the reason the null is required),
and the baseline guard. The full run reproduces D1–D5. Failures carry prefix
`XD-MBYG04K-URS3LF`.
