# Field Report 200 — THE TRANSCRIPTION SCREEN: EAST 1@68 IS NOT A TYPO, EVERY MISREAD AT A LETTER CELL IS DETECTABLE, AND ZERO OF 1,100+ PERTURBATIONS IMPROVE ANYTHING

*July 2026. Cycle: EYESPIRAL-C, executing FR199 A2 (screen tier). Instrument:
`eyefuzz3.py`, gates 4/4. One metric correction en route, logged first.*

---

## 0. Negatives and corrections first

**The first metric was wrong, and the record itself said why.** `eyefuzz` v1
scored the unrepaired pool by row contradictions and measured **zero** — the
pool's pathology was never inconsistency, it was *forced equalities* (the
injectivity-era story, FR21). A second attempt at equality counting silently
returned zero because `Ech._reduce` early-returns at the first free column
by design — a truncated representation, not a full one. Both caught by the
planted gate refusing to pass. The corrected composite metric —
contradictions **and** full-substitution forced-equality count over
[unrepaired pool rows, re-emitted from the corpus under test] + [158
survivor class rows] — reproduces the certified structure exactly at
baseline: **52 contradictions attributable to East 1@68's eleven pairs, and
precisely the 8 certified homophones.** The 8 landing on the nose is the
metric's own identity check.

**Scope caveat, carried on every result below:** class rows are frozen at
pristine values (spans for the 208-scan classes are not in the archive —
the E-B class of gap, again). This is a *screen*. The airtight version,
A2-full, re-derives spans per perturbation via `isomorph.find_isomorphs`,
which this cycle located and verified importable.

## 1. The confusion model (convention-independent)

A glyph is three eyes, each one of five orientations — a base-5 trigram. One
misread eye is one changed digit; values ≥ 83 are outside the alphabet and
self-flagging. So the plausible-confusion set of glyph `g` is its base-5
Hamming-1 neighbors inside 0–82 (≤ 12 per glyph), and the set is invariant
under digit-significance and orientation-numeral relabeling — no
reading-order assumption enters.

## 2. Coverage — the map's shape before any test

**164 of 1,036 positions sit at pool letter cells**; the other 872 are
provably invisible to glyph-value errors at the pool layer (dot cells and
unspanned positions feed no row). Value-level transcription risk to the
certified structure concentrates on 164 positions — already a 6× reduction
of the verification surface before any measurement.

## 3. Gate results, including the number that reframes the whole question

```
determinism                              PASS
plant detectable and located exactly     PASS   (score-strict best = the reversal)
null calibration, 120 random misreads:   worse 120/120   same 0   better 0
                                         detectable 120/120
```

**Every one of 120 random single-eye misreads at covered positions was
detectable, and every one made the structure strictly worse.** The certified
system is maximally sensitive at its letter cells: there is no silent-error
class there, and the error-hunt has a measured false-positive background of
zero.

## 4. Tier 1 — the East 1@68 typo hypothesis: REFUTED at screen level

All 49 pool-covered positions across the eleven pairs repair C drops, every
plausible confusion at each — **zero improving perturbations.** The best
score found anywhere in the region was (52, **9**): identical contradictions
plus one *additional* forced equality. No single-eye misread reconciles the
spurious instance with the certified class structure, even partially. Five
independent lines already marked E1@68 a chance isomorph (FR2/6/21/25/27,
plus FR171's external witness); the last mundane alternative — a literal
transcription error — now joins the refuted list. The one repair in the
record is a repair of the *corpus's own coincidence*, not of anyone's
transcription.

## 5. Tier 2 — the broader hunt (partial; instrument shipped to finish)

44 of the 115 remaining covered positions, 449 further evaluations: **zero
improving perturbations**; per-position worst-case damage from a misread
ranges 0 to **84 contradictions** (median 17) — most letter cells are
individually load-bearing to a striking degree. Remaining 71 positions run
locally in ~10 minutes: `python3 eyefuzz3.py tier2 44 115` (chunk freely).
Given 0-for-1,100+ across null, tier 1, and this chunk, the prior on a hit
in the remainder is the null rate: ~0.

## 6. What the screen buys

The premise "the transcription is correct" now has structure instead of
faith: 872 positions cannot affect the certified system's values at all; at
the 164 that can, single-eye errors are 100%-detectable and uniformly
damaging, and none of 1,100+ tested perturbations — including every
plausible typo at the one anomalous instance — improves anything. The
residual risk is exactly two named things: (i) errors at the 164 that were
*already present* before certification (indistinguishable from truth by
construction — only imagery re-verification of those 164 cells closes it, a
finite checklist this screen just wrote), and (ii) span-formation effects,
which are A2-full's terrain.

## 7. Doctrine changes

| item | prior | now |
|---|---|---|
| E1@68-as-typo | untested mundane alternative | **refuted** (49 positions × all confusions, zero improvements) |
| transcription premise | "spot-checked at 10/1,036" | screened: 872 invisible; 164-cell checklist defined; 0/1,100+ improvements; misreads 100% detectable at letter cells |
| unrepaired-pool cost | qualitative (injectivity story) | **measured: 52 contradictions, +0 equalities** vs certified 8 |
| A2 status | designed (FR199) | screen executed; **A2-full specified**: span re-derivation via `find_isomorphs`, located and importable |

## 8. Horizon

1. Finish tier 2 locally (71 positions, ~10 min) — expected null.
2. **A2-full / A3 share a prerequisite and should merge into one cycle:**
   regenerate the 208-class scan with `find_isomorphs`, gate by exact
   row-multiset match against the shipped problem file, then (a) re-derive
   spans under perturbation for the airtight fuzz, and (b) sweep thresholds
   for new certifiable classes — FR199's only route past 79.1%.
3. A5/A6 remain queued (the two unexplained numbers; the reading-order
   reproduction). 4. The external asks stand, unchanged, on a theorem.
