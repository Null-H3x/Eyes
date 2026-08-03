# Field Report 102 — LINEARITY IS PARTLY DERIVED, AND DRIFT EQUALITY HAS BEEN UNSUPPORTED FOR SEVENTY-FIVE CYCLES

*Instrument: `eyekey.py` (9/9 gate, null-space analysis over GF(83)). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. The question, and why it was the right one

FR101 settled the success criterion — **solve for the unknown variables and pin
the exact cipher mechanism** — and nominated as horizon item 1 the audit of the
model's load-bearing structural claim:

```
K_g[t] = drift * t + kappa_g          (tech ref 3.2; assumption ledger A2)
```

A2 carries status **[MEASURED]**, and that status is honestly earned: FR56 and
FR91 tested for a **periodic** component and found none at any period 2–90,
with z = +13.1 detection power. **But "not periodic" is not "linear."**
Aperiodic non-linear keystreams — polynomial, exponential, PRNG-driven,
autokey — were never in that alternative set. The audit was owed.

---

## 1. The structural test

A certified same-passage alignment between (m1 at s1) and (m2 at s2) asserts, at
every cell i,

```
q[c1[s1+i]] - q[c2[s2+i]] = (base_m1 - base_m2) + (K_g1[s1+i] - K_g2[s2+i])
```

and the skeleton requires that be **constant** across the alignment — FR32's w,
drift-free and forced for seven message pairs. Therefore

```
K_g1[s1+i] - K_g2[s2+i] = const_a        at every cell of alignment a
```

This is a homogeneous linear condition on `K` over GF(83) depending only on the
alignment **geometry** — which triplets, which positions. Not on `q`, not on the
drift, not on the plaintext. So the space of keystreams consistent with the
corpus's own alignment evidence is computable **exactly**, with no statistics
and no anchors.

The linear family spans four dimensions: `K_g[t] = t` (the drift direction) plus
three per-triplet constants (gauge, absorbed by `base_m`). Positions no
alignment reaches are trivially free and excluded from the comparison.

Gate 9/9, with both controls live: a dense synthetic geometry **does** force
linearity, a sparse one **does not**, and a planted quadratic keystream is
correctly rejected by a forcing system.

---

## 2. Result: linearity is partly derived

| cell policy | alignments | constraints | covered K | null dim | linear dim | excess |
|---|---:|---:|---:|---:|---:|---:|
| **lettered (doctrine)** | 54 | 289 | 115 | 33 | 4 | **29** |
| full span (sensitivity) | 54 | 735 | 180 | 13 | 4 | 9 |

The geometry does **not** force linearity. But the excess decomposes, and the
decomposition is the substance:

**Global smooth bends are EXCLUDED — a new result.** Explicitly tested against
the constraint system: `K_g[t] = t²`, `t³`, and `2^t` are each **outside** the
null space, under both cell policies. Combined with FR56/FR91's periodic
exclusion, the keystream cannot bend polynomially, exponentially, or
periodically. This is the first structural (rather than statistical) evidence
for the progressive form, and it strengthens A2.

**28 of the 29 excess dimensions are local wiggle.** They track the 30 covered
positions that appear in ≤ 2 constraint rows — a coverage limit of the alignment
evidence, not a rival mechanism. A keystream that differs from linear at two
sparsely-constrained positions is not an alternative cipher; it is an
unmeasured corner.

**The remaining dimension is structural, and it is the finding.**

---

## 3. One global drift is NOT forced

Testing the three per-triplet drift directions separately against the
constraint system:

```
K_g[t] = t on triplet T1 only   ->  IN the null space
K_g[t] = t on triplet T2 only   ->  not in the null space
K_g[t] = t on triplet T3 only   ->  not in the null space
```

T2 and T3 are locked to a common drift; **T1's drift floats free.** The reason
is visible in the alignment census: of 54 certified alignments, exactly **three**
cross triplets, and all three are class **#2⁻** linking T2 to T3 (East 3@64 with
East 4@73, West 4@76, East 5@74). **After repair A, no alignment bridges T1 to
anything.**

---

## 4. SELF-CORRECTION OF THE SERIES — a broken deduction, twenty-two cycles old

The instrument found this from geometry alone. Tracing it back to doctrine
locates a propagation error of exactly the FR52 class.

**FR3 §6** derived drift equality:

> Under the progressive family, each increment equality reads
> `drift_gA·(j′−j) = drift_gB·(j′−j)` with `j′−j` invertible mod 83, so:
> **#2⁻ forces drift₂ = drift₃** and **#M⁻ forces drift₁ = drift₂**. All three
> drifts are equal.

A two-link chain. The atlas shows what happened to it:

