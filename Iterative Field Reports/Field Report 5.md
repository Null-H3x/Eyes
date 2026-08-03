# Field Report 5 — Structural Cribs as q-Relations

**Series note.** Fifth report of the iterative series. Doctrine remains Field Guides
1–5; FG6 stays reserved. This cycle converts FR4's structural leads into exact,
language-free, falsifiable mod-83 relations and tests them against the repo's own
certified pin component, using `iso_relax`'s machinery unmodified through a new
harness, `eyepin.py`, selftest 12/12 green before corpus contact.

**Scope constraint (given).** Isomorphs untouched; the repo's consensus machinery is
reused as-is; family space = the FR1 survivor set under the FR4 one-gauge reading
(conditional on progressive + shared templates, per FG4 discipline).

**One-paragraph verdict.** The registered battery returns **UNCHECKABLE across the
board** — an honest negative: the boundary-token relation (q[1] − q[47] ≡ 4), the
doubled-header relation (q[5] − q[66] ≡ 1), and the indicator-block window are
neither supported nor falsified, because the certified pin component simply does not
reach the hypothesis glyphs (glyphs 1 and 66 are entirely unlinked; only one
indicator is linked, and it is collision-tainted). The cycle's yield is elsewhere,
and it is substantial. First, a **soundness result** about pairwise determination:
my initial harness certified relations inside a consensus-surviving contaminated
island on the audit plant — internally consistent, truth-wrong — forcing the
certified-domain formalization (reference-anchored determination only, iso_relax's
implicit rule made explicit) plus a demonstration that anchor calibration, not the
domain filter, is the first line of defense. Second, the **reproduction guard**
lands exactly: linked 22, distinct 19, pins 16, census ratio 0.012. Third, the
constructive centerpiece: the certified component **intersects the opening
templates**, and after excluding the six collision-tainted symbols, eight template
slots carry pin-grade q-values — yielding a small set of **exact plaintext
token-difference facts about the opening text itself**, including: the two frames'
first post-header tokens differ by exactly 3, and frame A's tokens at slots 15 and
19 differ by 3 again. These are hard constraints the Eye Crib Tester can consume
today.

---

## 1. Corrections and negatives first

**My first pairwise test was unsound, and the audit plant proved it.** The naive
extension of iso_relax's gauge-invariance test to arbitrary pairs certified mutual
differences inside a disconnected subcomponent of the overdetermined plant — 28
internally consistent, truth-wrong annex pairs, traceable to a false pair that
survived consensus into an island. iso_relax is implicitly protected because its
global-reference test only certifies the reference's component; the harness now
makes that rule explicit (`certified_domain`), demotes disconnected pairwise
relations to a labeled annex that can never produce a verdict, and the selftest
*asserts* the contaminated island is excluded. This is a transferable soundness
lesson for anyone extending the pin machinery: **pairwise determination without
reference anchoring is not evidence.**

**Calibration is upstream of everything.** A second negative exhibit, kept in the
selftest deliberately: running the plant at the corpus's base_len (13) instead of
the audited plant calibration (10) contaminates even the reference component — 15
truth-wrong certified pairs. The domain filter cannot rescue a miscalibrated
anchor tier. The corpus run therefore opens with a hard reproduction guard (must
re-derive linked 22 / distinct 19 / pins 16 or die), which passed exactly.

**A post-run refinement, disclosed.** The 22-symbol certified domain contains the
three known value collisions (glyph pairs {0,10}, {9,63}, {40,72} sharing certified
values — exactly the 22−19 gap, and 22−6 = the 16 pins). Colliding symbols carry
internally consistent contamination by the same logic as the island, so the
template-skeleton artifact below is **pin-grade filtered** (16 symbols only), two
initially attractive template slots (A@9, A@12) were dropped, and an initially
logged relation between glyph 5 and glyph 63 is downgraded to annex because 63 is
tainted.

**One post-hoc observation carried from the reproduction step.** Seeing the pin
table exposed q[49] − q[48] = 3 before the battery ran. The registered battery was
frozen beforehand and does not include it; it reappears below as a pin-grade
descriptive fact, never as a tested hypothesis.

## 2. The idea

FR4's one-gauge deduction makes the corpus a single monoalphabet in u-space
(u = p + t). A structural hypothesis about plaintext tokens therefore becomes an
exact relation between q-values of specific glyphs — language-free, unaffected by
the A-vs-B gate, and falsifiable against already-certified material. Registered
before the pin table was seen:

| hypothesis | relation | rationale |
|---|---|---|
| H1 boundary token | q[1] − q[47] ≡ 4 | same closer token at T3-slot 20 (glyph 47) and T1-slot 24 (glyph 1): (D+24)−(D+20) |
| H3 doubled header | q[5] − q[66] ≡ 1 | header = one token written at t=1 and t=2 |
| H2 indicator block | nine indicator q-values fit a width-9 circular window, distinct | indicators as nine consecutive labels, any order |

Verdict rules, frozen: SUPPORTED (forced difference equals hypothesis; coincidence
price 1/83 per equation, stated), VIOLATED (exact falsification), UNCHECKABLE (no
reference-anchored determination). H2: with k ≥ 2 determined indicators, window
embeddability with exact enumerated coincidence price.

