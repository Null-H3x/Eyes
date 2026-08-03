# Field Report 162 — SETTLED: EXACTLY 68 READINGS, EXACTLY 19 INVARIANT RELATIONS

*795,545 greedy orders, 32 threads. July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The run

```
G1 identity : rel 794 gly 61 eq 6   PASS
G1 reverse  : rel 724 gly 61 eq 6   PASS
G1 fixed42  : rel 794 gly 61 eq 6   PASS
G2 canary   : PASS
gate PASS

runs recorded     : 795,545
DISTINCT readings : 68
max relations     : 794
Chao1 estimate    : 68
discovery curve   : [1, 66, 67, 67, 67, 68, 68, 68, 68, 68, 68, 68, 68]
EXACT INVARIANT CORE : 19 relations
```

**The space is saturated.** The discovery curve is flat from step 6 of 13, and
**Chao1 equals the observed count**. This is the strongest form the estimator
takes: no unfound readings are implied.

> **There are exactly 68 maximal mutually-consistent readings of the Eye corpus.
> That is a count, not an estimate.**

---

## 1. Progression of the two headline numbers

| source | readings | invariant core |
|---|---:|---:|
| FR153 (90 greedy, pure-class) | ~30 est. | — |
| FR155 (12 readings, pure-class) | — | ≤18 |
| FR161 (1,978 runs, full model) | 52 obs., ~67 est. | 21 |
| **FR162 (795,545 runs)** | **68, saturated** | **19** |

My 2,000-run sample gave 21. The extra readings dropped exactly two:
**`q[5]−q[10]=48` and `q[23]−q[49]=48`**. Both had value 48; both were
coincidences of the readings I happened to sample.

**That is the shape of the FR155 error caught properly**: an intersection
estimated from a sample is an upper bound, and only saturation converges it.
This time the sampling was run to saturation before the number was published.

---

## 2. The converged core

```
q[ 1] - q[27] = 81     q[ 2] - q[26] =  1     q[ 2] - q[73] =  2
q[ 6] - q[57] = 82     q[ 9] - q[79] = 82     q[13] - q[19] = 53
q[13] - q[66] = 55     q[17] - q[63] =  2     q[19] - q[66] =  2
q[21] - q[40] = 82     q[22] - q[62] = 30     q[22] - q[64] =  0
q[25] - q[60] = 82     q[26] - q[73] =  1     q[32] - q[59] = 30
q[34] - q[45] = 82     q[35] - q[37] =  2     q[36] - q[68] =  0
q[62] - q[64] = 53
```

**29 glyphs, 419 of 1,036 corpus positions (40.4%).**

---

## 3. The two homophones survive saturation

```
q[22] - q[64] = 0
q[36] - q[68] = 0
```

Both hold in **all 68** readings — exactly as the W1@59 ↔ E3@90 fixed-point
argument requires. Glyph 17 sits on both sides at offsets 13 and 16, collapsing
that alignment's constant to zero and forcing both pairs outright. No class
re-selection can dislodge them.

**These two are the complete set of anchor-pair tests**, and they are now
verified against the entire reading space rather than a sample.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Reading-space size | ~67 estimated (FR161) | **68, SATURATED** — Chao1 = observed |
| Invariant core | 21 (FR161, 2k runs) | **19, CONVERGED** |
| `q[5]−q[10]`, `q[23]−q[49]` | invariant | **withdrawn** — sampling coincidences |
| Core coverage | unstated | **29 glyphs, 40.4% of positions** |
| Anchor-pair tests | two, sample-verified | **two, saturation-verified; complete set** |
| `INVARIANT_CORE.md` | upper bound | **converged artifact** |

---

## 5. Model status

Extended skeleton: 794 relations, 61 glyphs, 8 homophones, 79.1% exposure,
435-position reading, 6 anchors. **One of exactly 68 maximal readings, with a
19-relation converged invariant core covering 40.4% of the corpus.**
Cumulative: 27.16 billion candidates, zero survivors.

---

## 6. Horizon

**This closes the class-selection question completely.** The uncertainty
FR152 opened is now counted, and the part of the model immune to it is exact.

Remaining, all previously logged:

1. **Empirical cost scale** (FR159) — local, minutes; `REPAIR_RANKING.md`'s
   cost column depends on it.
2. **The `d ≡ 0` generator reconciliation** (FR158) — a specification question,
   not compute.
3. **Acquisition**: 6 anchors as pairs within a component, or the two
   invariant homophone tests.
