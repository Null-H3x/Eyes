# Field Report 122 — REPAIR C: ONE HOMOPHONE BUYS THREE MESSAGES AND 20 POINTS OF COVERAGE

*Instrument: coverage/consistency trade analysis on the canonical build.*
*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. Why coverage was attacked

FR121 established the binding constraint with a number: word-crib power is
**testable placements / possible placements**, and at 44.5% fragmented coverage
the mean across fifteen k≥3 candidate words is **6.3%**. Zero hits left ~94% of
the hypothesis space untested. Raising coverage is therefore not housekeeping —
it multiplies the value of every hypothesis anyone proposes.

---

## 1. Diagnosis: T1 is one alignment from readable

Block-group composition under repair A:

```
group 1: 34 blocks, 461 positions  -- East 3, East 4, East 5, West 2, West 3, West 4
group 2: 15 blocks, 216 positions  -- East 1, East 2, West 1        <-- ALL OF T1
```

**T1 is fully linked internally — 216 positions across all three messages — and
simply not connected to the main group.** Only one atlas class spans T1 and
another triplet:

```
#M-  instances: East 1@40, East 1@68, West 1@40, West 1@70, East 2@45,
                East 2@80  (all T1)  +  East 3@101 (T2)   <-- DISCARDED
```

**East 3@101 is the sole bridge, and every repair since FR25 discards it.**

---

## 2. Measurement: what the bridge is worth

| pool variant | relations | glyphs | forced equalities | coverage | T1 |
|---|---:|---:|---:|---:|---|
| repair A (drop E3@101 + E1@68) | 384 | 56 | **0** | **44.5%** | no |
| **drop E1@68 only** | **409** | **57** | **1** | **65.3%** | **yes** |
| drop E3@101 only | — | — | — | 44.5% | contradictory |
| full pool | — | — | — | 65.8% | contradictory |

> **Keeping East 3@101 and dropping only East 1@68 gives MORE relations, MORE
> glyphs, and 20.8 more points of coverage, at the cost of exactly ONE forced
> equality: `q[36] = q[68]`.**

Coverage rises 461 → **677 positions**, and all nine messages join the linked
group.

---

## 3. The finding: a third repair nobody enumerated

FR25 posed the fork as A (drop E3@101 + E1@68) versus B (drop E3@101 + E4@51).
**Both discard East 3@101.** The option of discarding *only* E1@68 was never
on the table — and attributing the six false equalities shows why it should
have been:

```
full pool          : 6 equalities (contradictory with the passage)
drop E3@101        : contradictory
drop E1@68 ONLY    : 1 equality  [(36, 68)]
drop BOTH          : 0 equalities
```

**East 1@68 carries five of the six; East 3@101 carries one.** FR25 framed the
repair around East 3@101 because every *minimal core* contains it — true, and
compatible with East 1@68 carrying the arithmetic weight. The framing followed
the core structure and never asked which instance was the cheaper thing to
lose.

**Call it repair C: drop East 1@68 only, accept `q[36] = q[68]` as a homophone
pair.**

- **Cost:** one homophone pair. The alphabet becomes 82 rather than 83, and
  strict bijectivity is given up.
- **Gain:** +25 relations, +1 glyph, +20.8 coverage points, and **three
  messages that were entirely dark.**

It also strengthens the independent case against East 1@68 — FR2's structural
anomaly and FR27's embeddedness both pointed at it, and FR110 showed
embeddedness was atlas nesting rather than evidence. Repair C rests on
arithmetic weight instead: **East 1@68 is where the contradictions actually
live.**

---

## 4. What it costs epistemically, stated plainly

Repair C **is not free**, and the cost is not the one homophone:

- **Bijectivity is abandoned.** FR118 and the alphabet-size work established
  injectivity is load-bearing for the 17-ratio narrowing — *all 65 rejected
  ratios fail on injectivity, none on linear contradiction*. Accepting one
  homophone does not by itself reopen all 82 ratios, but the principle that
  justified the filter is weakened and the narrowing must be re-derived.
- **The two-drift row form no longer applies.** The bridge that buys the
  coverage is precisely a T1↔T2 straddling pair, so `d1` and `d2` are forced
  equal by it. That is not a defect — it *resolves* FR102's open question — but
  it means repair C and the two-drift model are alternatives, not companions.

**Repair C therefore trades the drift-ratio narrowing for coverage.** Which is
worth more depends on whether the next move is reading the corpus or pinning
the drift.

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| **Repair fork** | A vs B vs AB, all dropping E3@101 | **repair C added**: drop E1@68 only |
| Why T1 is dark | unexplained | **East 3@101 is its sole bridge**; every prior repair discarded it |
| Cost of repair A | "discards two well-supported instances" | **+ 216 positions and three whole messages** |
| The six false equalities | attributed to E3@101 (minimal cores) | **E1@68 carries five; E3@101 carries one** |
| Maximum coverage | 44.5% | **65.3% under repair C**, 65.8% full pool |
| Drift equality (FR102) | open | **forced** under repair C — the bridge is a T1 straddle |

---

## 6. Model status

Standing model unchanged (repair A): 384 relations, 56 glyphs, 74.1% exposure,
44.5% linked coverage, 17 ratios. **Repair C is now a live alternative**: 409
relations, 57 glyphs, 65.3% linked coverage, one homophone, drift equality
forced. Cumulative: 27.16 billion candidates, zero survivors.

---

## 7. Horizon (constructive)

1. **Build the repair-C readings.** 677 positions across all nine messages is
   a 47% larger artifact than FR119's, and it would take mean word-crib power
   from 6.3% toward ~15-20%. This is the direct payoff and the obvious next
   build.
2. **Re-derive the ratio narrowing under repair C.** Injectivity minus one
   permitted collision is a weaker but non-empty filter; how many ratios
   survive it is computable and decides whether repair C costs the narrowing
   entirely or only partly.
3. **Repair C makes the fork testable by acquisition.** It forces `d1 = d2`,
   while repairs A and B leave the ratio free. **A recovered ratio ≠ 1 refutes
   repair C outright** — the sharpest falsification the fork has ever had.
