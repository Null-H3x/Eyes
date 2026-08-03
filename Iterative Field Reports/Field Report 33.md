# Field Report 33 — The First Widening, and What It Costs

**Series note.** Thirty-third report of the EYESPIRAL series. FR31 established that every
internal route to enlarging the determined skeleton was closed; FR32 found and supported
one new same-passage region. This cycle feeds it in. Instrument `eyewiden.py`, selftest
7/7 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** The passage recruits, and the skeleton widens for the first
time in the series — but not as a whole. Added with full-span rows it recruits every
unknown glyph in its span and produces **three injectivity violations**. Cell by cell,
exactly **one cell — offset 4 — violates on its own**; the other twelve are jointly clean.
That is the structure FR6/FR7 established for the atlas classes and FR19 verified
exhaustively (all 153 atlas dot offsets genuinely vary): same-passage regions carry
**variable-interior cells**. Keeping the twelve takes determination **223 → 350**, glyphs
**47 → 54**, corpus exposure **64.6% → 72.3%**, and the largest component from 19 to 24
glyphs, with injectivity clean and the gauge ladder unchanged. The cost is real and is
reported as a regression: the T1 opening, which the repaired pool accepted at 82/82 drifts
(FR26), now contradicts at **0/82** — so the widening forces onto T1 the same
stamped-header reading FR29 proposed for T3. And the recruitment makes FR5's **H1**
expressible for the first time since cycle five, because glyph 1 — which FR18 diagnosed as
dot-only and unreachable — now sits in component 1 alongside glyph 47. H1 would pin the
drift to **31**. But the test **cannot fail**, and saying so is the point.

---

## 1. Corrections and caveats first

**A test I built that cannot fail, caught late.** H1 predicts q[1] − q[47] = 4. With both
glyphs now in one component the difference is determined as 51·drift (FR30), and 51 is
invertible mod 83 — so *some* drift always satisfies H1. Consistency is therefore **not
evidence**; the test has no discriminating power on its own. CHALLENGE II should have
caught this before I ran it, and did not. What the result actually provides is a
conversion: a vague plaintext hypothesis becomes a specific, falsifiable claim about the
drift, which becomes a genuine test the moment a second hypothesis or an external anchor
pins the drift independently.

**A regression, reported rather than buried.** FR26's rails had the repaired pool
accepting the T1 opening at 82/82 drifts. With the passage added it is 0/82. The widening
is not free.

**The offset-4 exclusion is a hypothesis, not a fitted parameter.** Injectivity is the
only tool available for deciding which cells of a *newly discovered* passage are constant,
since it has no published pattern. The claim is that offset 4 is a variable-interior cell
— exactly what the atlas encodes as a dot everywhere else — not that the passage is
spurious. Twelve of thirteen cells cohering is the evidence for the passage; one variable
cell is the norm.

## 2. W1 — the passage, cell by cell

| offset | E4 | W4 | status | recruits |
|---|---|---|---|---|
| 0 | 4 | 35 | clean | 35 |
| 1–2 | 34/57, 60/19 | | clean | — |
| 3 | 63 | 1 | clean | **1** |
| **4** | **58** | **66** | **violates injectivity** | 58 |
| 5 | 80 | 18 | clean | 18, 80 |
| 6 | 17 | 27 | clean | 27 |
| 7–8 | | | clean | — |
| 9 | 75 | 74 | clean | 74, 75 |
| 10–12 | | | clean | — |

Offset 4 alone forces the equalities q[21] = q[71] and q[68] = q[73].

## 3. W2 — the widened skeleton

| | determined | violations | glyphs | corpus exposure |
|---|---|---|---|---|
| baseline (FR26) | 223 | 0 | 47 | 64.6% |
| **+ passage (12 cells)** | **350** | **0** | **54** | **72.3%** |

Components: **24, 10, 7, 3, 2, 2, 2, 2, 2**. Newly recruited: **1, 18, 27, 35, 74, 75, 80**.

Component 1 now holds 24 glyphs covering 30.6% of the corpus; component 2 grows to 10 and
absorbs glyph 66.

## 4. W3 — rails

| rail | result |
|---|---|
| 1 gauge | 0/82 — unchanged |
| 3 gauges | 0/82 — unchanged |
| 9 gauges | 82/82 — unchanged |
| + T1 openings | **0/82 — regression from 82/82** |
| + T3 openings | 0/82 — unchanged |

The gauge theorem is untouched. The T1 opening is the price.

## 5. W4 — H1, and what it is worth

q[1] − q[47] = 51 at drift 1, so 51·d in general; H1's predicted 4 holds at exactly
**d\* = 31**. As §1 says, this cannot fail and so supports nothing by itself. Its value is
structural: the series now has a **plaintext hypothesis expressed as a drift value**, and
two such hypotheses pointing at different drifts would falsify one of them.

H3 (q[5] − q[66] = 1) remains uncheckable — glyph 5 sits in component 1 and glyph 66 in
component 2, so their difference is not determined. One more passage bridging those two
components, or one external anchor in either, would settle it and turn H1 into a real test.

## 6. Where this leaves the model

- **Determined skeleton:** 350 relations over 54 glyphs, components 24/10/7/3 and five
  pairs, injectivity clean, 72.3% of corpus positions exposed.
- **Conditionality unchanged:** everything is a multiple of the drift (FR30), so the
  architecture is known and its scale is not.
- **Anchors:** ten components means two anchors in the largest plus one each elsewhere;
  the packing tail (FR27) still makes the last one redundant.
- **Openings:** both T1's and T3's must now be read as stamped material rather than
  encrypted shared plaintext.

## 7. Horizon

(1) **Bridge components 1 and 2.** That single link would make H3 checkable and, with H1,
give two independent drift predictions — the first genuine internal test of the drift the
series has had. The FR32 rescan with free w over unfixed message pairs is the natural
search. (2) **Re-run the FR32 scan with the widened skeleton**: more determined glyphs
means more informative cells per window pair, so the search that found this passage should
now be strictly more sensitive. (3) Standing: #2⁻'s instance-level audit; two external
anchors in component 1.

## 8. Reproduction

`eyewiden.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
7-check gate — baseline reproducing FR26's skeleton exactly, full-span rows shown to
over-assert, exactly one cell individually unsafe, the twelve jointly clean, recruitment
measured, the gauge ladder unchanged, and the baseline guard. The full run reproduces
W1–W4. Failures carry prefix `XD-MBYG04K-URS3LF`.
