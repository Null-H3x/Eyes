# Field Report 14 — The Contradiction Is Body-Internal

**Series note.** Fourteenth report of the iterative series. FR11, FR12 and FR13 each
nominated the same top item — test branch (i) of the trilemma, the proposal that the
literal openings are not shared plaintext — and it kept slipping because the test as
specified does not exist. This cycle finds the test that does, and it eliminates the
branch. Instrument `eyerun.py`, selftest 5/5 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** Branch (i) resolves nothing, because **the contradiction
does not need the openings at all.** Sharpening FR11's mechanism from aggregate
agreement rates to *runs* of consecutive literal agreement makes the evidence
enormously stronger: cross-triplet pairs, which share neither keystream nor offset,
produce **zero** body runs of length ≥ 2 across all 27 of them, while East 4 / East 5
produce **three separate runs of length 3** (individual chance ≈ 2.4 × 10⁻⁶) and
East 1 / West 1 produce a run of **length 13** (chance ≈ 5 × 10⁻²⁵). Since the shared
keystream cancels exactly in a literal comparison, a run is possible only when the two
messages share an offset. E1/W1 sharing an offset is permitted by FR9's matrix and its
merge stays satisfiable at all 82 drifts — the positive control. **E4/E5 sharing an
offset is forbidden: the merge is unsatisfiable at every one of the 82 non-degenerate
drifts, with no opening pair anywhere in the constraint pool.** So the opening/body
contradiction of FR9–FR13 is body-internal, and discarding the openings as plaintext
leaves it untouched. The two surviving branches then localise sharply: removing
*either* cross-triplet class **#2⁻ or #M⁻ — alone —** restores a live system, and the
admissible key-reset positions for T3 turn out to be exactly the gaps in the
proven-arithmetic map FR13 derived independently.

---

## 1. Corrections and negatives first

**The test I kept nominating was ill-posed, and I should have caught it three reports
ago.** "Extend the agreement statistic into the opening spans" cannot work: within a
triplet the openings agree at 100% *by construction* — that identity is the premise
under examination, not a measurement of it. Three cycles carried that item forward on
its horizon list without anyone noticing it was empty. The repair was to look for the
comparison that is actually free of the premise, which turned out to be in the body,
not the openings.

**FR11's statistic was weaker than the data allows.** Aggregate agreement gave E4/E5
at ×9.2, p = 3.5 × 10⁻⁸. The same evidence expressed as runs is ~2.4 × 10⁻⁶ *per run*
with three of them and an empirical null of exactly zero. Nothing was wrong with FR11;
it simply left power on the table by summing over positions instead of using their
contiguity.

**Degeneracy convention, stated once.** "Excluded" throughout means excluded at every
non-degenerate drift. With drift left free these systems remain formally satisfiable by
flattening the keystream, which is monoalphabetic and FG1-excluded — the same pattern
this series has now recorded six times. Both readings are printed by the instrument.

## 2. C1 — runs, and why they are the right statistic

For two messages of one triplet the keystream cancels exactly in a literal comparison
(FR11): c₁[t] = c₂[t] ⟺ p₁[t] − p₂[t] = off₂ − off₁, under any keystream, any drift,
any alphabet. So a *run* of consecutive agreements costs base^L under distinct offsets,
where base is measured directly from cross-triplet pairs.

| pair | FR9 verdict | body runs (t ≥ 25) | chance |
|---|---|---|---|
| East 1 / West 1 | permitted | @29 L=4; **@37 L=13** | 3 × 10⁻⁸; **5 × 10⁻²⁵** |
| East 4 / East 5 | **forbidden** | **@25, @29, @38, each L=3** | 2.4 × 10⁻⁶ each |
| all 27 cross-triplet pairs | — | **none** | empirical null |
| every other within-triplet pair | — | none | — |

The empirical null is the point: runs of length ≥ 2 do not occur between messages that
share no offset, anywhere in this corpus. The selftest reproduces the mechanism in both
directions — a planted shared phrase surfaces as a literal run when offsets are equal,
and vanishes completely when they are not.

## 3. C2 — the contradiction needs no openings

