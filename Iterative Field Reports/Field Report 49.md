# Field Report 49 — Auditing the Rest, and What Holds the Model Up

**Series note.** Forty-ninth report of the EYESPIRAL series. FR48 withdrew one figure for
circularity and asked whether any others share the same shape. This cycle runs that audit
and adds a sensitivity map. Instrument `eyeaudit2.py`, selftest 7/7 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** The audit comes back clean: **FR35 was a localised error, not a
symptom of a systemic one.** The sharpest candidate was FR15's pattern-weight nulls — a
class pattern is the equality skeleton *shared* by its instances, so an instance that fits
poorly weakens the pattern, and pricing that instance against the weakened pattern would be
circular. **No instance weakens its class pattern**, across all thirteen classes, and the
detector is shown to fire on a planted misfit. The atlas is internally consistent: zero
instances violate their own class pattern. Every other figure uses evidence structurally
independent of what it supports — FR14's merge rests on raw ciphertext runs against an
empty cross-triplet null (0 of 27 pairs), FR27's embeddedness on the spans of *other*
classes, FR37 and FR38 on explicitly held-out data, FR40 on a positive control. The
constructive half is a **sensitivity map**: most atlas classes can be withdrawn with **no
loss at all**, because FR38 established the classes are mutually predictive. Two pieces
carry the model — the FR32/33 passage (−161 relations) and class #2 (−159) — and **the
strict tier is fully redundant**, costing nothing when removed.

---

## 1. Corrections first

**Two of my own selftests were vacuous and were replaced before publication.** One
asserted `len(w) >= 0`, which is true of any list; the other ended in `or True`. Both
would have passed regardless of the corpus. They are now real: the weakening detector is
verified to fire on a planted misfit instance, and the cross-triplet null is computed
properly (0 runs across all 27 pairs). Shipping a gate that cannot fail is the same error
this series has been auditing others for.

**A conclusion I drafted and the data contradicted.** I had written that the passage and
the strict tier are the load-bearing pieces. The strict tier costs **zero** relations when
withdrawn — it is entirely redundant with the classes. Corrected in §4.

## 2. A1–A2 — the atlas, and the pattern nulls

| check | result |
|---|---|
| instances violating their own class pattern | **0** |
| instances that *weaken* their class pattern | **0** |

The second is the one that mattered. If an instance shares fewer equalities than its
siblings, the class pattern is the intersection and is therefore shaped by that instance;
FR15's shuffle null would then be pricing a match against a pattern the instance helped
define. Across all thirteen classes, no instance does this — every instance satisfies the
full shared skeleton exactly. **FR15's nulls are not circular.**

## 3. A3 — the remaining figures

| figure | evidence | verdict |
|---|---|---|
| E4/E5 merge (FR14) | literal ciphertext runs; null = cross-triplet | independent |
| E3@101 coincidence (FR15) | shuffle null on an unweakened pattern | independent |
| E1@68 embeddedness (FR27) | spans of *other* classes | independent |
| leave-one-out (FR37) | skeleton minus the pair | held out |
| class-level CV (FR38) | skeleton minus the whole class | held out |
| plaintext channel (FR40) | positive control on near-duplicates | validated |
| **passage support (FR35)** | **skeleton built from the passage** | **withdrawn (FR48)** |

FR14's null deserves a note: the twenty-seven cross-triplet pairs share no keystream, so
they are independent of the E4/E5 claim by construction, and **not one of them carries a
literal body run of length ≥ 2** while E1/W1 carries two and E4/E5 carries three.

## 4. A4 — the sensitivity map

| withdrawn | relations | glyphs | exposure | lost |
|---|---|---|---|---|
| (nothing — current model) | 384 | 56 | 74.1% | — |
| **the FR32/33 passage** | 223 | 47 | 64.6% | **−161** |
| **class #2** | 225 | 55 | 72.9% | **−159** |
| class #C1 | 338 | 56 | 74.1% | −46 |
| class #2⁻ | 360 | 55 | 73.1% | −24 |
| class #2+ | 382 | 55 | 73.1% | −2 |
| class #4 | 383 | 54 | 71.8% | −1 |
| #1, #3, #3+, #C0, #F, #M, #M⁻, #S | 384 | 56 | 74.1% | **0** |
| **the strict tier** | 384 | 56 | 74.1% | **0** |

Eight of thirteen classes cost nothing, which is FR38's mutual-predictiveness result seen
from the other side: what one class asserts, the others already imply. The strict tier —
eighteen pairs that have been carried since the beginning — turns out to be entirely
redundant, which is worth recording because it is easy to assume those pairs are doing work
they are not.

## 5. What this means

The model rests on two pieces of evidence: the FR32/33 passage, priced at 3.6 × 10⁻⁶ (FR48)
and load-bearing for 161 relations, and class #2, load-bearing for 159. Everything else is
either redundant or marginal. That is a concentrated dependency, and it is now explicit
rather than implicit.

It also sharpens what a future correction would cost. FR48 noted that the passage
discriminates the repairs, so doubt about it reopens FR25's fork; this cycle adds that the
same doubt would cost 161 relations and 9.5 points of exposure. **The passage is the single
most consequential piece of evidence in the model**, and it rests on five held-out cells.

## 6. Where the model stands

384 relations over 56 glyphs, components 25/11/7/3 plus five pairs, injectivity clean,
74.1% exposure. Repair A the unique maximal reading (likelihood ratio ~2.8 × 10⁵ over B).
Drift unpinned, H4 the only surviving hypothesis. Plaintext: large inventory, no detected
structure. Openings: stamped headers, untestable independently. No further circularity in
the support figures.

## 7. Horizon

(1) **Two external anchors in component 1** remain the only route to the drift.
(2) **The success criterion** is unchanged as the most consequential open item.
(3) **Class #2 now deserves the scrutiny the passage received** — it carries 159 relations,
nearly as many as the passage, and has never been audited individually the way #M⁻ and #2⁻
were in FR15.

## 8. Reproduction

`eyeaudit2.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
7-check gate — atlas integrity, no weakening instances, the weakening detector firing on a
planted misfit, the cross-triplet null computed properly, the model reproducing, the
passage's withdrawal costing relations, and the baseline guard. The full run reproduces
A1–A5. Failures carry prefix `XD-MBYG04K-URS3LF`.
