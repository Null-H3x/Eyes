# Field Report 37 — The Test the Series Never Ran

**Series note.** Thirty-seventh report of the EYESPIRAL series. FR36 left only items
blocked by coverage or by housekeeping, which made this the right moment to challenge
something the series has never examined: every result to date has been checked against the
evidence that produced it. Instrument `eyeloo.py`, selftest 6/6 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** Thirty-six cycles of consistency rails, injectivity checks,
minimal cores and shuffle nulls have all asked whether the construction is *internally
coherent*. None asked the question a model should be made to answer: does it predict
evidence it has not seen? Leave-one-out cross-validation does. For each certified pair,
the entire skeleton is rebuilt **without** it, and that pair's own cells are then asked to
agree on a single w = base_diff/drift — the pair never contributing to the model that
predicts it. **Every one of 59 testable held-out pairs is correctly predicted, against a
chance rate of 1.2–1.8% measured on random window pairs.** If the construction were
absorbing evidence rather than capturing structure, the expected number predicted would be
about 1. And the test does something second, unplanned but arguably more valuable: run
without dot masking it scores 44/62, and **every one of the 18 failures involves a dot
cell** — so masking moves the score from 71% to 100%. That is an independent confirmation
of the variable-interior doctrine FR6 proposed, FR7 implemented and FR19 verified, arrived
at from a direction that had nothing to do with any of them. The one negative: #2⁻'s
bridge, FR15's last unaudited item, has **no testable cell** once dots are masked, so
cross-validation cannot evaluate it — the item is not closed, it is shown to be
unreachable by this route.

---

## 1. Why this was the right challenge

The series has been rigorous about internal coherence and, until now, silent about
out-of-sample prediction. Those are different virtues. A construction can be perfectly
self-consistent and still be an elaborate restatement of its inputs — which is exactly the
failure mode FR23 caught when a configuration passed injectivity by determining nothing,
and FR35 caught when injectivity was mistaken for evidence. The held-out test is immune to
that class of error, because the pair being predicted contributed nothing to the
prediction.

## 2. L1 — the result

| condition | predicted | rate | failures |
|---|---|---|---|
| dot masking **off** | 44 / 62 | 71.0% | 18 |
| dot masking **on** | **59 / 59** | **100.0%** | **0** |

Chance rates, measured on random window pairs drawn with the same length distribution:
**0.8%** unmasked, **1.2%** masked.

Under the hypothesis that the skeleton absorbs rather than captures, the expected number
of held-out pairs predicted is 59 × 0.012 ≈ 0.7. Fifty-nine were.

## 3. L2 — the dot comparison, which is a second result

The 18 failures without masking are not scattered: they are the long dotted classes — the
#1/#C0/#C1 family at W1/E2, and the #2/#S regions in T3 — and every one of them involves a
cell the atlas marks as a dot.

This matters because dot masking is not a tuning knob here. FR6 proposed variable interior
to explain the atlas contradiction, FR7 built the sound-rows repair around it, and FR19
verified that all 153 atlas dot offsets genuinely vary. If that doctrine were wrong,
masking would change little. It moves the score from 71% to 100%, and it does so on
held-out data. **Three independent lines now support the variable-interior reading**, the
third arrived at without looking for it.

## 4. L4 — #2⁻'s bridge, honestly not closed

FR15 audited #M⁻'s bridge and found it coincidence-grade; #2⁻'s bridge (East 3 @ 64 ×
East 4 @ 73) has been the last unaudited structural item since. Cross-validation reaches
it and then stops:

| condition | testable cells | w values |
|---|---|---|
| dots unmasked | 3 | 40, 50, 64 — disagreeing |
| dots masked | **0** | — |

All three of its cells are dot cells, and dot cells disagree by construction. So the
disagreement is not evidence against the bridge, and with them masked there is nothing
left to test. **The item is not closed; it is shown to be unreachable by this method.**
That is a smaller claim than a verdict, and it is the one the evidence supports.

## 5. What this changes

Nothing about the model's content — 384 relations over 56 glyphs, components 25/11/7/3
plus five pairs, injectivity clean, 74.1% exposure, drift unpinned. What changes is its
standing. The skeleton is no longer only a self-consistent construction; it is one that
predicts evidence withheld from it, at a rate that chance does not approach. That is the
first result in the series that would survive the objection "you built the model from
these pairs, so of course it agrees with them."

It also raises the cost of the outstanding debt. Repair A remains a hypothesis — that a
three-pair skeleton match at E1@68 is spurious — and the skeleton that hypothesis
underwrites now passes a test it could easily have failed. That does not prove repair A,
but it does mean the alternative has to explain why a wrong repair yields a model with
perfect out-of-sample prediction.

## 6. Horizon

(1) **Extend the held-out test to the atlas classes themselves** — hold out a whole class
rather than one pair, which is a stronger version of the same question and would test
whether classes are mutually predictive. (2) **The scattered-alphabet variant** of branch
B remains untouched and blocked by coverage (FR36). (3) The acquisition target is
unchanged: two external anchors inside component 1. (4) #2⁻'s bridge needs a method that
does not route through its dot cells, or it stays open indefinitely.

## 7. Reproduction

`eyeloo.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
6-check gate — the skeleton reproduced, the delta map at 56 glyphs, the hold-out machinery
verified to remove the pair, the chance rate bounded, dot masking shown to be
consequential rather than cosmetic, and the baseline guard. The full run reproduces L1–L4.
Failures carry prefix `XD-MBYG04K-URS3LF`.
