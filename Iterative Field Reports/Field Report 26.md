# Field Report 26 — The Skeleton That Survives the Rails

**Series note.** Twenty-sixth report of the EYESPIRAL series. FR25 found two
two-instance repairs of the constraint pool that determine alphabet relations without
asserting a false equality. This cycle runs them against the rails the series has
already established — because a repair that fixes injectivity while reopening an old
contradiction is not a repair — and then extracts what the surviving configuration
actually says. Instrument `eyeskel.py`, selftest 7/7 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** Both repairs pass the rails, and two of the three improve.
The gauge ladder is unchanged — one and three gauges remain unsatisfiable at every
non-degenerate drift, so FR9's theorem is not disturbed. But **FR14's body-internal
contradiction is resolved**: the E4/E5 offset equality that literal body runs *force*
(three runs of length 3 at chance 2.4 × 10⁻⁶ each, against an empirical null of zero
such runs among all 27 cross-triplet pairs) goes from unsatisfiable at 0/82 drifts to
satisfiable at **82/82**. So does FR10's T1-opening contradiction. Only the T3 opening
still contradicts, and no single class or instance removal clears it. With the merge
admitted — it is evidence-forced, not assumed — **repair A determines 223
pair-differences with zero injectivity violations**, in components of 19, 7, 7, 3 and
smaller. That is the first configuration in twenty-six cycles that determines a
substantial relational inventory and survives every check. It also **corrects FR17**,
which concluded offset information was orthogonal to determination: FR17 measured with
`certified_domain`, which FR23 later showed unreliable, and measured per pair the merge
takes determination from 28 to 223. The caveat is sharp and is stated as a headline: the
pair *set* is drift-invariant — which glyphs are linked, and the whole component
structure — but **not one of the 223 values survives a change of drift**. The shape is
structural; the content is conditional. The route out is that a pair-difference varies
**bijectively** with the drift, so two external anchors inside one component pin the
drift *and* determine the component.

---

## 1. The rails

| rail | full pool | repair A (−E3@101 −E1@68) | repair B (−E3@101 −E4@51) |
|---|---|---|---|
| gauge ladder, 1 gauge | 0/82 | 0/82 | 0/82 |
| gauge ladder, 3 gauges | 0/82 | 0/82 | 0/82 |
| gauge ladder, 9 gauges | 82/82 | 82/82 | 82/82 |
| pool alone | 82 | 82 | 82 |
| + T1 openings | **0** | **82** | **82** |
| + T3 openings | 0 | 0 | 0 |
| E4/E5 merge (run-forced) | **0/82** | **82/82** | **82/82** |

No regression anywhere, and two standing contradictions resolved. The E4/E5 line is the
important one: that merge is not a modelling choice but a requirement imposed by
evidence outside the constraint machinery entirely (FR11's cancellation identity, FR14's
run census). The full pool cannot accommodate it at any drift; both repairs can at every
drift.

The T3 opening remains contradictory, and neither a single class nor a single instance
removal clears it. Whatever that is, it is not the same defect.

## 2. The skeleton

Repair A with the E4/E5 merge, at drift 1: **223 determined pair-differences, zero
injectivity violations.**

| component | glyphs | corpus positions | members |
|---|---|---|---|
| 1 | **19** | 259 (25.0%) | 5, 6, 7, 10, 17, 20, 30, 34, 41, 45, 47, 48, 50, 57, 62, 64, 68, 71, 81 |
| 2 | 7 | 103 (9.9%) | 13, 19, 23, 44, 46, 49, 72 |
| 3 | 7 | 104 (10.0%) | 16, 21, 26, 40, 42, 67, 73 |
| 4 | 3 | 41 (4.0%) | 9, 63, 79 |

Within every component all pairwise differences are known and all offsets are distinct.
Component 2 is recognisably FR7's sound pin set minus the collided pair, and **glyph 4
has separated from 46** — the false equality that FR21 caught and FR25 traced is
genuinely gone rather than hidden.

