# Field Report 80 — THE INVENTORY BOUND TIGHTENS: 60 TO 76, ON A 1.9× SAMPLE

*Instrument: `eyeinv` (built on the sign-corrected `eyegeom` channel). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — the sign correction unlocks discarded data

FR39 discarded the two near-duplicate message pairs — East1/West1 and East4/East5 —
because *"85% and 90% of their coincidences sit at SHIFT ZERO"*, which is shared
passage rather than token frequency. With the whole pairs removed, the estimate ran on
five pairs and 6,384 position pairs.

FR79's sign correction changes what is possible. At the correct residue the channel
**locates passages by shift**, so contamination can be excluded surgically instead of
by discarding entire message pairs. The two largest pairs in the corpus become usable.

Exclusion shifts are taken from **prior knowledge** — FR32's discovered passage shifts,
plus shift 0 for the two near-duplicates by definition — not from the measurement
being made. That matters: excluding shifts chosen by inspecting the data would bias
the inventory estimate upward.

---

## 1. Result

| exclusion window | usable pairs | hits | geometry null | z | effective alphabet |
|---:|---:|---:|---:|---:|---:|
| ±0 | 12,923 | 292 | 163.0 | **+10.47** | 44.3 |
| ±1 | 12,508 | 155 | 143.5 | +0.96 | 80.7 |
| **±2** | **12,314** | **150** | **140.9** | **+0.75** | **82.1** |
| ±3 | 12,133 | 149 | 136.2 | +1.08 | 81.4 |
| ±5 | 11,730 | 136 | 130.8 | +0.44 | 86.2 |
| ±8 | 11,177 | 135 | 125.8 | +0.79 | 82.8 |

The unexcluded row shows the passages loudly (z = +10.47). One position of exclusion
removes them and the estimate stabilises between 80 and 86 across every wider window —
**flat in the exclusion parameter**, which is what a genuine inventory estimate should
be and what a passage artifact would not be.

```
effective alphabet   82.1     Poisson CI [75.9, 89.4]
usable pairs         12,314   (1.9x FR39's 6,384)
```

Consistent with every prior estimate: FR39's 88.7, FR57's 84.6 [77.3, 93.4], FR79's
91–95 on five pairs.

---

## 2. The bound tightens

Power at this sample size:

| true inventory | expected hits | z vs null | |
|---:|---:|---:|---|
| 26 (English) | 474 | +28.0 | excluded |
| 29 (Finnish) | 425 | +23.8 | excluded |
| 40 | 308 | +14.0 | excluded |
| 50 | 246 | +8.9 | excluded |
| **60 (FR39's bound)** | 205 | **+5.4** | **excluded** |
| 70 | 176 | +2.9 | not excluded |
| 80 | 154 | +1.1 | consistent |

Observed: 150 hits, z = +0.76.

> **FR39 concluded inventory > ~60. FR80 concludes inventory > ~76**, on a 1.9× larger
> sample, with the two largest message pairs restored.

This is the first *tightening* of that bound since FR39 established it, and it comes
from correcting an error rather than from new evidence.

---

## 3. What it costs the endgame

The deliverable gets marginally worse again. FR66 exhibited a token stream sitting on
the alphabet-83 line; FR72 showed it has no separators above 4%; this raises the floor
on its inventory from 60 to 76.

An inventory of 76+ over an 83-symbol space means the plaintext uses **nearly the
entire available range with near-uniform frequency**. There is very little room left
for it to be a structured encoding of anything smaller.

---

## 4. Sign audit, continued

FR79 flagged that two of three checked uses of `w` contained the error. Completing the
survey of uses I can inspect:

| use | status |
|---|---|
| FR32's seven forced values | **correct** — verified 6/6 by FR74's independent scan |
| FR43 indicator constraint | **error**, corrected FR78 |
| FR39 coincidence channel | **error**, corrected FR79 |
| FR74 `eyebridge4` | **correct** — it is what verified FR32 |
| FR57 `eyegeom` (mine) | **inherited FR39's error** |

**FR57's numbers were measured at the wrong residue.** Its reported figures — 112
observed, 113.1 geometry null, gap −0.98% — are the +w values, and FR79 showed the
signal lives at −w. FR57's *conclusion* that FR39 stands is now supported by FR79/FR80
rather than by FR57's own measurement, and its numbers should be superseded by this
report's.

Three of five uses contained the sign error. It is not an isolated slip.

---

## 5. Model status

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity clean;
exposure 74.1%; alphabet 14.46 bits; message bases 19.13 bits (14.55 under the
indicator constraint); alphabet size in [56, 83]. **Plaintext effective inventory
82.1, CI [75.9, 89.4], on 12,314 pairs.**

**Cumulative sweep total: 193.6 million candidates, zero survivors.**

---

## 6. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Inventory bound | > ~60 (FR39) | **> ~76**, CI [75.9, 89.4] |
| Effective inventory estimate | 84.6 (FR57) | **82.1** on 1.9× the sample |
| Near-duplicate pairs | discarded whole (FR39) | **usable** with shift-based exclusion |
| Usable sample | 6,384 pairs | **12,314 pairs** |
| FR57's measured figures | certification of FR39 | **wrong residue**; superseded by FR79/FR80 |
| `w` sign errors | 2 of 3 uses | **3 of 5 uses** |

---

## 7. Horizon

1. **Extend to the full 56-glyph skeleton.** This estimate uses my 46 held glyphs; the
   five two-glyph components would add pairs and tighten the CI further. Needs their Δ
   values.
2. **Acquire glyph 76** (FR78) — West 2's indicator, dual payoff as alphabet anchor and
   base constraint.
3. **The success criterion** (FR66, FR72, FR73, FR79). Each cycle has made the
   deliverable description worse and none has changed the decision. Inventory ≥ 76 over
   83 symbols is close to the ceiling.
4. **Audit the atlas for within-T2 classes** (FR76, FR77). Five channels find nothing.
