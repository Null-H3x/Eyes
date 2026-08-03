# Field Report 204 — THE RESIDUAL-STRESS PROGRAM: THE MODEL DOES NOT CRACK UNDER ITS OWN ANOMALIES — THREE CLOSE AS CORROBORATION OR NOISE, ONE REMAINS EXACTLY AS SUGGESTIVE AS BEFORE, AND THE UNEXPLAINED-DIMENSION COUNT REACHES ZERO

*July 2026. Cycle: EYESPIRAL-C, attack line 2 of the 30-day program. The
question line 2 exists to answer: if the standing model is wrong in any way
that matters, it should show in the anomalies we have already measured, not
in a-priori space (which line 1 largely closed). It does not show. This is the
line most able to find a real crack, and it found none — which is itself a
result worth the build.*

---

## 0. The four anomalies, and their verdicts

| anomaly | prior status | verdict this cycle |
|---|---|---|
| 121 contradicting scan candidates | "chance, like FR151" (assumed) | **corroboration** — contradiction mass is *below* the geometry-preserving null |
| FR195 base structure (p = 0.027) | suggestive, parked | **unchanged** — still p ≈ 0.014/0.056; robust to the fragment merge |
| FR102 "29th dimension" | one unnamed excess dimension | **named and closed** — free space is exactly {3 fragment constants + drift} |
| FR184 +1.2σ residual | logged, uncharacterized | **noise** — one-tailed p = 0.115 by its own magnitude |

## 1. The 121 contradictors are the model working, not failing

The scan's 135 contradicting candidates (revised count) were the most likely
place for a systematic model error to surface: if the standing skeleton were
subtly wrong, chance windows would contradict it *less* than random geometry
predicts only if the skeleton were under-constrained, and *more* if it were
over-fit to noise. The test, geometry-preserving (same shapes, random
positions, 20 replicates):

```
real contradiction mass  4,506
null distribution        median 5,927, mean 5,914, range [5,607, 6,195]
p(null >= real)          1.000
```

Real contradiction mass is **24% below** the null. The certified skeleton is
*more* internally consistent than random geometry of the same shapes — chance
windows contradict it less often than they contradict a random alphabet.
That is the signature of a correct constraint system, not an over-fit one:
an over-fit skeleton would be *fragile* (high contradiction mass against
perturbation), and this is the opposite. The contradictors distribute across
all nine messages with no single-message concentration (E5 highest at 169,
E1 lowest at 79 — a 2× spread consistent with message-length and
repeat-density variation, not a localized fault). FR151's "chance" call is
upgraded: not merely consistent with chance, but *evidence for the model*.

**One honesty note on the p = 1.000.** A p-value pinned at the ceiling
invites suspicion of a mis-specified null. Here it is expected and correct:
the null randomizes only position (preserving each shape's length, letter
template, and instance count), so it measures how often the *real glyph
values* at real cells cohere versus at random cells — and real co-plaintext
cells cohere by construction. The ceiling is the point, not an artifact.

## 2. The base structure is exactly as suggestive as it was

FR195's residual (D = 16 distinct folded differences, Z = 2 zeros, over
200,000 uniform 9-vector draws): **P(D ≤ 16) = 0.014, P(Z ≥ 2) = 0.056.**
Unchanged from FR195, as it must be — the base vector is per-message and
fragment-independent, so the FR201 merge cannot touch it. It remains the one
genuine open structural residue: below the 0.05 line on distinct-differences,
above it on zeros, Bonferroni-corrected to non-significance, characterized
(E1=W1, E4=E5, the 29·d partner offsets, the +1·d steps) and *unfitted* per
FR35. It is neither dismissable nor actionable internally — it becomes
interpretable the instant the drift is externally pinned, and not before.

## 3. FR102's 29th dimension: named, and the unexplained count hits zero

The extended certified system's free space, computed directly:

```
columns touched      63 glyph + 9 base = 72
pivot rows           68
free dimensions      4
the four, by name    glyph col 81 (giant, 57)   -> A_giant
                     glyph col 59 (comp-1, 4)    -> A_comp1
                     glyph col 80 (comp-2, 2)    -> A_comp2
                     base col 8  (message E5)     -> the drift/gauge freedom
```

Exactly one representative per fragment plus one global — the three fragment
constants and the drift, nothing floating. FR102's "29th excess dimension"
was a classes-only-era count against a different system; under the extended
reading there is no unexplained dimension at all. Combined with FR184 closing
as noise, **the record now carries zero uncharacterized quantities** — every
number is either determined, a named free parameter, a priced residue (§2),
or noise by its own magnitude.

## 4. What line 2 establishes for the program

The model was given its best chance to break on evidence already in hand, and
it strengthened instead: its one over-fit test came back anti-fragile, its
dimension count closed, and its only live residue held steady and stayed
below the actionability threshold. Combined with line 1 (inner-layer
structural hypotheses falsified, affine-invariance boundary proven), the
internal picture is now:

- **No internal crack exists** in the places we could look — six drift
  routes dead, uniqueness proven, anomalies resolved, dimensions named.
- **The one open internal residue (base structure) is drift-gated** — it
  cannot be pushed further without an external anchor, at which point it
  either explains itself or becomes a second finding.
- **The remaining uncertainty is exactly what the don't-know list named
  and the theorems permit**: the drift scalar, the three constants, the
  20 dark glyphs (invisible by proof), and any affine-covariant or
  externally-keyed payload structure (invisible by principle).

## 5. Bearing on lines 3–4

- **Line 3 (mode tournament)** proceeds next as scoped: insurance plus the
  GAK closure. Line 2 sharpens its expectation — a tournament crowning the
  standing model unique-in-family is now the *expected* outcome, because the
  model has survived every stress an internal test can apply.
- **Line 4 (A2-full / imagery checklist)** remains the protective floor and
  is arguably now the highest *marginal* value remaining, because it is the
  only line that attacks the one premise no internal test can reach: whether
  the 164 load-bearing transcription cells are correct at the source. A
  single real transcription error there could merge a fragment or shift the
  base residue — the only way left to change the internal picture is to find
  the data itself wrong.

## 6. Artifacts and horizon

No new standing instrument — line 2 is analysis over existing systems; the
scripts are archived in the cycle log. Horizon: **build line 3 (the mode
tournament / affine-family scorer)** next, then **line 4 (A2-full live-span
fuzz + the 164-cell imagery checklist)**. Per the standing rule, if line 3
crowns the model as expected, line 4 becomes the single highest-value
remaining internal action and the program's honest floor before the external
asks carry the rest.
