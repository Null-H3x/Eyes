# Field Report 159 — CLAIM 2 VERIFIED IN PREMISE, REVERSED IN CONCLUSION: THE E1@68 PRICE WAS TOO HIGH, NOT TOO LOW

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The claim

> *"E1@68 isn't a 9-window — extend the pair E1@53 ↔ E2@65 and the column map
> stays a bijection for 25 symbols, so the 10⁻⁵·⁸ price is computed for the
> wrong object."*

---

## 1. The premise verifies exactly

```
off  E1pos E2pos   E1   E2
  0     53    65   24   61
 ...
 24     77    89   51   18
 25     78    90   41   72   BREAKS: y=72 already <- 11, now 41

bijective for 25 consecutive positions (E1 53..77, E2 65..89)
distinct symbols in the map : 22
```

**Precisely 25, as stated.** East 1@68 falls at offset 15, inside the span. The
isomorph pattern over it matches on both sides:
`...............A.B.CB.AC.`

---

## 2. But the pricing goes the other way

The 25-window carries **k = 3 assertions** — the same as the 9-window, because
the extension adds sixteen positions and no new repeated letters. By the FR128
formula the cost is unchanged at 5.76.

**So I measured the bijection directly instead**, over all 928,332 window pairs
in the corpus:

```
bijective-run length distribution:
   L=34:   2      L=28:  38      L=25: 102
   L=33:  10      L=27:  40      L=24: 176
   L=30:  14      L=26:  76      L=23: 410

pairs with a bijective run >= 25 : 322  (0.0347%)
chance of a 25-long bijection    : 3.47e-04
   as a cost                     : 3.46
FR128's price for the site       : 5.76
```

> **A 25-position bijective column map is about 200× MORE common than FR128's
> price implies. The correct cost is ~3.46, not 5.76.**

**The claim is right that the price is for the wrong object, and wrong about the
direction.** FR128 treated the site as a k=3 pattern match at 83⁻³; measured
against what the corpus actually produces, long bijective runs are far more
frequent than the independence assumption predicts — because instances are
nested and correlated, exactly as FR136 found for classes.

---

## 3. What this does to the repair ranking

FR128 ranked 62 repairs by `−log₁₀ P(dropped instances are chance)` using the
`k·log₁₀(83)` formula throughout. **If that formula overprices a 25-bijection by
2.3 orders of magnitude, it overprices other sites too, and the ranking is
built on it.**

The ranking's *conclusion* survives for a different reason: FR150 found **East
3@101 is inert** — keeping or dropping it changes nothing under the extended
skeleton — so the fork the ranking was built to adjudicate has dissolved. But
**`REPAIR_RANKING.md`'s cost column should be read as indicative, not
calibrated.**

**A third pricing error in the same series**: FR127 used the wrong objective
(coverage), FR128 corrected it to evidential cost, and FR159 now finds that cost
mis-calibrated because it assumed independence.

---

## 4. Longest bijective run in the corpus

```
East 4@68 x West 4@71 : 34 positions
```

Longer than the E1/E2 span and not previously noted. Worth checking whether it
is in the class inventory.

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| E1@53 ↔ E2@65 bijection | unknown | **verified: exactly 25 positions** |
| E1@68 as a 9-window | FR128's object | **sits at offset 15 of a 25-span** |
| Price of the site | 5.76 | **~3.46 measured** — FR128 overpriced by ~200× |
| `k·log₁₀(83)` cost formula | calibrated | **assumes independence; instances are nested** |
| `REPAIR_RANKING.md` | ranked by cost | **cost column indicative, not calibrated** |
| Longest corpus bijection | unknown | **34**, East 4@68 × West 4@71 |

---

## 6. Model status

Unchanged in content: extended skeleton, 794 relations, 61 glyphs, 8 homophones,
79.1% exposure, 435-position reading, 6 anchors, ~30 maximal readings, 18
invariant relations. **The repair ranking's cost scale is downgraded to
indicative.** Cumulative: 27.16 billion candidates, zero survivors.

---

## 7. Horizon

1. **Re-derive the cost scale empirically** rather than by the independence
   formula — measure how often each pattern class arises in the corpus, as done
   here for the 25-bijection.
2. **Check whether East 4@68 × West 4@71 (34 positions) is in the class
   inventory**; if not, the enumeration is missing its longest structure.
3. **Reconcile the synthetic generators** (FR158, still open) — the `d ≡ 0`
   inference depends on it.
