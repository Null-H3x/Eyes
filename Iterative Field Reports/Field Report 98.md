# Field Report 98 — THE SKELETON FILTER IN C: 85× TO 178×, AND A KILL-SWITCH THAT ACTUALLY KILLS

*Instrument: `eyefast.c` (18-check gate, hardcoded reference vectors, OpenMP). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — the problem set, and why this is the executable one

FR97 closed the last internal route to the alphabet size and confirmed the
standing picture: every remaining question about `C` routes through external
evidence — glyph images (for MSB counting, MDL segmentation, the new
encounter-order construction family) or a generator sweep large enough to
find `C` if it is low-complexity. The glyph-image vectors cannot be run in
this environment. **The sweep can be made faster here, and that is the piece
of the endgame the analysis box can still move.**

G3 in the queue — *"port the skeleton filter into the GPU sweep"* — has sat
as engineering since FR60, blocked behind the more urgent generator-source
work of FR92–96. It is now the highest-value executable item: `eyerunner.py`
runs at 18.8k seeds/s single-core Python, and G2 (fastrand full 2³²) plus G1
(the timestamp window) are the last motivated reductions of the seed space.
A verified C reference makes both cheap, and gives any future CUDA kernel a
Python-independent ground truth to match.

**The failure mode this must avoid is the one FR60 and FR95 are about:** a
filter that silently stops firing and reports a clean null indistinguishable
from a real one. Porting the arithmetic is easy; porting the *paranoia* is
the point.

---

## 1. What was ported, and the traps in porting it

`eyefast.c` transcribes `eyerunner.py`'s skeleton filter, all four
generators, `verify_hit`, the canary mechanism, and the JSON schema. The
non-obvious correctness hazards, each handled and gate-checked:

| trap | resolution |
|---|---|
| **LGM state width** | 64-bit `long long`; Schrage margin 4,636 inside 2³¹−1 (FR96) holds trivially. Output uses **his** constant `4.656612875e-10` verbatim, never `1/(2³¹−1)` — FR96 showed the two diverge on ~1 draw in 5e17. |
| **fastrand signed overflow** | his C relies on `int` overflow (UB in modern C); the port uses `uint32_t`, whose wraparound is defined and bit-identical. Seed is `(seed ^ 12) & 0xFFFFFFFF` per FR94 (B6). |
| **float determinism** | compiled `-ffp-contract=off`, no `-ffast-math`. Python `float` is IEEE binary64 is C `double` on x86-64/SSE2; the two FP expressions contain no fusable multiply-add. |
| **floor-map exactness** | `v/32768.0` is exact (`v < 2¹⁵`), times `(i+1) ≤ 83` stays under 23 significand bits — exact truncation, matching Python `int()`. |
| **seed 0** | LGM skips it (his `Next()` asserts, B1); **fastrand tests it** — its stream has initial state 12 (`seed^12`), which `eyerunner.py` silently excluded by skipping seed 0 for all generators. A bijection, so no other seed covers state 12. Improvement **P1**, gate-checked. |

**Reference vectors are hardcoded, not computed.** The gate carries FR96's
four seed-1234 decks as literals; a build that does not reproduce them
refuses to run. This is stronger than `eyerunner.py`, which emits its own
vectors — here they are an external check the binary is held to.

---

## 2. Parity — every cell of every deck, exact

`--parity` dumps 238 decks (each generator at fixed probes spanning
seed magnitudes 1 … 2³²−1, plus 50 random probes) and the Python runner
re-generates the same seeds:

```
decks compared: 238   fy_lgm 59, fy_lgm_fwd 59, fy_fastrand_floor 60, fy_fastrand_mod 60
mismatches: 0
```

The port is not merely statistically close; it reproduces the Python stream
bit-for-bit at every one of 238 × 83 = 19,754 positions. The fastrand probes
deliberately include seeds above 2³¹ (2147483648, 3999999999, 4294967295) —
the range G2 needs and the range where a careless `int` cast would diverge.

---

## 3. SELF-CORRECTION — I reported the kill-switch as broken; it was my test harness

The FR95 design includes a sabotage build (`-DSABOTAGE=k`) that kills the
filter after *k* calls, simulating a filter that passes the startup gate then
dies mid-sweep. The in-stream canary must catch it. My first sabotage run
**exited 0 with no abort**, and I spent three diagnostic passes reasoning
about OpenMP atomics and call-count phases before finding the actual fault:

```
BAD:   ./eyefast_sab ... 2>&1 | tail -5 ; echo "exit=$?"     # $? is tail's, not the binary's
GOOD:  ./eyefast_sab ... >out 2>err ; echo "exit=$?" ; cat err
       -> exit=2
       -> XD-MBYG04K-URS3LF CANARY MISSED at seed 5000 -- filter is dead, run invalid
       -> XD-MBYG04K-URS3LF run VOID: canary missed (see above)
```

