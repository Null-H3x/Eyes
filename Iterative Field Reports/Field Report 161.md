# Field Report 161 — THE INVARIANT CORE CONVERGES AT 21; A SIX-HOUR RUN BUYS NOTHING

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. Measured before spending

A 2,500-order run of `eyemax` was executed locally (1,978 reaching the
700-relation floor) specifically to price the offered compute before using it.

```
runs recorded     : 1,978
DISTINCT readings : 52
max relations     : 794
frequency profile : [494, 226, 216, 140, 119, 108, 80, 72, 65, 52, ...]
Chao1 estimate    : 67
discovery curve   : [1, 29, 36, 40, 45, 45, 47, 49, 49, 49, 49, 50, 52]
```

**The reading space is larger than FR153 estimated** — 52 found against a
~30 Chao1 from 90 greedy runs, now revised to ~67. FR153's estimate was low
because it sampled the pure-class system; this is the full model with the
FR32/33 passage seeded.

---

## 1. But the core converges, and that is the deliverable

```
readings  invariants
       1         724
       2         131
       5         118
      12          57
      20          51
      25          40
      35          21
      40          21
      45          21
      50          21
      52          21
```

> **Converged at 21 relations after ~35 readings, and flat across the next
> seventeen.** More sampling finds more *readings*; it does not shrink the
> *core*.

**Recommendation: run 1,000,000 orders (~37 minutes), not 10,000,000 (~6
hours).** The 10× buys additional readings that no longer affect the answer.
The 1M run is still worth doing: Chao1 says ~15 readings remain unfound, and
confirming the core survives them is the point.

---

## 2. The converged core

```
q[ 1] - q[27] = 81     q[ 2] - q[26] =  1     q[ 2] - q[73] =  2
q[ 5] - q[10] = 48     q[ 6] - q[57] = 82     q[ 9] - q[79] = 82
q[13] - q[19] = 53     q[13] - q[66] = 55     q[17] - q[63] =  2
q[19] - q[66] =  2     q[21] - q[40] = 82     q[22] - q[62] = 30
q[22] - q[64] =  0     q[23] - q[49] = 48     q[25] - q[60] = 82
q[26] - q[73] =  1     q[32] - q[59] = 30     q[34] - q[45] = 82
q[35] - q[37] =  2     q[36] - q[68] =  0     q[62] - q[64] = 53
```

**21 relations**, up from FR155's 18 — and the two counts are not comparable.
FR155 measured the **pure-class** system (496 relations); this measures the
**full model** with the passage seeded (794). Different objects. This is the one
that describes the standing model.

---

## 3. The community's fixed-point analysis is confirmed at scale

Exactly two invariant relations are homophones:

```
q[22] - q[64] = 0
q[36] - q[68] = 0
```

**Both survive all 52 readings**, which is what the W1@59 ↔ E3@90 fixed-point
argument predicts: a single alignment with glyph 17 on both sides forces them
outright, so no amount of class re-selection can dislodge them.

**Two invariant homophones, and no others.** That is the complete set of
anchor-pair tests, and it holds regardless of which of ~67 readings is correct.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Reading-space size | ~30 (FR153, pure-class) | **~67** for the full model; 52 observed |
| Invariant core | ≤18, shrinking (FR155) | **21, CONVERGED** at ~35 readings |
| FR155 vs FR161 counts | apparent conflict | **different systems** — pure-class vs full model |
| Recommended run | 10⁶ or 10⁷ | **10⁶ (~37 min)**; 10⁷ buys nothing |
| Invariant homophones | two, from FR158's argument | **confirmed empirically across 52 readings** |

---

## 5. Model status

Extended skeleton: 794 relations, 61 glyphs, 8 homophones, 79.1% exposure,
435-position reading, 6 anchors. **One of ~67 maximal readings, with a
21-relation converged invariant core.** Cumulative: 27.16 billion candidates,
zero survivors.

---

## 6. Horizon

1. **Run `bash run_maxset.sh 1000000 32`** — 37 minutes, confirms the core
   against the ~15 unfound readings.
2. **If the core holds at 21, `INVARIANT_CORE.md` becomes a converged artifact**
   rather than an upper bound, and it is the thing to hand any external solver.
3. **Do not run 10⁷.** Measured, not assumed.
