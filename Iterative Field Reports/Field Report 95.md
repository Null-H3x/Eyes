# Field Report 95 — THE RUNNER AUDITED: SIX BUGS, AND A FILTER THAT CAN PROVE IT WAS ALIVE

*Instrument: `eyerunner.py` (10-check startup gate, in-stream canaries, JSON export). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — the failure mode a long run cannot survive

The GPU queue's top items are multi-hour sweeps. The failure that matters is not a
crash — a crash is loud. It is a **filter that silently cannot fire**, which runs for
four hours and reports a clean null **indistinguishable from a real one**.

FR60 is the precedent: EyeStat's chi² pre-filter had zero discrimination at the
certified plaintext inventory, ran 34 billion seeds, and its "zero survivors" was
**silence, not evidence**. That mistake cost the project a month of GPU time and was
not caught for dozens of cycles.

The runner must therefore be able to **prove it was working**, not merely assert it.

---

## 1. Six bugs found

| # | bug | consequence |
|---|---|---|
| **B1** | `LGM(0)` silently remapped seed 0 → 1 | his `Next()` asserts `seed`; we were testing a stream he cannot produce. **Now skipped.** |
| **B2** | `int(seed) % M31` on init | his cast is `(long)seed` with no reduction, so seeds above 2³¹ diverge. **Now refused with an error** rather than silently testing a different stream. |
| **B3** | `if j > i: j = i` clamp | provably never fires (max `Next()` × 83 = 82.99999…), so a clamp **masks** a mistyped scale constant. **Now an assertion.** |
| **B4** | hits only printed | the filter uses 46 of 56 glyphs and is necessary-not-sufficient. **Hits now persisted in full** — generator, seed, direction, drift, permutation — for downstream verification. |
| **B5** | no in-stream positive control | the FR60 failure mode exactly. **Canaries added.** |
| **B6** | `fastrand` seeded with the raw value | `set_fastrand_seed` is `seed ^ 13 - 1`, which by C precedence is **`seed ^ 12`**. Carried from FR94. |

Two further bugs were introduced *while building the canary system* and caught by its
own tests:

- **Random base tuples are injective only ~0.05% of the time** — that *is* the packing
  constraint. Building canaries by random draw failed at 4 of 8. Fixed by finding valid
  packings once and reusing them.
- **Scale-invariance was applied incorrectly.** FR53 says `{d·b_c}` packs `{d·S_c}` —
  the **bases scale with the drift**. I scaled the Δ values and left the bases fixed, so
  only drift 1 produced valid canaries.

---

## 2. The canary mechanism, and proof that it works

Known-consistent alphabets are injected into the **live stream** at a configurable
rate. Every one must be caught; a single miss aborts.

**Test 1 — fully dead filter.** `skeleton_ok` forced to `return False`. Caught at the
**startup gate** (canary construction itself requires the filter), before any sweeping.

**Test 2 — the one that matters.** Filter sabotaged to die after 60,000 calls,
simulating an intermittent failure that **passes the startup gate cleanly**:

```
gate clean; sweeping 200,000 seeds from 1 with fy_lgm
XD-MBYG04K-URS3LF CANARY MISSED at seed 19900 -- filter is dead, run invalid
```

**A startup gate alone would have reported a clean null.** The in-stream canary caught
it. That is the whole point of the design, and it is now demonstrated rather than
argued.

---

## 3. Verified operation

```
startup gate           10/10  (Park-Miller KAT, 379 relations, permutation validity
                              for all 4 generators, positive control, 0/20,000 false
                              positives, drift recovery)
600,000-seed run       canaries 60/60, 18,853 seeds/s, clean JSON
checkpoint + resume    interrupted at 800,000; resumed and completed 1,200,000
                       with canaries 120/120 and correct post-resume rate
```

Resume was tested by forcing an interrupt, confirming the checkpoint state, and
restarting — the rate calculation was also fixed to measure from the resume point
rather than from zero.

---

## 4. The export

`eyerunner.py` is **self-contained** — no imports from the analysis environment — and
emits JSON I can ingest directly:

```json
{ "version", "generator", "seed_start", "seed_count", "seeds_tested",
  "directions", "candidates", "elapsed_s", "rate_seeds_per_s", "resumed_from",
  "relations_used": 379, "glyphs_used": 46,
  "filter", "selectivity_note",
  "canaries_planted", "canaries_caught", "canary_integrity",
  "hits": [ {generator, seed, direction, drift, permutation} ],
  "hit_count", "gate": [ {check, pass, detail} x10 ] }
```

**`canary_integrity` is the field to check first.** If it is `false` or the counts
disagree, the run is void regardless of what `hits` says.

Usage:

```
python3 eyerunner.py --gen fy_lgm --start 1 --count 10000000 --out run1.json
python3 eyerunner.py --gen fy_fastrand_floor --start 1 --count 4294967295 --out g2.json --resume
```

---

## 5. Model status

Unchanged. This cycle produced no new corpus results.

384 relations over 56 glyphs; injectivity clean; exposure 74.1%; residual 33.59 bits;
inventory 82.5 CI [73.0, 93.7]; determinacy threshold 81.2, unresolvable by 51×.

**Cumulative sweep total: 1.38 billion candidates, zero survivors.**

---

## 6. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Seed 0 | silently remapped | **skipped** — his code asserts it |
| Seeds ≥ 2³¹ for LGM | silently reduced mod M31 | **refused** — the cast diverges |
| Range clamp in Fisher-Yates | silent `j = i` | **assertion** — a clamp hides a wrong scale constant |
| Hits | printed | **persisted in full** for 56-glyph verification |
| Long-run integrity | unverifiable | **canary-certified**, mid-run failure demonstrated caught |
| Canary construction | — | must use valid packings; **bases scale with drift** (FR53) |

---

## 7. Horizon

1. **Run G2 then G1** from the GPU queue with `eyerunner.py`, and send back the JSON.
   Check `canary_integrity` before reading `hit_count`.
2. **Any hit needs full verification** against the 56-glyph skeleton, injectivity and
   packing before it is believed. The runner persists everything required.
3. **Read `procedural_triangles.cpp` in full** (FR94). 704 lines, only the seeding block
   has been read.
4. **The success criterion** (FR82 §7). Unchanged.
