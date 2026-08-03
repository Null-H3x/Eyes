# Field Report 13 — The Shape of the Keystream

**Series note.** Thirteenth report of the iterative series. FR12 closed the two-term
linear-recurrence corner by sweeping it; this cycle stops sweeping model families and
asks what the corpus forces about the keystream's **shape** directly, with no model
assumed — then measures how much departure from that shape the openings require.
Instrument `eyeshape.py`, selftest 5/5 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** A perfect isomorph pair inside one triplet, at shift D over
a span of length L, forces K_g[t+D] − K_g[t] to be constant for t across that span —
because the two messages share the keystream and their bases contribute a single
constant. Nothing else is assumed: no recurrence, no drift, no alphabet, no PRNG. At
D = 1 this says the keystream's **first difference** is constant, i.e. K is
**arithmetic** there. Mapping every such range gives the first model-free cartography
of the keystream in this project: **T3's keystream is provably arithmetic across 61
positions — [35, 66) and [68, 98) — and T2's across 14**, with T1 constrained only at
higher shifts. This is why progressive has fitted the body so well for so long: on the
stretches the corpus can see, the body keystream really is arithmetic. The second half
of the cycle prices the escape. Modelling K as piecewise affine and sweeping
break-points, **a single key reset restores formal consistency** between the atlas
classes and the literal openings, and the admissible positions are sharply localised:
T3 admits a break only at 36, 102 or 103, T1 only at 31 or 93–97, while T2 is
permissive (it is the weakly-coupled triplet throughout this series). But the health
measure undercuts the fix: without the openings, all three exercised segment slopes
are free; with the openings plus a reset, **only one of six** is. The openings flatten
the keystream almost everywhere. For the fifth cycle running, a resolution of this
contradiction buys consistency by giving up determination.

---

## 1. Corrections and negatives first

**The degeneracy guard was fooled twice more, in two new ways.** (i) With a break-point
at position 18, segment 0 contains no pair cells at all; its slope variable is
unconstrained, so "is it forced to zero?" answered no and every break position read
LIVE. (ii) Restricting to segments that pair cells *touch* was still wrong, because
Δ = 0 opening pairs have their keystream terms **cancel identically** from the row —
the segment is nominally touched but its slope never appears. Both bugs manufactured
structure out of variables the evidence never constrains. The final rule, now a
regression test in the gate: a slope counts as exercised only if it **survives in some
row after cancellation**. Stated generally, and worth carrying forward as doctrine: *in
a linear model test, a variable absent from every row is free by construction, and
asking whether it is forced always answers no.* Across FR12 and FR13 this same failure
mode appeared five times in five different disguises; it is the dominant hazard in this
kind of analysis.

**No pins gained.** This cycle maps a shape and prices an escape; it certifies nothing
new about the alphabet.

## 2. C1 — model-free keystream cartography

The derivation is three lines. For two messages of one triplet, offset
off_m[t] = base_m + K_g[t]. A perfect isomorph pair at shift D requires the offset
difference to be constant across the span; the bases contribute one constant, so
K_g[t+D] − K_g[t] is constant on [p₁, p₁+L). No keystream model enters.

| triplet | shift | difference constant on |
|---|---|---|
| T1 | 2, 5, 10, 12, 23, 25, 28, 30, 35, 40 | various, e.g. shift 5 on [30, 53) |
| T2 | **1** | **[23, 37)** |
| T2 | 5, 6 | [18, 32) |
| T3 | **1** | **[35, 66), [68, 98)** |
| T3 | 2 | [51, 63), [69, 99) |
| T3 | 3 | [68, 101) |

**Provably arithmetic: T3 on 61 positions, T2 on 14.** T1 has no shift-1 pair, so its
shape is constrained only at higher shifts — consistent with T1 being the triplet whose
structure this series has repeatedly found hardest to pin.