## 3. The battery result

Reproduction guard: **linked 22, distinct 19, pins 16 — matches certified.**
Consensus solution touches 37 symbols; certified domain 22; pin-grade 16.

| hypothesis | status | detail |
|---|---|---|
| H1 boundary | UNCHECKABLE | glyph 1 entirely unlinked; glyph 47 in solution but outside the certified domain; annex also empty |
| H3 doubled header | UNCHECKABLE | glyph 66 entirely unlinked; glyph 5 is pin-grade but has no linked partner |
| H2 indicator block | UNCHECKABLE | only glyph 63 linked among the nine, and it is collision-tainted |

Not falsified, not supported. The hypotheses are healthy and waiting for reach.

**The targeting guide** (from the occurrence maps): no hypothesis is blocked in
principle. Glyph 1 occurs 14 times across six messages at spread positions (not
only the position-24 stack), glyph 47 occurs 21 times, glyph 66 occurs 23 times —
all linkable by position-difference machinery the moment any certified pair
touches them. Each hypothesis converts to CHECKABLE the day a relaxation tier, a
bridge crib, or a new certified isomorph links its glyphs into the reference
component. The sparsest case is indicator glyph 27 (three occurrences) — the E4
indicator is the hardest to ever link; the others range 8–16 occurrences.

## 4. The certified template skeleton (the constructive artifact)

The pin-grade component intersects the opening templates at eight slots:

| frame | t | glyph | q (ref gauge) | p_gauge = q − t |
|---|---|---|---|---|
| A | 3 | 49 | 71 | 68 |
| A | 14 | 59 | 78 | 64 |
| A | 15 | 18 | 28 | 13 |
| A | 19 | 5 | 35 | 16 |
| B | 3 | 48 | 68 | 65 |
| B | 5 | 13 | 13 | 8 |
| B | 22 | 13 | 13 | 74 |
| B | 23 | 49 | 71 | 48 |

Gauge differences are absolute. The independent token-difference facts (glyph-repeat
tautologies labeled and excluded): frame A — p[14]−p[3]=79, p[15]−p[14]=32,
p[19]−p[15]=**3**; frame B — p[5]−p[3]=26, p[22]−p[3]=9 (and the glyph-13 repeat
forces p[22]−p[5]=−17 automatically; glyph 49 recurring at B@23 anchors the frames
to each other, so all cross-frame differences in the table are determined). The
headline cross-frame fact: **p_A[3] − p_B[3] = 3** — the two openings' first
post-header tokens differ by exactly 3 in plaintext value. And the same difference,
3, recurs inside frame A between slots 15 and 19. Six independent glyph values
anchor the whole skeleton; every stated difference is exact mod 83 and pin-grade.

For the Eye Crib Tester: any candidate opening reading must reproduce these
differences exactly at these slots. That is a filter of strength (1/83) per
independent equation against arbitrary candidates — five independent equations,
~1/83⁵ ≈ 2.5×10⁻¹⁰ combined — applied before any language or structure scoring.

## 5. Consequences

The pin wall's character is now sharper. The certified component is not merely "22
symbols linked": it is 16 sound symbols whose reach into the crib-critical opening
region is exactly eight slots, with the remaining six linked symbols carrying
demonstrable internal contamination (the collision triples). Growth strategies
should be evaluated by whether they extend the *pin-grade* set, and the audit
plant's island shows why census-tier growth (the 83-linked / 0.012-ratio state) is
not progress toward that. The structural-hypothesis program is validated as
machinery — battery, soundness model, and pricing all plant-proven — and blocked
only by reach, with a concrete per-hypothesis linking target list.

## 6. Horizon

(1) **Skeleton-constrained crib runs**: feed §4's equations to the Eye Crib Tester
as hard pre-filters for opening candidates in both frames — the first crib
machinery input in the series that is exact rather than statistical. (2) **Reach
campaigns**: the highest-value single link is glyph 47 or glyph 1 into the
reference component (activates H1); glyph 66 activates H3; any second untainted
indicator activates H2. Candidate route: bridge cribs at the six-deep 3–5 stack
(FR3) whose acceptance would certify new pairs touching these glyphs. (3) The
standing items — pipeline run under the objective-gate caveat, E3 dual-grouping,
boundary-token cascade — remain queued; (2) feeds all of them. (4) FR1 residuals
unchanged, lower priority.

## 7. Reproduction

`eyepin.py` (expects the repo checkout; `EYEFORWARD_DIR` / `EYE_CORPUS` overrides):
`python3 eyepin.py --selftest` — 12 checks including the contaminated-island
exclusion and the miscalibration negative exhibit; `python3 eyepin.py` — gate,
reproduction guard (hard-fails unless linked 22 / distinct 19 / pins 16),
hypothesis-glyph status map, registered battery, pin-grade template skeleton, and
the labeled post-hoc note. All failures carry prefix `XD-MBYG04K-URS3LF`. The
skeleton table is checkable by hand: take the exported pin values, subtract the
slot index mod 83, difference the results.
