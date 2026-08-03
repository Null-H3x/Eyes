# Field Report 28 — The Last Contradiction, and a Re-Derived Exclusion

**Series note.** Twenty-eighth report of the EYESPIRAL series. FR27 favoured repair A and
left two items: locate the T3 opening contradiction, the last one standing, and put the
skeleton to work. This cycle does both, and corrects a framing I reached for on the way.
Instrument `eyealpha.py`, selftest 6/6 green with planted positive controls.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** The T3 opening contradiction is **genuinely three-way**: under
the repaired pool every *pair* of T3 messages may share an offset — E4/W4, E4/E5 and
W4/E5 each satisfiable at 82/82 drifts — while **any two of those constraints together,
and hence the triple, contradict at 0/82.** That corrects a framing I tried mid-cycle:
the doctrine records W4 as T3's odd message, so I looked for the contradiction to single
it out, and it does not. The constraint is symmetric and names no culprit. Separately,
the structured-alphabet corner is **re-derived rather than inherited**. The doctrine
carries alphabet_sweep's exclusion across ~9M hypotheses, but that was computed against
the pool FR21–FR25 showed asserts six equalities a permutation forbids; an exclusion
resting on partly-false constraints is not safe to carry. Re-run against FR26's repaired
skeleton — 223 relations, zero violations — **affine alphabets are excluded** (78 distinct
implied multipliers at the best drift, where a true affine C gives exactly one), **power
maps are excluded** (no drift/exponent pair fits every relation), and keyword-mixed
alphabets get no support (the best ordered-tail count, 8 of 223, is precisely the
expected maximum over 82 drifts at chance). The gate plants an affine and a power
alphabet first and recovers both exactly, so these are exclusions with teeth rather than
a test that cannot see anything.

---

## 1. The last contradiction, located

FR26 left an asymmetry unexplained: under the repaired pool the T1 opening is satisfiable
at every drift, while the T3 opening contradicts at every drift. Neither the
structural-prelude reading nor the plaintext reading predicts that.

Decomposing the T3 constraint — each opening pair is an exact Δ=0 identity, so each forces
two messages to share an offset:

| constraint | satisfiable drifts |
|---|---|
| E4/W4 | 82/82 |
| E4/E5 | 82/82 |
| W4/E5 | 82/82 |
| E4/W4 + E4/E5 | **0/82** |
| E4/W4 + W4/E5 | **0/82** |
| E4/E5 + W4/E5 | **0/82** |
| all three | **0/82** |

**Every pair of T3 messages may share an offset; no two such claims may hold at once.**
Since any two of these force all three messages onto one offset, the content of the
finding is that **T3's three messages cannot share a single offset**, though any two can.

**A framing I had to drop.** The doctrine records T3's near-duplicate pair as E4/E5 with
W4 the odd message (27.2% body agreement), so I expected the contradiction to isolate W4
and looked for it to do so. It does not: all three pairwise merges behave identically.
The constraint is symmetric, and reading a culprit into it would have been pattern-matching
to a fact from a different measurement.

The natural reading is that the T3 opening is not shared plaintext across all three
messages under the body's cipher parameters — but the test does not establish that, and I
am not claiming it.

## 2. Why the alphabet corner needed re-deriving

The doctrine records the structured-alphabet corner as EXCLUDED, on ~9M scored hypotheses
from alphabet_sweep. That result was computed against the constraint pool that FR21–FR25
later proved asserts six equalities a permutation forbids. An exclusion derived from
partly-false premises is not safe to carry forward, whatever its scale — so the families
are re-run against evidence that is not known to be false.

The test is sharp. If C is affine, q[g] = a·g + b, then every relation q[y] − q[x] = D
implies a = D·(y−x)⁻¹, and **all 223 relations must agree on a single multiplier**. The
skeleton's values are drift-dependent (FR26), so the sweep covers all 82 non-degenerate
drifts; a hit would have determined the drift *and* the alphabet at once, which is why it
was worth running despite a low prior.

## 3. Results

| family | result |
|---|---|
| affine, q[g] = a·g + b | fewest distinct multipliers at any drift: **78** (need 1) — **EXCLUDED** |
| power, q[g] = g^k | drift/exponent pairs fitting every relation: **none** — **EXCLUDED** |
| keyword-mixed (ordered tail) | best 8/223 at drift 32; chance 2.7 per drift, and 8 is the expected maximum over 82 drifts — **no support** |

**The positive controls are the point.** A planted affine alphabet is detected and its
multiplier recovered exactly (37); a planted power alphabet is detected and its exponent
recovered exactly (5); a random permutation is rejected by both; the ordered-tail detector
fires completely on an ordered alphabet. Without those the exclusions would be worthless.

## 4. What this does and does not establish

**Does.** C is not generated by a simple algebraic rule — affine or power — on evidence
that is not known to be false. This supersedes alphabet_sweep for the repaired pool: a
re-derived exclusion is worth more than an inherited one, even a much larger inherited
one, when the inheritance chain runs through constraints since shown false.

**Does not.** Constrain the corpus otherwise. A random permutation returns the same
verdict on all three families, so these are exclusions of *structure*, not measurements of
the corpus. And the exclusions are conditional on repair A, which FR27 favoured but did
not prove.

## 5. Where the programme stands

After twenty-eight cycles the position is more definite than it has been:

- **A determining, injective, rails-passing reading exists** — repair A plus the
  evidence-forced E4/E5 merge — giving 223 relations in components of 19, 7, 7, 3, 3
  (FR26), favoured over its alternative by embeddedness (FR27).
- **Its content is drift-conditional**, but one known pair-difference pins the drift
  bijectively, so two external anchors in component 1 determine 19 glyphs and a quarter of
  the corpus (FR26), and nine anchors leave only 44 completions (FR27).
- **The alphabet is not algebraically simple** (this cycle), so the remaining route to C
  is anchors and cribs rather than a generating rule.
- **One contradiction survives**: T3's three messages cannot share one offset.

## 6. Horizon

(1) **Price the T3 three-way constraint** the way FR15 priced the bridges: is the T3
opening's three-way identity as well-supported as its pairwise parts, and what would it
cost to read one of the three as not-shared? (2) **The 15 candidate glyphs** (FR18) remain
the only route to widening the skeleton without external anchors, and no non-isomorph
constraint form has yet been found for them. (3) **#2⁻'s instance-level audit** is the
last standing item from FR15. (4) The crib machinery can now be fed 223 exact relations
plus the packing constraint, but the guardrail holds: no natural-language scoring until
A-vs-B resolves.

## 7. Reproduction

`eyealpha.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
6-check gate — planted affine and power alphabets detected with their parameters
recovered, a random permutation rejected by both, the ordered-tail detector firing on an
ordered alphabet, and the baseline guard. The full run reproduces T1's decomposition of
the T3 constraint and T2's family sweep. Failures carry prefix `XD-MBYG04K-URS3LF`.
