# Field Report 108 — FR54 REPRODUCES, THE OPENING IS SIZE-LIMITED, AND THE TAIL ORDERING WAS SUBOPTIMAL

*Instrument: `eyeprice.py` (5/5 gate, canonical machinery). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. My CHALLENGE I hypothesis was wrong

Before building, I predicted the mechanical "+1 to every anchor count"
correction would miss something specific: FR107 measured that 42 of 56 glyphs
depend on `d1`, leaving **fourteen that do not**, and I reasoned that a
component composed entirely of `d1`-independent glyphs could never resolve
`d1` and therefore could not serve as the opening move.

**No such component exists.** Every component carries at least some
`d1`-dependence:

```
C1 22/25   C2 9/11   C3 4/7   C4 2/3   C5-C9 1/2 each
```

The fourteen `d1`-independent glyphs are spread thin, never concentrated. The
hypothesis was reasonable and it is refuted — logged rather than quietly
dropped, since a plausible-but-false prediction is worth as much to the record
as a confirmed one.

**But the constraint it predicted is real, for a different reason** — see §2.

---

## 1. FR54's figures reproduce exactly

FR54's per-component yields were computed 54 cycles ago on a skeleton this
archive could not rebuild until FR104 restored the `iso_relax` chain. Re-measured
from the canonical build, with no inheritance:

| component | glyphs | positions | exposure | FR54 published | |
|---|---:|---:|---:|---|---|
| C1 | 25 | 323 | 31.2% | 25 / 323 / 31.2% | **MATCHES** |
| C2 | 11 | 179 | 17.3% | 11 / 179 / 17.3% | **MATCHES** |
| C3 | 7 | 104 | 10.0% | 7 / 104 / 10.0% | **MATCHES** |
| C4 | 3 | 29 | 2.8% | — | |
| C5–C9 | 2 each | 24, 29, 24, 29, 27 | 2.3–2.8% | — | |

**R3 satisfied with no discrepancy.** A figure computed before the restoration
gap reproduces after it — a useful datum about the archive's reliability, given
E6's finding that the pool itself could not be rebuilt.

---

## 2. Opening eligibility is a SIZE constraint, not a provenance one

Under two drifts the opening move must determine `base_C`, `d1` and `d2`
together — three unknowns, so **three anchors inside one component** (FR107).
Tested by planted-truth simulation rather than by inspecting coefficients (R2):

```
components that CAN open : C1, C2, C3, C4
components that CANNOT   : C5, C6, C7, C8, C9
```

The five two-glyph components are ineligible **because three anchors do not fit
in two glyphs**, not because they are `d1`-blind. A two-glyph component admits
at most one pair-difference, which is the `k = 2` case FR107 measured: seventeen
survivors, never one.

**Consequence for acquisition:** the opening must land in C1, C2, C3 or C4.
Witness opening triples, verified to leave exactly one `(d1, d2)`:

```
C1: (5, 27, 50)      C2: (13, 23, 25)      C3: (16, 42, 73)
```

---

## 3. The corrected cumulative table

Opening with the largest eligible component (C1) at three anchors, then one
anchor per remaining component taken by decreasing yield:

| anchors | glyphs | positions | exposure | FR54's one-drift stage |
|---:|---:|---:|---:|---|
| **3** | 25 | 323 | **31.2%** | 2 anchors |
| 4 | 36 | 502 | 48.5% | 3 |
| 5 | 43 | 606 | 58.5% | 4 |
| 6 | 46 | 635 | 61.3% | 5 |
| 7 | 48 | 664 | **64.1%** | 6 (63.6%) |
| 8 | 50 | 693 | **66.9%** | 7 (66.4%) |
| 9 | 52 | 720 | **69.5%** | 8 (68.7%) |
| 10 | 54 | 744 | **71.8%** | 9 (71.5%) |
| **11** | 56 | 768 | **74.1%** | 10 |

**Total: 11 anchors for 56 glyphs and 74.1%**, where FR54 priced 10.

---

## 4. NEW — FR54's tail ordering was suboptimal, independently of the drift

Compare the two curves stage for stage (my anchor *a* against FR54's *a−1*).
The first four stages agree exactly. **The middle four do not**, and the
difference has nothing to do with the two-drift correction:

FR54's published increments after C3 run `2.8, 2.3, 2.8, 2.3, 2.8, 2.6` — the
five two-glyph components taken in **index order** (24, 29, 24, 29, 27
positions). Taken by **decreasing yield** (29, 29, 27, 24, 24) the curve rises
faster:

```
FR54 stage 6 : 63.6%        corrected : 64.1%   (+0.5)
FR54 stage 7 : 66.4%        corrected : 66.9%   (+0.5)
FR54 stage 8 : 68.7%        corrected : 69.5%   (+0.8)
FR54 stage 9 : 71.5%        corrected : 71.8%   (+0.3)
```

Endpoints are identical, as they must be — the gain is entirely mid-curve, and
matters only to an acquirer who stops early. Small, but it is a genuine
correction to a published ordering and FR54's own thesis was that *"a programme
acquiring anchors opportunistically rather than by this ordering will spend
considerably more for the same exposure."* The same argument applies to FR54's
own tail.

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| FR54 per-component yields | published pre-restoration | **reproduced exactly** on canonical machinery |
| Opening move | 3 anchors (FR107), component unspecified | **must land in C1–C4**; C5–C9 are too small to open |
| Reason for ineligibility | predicted: `d1`-blindness | **size** — no component is `d1`-blind |
| Total anchor count | 11 (FR107, inferred) | **11, verified** with the full cumulative table |
| FR54 tail ordering | authoritative | **suboptimal** — index order, not yield order; up to +0.8 points mid-curve |
| Opening targets | unspecified | witnesses given: C1 (5,27,50), C2 (13,23,25), C3 (16,42,73) |

---

## 6. Model status

384 relations over 56 glyphs; injectivity clean; exposure 74.1%; components
[25, 11, 7, 3, 2, 2, 2, 2, 2] ratio-invariant. Alphabet [56, 83], floor 56.
**Acquisition: 11 anchors, opening with three in C1–C4 spanning ≥2 blind
clusters.** Cumulative: 27.16 billion candidates, zero survivors.

---

## 7. Horizon

1. **Write the single acquisition specification.** Every piece now exists and
   is verified: component ordering and yields (this cycle), the three-anchor
   opening and its eligibility (this cycle, FR107), blind clusters to avoid
   (FR106), witness triples (this cycle), and what the anchors deliver
   (FR46/FR54). It is spread across six reports and should be one document.
   This is the last unexecuted item on the acquisition side.
2. **Audit remaining figures for reused gauges** (FR107 horizon 3). Untouched.
   Anything computed "at drift 1" deserves the FR107 question.
3. **Nothing further is owed on anchor pricing.** The programme is specified;
   what remains is acquisition itself, which this series cannot perform.
