# Field Report 125 — ZERO AT k≥3, AND A CROSS-BLOCK EXCESS THAT SURVIVES ITS NULL

*Instrument: `eywordsC.py` (5/5 gate). July 2026. Cycle: EYESPIRAL-C.*

---

## 0. What changed since FR121

FR121 tested vocabulary against 17 candidate readings over 461 positions: a hit
only narrowed the candidate set and chance was 17× inflated. Repair C
(FR122–124, audited 7/7) gives **one** structure over **686** positions across
**all nine** messages, so a hit is decisive rather than discriminating and
chance drops by 17×.

Vocabulary expanded to 130 words — Noita nouns, Finnish cosmology, knowledge
terms, function words and doubles, numbers, Kalevala names, Hermetic
vocabulary, English equivalents. **18 carry k ≥ 3.**

---

## 1. The headline: still zero

```
k>=3 words          : 18
hits                : 0
false-positive expectation (summed) : 0.002
shuffled null, k>=3 : 0
mean POWER          : 9.9%   (FR121 repair A: 6.3%)
```

| word | k | testable | power | hits |
|---|---:|---:|---:|---:|
| KALEVALA | 3 | 147 | **15.2%** | 0 |
| MARJATTA | 3 | 146 | 15.1% | 0 |
| KAIKKI | 3 | 147 | 14.9% | 0 |
| MAAILMA | 3 | 139 | 14.2% | 0 |
| YLHÄÄLLÄ | 4 | 103 | 10.6% | 0 |
| TODELLINEN | 3 | 99 | 10.4% | 0 |
| TOSITIETO | 4 | 69 | 7.2% | 0 |
| LEMMINKÄINEN | 5 | 39 | 4.2% | 0 |

**Power rose 6.3% → 9.9%, so ~90% of the hypothesis space is still untested.**
The vocabulary is not refuted; it is mostly unexamined, and the reason remains
coverage fragmentation rather than word quality.

---

## 2. An excess that survived three attempts to kill it

The 112 words with k < 3 produced **531 hits against 305 expected** — the
*opposite* of FR121's 44%-of-chance deficit, and large enough to demand the
FR41/FR42 treatment.

**Attempt 1 — flat shuffle** (the wrong null; destroys block geometry):
mean 340.2. Excess survives.

**Attempt 2 — within-block shuffle** (preserves block membership and value
multisets): mean 282.6, **z = +9.9**. Excess survives.

**Attempt 3 — the decisive split.** FR30 proved within-block coincidences are
*drift-independent*: they are fixed by the Δ geometry and carry no plaintext
information. Only **cross-block** coincidences depend on the model's free
constants. Splitting:

```
REAL   within-block 122        cross-block 409
NULL   within-block  80.6±47.0 cross-block 207.6±41.4
z      within-block +0.88      cross-block +4.87
```

> **The within-block component is at chance (z = +0.88) — correctly, since it
> is geometry. The excess lives entirely in the CROSS-BLOCK component, at
> z = +4.87, which is exactly where plaintext information is supposed to be.**

This is the first short-range plaintext-repeat signal in this series to survive
a geometry-preserving null. **FR41 made a claim of this shape and FR42 withdrew
it precisely because the excess vanished when the geometry was preserved.**
Here the geometry-carrying half is flat and the informative half is not.

---

## 3. Why it is logged as WATCH-GRADE, not claimed

Reasons for caution, stated before anyone builds on it:

1. **Only five null draws.** z = +4.87 on 5 draws is suggestive, not
   established; the sd is poorly estimated.
2. **k < 3 patterns cannot discriminate readings**, so this is a claim about
   *the plaintext*, not evidence for repair C or any drift.
3. **Aggregated across 112 heterogeneous words** of differing span and
   assertion count — the FR40 multiplicity problem in a new dress.
4. **The structure is conditional** on repair C, which is conditional on
   E1@68 being spurious, non-bijectivity, and the progressive form (FR118).

**PRE-REGISTERED for a future cycle:** cross-block short-range coincidence
excess, geometry-preserving within-block null, ≥500 draws, one-sided, α = 0.01.
If it survives that, it is a genuine plaintext property — short-range repeat
*enrichment* — and the first positive structural statement about the plaintext
this project has produced.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Vocabulary batch | 17 readings, 461 positions | **1 structure, 686 positions, all nine messages** |
| Mean k≥3 power | 6.3% | **9.9%** |
| k≥3 hits | 0 | **0** — vocabulary still ~90% unexamined |
| k<3 hit rate | 44% of chance (FR121, repair A) | **174% of chance** (repair C) |
| The excess | — | survives flat AND within-block nulls; **isolated to the cross-block component**, z = +4.87 |
| Within-block coincidences | FR30: drift-independent | **confirmed empirically**: z = +0.88, flat as predicted |

---

## 5. Model status

Unchanged. Repair A: 384 relations, 56 glyphs, 17 ratios, 44.5%. Repair C: 409
relations, 57 glyphs, drift forced, 66.2%, one homophone. Both conditional on
the progressive form. Cumulative: 27.16 billion candidates, zero survivors.

---

## 6. Horizon

1. **Run the pre-registered cross-block test properly** — 500+ draws, the
   geometry-preserving null, one-sided at α = 0.01. It is cheap and it is the
   first plaintext signal to get this far.
2. **If it holds, it is a grammar.** "Short-range repeat enrichment" is exactly
   the kind of predicate `eyehypo.py` consumes, and a grammar satisfied by the
   plaintext is a constraint every future crib must respect.
3. **Coverage remains the limit on word testing.** 9.9% power means the
   vocabulary route stays weak until coverage or contiguity improves further.
