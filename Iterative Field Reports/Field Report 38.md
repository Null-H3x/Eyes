# Field Report 38 — Thirteen Structures, One System

**Series note.** Thirty-eighth report of the EYESPIRAL series. FR37 introduced held-out
testing and noted its own version was the generous one. This cycle runs the strict version
and closes the last standing structural item from FR15. Instrument `eyeclass.py`, selftest
5/5 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** FR37's leave-one-pair-out test was real but generous: removing
one pair of class #M leaves fourteen siblings to carry the prediction. Removing the
**entire class** does not — nothing from it survives, so any prediction must come from
*other* classes through shared glyphs. Run that way, **41 of 41 testable held-out pairs
are predicted, across all thirteen classes, with the whole class removed each time.**
Chance is 1.5%, so if the classes were thirteen independent facts the expected number
predicted would be **0.6**. A planted spurious class — random windows with a matching
length profile — scores **0 of 23**. The corpus's repeated structures are therefore not a
collection of separate observations but a single coherent system, and that coherence is
now measured out-of-sample. Separately, **FR15's last unaudited item closes**. FR37 showed
cross-validation cannot evaluate #2⁻'s bridge because every one of its cells is a dot; a
different question can be asked instead — are the rows it emits *implied* by the rest of
the pool? All six classify **redundant**. The bridge asserts nothing the other classes do
not independently give, so it is **corroborated rather than untested** — the opposite
verdict to #M⁻'s bridge, which FR15 retired at coincidence grade. The two cross-triplet
bridges are now cleanly separated on evidence.

---

## 1. Why FR37's test needed strengthening

Holding out one pair at a time asks whether the pool minus one element still implies that
element. For a class with fifteen pairs, the fourteen survivors pin nearly everything the
removed one asserts, so the test is close to asking whether a class is internally
consistent — which FR7 already established. The stronger question is whether the classes
predict *each other*.

## 2. K1 — the class-level test

| class | pairs | testable | predicted | rate |
|---|---|---|---|---|
| #1 | 6 | 6 | 6 | 100% |
| #2 | 3 | 3 | 3 | 100% |
| #2+ | 1 | 1 | 1 | 100% |
| #2⁻ | 6 | 3 | 3 | 100% |
| #3 | 3 | 3 | 3 | 100% |
| #3+ | 1 | 1 | 1 | 100% |
| #4 | 3 | 1 | 1 | 100% |
| #C0 | 1 | 1 | 1 | 100% |
| #C1 | 1 | 1 | 1 | 100% |
| #F | 3 | 2 | 2 | 100% |
| #M | 15 | 9 | 9 | 100% |
| #M⁻ | 21 | 9 | 9 | 100% |
| #S | 1 | 1 | 1 | 100% |
| **total** | **65** | **41** | **41** | **100%** |

The testable counts drop when a class is removed — #M falls from 15 pairs to 9 testable —
because removing it also removes glyphs from components. That is the mechanism working
correctly: the surviving cells are the ones other classes can still speak to, and those
are exactly the out-of-sample ones.

## 3. K2 — calibration, in both directions

| measure | result |
|---|---|
| chance agreement, random window pairs | 24 / 1577 = **1.5%** |
| expected predictions if classes were independent | **0.6** |
| observed | **41** |
| **spurious class** (planted, matched length profile) | **0 / 23** |

The negative control is the part that makes the positive result mean something. A test
that predicts everything would be worthless; this one predicts every real class and none
of a fabricated one.

## 4. K4 — #2⁻'s bridge, closed positively

FR15 audited the two cross-triplet bridges and could price only one: #M⁻'s bridge
(East 3 @ 101) came out at p ≈ 0.10 and was retired, and its removal is half of repair A.
#2⁻'s bridge (East 3 @ 64 × East 4 @ 73) has been open ever since. FR37 reached it and
stopped, correctly: all three of its testable cells are dots, which disagree by
construction, so their disagreement is not evidence and masking them leaves nothing.

A different question is available. The bridge emits six sound rows. Are they implied by
the rest of the pool?

| verdicts on its six rows | result |
|---|---|
| redundant | **6** |
| pivot | 0 |
| contradiction | 0 |

Every constraint the bridge asserts is independently derivable from the other classes,
which is why removing it changes nothing — 384 relations and 56 glyphs either way. **The
bridge is corroborated**, and the two cross-triplet bridges now have opposite verdicts on
comparable evidence: one retired at coincidence grade, one implied by the rest of the
corpus.

## 5. What this changes

The model's content is unchanged: 384 relations over 56 glyphs, components 25/11/7/3 plus
five pairs, injectivity clean, 74.1% exposure, drift unpinned. What changes is the
standing of the atlas itself. Before this cycle the thirteen classes were thirteen
certified observations that happened to cohere; now each is derivable from the others,
measured out-of-sample, with a working negative control.

That also bears on the outstanding debt. Repair A asserts that E1@68 — a three-pair
skeleton match — is spurious. The system that assumption underwrites now passes two
independent held-out tests it could have failed. That is not proof, but the alternative
must explain why a wrong repair produces a model whose every class predicts every other.

**Ledger status:** with #2⁻ closed, there are no unexecuted internal structural items
left. Every remaining route needs external input.

## 6. Horizon

(1) **The scattered-alphabet variant** of branch B is the one substantive open question
that does not require anchors, and FR36 showed it needs roughly double the current
component coverage — which FR31, FR34 and FR35 established cannot come from inside the
corpus. (2) **Acquisition remains the only lever**: two external anchors in component 1
fix rotation and drift together and determine 25 glyphs; nine anchors leave 44 enumerable
completions (FR27). (3) On an anchor's arrival, H1 becomes a genuine test immediately —
it predicts drift 31.

## 7. Reproduction

`eyeclass.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
5-check gate — class removal verified total, a real class predicted with the whole class
removed, the **spurious-class negative control** failing to be predicted, the #2⁻ bridge's
rows confirmed redundant, and the baseline guard. The full run reproduces K1–K4. Failures
carry prefix `XD-MBYG04K-URS3LF`.
