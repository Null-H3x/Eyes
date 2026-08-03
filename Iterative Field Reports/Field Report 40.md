# Field Report 40 — The Control FR39 Needed

**Series note.** Fortieth report of the EYESPIRAL series. FR39 reached a strong negative
conclusion about the plaintext and left one gap in the argument; this cycle closes it, and
follows up an anomaly two reports have now recorded without explaining. Instrument
`eyevalid.py`, selftest 5/5 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** FR39 measured the plaintext coincidence rate, found it flat,
and concluded the effective alphabet exceeds ~60. That argument had an alternative it did
not rule out: **if the model were wrong**, the reconstructed plaintext would be scrambled
and would look flat for reasons having nothing to do with the corpus. A null is only
informative if the instrument can detect the signal when it is there. The corpus supplies
the control, and FR39 had already isolated it: the **near-duplicate pairs share
plaintext**, which is exactly why FR39 excluded them. Run the channel *on* them and it
fires — **East 1 / West 1 at z = +5.53, East 4 / East 5 at z = +6.96**, with 85% and 90%
of those coincidences at shift zero — while a non-near-duplicate pair sits quiet at
z = −0.65. **The instrument detects shared plaintext where shared plaintext exists and is
silent where it does not**, so FR39's flat reading elsewhere is a statement about the
plaintext rather than an artefact of a broken reconstruction. Second, the anomaly: both
FR30 (z = −1.96) and FR39 (z = −0.56) found coincidence counts *below* the flat
expectation, and FR39's IoC-style estimate came out at 88.7 — above 83, which no genuine
83-symbol alphabet can produce. Binning by positional distance puts the deficit in the
**same bin, 6–15, in both channels independently**, pooling to **2 coincidences against
11.7 expected, z = −2.85**. That is suggestive and it is also exactly the shape of a
post-hoc finding, so it is logged **watch-grade with a pre-registered test** for a future
cycle rather than claimed.

---

## 1. V1 — the positive control

| pair | hits | pairs | flat | z | share at shift 0 |
|---|---|---|---|---|---|
| East 1 / West 1 | 20 | 519 | 6.3 | **+5.53** | 85% |
| East 4 / East 5 | 20 | 400 | 4.8 | **+6.96** | 90% |
| East 4 / West 4 (negative control) | 4 | 459 | 5.5 | −0.65 | — |

This is the check FR39 should have carried and did not. The channel is not merely quiet on
the corpus — it is **demonstrably capable of being loud**, and it is loud in exactly the
place where the corpus is independently known to repeat itself. The concentration at shift
zero confirms the mechanism: those are aligned shared passages, not diffuse token
frequency.

With that established, FR39's conclusion is properly supported rather than merely
consistent: **the plaintext effective alphabet exceeds roughly 60, however the tokens are
numbered.**

## 2. V2 — the deficit, by distance

| distance | within: pairs | hits | z | cross: pairs | hits | z |
|---|---|---|---|---|---|---|
| 1–5 | 353 | 6 | +0.85 | 270 | 1 | −1.26 |
| **6–15** | 532 | 1 | **−2.15** | 436 | 1 | **−1.87** |
| 16–30 | 576 | 5 | −0.74 | 491 | 8 | +0.86 |
| 31–60 | 810 | 4 | −1.85 | 773 | 13 | +1.22 |
| 61–200 | 962 | 16 | +1.30 | 1091 | 16 | +0.79 |

Pooled at 6–15: **2 coincidences / 968 pairs, flat 11.7, z = −2.85.**

## 3. V3 — why this is not a claim

For i.i.d. plaintext the coincidence rate cannot fall below 1/83 in expectation — that is
a property of the index of coincidence, not an empirical regularity. So a persistent
deficit requires anti-correlation of some kind: local avoidance of repeated tokens. Two
channels built on different pair populations showing their deficit in the same bin is the
kind of coincidence that deserves attention.

It is also precisely what a post-hoc artefact looks like. I chose the bin after seeing the
data, across five bins and two channels, which is ten opportunities; a −2.85 becomes
unremarkable under that correction. The honest treatment is to register it and test it
cleanly next time:

> **Pre-registered:** distance bin (6, 15), both channels pooled, one-sided deficit test,
> α = 0.01.

If it survives on that pre-registration it is a real property of the plaintext — local
avoidance of repeats — and would be **the first structural evidence for branch B that
survives FR36 and FR39**, because it is a correlation effect rather than an
inventory-size effect and neither of those tests could see it.

## 4. V4 — the doctrine question, stated for decision

FR39 established that the plaintext effective alphabet exceeds ~60 and this cycle
validates the instrument behind that. The consequence has not changed and should be put
plainly:

> Recovering C yields a **token stream, not a reading**. Two external anchors would
> determine 25 glyphs and a quarter of the corpus — as numbers.

Whether that constitutes solving the Eye Messages is a question about the project's
success criterion rather than about the corpus, and it is better settled before more
effort goes into acquisition than after. Three positions seem defensible: that recovering
the alphabet and offsets is itself the solution and the inner layer is a separate problem;
that the project should pivot to characterising the inner layer directly; or that the
watch-grade distance effect, if it survives pre-registration, reopens the possibility that
the stream is structured after all.

## 5. Where the programme stands

- **384 relations over 56 glyphs**, components 25/11/7/3 plus five pairs, injectivity
  clean, 74.1% exposure, drift unpinned.
- **A-vs-B resolved against the readable branch**, now with a validated instrument.
- **One live anomaly**, pre-registered.
- **Acquisition remains the only lever on the drift**, and its yield is now honestly
  priced: the alphabet, not a reading.

## 6. Horizon

(1) **Run the pre-registered distance test** on a clean footing — it is the only live
candidate for structure in the plaintext. (2) **Settle the success criterion** (§4); it
governs whether acquisition is worth pursuing. (3) Two external anchors in component 1
remain the only route to the drift, and H1's prediction of drift 31 becomes testable the
moment one arrives.

## 7. Reproduction

`eyevalid.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
5-check gate — the channel detecting known shared plaintext, staying quiet on a
non-near-duplicate pair, distance bins partitioning the pairs completely, the z statistic
calibrated on synthetic flat data, and the baseline guard. The full run reproduces V1–V4.
Failures carry prefix `XD-MBYG04K-URS3LF`.