| class | instances | triplets spanned |
|---|---|---|
| **#2⁻** | E3@64 (T2), E4@73, W4@76, E5@74 (T3) | before **and after** repair A: T2–T3 |
| **#M⁻** | E1@40, E1@68, W1@40, W1@70, E2@45, E2@80 (all T1), **E3@101 (T2)** | before: T1–T2 · **after: T1 only** |

**#M⁻'s sole non-T1 instance is East 3@101 — precisely the instance repair A
discards.** The link that forced `drift₁ = drift₂` was severed at FR25–FR27,
confirmed refuted at FR47, and the drift-equality conclusion was never
re-derived. It has stood on a withdrawn premise for seventy-five cycles.

FR3 itself flagged the exposure in the same paragraph — *"under general-K they
are the certified subset … **T1 weakly attached**"* — and the progressive-family
deduction papered over it. Two independent routes now agree: the geometry says
T1 is unbridged, and the provenance says the bridge was removed.

**Sixth propagation error of this shape** (FR39, FR42, FR45, FR48, FR97, FR102).
The standing guard applies unchanged: *any figure derived from the skeleton must
be recomputed whenever the skeleton changes.* Repair A changed the skeleton
profoundly and this figure was not recomputed.

---

## 5. What it costs, and what may rescue it

**The consequence is not contained.** Tallying which drift group supplied each
component's relations:

| component | glyphs | evidence sources |
|---|---:|---|
| 1 | 25 | **T1 and T2/T3 — mixed** |
| 2 | 11 | **T1 and T2/T3 — mixed** |
| 3 | 7 | **T1 and T2/T3 — mixed** |
| 4 | 3 | T2/T3 only |

**43 of 46 skeleton glyphs** sit in components whose Δ tables were computed from
relations of both groups under a single-drift premise. If `drift₁ ≠ drift₂₃`,
those tables need re-derivation.

**But the conclusion may survive on new evidence.** Building the relation graph
over skeleton glyphs (310 edges: 202 from T1 alignments, 108 from T2/T3) and
testing whether any T2/T3 edge closes a cycle already spanned by T1-only edges:
**8 such mixing cycles exist** (e.g. glyph pairs (40,21) and (68,71)). Around
any mixing cycle, consistency forces an algebraic relation between `drift₁` and
`drift₂₃`. The single-drift solution is **one point** on that relation — and the
skeleton's observed consistency (384 relations, zero injectivity violations) is
evidence that point is occupied.

**Whether it is the only point is not established, and is the next cycle's
question.** What this report claims is narrower and certain: *the argument for
drift equality is broken, and the conclusion currently rests on nothing.*

---

## 6. Doctrine changes

| item | prior status | status now |
|---|---|---|
| **A2 progressive keystream** | [MEASURED] — no periodic component 2–90 | **strengthened**: global polynomial and exponential bends now excluded *structurally*; qualified: geometry leaves 28 dims of local wiggle at weakly-pinned positions |
| **Drift equality across triplets** | asserted FR3, treated as settled | **UNSUPPORTED** — #M⁻'s bridge was discarded by repair A; T2 = T3 stands, T1 floats |
| FR30 one-parameter family | one drift fixes 384 relations | **conditional** on drift equality; otherwise two parameters |
| FR54 "second anchor pins the drift for the entire system" | stated | **conditional** — may pin only the anchored triplet's drift |
| Cross-triplet bridges | two (#2⁻, #M⁻) | **one** (#2⁻, T2–T3); #M⁻ is T1-internal after repair A |
| Component evidence provenance | untracked | tracked: components 1–3 mix drift groups, 43 of 46 glyphs |

---

## 7. Model status

Relations, components, exposure, injectivity: unchanged in *content* (384 over
56 glyphs, 74.1%, clean). Changed in *conditionality* — the Δ tables of
components 1–3 now carry an explicit dependence on drift equality that was
previously invisible. **Cumulative: 27.16 billion candidates, zero survivors.**

---

## 8. Horizon

1. **Does skeleton consistency force `drift₁ = drift₂₃`?** Rebuild the
   constraint system with two independent drift parameters and enumerate the
   consistent ratios. Eight mixing cycles exist, so the relation is non-trivial;
   if the ratio is forced to 1, drift equality is restored on sound evidence and
   the model is undamaged. If a second ratio survives, the model is a
   two-parameter family and the anchor arithmetic changes. **Internal,
   executable, and it directly serves the settled criterion** — this is
   mechanism-pinning in the exact sense FR101 defined.
2. **Re-price the anchor programme against the outcome.** FR54's ordering
   assumes one drift; under two, an anchor in a T1-sourced component may not
   pin T2/T3 and the acquisition cost rises.
3. **The remaining keystream freedom is a coverage limit, not a hypothesis.**
   The 28 local dimensions sit at positions ≤2 alignments reach; no test can
   close them from inside the corpus, and none needs to.
