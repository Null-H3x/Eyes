# Field Report 113 — THE DRILL FOUND A DEFECT: THE BLIND-CLUSTER RULE IS NEITHER NECESSARY NOR SUFFICIENT

*Instrument: `eyedrill.py` (4/4 gate, 200 planted acquisitions). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. Why run a drill at all

`ACQUISITION_SPEC.md` is now the project's principal deliverable. It was
assembled across FR46, FR54, FR101, FR106, FR107, FR108 and FR112, and amended
three times in this session as findings landed. **Every number in it has been
verified individually; the procedure had never been executed.**

FR46 made exactly this argument for the model — it had never been rebuilt end
to end, *"a test it could genuinely have failed"* — and it applies verbatim to
the spec. Each part correct, the assembly untested, is the failure mode that
hides errors.

**The drill:** plant a truth (repair, ratio, scale, bases), derive the true `q`
values, follow the spec literally — three anchors in an eligible component
spanning ≥2 blind clusters, solve for `(base, d1, d2)`, one anchor per
remaining component, propagate — and check recovery against the plant.

---

## 1. The spec failed

```
[R1] 200 planted trials, spec followed literally:
       (d1,d2) recovered exactly : 193/200
       all 56 glyph values exact : 193/200
       VERDICT: *** SPEC DEFECT ***
```

Seven trials in two hundred followed the spec's target-selection rule and did
**not** resolve the drift, leaving 17 candidates instead of 1.

---

## 2. SELF-CORRECTION — and my first diagnosis was also wrong

**My initial hypothesis:** "spans ≥2 blind clusters" is too weak; three anchors
need three *distinct* clusters, because two anchors in one cluster give a
ratio-blind difference and therefore only one informative equation.

**That is wrong, and instructively so.** A blind pair is not useless — it is
*more* useful. If `α_b − α_a = 0` the difference is independent of `d1`, so
that equation **isolates `d2` directly**, and the remaining equation then gives
`d1`. The spec's own witness `(5, 27, 50)` has 5 and 50 in one cluster and
resolves cleanly. I had the sign of the effect backwards.

**The correct criterion is a rank condition,** found by exhaustive enumeration
rather than by reasoning about clusters. Three anchors `{a, b, c}` in one
component resolve **iff the 2 × 2 system in `(d1, d2)` is non-singular**:

```
(alpha_b - alpha_a)(beta_c - beta_a) - (alpha_c - alpha_a)(beta_b - beta_a)  !=  0   (mod 83)
```

Exhaustively over all triples:

| component | triples | resolve | fail |
|---|---:|---:|---:|
| C1 (25 glyphs) | 2300 | 2250 (97.8%) | **50** |
| C2 (11) | 165 | 160 (97.0%) | **5** |
| C3 (7) | 35 | 32 (91.4%) | **3** |
| C4 (3) | 1 | 1 (100%) | 0 |

**The blind-cluster rule is neither necessary nor sufficient.** Failing triples
include `(0, 9, 17)`, `(0, 48, 68)` and `(0, 64, 81)` — each spanning **three
distinct clusters**, which the spec's rule would have approved. And
`(5, 27, 50)` spans only two and resolves. The rule correlates with the truth
and does not determine it.

The observed 7/200 (3.5%) is consistent with C1's 50/2300 (2.2%) given the
extra constraint that the sampled triples span ≥2 clusters.

---

## 3. The spec's failure modes DO hold

The warnings are not decoration. Each was verified to fail as stated:

| mode | result |
|---|---|
| **F1** three anchors inside one blind cluster `{0,1,27}` | 17 survivors — **fails as specified** |
| **F2** two anchors only | 17 survivors — **fails as specified** |
| **F3** anchors split across components | 1394 survivors, by construction |
| §7 item 4 ratio check | a ratio outside the 17 correctly flags the model or the anchor set |

So the spec is right about what *cannot* work and was wrong only about what
*can*. The three published witness triples all pass the corrected criterion —
`(5,27,50)` det 78, `(13,23,25)` det 9, `(16,42,73)` det 70 — so **no acquirer
following the spec's concrete examples would have been misled**; only one
inventing their own triple from the stated rule.

---

## 4. The correction, shipped

`ACQUISITION_SPEC.md` §4 step 2 now carries the determinant criterion as the
operative test, with the blind-cluster table demoted to background. Safe
opening triples verified by the criterion:

```
C1: (0, 1, 5)   C2: (13, 19, 23)   C3: (16, 21, 26)   C4: (4, 35, 37)
```

An acquirer with any three candidate glyphs can now check them directly rather
than consulting a cluster table that is right 97% of the time.

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| **Target-selection rule** | span ≥2 blind clusters (FR106/FR107) | **2×2 determinant ≠ 0** — exact |
| Blind-cluster rule | operative | **heuristic**; neither necessary nor sufficient (correlates ~97%) |
| Resolving triples | unquantified | C1 2250/2300, C2 160/165, C3 32/35, C4 1/1 |
| Published witness triples | verified by simulation (FR108) | **re-verified** by the exact criterion; all valid |
| Spec's failure modes F1–F3 | asserted | **verified** to fail as stated |
| The specification | untested as a procedure | **executed 200×**; defect found and corrected |

---

## 6. Model status

Unchanged by this cycle: 384 relations over 56 glyphs; injectivity clean at 17
ratios; exposure 74.1%; components (25, 11, 7, 3, 2, 2, 2, 2, 2); acquisition
10–11 anchors. Cumulative: 27.16 billion candidates, zero survivors.

---

## 7. Horizon

1. **The specification is now tested as well as verified.** With the
   determinant criterion in place a fresh drill should return 200/200; that
   confirmation is worth one run but not a cycle.
2. **The analysis side is complete.** Sweep exhausted (FR99), alphabet size
   settled (FR97), assets acquired (FR101), coordinate grammar closed (FR100),
   repair fork closed to internal analysis (FR111), gauge audit finished
   (FR112), and the deliverable now drilled (this cycle). Every remaining
   question is external.
3. **A closing methodological note.** Three cycles in a row found errors in
   work this series produced — FR109 in FR47/FR48, FR110 in FR27, FR113 in
   FR106/FR107. In each case the error survived because a plausible rule was
   never executed against a case it could fail. The general remedy is the one
   FR46 and this cycle used: **run the procedure, do not merely check its
   parts.**
