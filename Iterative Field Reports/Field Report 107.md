# Field Report 107 — A GAUGE IS NOT KNOWLEDGE: FR106 WITHDRAWN, FR103 REINSTATED

*Instrument: planted-truth anchor simulation on canonical Δ coefficients. July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. SELF-CORRECTION — FR106's headline is wrong

FR106 concluded that FR54's opening move (two anchors in component 1) resolves
the 17-way drift-ratio ambiguity "for free", and on that basis withdrew FR103's
claim that the programme needs one more anchor. **That conclusion is
withdrawn, and FR103 is reinstated.**

**The error.** FR106 measured the discriminating power of an anchor pair by
counting distinct predictions of `q[a] − q[b]` across the seventeen ratios
**with `d2 = 1` held fixed**. That gauge is legitimate for the injectivity
scan — injectivity is scale-invariant by FR53's P1 proof, so it constrains only
the *ratio* and never the *scale*, and fixing `d2 = 1` costs nothing there.

**An anchor pair does not inherit that gauge.** With `d2` free, an observed
difference `V` satisfies

```
V = d2 * P(r)        where P(r) is the prediction at d2 = 1
```

so every ratio `r` remains viable, each with its own `d2 = V / P(r)`. Seventeen
distinct predictions *at a fixed scale* do not discriminate the ratio *when the
scale is unknown*.

**The general shape, worth carrying:** a gauge fixed for one computation was
silently carried into a different computation where it was not available.
FR53's P1 — the very proof that licenses `d2 = 1` for injectivity — is also
what makes it illegitimate for anchoring, because scale-invariance means
injectivity can never supply the scale that anchoring needs. The proof that
justified the gauge is the proof that forbids reusing it.

---

## 1. The corrected algebra

Component C, model `q[s] = base_C + D_s(d1, d2)`. **Δ is linear in the drifts —
verified, not assumed:**

```
D_s = alpha_s * d1 + beta_s * d2
```

confirmed exactly at five independent points `(3,1) (1,2) (5,3) (7,11) (40,5)`
against coefficients extracted from `(1,1)` and `(2,1)`. **42 of 56 glyphs have
`alpha_s != 0`**, i.e. depend on `d1` at all; the other 14 rest purely on
T2/T3-group evidence.

So `k` anchors in one component give `k` equations in **three** unknowns
(`base_C`, `d1`, `d2`) — not two. Under a single drift there are only two
unknowns, which is why FR54's `k = 2` is correct *there* and does not transfer.

---

## 2. The planted-truth test

Non-circular by construction: plant a true `(d1*, d2*)` drawn from the valid set
(17 ratios × 82 scales = **1,394** pairs, since injectivity fixes only the
ratio), plant a base, reveal true `q` values at `k` glyphs, and count how many
of the 1,394 candidates admit *some* base consistent with the revealed values.
300 trials per `k`:

| anchors in component 1 | surviving `(d1, d2)` — min / median / max |
|---:|---|
| 1 | 1394 / 1394 / 1394 |
| **2** | **17 / 17 / 17** |
| **3** | **1 / 1 / 17** |
| 4 | 1 / 1 / 1 |

**Two anchors leave exactly seventeen candidates, every time.** Three resolve
generically. The `max = 17` at `k = 3` is not noise — see §3.

---

## 3. FR106's blind-cluster table survives, with a corrected meaning

The table was computed correctly; only its interpretation was wrong. It does not
say that two anchors suffice — it predicts **which anchor *sets* fail to
resolve**:

| three anchors drawn... | survivors |
|---|---|
| entirely from one blind cluster `{0,1,27}` | **17** |
| entirely from `{6,7,47}` | **17** |
| entirely from `{9,10,79}` | **17** |
| entirely from `{17,62,63}` | **17** |
| spanning different clusters `[0,6,9]` | **1** |
| spanning different clusters `[1,17,48]` | **1** |
| spanning different clusters `[27,7,79]` | **1** |

Always, across 60 trials each. **The blind clusters are exactly the sets within
which the ratio cannot move glyphs relative to one another**, so an anchor set
confined to one of them carries no more information than two anchors do.

---

## 4. The corrected acquisition specification

> **Under two drifts, the opening move is THREE anchors in component 1, not
> two, and they must span at least two different blind clusters.** That
> determines `base_C1`, `d1` and `d2` together, delivering 25 glyphs and 31.2%
> of the corpus. Then one anchor per remaining component, as FR54 has it.
>
> **Total: 11 anchors, not 10.**

FR103 §3 said "one more independent anchor than FR54 priced." That is exactly
right, and FR106 withdrew it in error. FR104 §4's "seventeen candidate
alphabets" is also correct as a description of the **two-anchor** state — it is
where the programme sits after FR54's opening move, and the third anchor is
what collapses it.

**Blind clusters, for target selection** (avoid confining the opening three to
any one of them):
component 1 `{0,1,27} {5,50} {6,7,47,57} {9,10,79,81} {17,62,63} {20,71}
{30,68} {34,45} {48,64}`; component 2 `{13,44} {19,49,66} {25,60}`;
component 3 `{16,26,73} {21,40}`; component 4 `{35,37}`.

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| **Anchors to resolve the drift** | 2 in component 1, ratio free (FR106) | **3 in component 1**, spanning ≥2 blind clusters |
| **Total anchor count** | 10 (FR54); "no extra cost" (FR106) | **11** |
| FR103's "+1 anchor" | withdrawn by FR106 | **reinstated and verified** |
| FR104's "17-way enumeration" | over-charge (FR106) | **correct** — it describes the two-anchor state |
| Blind-cluster table | "which pairs resolve" | **which anchor SETS fail**; validated at k=3 |
| Δ dependence on drifts | assumed linear | **verified linear** at 5 independent points; 42 of 56 glyphs depend on `d1` |
| Valid `(d1,d2)` space | 17 ratios | **1,394 pairs** — 17 ratios × 82 scales; injectivity fixes the ratio only |
| Reusing a gauge across computations | unexamined | **forbidden** — FR53's P1 licenses `d2=1` for injectivity *and* forbids it for anchoring |

---

## 6. Model status

384 relations over 56 glyphs; injectivity clean; exposure 74.1%; components
[25, 11, 7, 3, 2, 2, 2, 2, 2] ratio-invariant. Alphabet [56, 83], floor 56.
**Drift: two parameters, valid space 1,394 pairs, resolved by 3 correctly-chosen
anchors in component 1.** Cumulative: 27.16 billion candidates, zero survivors.

---

## 7. Horizon

1. **Re-run FR54's per-component yield on canonical machinery under two drifts.**
   Still owed and still unexecuted — three cycles have now circled it. The
   partition is ratio-invariant (FR105) so the yields should be unchanged, but
   the opening-move count has just changed from 2 to 3 and the cumulative
   exposure table inherits that.
2. **Write the single acquisition specification.** It now spans FR54 (component
   ordering), FR105 (ratio-invariance), FR106 (blind clusters) and FR107 (three
   anchors, cluster-spanning). An acquirer should not have to assemble it from
   four reports.
3. **Audit the remaining figures for reused gauges.** This cycle's error class
   is new to the series: not a stale figure (FR52) nor a circular measurement
   (FR48), but a *gauge fixed for one purpose and reused where it does not
   hold*. Any quantity computed "with `d2 = 1`" or "at drift 1" deserves the
   same question FR107 asked.
