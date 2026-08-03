# Field Report 112 — PACKING IS RATIO-DEPENDENT: P1's "PERMANENTLY" WAS SCOPED TO ONE DRIFT

*Instrument: `eyepack3.py` (4/4 gate incl. a P1 confirmation control). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. Target selection

FR107's gauge audit had three remaining candidates. Applying the signature —
*at risk iff a parameter was fixed for convenience AND the conclusion concerns
a case where it is unknown*:

- **the gauge ladder (0/82, 0/82, 82/82)** is already a sweep over all 82
  drifts; the parameter was never fixed. Condition (a) fails. Not at risk.
- **FR21's injectivity census** qualifies, but FR109 re-ran injectivity across
  all ratios for both repairs, which subsumes it.
- **FR27's packing residual curve** is the live one, and the reason is sharp.

**FR53 proved P1:** packing is invariant under scaling, therefore carries
"ZERO drift information, PERMANENTLY". The proof is about a **single global
scale** — multiplying every component's values by an invertible `d` preserves
disjointness. **A ratio between two independent scales is not a global
scaling**, which is precisely the gap FR104 exploited to make injectivity
informative after FR53 had proved it useless. And FR105 measured that the Δ
values differ at every one of the 17 clean ratios, so packing has every reason
to move with them.

**Why it matters:** FR27's curve underwrites *"nine anchors leave 44 enumerable
completions"*, carried into `ACQUISITION_SPEC.md`.

---

## 1. The control confirms P1 before the test runs

R3, pre-registered: scaling **both** drifts by the same factor must leave the
packing counts unchanged.

```
t4_R3_global_scale   PASS   (d1,d2) = (1,1) and (7,7) give identical counts
```

FR53's proof is confirmed, and the instrument is shown not to be merely noisy.
Whatever follows is about the ratio, not about scale.

---

## 2. The finding — packing is ratio-dependent

Allowed relative placements per component pair (of 83), across the clean ratios:

| ratio | C1–C2 | C1–C3 | C1–C4 | C2–C3 | C2–C4 |
|---:|---:|---:|---:|---:|---:|
| 1 | **10** | 21 | 38 | 41 | 57 |
| 8 | **1** | 18 | 37 | 33 | 54 |
| 9 | 2 | 15 | 31 | 40 | 55 |
| 28 | **1** | 13 | 32 | 36 | 55 |
| 48 | 2 | **12** | 32 | **30** | 53 |
| 55 | **1** | 14 | 32 | 34 | 53 |
| 78 | 5 | **24** | 33 | 35 | 55 |
| 82 | 9 | 23 | **40** | 36 | 54 |

**[R2] Seventeen distinct profiles across seventeen ratios.** Not one repeats.

> **FR53's P1 is correct and its scope is narrower than the doctrine records.**
> Packing carries zero information about a *global scale* — permanently, as
> proved. It carries substantial information about the *ratio* between two
> scales, a case P1 never addressed because the two-drift model did not exist
> when it was written.

The spread is large: C1–C2 ranges from **10 allowed placements down to 1**, and
the joint pruning varies from `log10 = −5.03` at ratio 1 to `−6.47` at ratio 28
— an order of magnitude and a half. FR27's published 147,000× pruning
(`log10 ≈ −5.17`) is essentially the **equal-drift** value.

---

## 3. The hoped narrowing FAILS

If some ratio admitted no joint packing it would be excluded, tightening the
seventeen. Tested by exact backtracking over all nine components:

```
all 17 ratios: PACKS  (10-12 search nodes each)
ratios with no joint packing: none
```

**Packing excludes no ratio.** It constrains *placements*, not the ratio
itself. Pairwise feasibility does not imply joint feasibility in general, so
this had to be checked rather than assumed — but here they coincide.

---

## 4. A small positive: packing can save an anchor, at three ratios

A component pair with exactly one allowed placement means fixing one base
determines the other — an anchor saved.

| ratios | forced pair | anchors saved |
|---|---|---:|
| **8, 28, 55** | C1–C2 | **1** (11 → 10) |
| the other 14 | none | 0 |

So the acquisition cost is itself ratio-dependent: **11 anchors at fourteen of
the seventeen ratios, 10 at three of them.** This cannot be exploited in
advance — the ratio is precisely what the anchors are being acquired to
determine — but it means an acquirer who has anchored C1 should **check whether
C2's base is already forced before spending an anchor on it.**

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| **FR53's P1** | "packing carries zero drift information, permanently" | **correct for a global scale only**; packing is ratio-dependent |
| FR27's packing pruning (147,000×) | a corpus constant | the **equal-drift** value; ranges `log10` −5.03 to −6.47 across ratios |
| FR27's residual curve / "44 completions at 9 anchors" | unconditional | **ratio-conditional** |
| Packing as a drift constraint | none (FR27, FR53) | **partial** — discriminates placements, excludes no ratio |
| Joint packing feasibility | untested per ratio | **all 17 pack**; pairwise and joint coincide here |
| Acquisition cost | 11 anchors | **11 at 14 ratios, 10 at ratios 8, 28, 55** |

---

## 6. Model status

384 relations over 56 glyphs; injectivity clean at 17 ratios; exposure 74.1%;
components (25, 11, 7, 3, 2, 2, 2, 2, 2). All 17 ratios jointly packable.
Acquisition 10–11 anchors depending on the ratio. Cumulative: 27.16 billion
candidates, zero survivors.

---

## 7. Horizon

1. **The gauge audit is complete.** Three targets examined across FR109, FR110
   and this cycle; **all three were affected** — the repair fork reopened,
   embeddedness died, and P1's scope narrowed. The remaining candidates (gauge
   ladder, FR21 census) were shown above not to qualify or to be subsumed. The
   error class introduced in FR107 has now been swept.
2. **The pattern is worth recording as doctrine.** Every proof and measurement
   in this project that predates the two-drift model was written under the
   implicit premise of one drift. FR53's P1 is the clearest case: a correct
   theorem whose stated scope ("permanently") outran its hypothesis. Any future
   result asserting permanence should name the parameter it is permanent in.
3. **Nothing internal remains on the drift or the repair.** Both are formally
   acquisition questions (FR111), the programme is specified and priced, and
   this cycle closes the last audit. The next substantive move is external.