Repair B gives the same shape with slightly different content: 203 determined
differences, largest component 17.

**The correction to FR17.** FR17 imposed the run-forced merges, saw certification stay
at ten symbols, and concluded across three cycles that offset information is orthogonal
to determination. It is not. The measurement was `certified_domain`, which FR23 showed
over-reports and under-tests when free parameters exist. Measured per pair, on a pool
that can actually accept the merge, E4/E5 takes determination from 28 to 223 — a factor
of eight. Offsets were never orthogonal; the pool could not accept the constraint, and
the measure could not see the difference.

## 3. The caveat, stated plainly

| drift | same pair set as drift 1 | values agreeing |
|---|---|---|
| 2, 3, 7, 17, 41, 82 | yes | **0 / 223** |

Which glyphs are relationally linked, and the entire component structure, is
drift-invariant — a genuine structural fact about the corpus. What the differences *are*
is entirely conditional on the drift, which eyedrift certifies as unidentifiable. Every
number in §2's offset tables is a drift-1 reading, not a corpus fact, and this report
does not claim otherwise.

## 4. The route that opens

The caveat contains its own resolution. A pair-difference in component 1 takes **82
distinct values over the 82 non-degenerate drifts** — the map is bijective. So one known
difference pins the drift uniquely.

That gives the R6 programme a concrete and much cheaper target than anything the series
has had:

- **Two external anchors inside component 1** — any two of its nineteen glyphs — fix the
  global rotation and pin the drift, thereby determining all nineteen and exposing **259
  corpus positions, 25%**.
- With the drift then fixed, every other component needs **one** anchor each.
- **Ten anchors total** determine 47 glyphs and 669 positions — **64.6%** of the corpus.

Compare FR17's estimate, which was computed against the unrepaired global-drift pool and
therefore inherited its falsehood: eight anchors for 51 glyphs. The corrected figure is
close in magnitude but rests on a configuration that is no longer known to be false, and
it identifies *which* anchors matter — the first two must land in the same component.

## 5. What is and is not established

**Established.** Both repairs survive the gauge ladder without regression and resolve two
standing contradictions. Under repair A the corpus determines 223 relations with no
injectivity violation, in a component structure that is drift-invariant. The E4/E5 merge
is forced by evidence independent of all constraint machinery.

**Not established.** That either repair is *correct*. FR25 priced them: E3@101 is cheap
to discard, but the second removal — E1@68 or E4@51 — asserts that a three-pair skeleton
match is coincidence, roughly a one-in-six-hundred claim. The skeleton is the best
available reading of the corpus *conditional on one such instance being spurious*, and
that condition is the outstanding debt.

**Still open.** The T3 opening contradiction, which neither repair touches and which no
single removal clears.

## 6. Horizon

(1) **Discriminate repair A from repair B.** They differ in yield (223 versus 203) and in
which glyphs land where; a crib or anchor that falls in a component under one but not the
other would separate them empirically. (2) **The T3 opening** is now the only surviving
contradiction and deserves the treatment FR25 gave the equalities: minimal cores, then
pricing. (3) **Feed the skeleton to the crib machinery** — 223 exact relations is a far
stronger pre-filter than the five equations FR5 offered, and unlike those it is not built
on rows the series has since retracted. (4) Standing: #2⁻'s instance-level audit, the 15
candidate glyphs.

## 7. Reproduction

`eyeskel.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
7-check gate — FR9's gauge theorem and FR14's body-internal contradiction reproduced on
the full pool before any new claim, the repair resolving the latter, the determination
and injectivity counts, the component structure, the drift-invariance asymmetry asserted
rather than assumed, and the baseline guard. The full run reproduces R1–R3, the skeleton,
the drift table and the anchor arithmetic. Failures carry prefix `XD-MBYG04K-URS3LF`.
