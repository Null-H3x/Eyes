# Field Report 69 — "83 CONSECUTIVE VALUES" IS NOT "0 TO 82": THE OFFSET AUDIT

*Instrument: `eyeoffset` (built on `eyesep` / `eyeorder`). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — a phrase I read past

The wiki scour recorded that the orthodox reading *"uses exactly **83 consecutive
values** with no gaps from the 125 possible."* I quoted that line as corroboration of
the base-5 trigram reading and moved on.

**Consecutive is not the same as 0 to 82.** A run of 83 consecutive values inside
0–124 can begin anywhere in [0, 42]. If the community labelled the observed values by
sorted order — which is the natural thing to do — then

```
community label g  ,  true trigram value v = g + k  ,  k unknown in [0, 42]
```

Every digit-based analysis in this series used the digits of **g**, not of **v**.
FR58's frame stabiliser, FR59's separability exclusions, FR59's four-state MSB
prediction, and FR62's digit-derived orderings all silently assume **k = 0**.

That assumption has never been examined, and it is not implied by anything the corpus
shows: a shift changes the base-5 digit decomposition entirely while leaving the
label set contiguous, so contiguity cannot detect it.

---

## 1. FR59's separability exclusion is offset-robust

Re-running all four separability families at every offset:

```
43 offsets x 4 families = 172 tests
FITS: NONE
```

Digit-separable construction is excluded **at every possible offset**, not merely at
k = 0. FR59's conclusion strengthens rather than weakens: it now holds without the
assumption that made it conditional.

---

## 2. FR62's digit-derived orderings are offset-robust

Thirteen digit-derived generators (all six digit-position orderings, digit sum,
product, max, min, sorted ascending and descending, spread), recomputed from the
digits of `g + k` at every offset, against every affine pre-composition, both
directions:

```
7,609,108 candidates in 3 seconds
SURVIVORS: NONE
```

---

## 3. THE MSB PREDICTION CHANGES CHARACTER, AND IMPROVES

FR59 predicted the most significant visual feature shows **four** distinct states,
and offered it as a falsification test of the base-5 reading. Across offsets:

| MSB states | offsets | which |
|---:|---:|---|
| 4 | **36 of 43** | all except below |
| 5 | **7 of 43** | k = 18, 19, 20, 21, 22, 23, 24 |

**This is a better test than FR59 described, not a broken one.** The prediction is no
longer binary:

- Counting **four** states confirms the base-5 reading and leaves 36 offsets live.
- Counting **five** states does **not** falsify base-5. It **pins k to one of seven
  consecutive values**, 18 through 24.

So the measurement is informative either way, and in the less likely branch it is
*more* informative. FR59 framed a five-count as fatal to the reading; that was wrong,
and the correction converts a falsification test into a parameter estimate.

---

## 4. What this costs and what it buys

**Costs nothing in results.** Every digit-based exclusion in the series survives the
generalisation. No published finding is withdrawn.

**Costs a caveat.** FR58's stabiliser of 432 was computed for the set `{0..82}`.
Under an unknown offset the correct quantity is the stabiliser of `{k..k+82}`, which
differs by offset. The 432 figure should be read as *"conditional on k = 0"* until k
is determined. This does not affect the ordering sweeps, which were run against
labels and are covered by affine pre-composition, but it does affect any future claim
about how ambiguous the frame is.

**Buys a sharper external test.** §3 upgrades the glyph-inventory measurement from a
yes/no check to a parameter estimate, and it remains the cheapest open item in the
programme.

---

## 5. A note on how this was found

This did not come from measurement. It came from re-reading a sentence I had already
quoted approvingly and noticing that I had substituted a stronger claim for what it
said. "83 consecutive values from the 125 possible" was recorded in FR68 as
*confirming* the reading; it does confirm the reading, and it also leaves a free
parameter that the same sentence declines to specify.

Tenth-plus item in this series to be settled by inspection rather than by
instrumentation, and the second in three cycles to come from external text rather
than from the corpus.

---

## 6. Model status — unchanged

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity
clean; exposure 74.1%; 22,550 consistent alphabets; 14.46 bits; first anchor spent on
gauge; alphabet size proven in [56, 83]; separability and digit-orderings now
excluded at all 43 offsets.

**Cumulative sweep total: 92.1 million candidates, zero survivors.**

---

## 7. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Label offset k | implicitly 0, never stated | **UNKNOWN in [0, 42]**; contiguity cannot detect it |
| FR59 separability exclusion | conditional on k = 0 | **offset-robust**, 172 tests, zero fits |
| FR62 digit orderings | conditional on k = 0 | **offset-robust**, 7.6M candidates, zero survivors |
| FR58 stabiliser = 432 | stated absolutely | **conditional on k = 0** |
| FR59 MSB prediction | four states, else base-5 falsified | **four for 36 offsets, five for k in [18,24]**; a five-count estimates k rather than falsifying |

---

## 8. Horizon

1. **Count the MSB states on the glyph inventory.** Now strictly more valuable than
   when FR59 proposed it: four confirms the reading, five pins k to seven values.
   Still needs only the glyph set.
2. **The Cauldron Room's 30-bit key.** Carried from FR68, still unexamined, still the
   only evidence that keyed material exists in-game.
3. **Eye-level transcription.** Under the five-orientation reading, the first eye of
   every trigram must never take orientation `4 − (k mod 5)`-dependent values; with k
   unknown this becomes a joint test of segmentation and offset.
4. **Decide the success criterion** (FR66 §1). Unchanged, and still prior to
   everything else.
