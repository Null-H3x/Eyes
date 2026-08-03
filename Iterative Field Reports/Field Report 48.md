# Field Report 48 — A Skeleton Cannot Corroborate What Built It

**Series note.** Forty-eighth report of the EYESPIRAL series. FR47 closed FR25's repair
fork by citing the passage's support, and noted that the passage now carries weight beyond
its own claim. This cycle audits that support and finds the figure it cited was measured
circularly. Instrument `eyecirc.py`, selftest 7/7 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** FR35 reported that the widened skeleton makes the FR32/33
passage "far better attested" — fourteen consecutive cells agreeing on w = 54, chance
83⁻¹³. **That measurement is circular and is withdrawn.** The widened skeleton was built by
adding the passage's own cells as constraints, so all fourteen agree by construction; the
instrument was asking constraints whether they hold. On the skeleton built *without* the
passage, exactly **five** of its cells are informative — offsets 1, 7, 10, 11, 12 — and all
five equal the independently established w = 54. That is FR32's original figure, 83⁻⁵ per
alignment and **3.6 × 10⁻⁶ across all 14,280 E4/W4 window pairs**, and it cannot be
improved: adding part of the passage never makes new cells testable, because the added
cells *recruit* glyphs rather than expose them. Leave-one-cell-out confirms the same five
and predicts all five correctly. **FR47's refutation of repair B survives the correction**,
and on a cleaner footing: repair A requires one three-pair skeleton match to be spurious
(~1 in 600); repair B requires a different three-pair match to be spurious **and** the
passage to be spurious as well, since B contradicts it. The likelihood ratio favours A by
about **2.8 × 10⁵**.

---

## 1. C1 — the circularity, exhibited

| skeleton | relations | informative passage cells | of which were the constraints |
|---|---|---|---|
| **without** the passage | 223 | 1, 7, 10, 11, 12 | **none** |
| **with** the passage | 384 | 0–3, 5–14 | **all fourteen** |

FR35 compared the second row against FR32's five and concluded the passage was better
attested. It was measuring its own inputs. The error is easy to make and easy to state:
**a skeleton cannot corroborate a passage it was built from.**

## 2. C2–C3 — the honest support

| cells added | relations | held-out testable | agreeing |
|---|---|---|---|
| none | 223 | 5 | 5 |
| offsets 0–3 | 249 | 4 | 4 |
| offsets 0–6 | 269 | 4 | 4 |
| offsets 0–9 | 350 | 3 | 3 |

Adding part of the passage never increases the testable count. The reason is structural:
the passage's other nine cells involve glyphs that are *not* in components until those very
cells are added, so they can recruit but never validate.

Leave-one-cell-out: **5 testable, 5 predicted correctly, no failures.**

| quantity | value |
|---|---|
| held-out cells agreeing on the established w | 5 |
| chance per alignment | 83⁻⁵ = 2.5 × 10⁻¹⁰ |
| E4/W4 window pairs | 14,280 |
| **expected by chance** | **3.6 × 10⁻⁶** |

Which is exactly where FR32 put it. The passage's support has not changed since cycle 32;
only the claim about it did.

## 3. C4 — re-pricing FR47

FR47 argued that passage + repair B is contradictory, and cited 83⁻¹³ to conclude B is
wrong. The correct figure is seven orders of magnitude weaker. A conclusion should not rest
on an inflated number even when it survives correction — so here is the corrected form,
which is also a better argument:

| reading | must assert | price |
|---|---|---|
| **repair A** | E1@68 is spurious | ~1.7 × 10⁻³ |
| **repair B** | E4@51 is spurious | ~1.7 × 10⁻³ |
| | **and** the passage is spurious | ~3.6 × 10⁻⁶ |

**Likelihood ratio favouring A: ≈ 2.8 × 10⁵.**

This is stronger than FR47's version because it compares what each repair must claim,
rather than appealing to a single number. Both repairs pay the same price for discarding a
three-pair skeleton match; B pays an additional 3.6 × 10⁻⁶ that A does not.

## 4. What this changes, and what it does not

**Changes.** FR35's claim that the widened skeleton makes the passage far better attested
is withdrawn. Any future report should quote **3.6 × 10⁻⁶** as the passage's support.

**Does not change.** The repair fork stays closed and repair A remains the unique maximum.
The model is unchanged: 384 relations over 56 glyphs, components 25/11/7/3 plus five pairs,
injectivity clean, 74.1% exposure.

**Methodological note.** This is the fourth circularity or pooling error the series has
caught in ten cycles — FR39's near-duplicate contamination, FR42's geometry-destroying
null, FR45's shared-prefix pooling, and now FR35's self-corroboration. They share a shape:
**a measurement that includes its own premises among its evidence.** The guard that catches
them is the same each time — ask what the test would return if the hypothesis were false,
and check that the answer differs.

## 5. Where the model stands

384 relations over 56 glyphs, components 25/11/7/3 plus five pairs, injectivity clean,
74.1% exposure. Drift unpinned, H4 the only surviving hypothesis. Repair A the unique
maximal reading, its rival refuted at a likelihood ratio of ~2.8 × 10⁵. Plaintext: large
inventory, no detected structure. Openings: stamped headers, untestable independently.

## 6. Horizon

(1) **Two external anchors in component 1** remain the only route to the drift.
(2) **The success criterion** is unchanged as the most consequential open item.
(3) **Every remaining support figure in the doctrine deserves the same audit this cycle
gave the passage** — specifically, whether it was measured on evidence that includes the
thing being measured. The passage was the obvious candidate because FR47 made it
load-bearing; it should not be assumed to be the only one.

## 7. Reproduction

`eyecirc.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
7-check gate — the pre-passage skeleton reproduced, exactly five informative cells without
the passage, all five giving the established w, the circular fourteen exhibited with all
fourteen identified as constraints, leave-one-cell-out predicting every testable cell, and
the baseline guard. The full run reproduces C1–C5. Failures carry prefix
`XD-MBYG04K-URS3LF`.
