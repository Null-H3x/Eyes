# Field Report 53 — Why Tightening Could Never Have Helped

**Series note.** Fifty-third report of the EYESPIRAL series. FR52 found the packing
constraint is about 160× tighter than published, which raised an obvious question: does a
constraint that much stronger now pin the drift? Instrument `eyeinvar.py`, selftest 7/7
green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** It does not, and the reason is a **proof rather than a
measurement** — which converts FR27's empirical negative into a permanent one. Sweeping all
82 non-degenerate drifts on the current 56-glyph skeleton, every drift still admits a
packing, exactly as FR27 found on the 47-glyph version. The explanation is that packing is
**scale-invariant by construction**: if {b_c} packs {S_c}, then multiplication by an
invertible d is a bijection of ℤ/83, so d·(b_c + S_c) = (d·b_c) + (d·S_c) are also pairwise
disjoint, and {d·b_c} packs {d·S_c}. The map is invertible, giving a **bijection between the
packings at drift 1 and those at any drift d** — so feasibility is preserved and so is the
count. Verified exactly on the four largest components: **275 packings at every drift
tested**. No amount of tightening can ever change this. FR27's finding and FR52's 160×
improvement are two instances of one structural fact, and the question is now closed rather
than merely unresolved. The cycle's second half builds the mechanism FR52 asked for: a
**canonical derivation** of every downstream figure from the current skeleton in one pass,
so nothing can silently go stale again.

---

## 1. I1 — the empirical answer, unchanged

| skeleton | glyphs | packing placements | drifts admitting no packing |
|---|---|---|---|
| FR27 (47 glyphs) | 47 | 1.5 × 10¹⁰ | **none** |
| **current (56 glyphs)** | 56 | **8.8 × 10⁷** | **none** |

A constraint 160 times tighter gives exactly the same verdict. That pattern is the clue
that something structural is going on rather than something contingent.

## 2. I2 — the proof

Let {b_c} be a valid packing for offset sets {S_c}, meaning the value sets b_c + S_c are
pairwise disjoint. For any d ≠ 0, multiplication by d is a bijection of ℤ/83 (83 is prime,
so every nonzero scalar is invertible — asserted in the gate). Therefore

> d·(b_c + S_c) = (d·b_c) + (d·S_c)

are also pairwise disjoint, so {d·b_c} is a valid packing for {d·S_c}. The map is
invertible, so it is a **bijection** between the packing sets at drift 1 and at drift d.

Two consequences: feasibility is preserved, and the **number** of packings is identical.
Verified by exact enumeration on the four largest components (25, 11, 7, 3):

| drift | 1 | 2 | 3 | 5 | 7 | 17 | 31 | 41 | 82 |
|---|---|---|---|---|---|---|---|---|---|
| exact packings | 275 | 275 | 275 | 275 | 275 | 275 | 275 | 275 | 275 |

**Packing carries zero information about the drift — permanently, not just at this
skeleton.**

This is the concrete form of the insight FR36 stated in general: every determined quantity
is a fixed multiple of the drift (FR30), so any test invariant under an invertible scaling
is structurally incapable of pinning it. Injectivity asks whether values are distinct;
packing asks whether sets place disjointly. Both survive scaling intact. FR27 discovered
this empirically, FR36 named the reason, and this cycle proves it for packing specifically
and closes the line.

## 3. I3 — the canonical derivation

FR52 found two figures stale and observed that nothing prevented a third. This is the
mechanism. Every number below is computed from the corpus in a single pass:

| figure | value |
|---|---|
| determined relations | **384** |
| injectivity violations | **0** |
| glyphs in components | **56** |
| component sizes | 25, 11, 7, 3, 2, 2, 2, 2, 2 |
| corpus exposure | **768/1036 = 74.1%** |
| gauge ladder (1 / 3 / 9 gauges) | 0/82, 0/82, 82/82 |
| packing placements | **8.8 × 10⁷** |
| packing pruning | **2.6 × 10⁷ ×** |
| 2 anchors in component 1 | **25 glyphs, 31.2%** |
| all anchors | 56 glyphs, 74.1% |
| adjacent pairs | 558 — *superseded; use FR39's 6,384 pooled* |

Any figure quoted elsewhere that disagrees with this table is stale by definition.

## 4. What this changes

**Changes.** The packing question moves from "does not discriminate the drift on the
current skeleton" to "cannot discriminate the drift, ever." That is worth having: it
removes a line of attack that would otherwise look more promising each time the skeleton
grows.

**Does not change.** The model: 384 relations over 56 glyphs, components 25/11/7/3 plus
five pairs, injectivity clean, 74.1% exposure, repair A the unique maximal reading, drift
unpinned with H4 the only surviving hypothesis.

## 5. Where the drift now stands

Three routes have been closed on structural rather than empirical grounds:

- **injectivity** — scale-invariant (FR21, FR36)
- **packing** — scale-invariant, proved here
- **the plaintext channel** — drift-free by construction (FR30)

And two hypotheses have been resolved: H1 retired on coherence (FR44), H4 surviving but
resting on an untestable premise (FR43, FR44). **External anchors remain the only route,
and the reason is now understood rather than merely observed.**

## 6. Horizon

(1) **Two external anchors in component 1** — 25 glyphs and 31.2% of the corpus from the
first two, and the second one pins the drift for the whole system because a pair-difference
is bijective in it. (2) **The success criterion** is unchanged as the most consequential
open item, and nothing measurable bears on it. (3) The canonical derivation should be
re-run whenever the skeleton changes, which is the standing answer to FR52's staleness
hazard.

## 7. Reproduction

`eyeinvar.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
7-check gate — the current skeleton, the packing count identical at every drift, every
nonzero scalar invertible mod 83 (why the proof holds), feasibility preserved under
scaling, the derived exposure and two-anchor yield matching the audited figures, and the
baseline guard. The full run reproduces I1–I3. Failures carry prefix `XD-MBYG04K-URS3LF`.
