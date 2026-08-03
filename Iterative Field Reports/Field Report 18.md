# Field Report 18 — The Ceiling Is Structural

**Series note.** Eighteenth report of the iterative series. FR17 closed by naming
reachability as the highest-value target: glyphs the constraint system cannot see are
glyphs no anchor can help. This cycle maps that boundary precisely, corrects FR17's
description of it, tests whether it can be moved, and finds it cannot. Instrument
`eyereach2.py`, selftest 6/6 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** FR17 stated that 32 glyphs "never appear inside any pair
span." That is wrong, and the truth is more interesting: **82 of the 83 glyphs occur
inside certified spans**; exactly one, glyph 27, falls outside every span. The real
boundary is finer. Rows are emitted only at pattern-**letter** cells, because FR7's
sound-rows repair masks dot cells as occurrence-variable — so **31 glyphs sit inside
certified material at dot cells and are invisible to the constraint system anyway,
holding 332 corpus positions, a full third of the corpus.** Testing whether that
ceiling is a calibration choice: sweeping the isomorph scan across L = 8…15 and
min-repeats 2…4 — settings whose own soundness checks out at z = 10 to 36 against
shuffled corpora — promotes **zero** glyphs to letter status at every single setting.
The cause is structural, and measurable: letter status requires a glyph to repeat at
short range, and while 49 of the 51 reachable glyphs have a repeat within fifteen
positions, **17 of the remaining 32 have none anywhere in the corpus.** The refined map
is therefore 51 reachable, 15 candidates (they do repeat closely, but their repeats do
not fall inside windows that form certified isomorphs), 17 structurally invisible, and
1 outside spans entirely — and it yields a concrete diagnosis for FR5's long-stalled
H1 hypothesis, which needs glyph 1: a dot-only glyph.

---

## 1. Correction first

**FR17's characterisation of the unreachable set was wrong.** I wrote that 32 glyphs
"never appear inside any pair span, so determining all 51 is not a full solve." The
count was right and the reason was not. Only glyph 27 — three occurrences — is truly
outside every certified span. The other 31 sit *inside* certified spans, at dot cells,
and are excluded by the sound-rows repair rather than by the corpus. That distinction
matters because it changes what could be done about it: an exclusion by the corpus is
permanent, an exclusion by a modelling choice might not be. This cycle tests exactly
that, and the answer turns out to be "permanent anyway" — but for a different and more
informative reason.

## 2. C1 — the taxonomy

| quantity | value |
|---|---|
| corpus positions | 1036 |
| positions inside a certified span | 385 (37.2%) |
| row-emitting cells (letter + dot-masked strict) | 159 |
| dot-only cells inside spans | 226 |
| **glyphs at row-emitting cells** | **51** |
| **glyphs only at dot cells** | **31** (332 occurrences, 32% of the corpus) |
| glyphs outside every span | 1 — glyph 27 |

The constraint system sees 159 of 1036 positions. The dot cells are not noise: they are
inside spans the atlas certifies, but FR6/FR7 established that dot interiors vary per
occurrence, so asserting equality there is exactly the over-assertion that produced the
atlas contradiction. Masking them was correct. The cost is now quantified: a third of
the corpus is placed beyond reach by that correctness.

## 3. C2 — the ceiling is not a calibration choice

Sweeping the isomorph scan and asking, at each setting, how many glyphs newly occupy a
letter cell:

| L | rep | pairs | null pairs | z | letter glyphs | **new** |
|---|---|---|---|---|---|---|
| 8 | 2 | 51 | 3.0 | 14.4 | 16 | **0** |
| 10 | 2 | 73 | 9.6 | 10.2 | 19 | **0** |
| 12 | 2 | 103 | 5.6 | 19.8 | 27 | **0** |
| 13 | 2 | 120 | 7.8 | 16.0 | 28 | **0** |
| 13 | 3 | 63 | 0.0 | ∞ | 23 | **0** |
| 15 | 2 | 169 | 5.4 | 36.3 | 41 | **0** |
| 15 | 3 | 82 | 0.0 | ∞ | 23 | **0** |