| merge imposed | satisfiable at non-degenerate drifts | run evidence |
|---|---|---|
| East 4 / East 5 | **0 / 82** | three L=3 runs |
| West 4 / East 5 | 0 / 82 | none |
| East 1 / West 1 | 82 / 82 | L=13 and L=4 runs |
| none (control) | 82 / 82 | — |

E1/W1 is the control and behaves exactly as it must: overwhelming run evidence for a
shared offset, and a constraint system that happily accommodates it. E4/E5 has run
evidence of the same kind and the atlas cannot accommodate it at any drift — **using
only atlas and strict pairs, with no opening data in the pool.**

**Therefore branch (i) is eliminated as a resolution.** Even if the literal openings
are a structural prelude carrying no plaintext, the body alone still forces an offset
equality the certified classes cannot carry. The contradiction FR9 discovered at the
openings was never really about the openings.

## 4. C3 and C4 — pricing what remains

**Branch (ii)** sharpens dramatically. Removing **either #2⁻ or #M⁻ on its own** turns
the body-internal system from degenerate to live. Both are the cross-triplet bridge
classes — the same two FR3 used to derive drift equality across triplets, and the same
ones that appeared in FR10's minimal cores. That is a far cheaper version of branch (ii)
than FR10's estimate of three or four classes: one class, and specifically one whose
same-plaintext status is the most questionable in the atlas, since it asserts a passage
recurring across *different* triplets. It is also self-consistent — drop either bridge
and FR3's drift equality goes with it, which is precisely the assumption the
contradiction needs in order to bite.

**Branch (iii′)** survives with a striking coherence check. Sweeping a single T3 key
reset, the admissible positions are {36, 66, 67, 68, 69, 102, 103}. FR13 proved
independently — model-free, from Δ=1 isomorph pairs — that K_T3 is arithmetic on
[35, 66) and [68, 98). Of the admissible break positions, 36 and 69 lie strictly inside
those ranges and so would need the two affine pieces to join continuously (not a real
reset). **The clean reset positions are exactly {66, 67, 68} — the gap between the two
proven-arithmetic ranges — and {102, 103}, past the end of coverage.** Two
independently-derived constructions agree on where the keystream is allowed to break.

## 5. Where the trilemma stands

- **(i) openings not shared plaintext — ELIMINATED** as a resolution (§3). The
  openings may still not be plaintext; that is now simply irrelevant to the
  contradiction.
- **(ii) some atlas class not same-plaintext — LIVE and cheap.** One cross-triplet
  bridge class (#2⁻ or #M⁻) suffices. Cost: FR3's drift-equality deduction and the
  cross-triplet depth stack.
- **(iii′) non-linear keystream — LIVE and localised.** A single T3 reset at 66–68 or
  102–103. Cost: FR13's health measure showed such resets flatten most segment slopes.

The two surviving branches are no longer symmetric in cost, and they make different
predictions about the same small set of objects — the cross-triplet bridges.

## 6. Horizon

(1) **Discriminate (ii) from (iii′) on the bridges.** Under (ii) the bridge classes are
pattern coincidences; under (iii′) they are real and the keystream breaks. FR10's
shuffle null said long isomorphs never arise by chance, but it did not test the
cross-triplet ones *specifically* — a targeted null on #2⁻ and #M⁻ alone is the obvious
measurement and it is cheap. (2) **The T3 gap at 66–68** now has two independent
reasons to be interesting; a focused look at what happens there in all three T3
messages is warranted. (3) Re-price FR3's drift-equality deduction, which rests
entirely on the two classes branch (ii) would discard. (4) Standing: FR8's
bridge-symbol search, anchor calibration at rep = 4.

## 7. Reproduction

`eyerun.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
5-check gate — the run mechanism in both directions on plants (shared offsets surface a
planted phrase; distinct offsets erase it), run-finder exactness, the empirical
cross-triplet null, and the E1/W1 positive control. The full run reproduces the
baseline guard, C1's run census with chance pricing, C2's merge tests across all drifts,
C3's class localisation and C4's break/arithmetic coherence. Failures carry prefix
`XD-MBYG04K-URS3LF`. The run census is checkable from the corpus with a two-line loop.
