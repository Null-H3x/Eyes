# Field Report 120 — THE CONSUMERS ARE BUILT, THE BLIND SWEEP IS EXHAUSTED, AND THE GAP IS STRUCTURAL

*Instrument: `eyehypo.py` (5/5 gate). Artifact: `HYPOTHESIS_CATALOG.md`.*
*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. What was built

Two consumers for hypotheses stated in the same currency as FR119's artifact —
plaintext **equality structure** — so nothing need be assumed about encoding:

- **PATTERN**: `A.B..B.A` at (message, start). Letters mark positions asserted
  equal; dots assert nothing.
- **GRAMMAR**: a predicate over a reading's decrypted stream.

Rather than hand-pick placements, each shape is tested at **every valid
placement**: 32 shapes × **5,232 placements**, plus 34 grammars, against all
17 readings.

---

## 1. Coverage is the binding constraint, and it excludes a third of the corpus

The 461 decrypted positions lie **entirely in T2 and T3**. East 1, West 1 and
East 2 have **zero** coverage — FR102's finding that T1 is unbridged after
repair A, surfacing as a practical limit on where anyone can test anything.

66 runs of ≥3 consecutive covered positions exist; the longest is 12
(East 4, 59–70). Full map in `HYPOTHESIS_CATALOG.md` §0.

---

## 2. Result: nothing discriminating, and the reason is arithmetic

**Patterns: 0 discriminating of 5,232 placements.** Chance calibration against
shuffled readings: **also 0 of 5,232.** No false positives, no signal.

**The discrimination gap.** A pattern asserting *k* equalities is satisfied by
chance at ≈83⁻ᵏ; across *P* placements and 17 readings the expectation is
17·P·83⁻ᵏ:

| shape | k | placements | expected chance hits | observed |
|---|---:|---:|---:|---:|
| `AA`, `A.A`, `A..A` | 1 | ~290 | **59.4** | 11–59 |
| `ABBA`, `ABAB` | 2 | 124 | 0.31 | 0–1 |
| `ABCABC`, `ABCCBA` | 3 | 47 | **0.001** | 0 |

> **Single-assertion shapes occur at exactly the chance rate and cannot
> discriminate 17 readings. Multi-assertion shapes never occur — which is also
> what chance predicts, so their absence is NOT evidence.**
>
> **A blind scan cannot win.** Any pattern strong enough to select one reading
> is too strong to arise by chance, and none is present.

This is a structural limit, not a shortfall of the catalog. It also says
something useful: **the value of a hypothesis here is entirely in knowing
*where* to place it**, which is outside information the corpus cannot supply.

---

## 3. Grammars: near-total refutation, two survivors

| grammar | satisfied | corroborates |
|---|---|---|
| bounded-window 20–70 | **0/17** | FR100's width-75 minimum |
| period 2–12 | **0/17** | FR56/FR91 (no periodicity 2–90) |
| no-repeat-within 2–12 | **0/17** | values do repeat at short range |
| at-most-K values, K ≤ 80 | **0/17** | inventory > 80 in every reading |
| monotone-blocks-6, -8 | 0/17 | |
| **monotone-blocks-4** | **5/17** | weakly discriminating |
| **value-82-absent** | **2/17** | weakly discriminating |

Three independent lines — FR100's width, FR56/FR91's aperiodicity, FR39's
inventory — are reproduced here from a completely different direction, on
materialised readings rather than statistics. **That is corroboration of the
model, obtained as a by-product.**

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Hypothesis consumers | none | **built** — `eyehypo.py`, pattern + grammar, auto-placement |
| Crib-testable territory | unstated | **T2/T3 only**; T1 has zero coverage |
| Blind pattern search | untried | **exhausted** — 5,232 placements, 0 discriminating, chance-matched |
| Discrimination gap | unrecognised | **structural**: k≥2 is never satisfied, k=1 never discriminates |
| Grammar families | untried | 34 tested; all but two refuted by every reading |
| Where value now lies | unclear | **targeted hypotheses with outside information**, k≥3, named location |

---

## 5. Model status

Unchanged: 384 relations over 56 glyphs; 74.1% exposure; 17 ratios; conditional
on the progressive form (FR118) and repair A (FR110). Cumulative: 27.16 billion
candidates, zero survivors.

---

## 6. Horizon (constructive)

1. **Targeted hypotheses.** The catalog is executable and waiting: a phrase at
   a named offset, a record structure anchored to a stated period, or a
   cross-message assertion about shared passages. `k ≥ 3`, in covered
   territory, for a stated reason.
2. **Extend coverage past 44.5%.** Twenty-nine block groups remain unlinked and
   T1 is entirely dark. Linking even one T1 block would open three messages to
   testing.
3. **`monotone-blocks-4` and `value-82-absent`** partially discriminate. Both
   are weak and neither is claimed — but they are the only two survivors of 34,
   and worth re-examining if a reason to prefer either appears.
