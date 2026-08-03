# Field Report 160 — THE MAXIMAL-SET HARNESS: GATED, SHIPPED, AND IT CAUGHT ITS OWN FIRST GATE

*Instruments: `eyemax.c`, `run_maxset.sh`, `eyemaxred.py`. July 2026. Cycle: EYESPIRAL-C.*

---

## 0. What compute is worth spending on

Four candidates, priced before building:

| candidate | verdict |
|---|---|
| **Maximal-set enumeration** | **worth it** — converts the headline uncertainty from an estimate to a count, and the invariant core from an upper bound to a converged number |
| Empirical cost scale (FR159) | not compute-bound — a census over ~10⁶ window pairs runs in minutes locally |
| The `d ≡ 0` question | not compute-bound — a specification disagreement about a generator |
| Re-opening the sweep | **do not** — 27.16B burned, no new generator family with a prior; FR99 doctrine |

**The invariant core is what an external solver actually checks a candidate
alphabet against.** It is currently "at most 18", estimated from 12 sampled
readings, and shrinks as sampling grows. Making it exact is the highest-value
thing compute can buy here.

---

## 1. The cheap check first

The 34-position bijection `East 4@68 × West 4@71` found in FR159 **is** in the
class inventory, at L=34 with k=7 — the surprise-10.84 class. The enumeration is
not missing its longest structure.

---

## 2. The gate caught the harness

First gate compared C runs against Python reference vectors by **seed number**.
It failed:

```
G1 seed 1: rel 724 gly 61 eq 7  (want 794 61 6)  FAIL
G1 seed 2: rel 794 gly 61 eq 6  (want 724 61 8)  FAIL
```

**The C was not wrong — the gate was.** C's xorshift and Python's Mersenne
Twister produce different shuffles from the same seed, so the comparison was
between different orders. The numbers were in the right range throughout.

Rewritten to **fixed, exported orders** — RNG-independent:

```
G1 identity : rel 794 gly 61 eq 6   PASS
G1 reverse  : rel 724 gly 61 eq 6   PASS
G1 fixed42  : rel 794 gly 61 eq 6   PASS
G2 canary   : PASS  (0 = 1 correctly rejected)
gate PASS
```

**This is the FR98 lesson working as intended**: a harness that cannot fail
reports success regardless. This one failed, was diagnosed, and now verifies
against a comparison that actually holds.

---

## 3. Throughput and the run

```
200 runs on 4 threads : 14 s   ->  ~14 runs/s/thread
32 threads            : ~450 runs/s
1,000,000 runs        : ~37 minutes
10,000,000 runs       : ~6 hours
```

**Recommended: `./run_maxset.sh 1000000 32`** — about 37 minutes, and enough to
saturate a space FR153 estimated at ~30. If the discovery curve is still
climbing at 10⁶, that itself is the finding: the space is far larger than
estimated.

Output is streamed as relation signatures; `eyemaxred.py` reduces it to the
distinct-reading count, the frequency profile, a Chao1 estimate, the discovery
curve, and **the exact invariant core**.

---

## 4. What the run will settle

- **The exact number of maximal readings** — currently ~30, a Chao1 estimate
  from 90 runs
- **The exact invariant core** — currently ≤18 and shrinking; this converges it
- **Whether `q[22]=q[64]` and `q[36]=q[68]` survive** at full sampling. FR158
  showed a single fixed-point alignment forces them, so they should — and if
  they do not, that alignment analysis is wrong

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| 34-position bijection | possibly missing from inventory | **present**, L=34 k=7 |
| Maximal-set count | ~30, Chao1 from 90 runs | **harness shipped** to settle it |
| Invariant core | ≤18, shrinking | **harness shipped** to converge it |
| Seed-matched cross-language gates | used here first | **invalid** — different RNGs; use fixed exported orders |

---

## 6. Model status

Unchanged: extended skeleton, 794 relations, 61 glyphs, 8 homophones, 79.1%
exposure, 435-position reading, 6 anchors, ~30 maximal readings, invariant core
≤18. Cumulative: 27.16 billion candidates, zero survivors.

---

## 7. Horizon

1. **Run `./run_maxset.sh 1000000 32`**, then `python3 eyemaxred.py maxset_out.txt`.
2. **Empirical cost scale** — local, minutes, and `REPAIR_RANKING.md`'s cost
   column depends on it.
3. **The `d ≡ 0` generator reconciliation** remains open and is not compute-bound.