Every setting, including the most permissive, promotes nothing. The settings are not
themselves suspect — the shuffle nulls put them at z = 10 to 36 — so more pairs simply
means more instances of the same 51 glyphs. This also settles the standing
anchor-calibration item from FR9 in the negative direction for *this* purpose:
recalibrating the scan will not widen the constraint system's field of view.

## 4. C3 and C4 — why, and the refined map

Letter status has a prerequisite: two occurrences of the glyph must fall close enough
to sit inside one window. Under the progressive reading a repeated ciphertext glyph at
gap d requires the plaintext values to differ by exactly d — a 1-in-83 coincidence per
position pair — so short-range repeats are intrinsically scarce, and the corpus divides
sharply on them.

| population | mean close pairs (window 15) | with none |
|---|---|---|
| row-emitting glyphs (51) | 2.57 | 2 |
| the rest (32) | 1.00 | **17** |

The refined map:

- **51 reachable now.**
- **15 candidates** — {1, 2, 11, 18, 22, 28, 29, 43, 52, 61, 69, 75, 77, 80, 82} — do
  repeat at short range, but their repeats do not fall inside windows that form
  certified isomorphs. These are the only glyphs a new constraint source could plausibly
  recruit.
- **17 structurally invisible** — {0, 3, 8, 15, 24, 27, 31, 33, 35, 38, 51, 53, 56, 65,
  70, 76, 78} — never repeat within fifteen positions anywhere in 1036 glyphs. No
  isomorph-based method can ever touch them.
- **1 outside spans** — glyph 27, which is also in the invisible set.

Two consequences worth carrying forward. First, for FR17's leverage map: **an external
anchor placed on a non-reachable glyph yields only itself**, because it has no
constraints to propagate through. The anchor target list in FR17 §4 is therefore also a
statement about which anchors are worth the cost of obtaining. Second, a concrete
diagnosis for a hypothesis that has been stalled since FR5: **H1 (the boundary-token
relation q[1] − q[47] ≡ 4) needs glyph 1, and glyph 1 is dot-only.** FR8 read H1 as
"reachable, pending a bridge symbol"; the truer statement is that it is blocked by the
stem reading itself, and no amount of component-bridging will fix it.

## 5. What this means for the programme

The constraint system's field of view is 51 glyphs and 159 positions, and that is close
to a hard limit for isomorph-derived evidence. Progress past it needs a constraint
source that is *not* an isomorph — something that relates glyphs without requiring them
to repeat at short range. Candidates, in rough order of plausibility: the literal
openings (currently excluded under the FR16 reading, but they relate 24 consecutive
positions across three messages without needing any repeat); external anchors, which
supply values directly rather than relations; and any structural reading of the
indicator block at position 0, which is language-free and touches nine glyphs the body
evidence barely constrains.

That reframes the openings. FR16 concluded they are best read as a structural prelude
imposing no cipher constraint — but if they *are* plaintext under some reading, they
are also the single largest untapped source of constraints on precisely the glyphs the
atlas cannot see. The tension is worth stating plainly rather than resolving by
assumption.

## 6. Horizon

(1) **Check whether the openings would recruit the 15 candidates.** Their spans cover
positions 1–24 across six messages; if the dot-only and candidate glyphs are
concentrated there, the branch-(i) decision has a much larger cost than FR16 priced,
and that cost is measurable. (2) **The 15 candidates deserve a targeted search**: their
close repeats exist, so a constraint form other than same-pattern isomorphy might
capture them. (3) **Recompute FR17's anchor ranking restricted to reachable glyphs**,
since anchors on the other 32 are worth exactly one glyph each. (4) Standing: audit
#2⁻'s core at instance level.

## 7. Reproduction

`eyereach2.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs
the 6-check gate — letter/dot disjointness, dot cells inside spans, the three glyph
populations partitioning the alphabet (51 + 31 + 1 = 83), letter detection on a
constructed pair, null machinery, and the baseline guard. The full run reproduces C1's
taxonomy, C2's scan sweep with nulls, C3's repeat analysis and C4's refined map.
Failures carry prefix `XD-MBYG04K-URS3LF`.