**The pipe to `tail` swallowed the exit code, and the abort message went to
stderr, which the pipe did not carry to where I was looking.** The kill-switch
works exactly as designed — a filter dying at 30,000 calls (just past the
~20,082 the gate consumes) is caught by the very first sweep canary at seed
5000, and the run is voided. Inline instrumentation confirmed the sabotaged
`skeleton_ok` returns 0 for that canary; the mechanism was never in doubt once
the output was read correctly.

The lesson is narrow and worth recording because it is a *testing* failure
rather than a code failure: **when the thing under test communicates through
an exit code and stderr, a harness that captures neither will report success
whatever happens.** The FR95 in-stream canary is verified live in the C port;
what failed was my reading of it.

---

## 4. Throughput

Measured here (single core; this container has `nproc` = 1):

| implementation | seeds/s | vs Python |
|---|---:|---:|
| `eyerunner.py` fy_lgm | 18,963 | 1× (confirms FR95's 18.8k — same harness) |
| `eyefast` fy_lgm, 1 thread | 1,604,621 | **85×** |
| `eyefast` fy_fastrand_floor, 1 thread | 3,371,544 | **178×** |

fastrand is ~2× LGM because it has no Schrage division. The 85–178× single-core
gain is pure C-over-CPython; OpenMP multiplies it further, though **not**
linearly — memory bandwidth, turbo throttling under all-core load, and the
canary critical section all take a cut. As **upper bounds** on Ben's
Threadripper 9970X:

```
                         32-core UPPER BOUND (linear scaling -- real is lower)
G2 fastrand full 2^32    both directions      ~1-2 minutes of CPU
G1 timestamp 2010-2021   LGM, both directions ~10-30 seconds of CPU
```

Even discounting the linear assumption heavily, **G1 and G2 are minutes of
CPU work, not hours.** The CUDA path on the 5080 remains available and would
exceed this, but is a separate port; `eyefast` is the verified CPU reference
it must reproduce, and both now carry the same hardcoded vectors.

---

## 5. What this delivers, and what it does not

**Delivers:** G3, executed and verified — the audited filter in C, bit-exact
to the Python reference, with the full paranoia design (18-check gate,
hardcoded reference vectors, live canaries, checkpoint/resume, hits persisted
with `verify_hit` output). G1 and G2 become CPU-minutes; the seed space that
motivated a GPU port is now cheap enough that the GPU is an optimization, not
a requirement.

**Does not deliver:** any change to the model, or to what a hit would mean.
The filter is still necessary-not-sufficient (46 of 56 glyphs), every hit
still needs `verify_hit`'s packing check and downstream 56-glyph
verification, and the selectivity is 83⁻⁴¹ (~1e-78, FR96) — so 1.38 billion
prior nulls stand and a sweep finding nothing still only says `C` is not in
the swept family. A faster null is still a null.

**Cumulative sweep total unchanged: 1.38 billion candidates, zero survivors.**
This cycle produced no new nulls — it built the instrument to produce them
cheaply.

---

## 6. Doctrine changes

| item | prior status | status now |
|---|---|---|
| G3 (filter in C/GPU) | queued engineering since FR60 | **executed** as `eyefast.c`, parity-exact, 85–178× single-core |
| Seed sweep cost | 18.8k/s Python; G1 25 min / G2 4 h projected on GPU | **CPU-minutes** on a 32-core host; GPU now optional |
| fastrand seed 0 | skipped by `eyerunner.py` (all-generator seed-0 skip) | **tested** in `eyefast` (state 12, bijection-unique); P1 |
| Reference vectors | emitted by the runner | **hardcoded** in the C gate; build refuses if they don't match |
| Kill-switch (FR95 test 2) | in Python | **verified in C**; my "broken" report was a harness error (piped exit code + dropped stderr) |
| Port verification | impossible before FR96 | `--parity` mode: 238 decks, 19,754 positions, zero mismatch |

---

## 7. Model status

Unchanged. 384 relations over 56 glyphs; injectivity clean; exposure 74.1%;
residual 33.59 bits; inventory 82.5 CI [73.0, 93.7]; alphabet in [56, 83],
floor re-derived FR97. **Cumulative: 1.38 billion candidates, zero survivors.**

---

## 8. Horizon

1. **Run G2 then G1 on the Threadripper with `eyefast`** — no longer
   GPU-gated. `./eyefast --gen fy_fastrand_floor --start 0 --count 4294967296
   --threads 64 --out g2.json`, then G1 over the timestamp window with
   `fy_lgm`. Read `canary_integrity` first, then any hit's `packing_ok`. Hand
   the JSON back for ingestion; it is schema-compatible with the runner's.
2. **A CUDA kernel is now the only remaining sweep optimization**, and its
   sole correctness requirement is reproducing the hardcoded reference
   vectors — the parity harness built here transfers directly.
3. **The glyph images remain the single blocking resource for everything
   else** — MSB counting, MDL segmentation, and FR97's encounter-order
   construction family all wait on them. With the sweep reduced to CPU-minutes,
   acquiring the image assets is now unambiguously the highest-value external
   action.
4. **The success criterion** (FR82 §7). Unchanged.
