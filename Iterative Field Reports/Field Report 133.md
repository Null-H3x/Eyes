# Field Report 133 — NO INTERNAL REPEAT STRUCTURE SURVIVES, AND THE ONE RUN THAT DOES IS THE OPENING

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. CHALLENGE I kills the distance clusters before measurement

FR132 noted the 41 within-message equal pairs cluster at distance 30 (7 pairs)
and 35 (6 pairs) — a periodicity that would be a real plaintext finding.

**Split by block membership first, per FR30:**

```
within-message equal pairs : 41
   WITHIN-block (geometry, no information) : 41
   CROSS-block (informative)               :  0
```

> **All 41 are within-block.** FR30 proved within-block coincidences are
> drift-independent — fixed by the Δ geometry and carrying no plaintext
> information. **The distance-30 and -35 clusters are entirely geometric.**

Twelfth horizon item to die on inspection rather than measurement, and the
cheapest: no null was needed, because there was nothing to test.

---

## 1. Where the information actually is

Cross-message pairs are necessarily cross-block, so they are the informative
set:

```
cross-message equal pairs : 191
   ASSERTED by an alignment : 12    (model input -- consistency check)
   NOT asserted (DISCOVERED): 179
```

**The model reproduces the 12 co-plaintext cells it was given** — a clean
consistency result — and outputs 179 equal pairs nobody put in.

Distribution across message pairs:

| pair | discovered |
|---|---:|
| East 2 / East 3 | 23 |
| West 1 / East 3 | 21 |
| East 1 / East 2 | 18 |
| East 1 / West 1 | 16 |
| East 1 / East 3 | 15 |

---

## 2. The discovered pairs do not form passages

If the messages shared text beyond the known alignments, discovered pairs would
line up in **consecutive runs at a fixed offset**. They do not:

```
consecutive runs (>=2) among 179 discovered pairs : 1
   East 1  2-4  ==  West 1  2-4   (length 3)
```

**One run, three long, and it is the message opening** — the universal head at
positions 1–2 plus one more. Everything else is scattered: 11 of 179 at offset
zero, the rest spread across 60-odd distinct offsets with no offset carrying
more than four pairs.

> **There is no undiscovered shared passage in the determined region.** 179
> equal pairs, one run, and that run is the opening everyone already knew about.

---

## 3. What the corrected reading establishes

Taken with FR132, the picture is consistent and uncomfortable:

- **No within-message repeat structure at all** — all 41 candidates are
  geometry.
- **No cross-message passage structure** beyond the openings and the twelve
  alignment cells the model was given.
- **179 scattered equal pairs**, at a rate consistent with 191 positions drawn
  over ~72 distinct values.

This is the sixth independent line reaching the same place: FR39 (no
language coincidence structure), FR41/42 (local avoidance was geometry),
FR115 (coincidence elevation at every candidate), FR126 (no cross-block
short-range excess under the correct null), FR132 (nearest repeat at distance
11, all geometric), and now FR133.

**The plaintext, where this project can see it, has no repeat structure of any
kind.**

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Distance-30/35 clusters | suggestive (FR132) | **geometry** — all 41 pairs within-block, zero informative |
| Long-range pairs as crib targets | nominated (FR132) | **withdrawn** — they carry no plaintext information |
| Cross-message discovered pairs | unmeasured | **179**, forming exactly **one** run of length 3 (the opening) |
| Undiscovered shared passages | open | **none** in the determined region |
| Model consistency | — | reproduces all 12 asserted co-plaintext cells |

---

## 5. Model status

Unchanged. Relative-plaintext reading: 191 positions (18.4%), 7 of 9 messages,
one free constant, drift-invariant, zero conflicts. Cumulative: 27.16 billion
candidates, zero survivors.

---

## 6. Horizon

1. **Measure the honest word-crib power against the corrected reading.**
   FR132 predicted it is near zero; with no short-range repeats and 191
   scattered positions it should be measured, not assumed, and then the
   vocabulary route can be closed or kept on evidence.
2. **Re-base or retire the stale tooling.** `eyehypo.py`, `eywordsC.py` and
   `eyedouble.py` consume withdrawn readings.
3. **The acquisition programme is untouched by all of this** — it depends on
   the skeleton, not the reading — and remains the only route that does not
   run into the plaintext's featurelessness.
