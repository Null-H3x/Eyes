# Field Report 19 — Three Routes Closed, and What the Ceiling Costs

**Series note.** Nineteenth report of the iterative series. FR18 established that the
constraint system can see only 51 of 83 glyphs and named three possible ways past that
ceiling. This cycle tests all three, closes all three, and then measures the thing that
actually matters — what the ceiling costs in readable text. Instrument `eyeend.py`,
selftest 5/5 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** All three recruitment routes are closed. **The literal
openings recruit nothing**: an opening pair is an exact Δ=0 identity, so both windows
carry the same glyph at every cell and the symbol terms cancel out of the row — 132
rows emitted, **zero** containing a symbol term. FR18's headline horizon item therefore
dissolves, and the branch-(i) cost is not larger than FR16 priced after all. **There
are no opening-to-body isomorphs** at any scan setting, at or below chance expectation.
**And no dot cell is constant**: across all 153 dot offsets in the atlas, every single
one varies across its class's instances, which vindicates FR6/FR7's stem reading as
exactly right rather than over-cautious and closes promotion by constancy. The
constructive half reframes what that ceiling means. Determining the 51 reachable glyphs
would expose **701 of 1036 positions — 67.7% of the corpus** — and, more importantly,
the residual is **scattered rather than blocking**: 179 of the 236 unknown gaps are a
**single position**, mean gap 1.42, with known runs averaging 3 and reaching 18. The
ceiling does not carve the corpus into readable and unreadable halves; it leaves
isolated holes in otherwise continuous text.

---

## 1. Corrections and negatives first

**FR18's headline horizon item was ill-posed, and I should have seen it from FR11.**
I proposed that the literal openings might recruit the glyphs the atlas cannot see,
since they relate 24 consecutive positions across six messages without needing any
repeat. But the openings are *exact* Δ=0 identities: at every cell both messages carry
the same glyph, so the row's symbol terms cancel identically and only base variables
survive. FR11 §1 already recorded this ("the openings add nothing because Δ=0 pairs
constrain only base variables, not symbols") and I did not connect it. Measured
directly: 132 rows, zero symbol terms. This is now the fourth horizon item in six
cycles to dissolve on inspection rather than on measurement — a pattern in how I have
been generating them that is worth naming, since each one costs a cycle's framing.

**A consequence worth stating plainly.** Because the openings cannot recruit glyphs,
the tension FR18 raised — that branch (i) might be much more expensive than FR16 priced
— does not exist. The openings are dispensable in exactly the way FR16 assumed.

## 2. The three routes

| route | test | result |
|---|---|---|
| R1 literal openings | do their rows carry symbol terms? | **0 of 132 rows** |
| R2 opening↔body isomorphs | scan sweep L = 8…15, rep 2–3, vs shuffle null | **0 found**, null expects 0.25–2.88 |
| R3 constant dot cells | per class, per dot offset, across all instances | **0 constant, 153 variable** |

R2 is the weakest of the three: with a null expectation between 0.25 and 2.88, finding
zero is unremarkable and the test is underpowered. Reported as null, not as evidence.

R3 is the most informative. FR6 and FR7 established that *some* dots vary — enough to
produce the atlas contradiction — and the sound-rows repair responded by masking them
all. That could have been over-correction. It was not: **every one of the 153 dot
offsets varies across its class's instances.** The stem reading is exactly right, and
there is no dot cell anywhere that could be promoted to letter status on grounds of
constancy.

## 3. The endgame arithmetic

The ceiling bounds which glyphs can be determined. It does not directly bound how much
text that exposes, and the two are very different questions.

- **51 reachable glyphs → 701 of 1036 positions, 67.7% of the corpus.**
- Residual: 335 positions across 32 glyphs, which would occupy the remaining 32
  alphabet slots as an unknown permutation.

| message | length | known | % | longest known run |
|---|---|---|---|---|
| East 1 | 99 | 67 | 67.7 | 11 |
| West 1 | 103 | 74 | 71.8 | 18 |
| East 2 | 118 | 76 | 64.4 | 6 |
| West 2 | 102 | 68 | 66.7 | 9 |
| East 3 | 137 | 88 | 64.2 | 10 |
| West 3 | 124 | 86 | 69.4 | 11 |
| East 4 | 119 | 78 | 65.5 | 8 |
| West 4 | 120 | 82 | 68.3 | 6 |
| East 5 | 114 | 82 | 71.9 | 9 |

Exposure is remarkably uniform — every message between 64% and 72%. And the shape of
the residual is favourable: known runs average 3.0 with thirteen runs of length ≥ 8 and
a longest of 18, while **179 of the 236 unknown gaps are a single position** (mean gap
1.42). The unknowns are isolated holes, not blocks.

## 4. What this means, and the caveat that limits it

Combined with FR17's leverage map the series now has, for the first time, an
end-to-end route stated in measured quantities: **eight well-chosen external anchors
determine all 51 reachable glyphs; those expose 67.7% of positions; the unknowns are
mostly isolated single gaps between known runs; and the 32 undetermined glyphs are
constrained to be a permutation of the remaining alphabet slots.**

**The caveat is real and it is the A-vs-B fork.** Whether isolated gaps can be filled
by context depends entirely on what the plaintext is. Under branch B — a flat token
inventory retaining structure — a text with two thirds of its positions known and
isolated holes is very likely readable, and the residual permutation falls out. Under
branch A — a further layer, high-entropy tokens, effective alphabet ≈ 79 per FG2/FG3 —
context does not help at all, and the favourable shape buys nothing. This report claims
the *shape* of the residual, which is a measurement; it does not claim readability,
which is not. A-vs-B remains the gate, exactly as WAY_FORWARD's Priority 2 has it.

## 5. Horizon

(1) **A-vs-B is now the binding constraint on the whole programme**, not merely on the
C-solver objective: it decides whether the endgame route in §4 terminates in readable
text or in a 32-glyph permutation nobody can fix. Every other open item is downstream
of it. (2) **The 15 candidate glyphs** (FR18) still want a non-isomorph constraint form;
R1–R3 closed the obvious ones, so anything new here has to be genuinely different in
kind. (3) **Audit #2⁻'s core** at instance level, the last standing item from FR15.
(4) Recompute FR17's anchor ranking restricted to reachable glyphs, since anchors
elsewhere are worth one glyph each.

## 6. Reproduction

`eyeend.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
5-check gate — the Δ=0 cancellation mechanism, run-finder exactness, null machinery, the
reachable-set count reproducing FR18, and the baseline guard. The full run reproduces
R1's row census, R2's sweep against nulls, R3's dot-constancy test and the endgame
readability map. Failures carry prefix `XD-MBYG04K-URS3LF`.