This is the strongest positive structural statement available about K, and it is
immune to every model question the last four reports have wrestled with. It also
explains the long-standing fit of progressive without endorsing it: arithmetic *where
observed* is not arithmetic *everywhere*, and the openings live outside every one of
these ranges.

## 3. C2 — how much departure is needed

| configuration | verdict |
|---|---|
| globally affine, atlas only | LIVE (3 of 3 slopes free) |
| globally affine, atlas + openings | **DEGENERATE** — the FR9–FR12 contradiction |
| one global break-point | LIVE at 47 of 92 swept positions |
| one break in T1 only | LIVE at 31, 93, 94, 95, 96, 97 |
| one break in T2 only | LIVE at 37 positions |
| one break in T3 only | LIVE at **36, 102, 103** |

A single key reset suffices. The localisation is the interesting part: T3 tolerates a
reset at only three positions out of ninety-two, and two of them — 102 and 103 — lie
**outside** the ranges where §2 proves K_T3 is arithmetic. That coherence is a check on
the whole construction: the break-point sweep independently avoids the stretches the
model-free cartography has already pinned. (The third, 36, sits at the edge of
[35, 66); a break there is compatible only if the two affine pieces join continuously,
in which case it is not a real reset — flagged, not resolved.)

## 4. C3 — but the fix is weak

Free slopes are the health measure: how many of the exercised segment slopes the
evidence leaves undetermined.

- atlas only, globally affine: **3 free of 3 exercised** — every triplet keeps a live
  drift.
- atlas + openings + one global reset: **1 free of 6 exercised**, at every break
  position tested.

So the reset restores formal consistency by driving five of six segment slopes to zero
— a keystream that is flat almost everywhere, which is piecewise monoalphabetic and
close to the corner FG1 excludes. This is the same pattern as FR8's collapse theorem,
FR9's d = 0, FR11's Gromark degeneracy and FR12's family sweep: **every escape from the
opening/body contradiction found so far pays for consistency with determination.** That
consistency of the failure mode is itself evidence — it suggests the problem is not
which keystream to choose but one of the two remaining premises.

## 5. Where the trilemma stands

FR12 closed premise (iii) for all linear keystreams. This cycle shows the natural
non-linear relaxation — piecewise affine, i.e. a key reset — technically works but
degrades the model badly, and that the keystream's observable shape is arithmetic
exactly where the atlas can see it. The weight continues to shift toward the two
premises that have never been directly tested:

- **(i) the literal openings are not shared plaintext.** Still the most economical
  resolution, still untested by a direct measurement. FR11 nominated extending its
  agreement statistic into the opening spans and it remains undone — this is now the
  single most valuable open item in the series.
- **(ii) some certified atlas classes are not same-plaintext.** Expensive (FR10's
  shuffle null puts the classes at z = ∞), but the class-level localisation in FR10 and
  the sharp break-point localisation here both point at the same small set of classes.

## 6. Horizon

(1) **Test branch (i) directly** — the opening-span agreement statistic, keystream-model
independent, nominated in FR11 and still the top item. (2) The continuity question at
T3's break position 36: determine whether the admissible break there is a genuine
discontinuity or a forced continuous join, which would reduce T3's real options to
{102, 103}. (3) Extend C1's cartography by looking for further shift-1 pairs at relaxed
scan settings — every one found converts directly into more model-free keystream shape.
(4) Standing: FR8's bridge-symbol search, anchor calibration at rep = 4.

## 7. Reproduction

`eyeshape.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
5-check gate — the shift-1/arithmetic characterisation, the Δ = 0 cancellation
regression test, and two corpus controls (atlas alone must be LIVE with three free
slopes; atlas plus openings must be DEGENERATE). The full run reproduces the baseline
guard, C1's cartography, C2's break-point sweeps and C3's health measures. Failures
carry prefix `XD-MBYG04K-URS3LF`. The C1 derivation is checkable by hand from any
within-triplet pair's coordinates.
