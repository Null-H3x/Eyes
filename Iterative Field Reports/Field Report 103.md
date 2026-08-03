# Field Report 103 — CONSISTENCY DOES NOT RESCUE DRIFT EQUALITY, AND #M⁻ CANNOT CARRY PAIRWISE SAME-PASSAGE

*Instrument: `eyetwo.py` (6/6 gate, two-drift system over GF(83)). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. The question

FR102 found that the alignment geometry does not force one global drift: after
repair A no alignment bridges T1, and FR3's chain lost its second link when
#M⁻'s only non-T1 instance (East 3@101) was discarded. But FR102 also found
**8 mixing cycles** in the relation graph, so skeleton consistency relates the
two drifts algebraically. The open question was whether that relation forces
the ratio to 1 — restoring drift equality on sound evidence — or leaves a
genuine second parameter.

The test is the full system. For a same-passage alignment, the shared plaintext
cancels and leaves, linear over GF(83) in every unknown:

```
q[c1[s1+i]] - q[c2[s2+i]] - b_m1 + b_m2 - d_g1*(s1+i) + d_g2*(s2+i) = 0
```

with unknowns `q[0..82]`, `b_m` (9), `d1`, `d2` — 94 in all. The coupling is
automatic because **q is global**: a glyph constrained by a T1 alignment and by
a T2/T3 alignment carries both drift terms into the same unknown.

Gate 6/6, both pre-registered R3 controls live: a synthetic corpus **without** a
cross-triplet bridge admits a planted `d1 ≠ d2`, and adding a bridge forces
equality.

---

## 1. SELF-CORRECTION — my first pool contradicted the established skeleton

The first corpus run returned "not forced", with witnesses. **It also returned
four forced-equal skeleton pairs at `d1 = d2 = 1`** — the model's own drift:

```
q[10] = q[71]   both component 1, Delta differ by 17
q[17] = q[81]   both component 1, Delta differ by 58
q[20] = q[64]   both component 1, Delta differ by 41
q[30] = q[50]   both component 1, Delta differ by 58
```

Four flat contradictions with a skeleton that is injectivity-clean by
construction. **A system that contradicts the model at the model's own
parameters is over-constrained, and its verdict is void** — whatever that
verdict happens to be. The reduction routine was verified correct on a planted
three-variable system first, so the fault was in the premises, not the algebra.

**Leave-one-class-out localises it exactly:**

| dropped class | alignments | forced-equal pairs |
|---|---:|---:|
| #M⁻ | 39 | **0 — injectivity restored** |
| #2, #F | 51 | 2 |
| #C0, #S, #2⁻ | 48–53 | 3 |
| every other class | 44–53 | 4 |

**#M⁻ is the sole cause.** My alignment set treated all C(k,2) instance pairs of
every class as mutually same-passage; #M⁻ has six surviving T1 instances, giving
fifteen such pairs — the largest single block in the pool.

**This is a genuine constraint on the pool, and the doctrine already implied
it.** #M⁻ is the shortest class (L = 8, pattern `A.B..B.A`, only four lettered
cells, k = 3 letters). FR15 priced it at **coincidence grade, p ≈ 0.10**, and
retired its cross-triplet bridge on that basis; FR49's sensitivity map found it
costs **zero relations** when withdrawn. What FR103 adds is the sharp form:
asserting #M⁻'s instances are *pairwise* same-passage is not merely weak
evidence — **it is inconsistent with the skeleton at every drift**, and must
not be done.

An earlier diagnostic that checked only *within-alignment* constancy passed 49
of 49 and would have let this through. The over-constraint lives in the
*cross-alignment* consistency that `b_m` and the drift term impose, which no
within-alignment test can see.

---

## 2. The answer, on the corrected pool

Excluding #M⁻ leaves 39 alignments (21 T1-internal, 3 cross-triplet, 15 other)
and a system consistent with the skeleton. Scanning `d1` with `d2 = 1` fixed by
the scale gauge, and requiring both consistency and injectivity on the 46
skeleton glyphs:

```
d1 values surviving:  77 of 82
equal-drift d1 = 1 :  SURVIVES
```

Two things follow, and they point in opposite directions:

**The model is not broken.** `d1 = 1` survives, so drift equality remains fully
consistent with the corpus. Nothing in FR102 or FR103 refutes it.

**But it is not forced.** Seventy-seven ratios survive the same test. The eight
mixing cycles constrain the pair `(d1, d2)` far too weakly to pin the ratio —
they eliminate five values, not eighty-one.

> **VERDICT: skeleton consistency does NOT rescue drift equality. On present
> evidence the model is a genuine two-parameter family — `d1` for T1, `d23` for
> T2 and T3 — with equality one consistent choice among seventy-seven.**

---

## 3. What this costs

**The drift is two unknowns, not one.** FR30's one-parameter family, FR26's
bijectivity result, and FR53's scale-invariance proof are all statements about
*a* drift; each now needs qualifying by which triplet group it applies to.

**FR54's anchor arithmetic is affected.** Its central claim — *the second anchor
supplies a pair-difference, bijective in the drift, and therefore pins the drift
for the entire system at once* — holds only under equality. Under two
parameters, an anchor pair landing in T1-sourced evidence pins `d1`; `d23`
needs its own constraint. The acquisition programme requires **one more
independent anchor than FR54 priced**, and FR54's ordering should be re-derived
with provenance tracked.

**What is unchanged:** the relations, components, exposure and injectivity
(384 over 56 glyphs, 74.1%, clean). The Δ tables are unchanged as *ratios*;
what changed is that components 1–3 mix evidence from two drift groups (FR102),
so their absolute scale now depends on two parameters rather than one.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| **Drift equality** | unsupported (FR102), possibly rescued by consistency | **not rescued** — 77 of 82 ratios survive consistency + injectivity; equality consistent, not forced |
| **Model parameterisation** | one-parameter family (FR30) | **two-parameter**: `d1`, `d23` |
| **#M⁻ pairwise same-passage** | implicitly available | **EXCLUDED** — contradicts the skeleton at every drift; 4 forced-equal pairs in component 1 |
| Pool construction | "all instance pairs of a certified class" | **invalid as stated**; class strength must gate pairwise assertion |
| FR54 anchor ordering | 2 anchors pin drift system-wide | **conditional on equality**; otherwise one more anchor needed |
| Within-alignment constancy checks | treated as sufficient validation | **insufficient** — blind to cross-alignment over-constraint |

---

## 5. Model status

384 relations over 56 glyphs; injectivity clean; exposure 74.1%; alphabet
[56, 83] floor 56. **Drift: two unpinned parameters.** Cumulative: 27.16
billion candidates, zero survivors.

---

## 6. Horizon

1. **Re-derive FR54's anchor ordering under two drifts**, with each component's
   evidence provenance tracked (FR102 §5 gives the tally: components 1–3 mixed,
   component 4 T2/T3-only). This directly prices the acquisition programme under
   the settled criterion and is internally executable.
2. **Audit the rest of the pool for the #M⁻ failure mode.** #M⁻ was caught
   because it broke injectivity; weaker classes may over-assert without breaking
   anything visible. The test is cheap — add each class's pairs and check
   consistency at `d1 = d2 = 1` — and FR49's sensitivity map plus FR50's
   skeleton-weight argument give the prior for which classes to distrust.
3. **A cross-triplet alignment involving T1 would settle the drift question
   outright.** None survives repair A. Whether one exists that the atlas missed
   is a search this series has not run since FR35, and it is now worth far more
   than it was: it would collapse two parameters to one.
