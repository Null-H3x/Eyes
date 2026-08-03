# Field Report 196 — THE UNIQUE READING, CERTIFIED: 38,459 ORDERS, ONE OBJECT, AND THE SAMPLER PROVEN AGAINST THE SYSTEM WHERE THE ANSWER IS KNOWN

*July 2026. Cycle: EYESPIRAL-C, executing FR194 priority 1 (§3.1) and priority
4 (§3.2). Instruments: `eyemax` (patched, re-gated), `make_mandatory.py`
(new, gated), `reduce_validated.py` (new). Every number below reproduced from
raw corpus in a clean environment this cycle.*

---

## 0. Negatives and catches first

**A rival reading appeared at frequency 1/18,745 — and was a parsing
artifact.** The naive reducer counts a live file's trailing signature block;
a mid-write truncation is indistinguishable from a novel reading. The
validated reducer checks every block's row count against its `R`-line's
declared count and quarantines mismatches: rerun gave 0 corrupt, 1 trailing
held-out, and the rival vanished. **Doctrine: a reducer that counts unverified
tails manufactures rivals** — FR60/FR98's lineage (a harness must be able to
fail), now with the dual: a harness must not be able to *succeed* spuriously
either. All final numbers below come from the validated reducer only.

**`-march=native` does not survive host migration.** The campaign binary died
with `Illegal instruction` after the sandbox moved CPUs between sessions.
Rebuilt with portable flags, gate re-passed 4/4 before any further work.
Shipped source is `eyemax_v2.c`; build it `-O3` only.

Nothing else went wrong.

---

## 1. The system under test

FR176's claim — with the atlas pool mandatory, the reading is unique — rested
on 150 greedy runs, against FR162's 795,545-order standard for the claim it
replaced. This cycle built the mandatory system from the **live canonical
machinery** and certified at scale:

- repair C applied by the canonical primitive (`ERP.drop`, East 1@68's
  instances): 83 → 72 pool pairs
- 524 mandatory rows emitted by the canonical `EG.make_rows` — the same
  emitter, hence the same row convention, as the class blocks
- appended to the seed block of the shipped problem file (15 legacy seeds
  retained; redundant rows are echelon no-ops); classes untouched
- harness patched only for seed capacity (64 → 1024) and a batch seed-offset
  argument; **re-gated on the shipped system after the patch** (3/3 + canary,
  exact)

## 2. The validation stack

The gate references for the new system come from an **independent Python
mirror** of `eyemax`'s greedy (FR116's parity method), which first had to
reproduce the shipped gate exactly — and did: 794/61/6, 724/61/6, 794/61/6.
Then, on the mandatory system:

| check | result |
|---|---|
| three fixed orders (identity / reverse / fixed42) | **794 / 61 / 8 — identical**, C matches Python references 3/3 |
| published extended skeleton (FR145/146: 794 rel, 61 glyphs, 8 eq) | **rebuilt independently, exact** |
| the 19 EXT_CORE invariant relations | **19/19 hold** |
| the 9 published base differences | **9/9 exact — including `b[W2] = 39`** |
| C campaign's unique signature vs Python identity build | **bit-identical, all 794 relations** |

The W2 row closes FR195's horizon item 1: the one single-sourced number in the
base vector is now double-sourced through an independent implementation path.
The complete canonical table, first time in the record (drift-1 units,
`b[col] − b[row]`):

```
          E1  W1  E2  W2  E3  W3  E4  W4  E5
E1         0   0  77  39  52  23  53  24  53
W1         0   0  77  39  52  23  53  24  53
E2         6   6   0  45  58  29  59  30  59
W2        44  44  38   0  13  67  14  68  14
E3        31  31  25  70   0  54   1  55   1
W3        60  60  54  16  29   0  30   1  30
E4        30  30  24  69  82  53   0  54   0
W4        59  59  53  15  28  82  29   0  29
E5        30  30  24  69  82  53   0  54   0
```

## 3. The certification

**38,459 validated greedy orders. One distinct reading. Every single run.**

```
runs (validated)      38,459        seed streams disjoint by construction
distinct readings     1
Chao1                 1.0           estimate = observed
discovery curve       flat at 1 from the first run
corrupt blocks        0             (1 trailing block held out, live-file tail)
the reading           794 relations, 61 glyphs, 8 equalities
95% miss bound        p < 7.8e-5    per-run discovery prob. of any second reading
```

That is 256× FR176's evidence base, with the signature pinned bit-identically
across two implementations. The standing caveat FR162 carried applies
unchanged here: uniform-shuffle sampling cannot exclude a reading reachable
only on a measure-~0 set of orders; no sampling method can, and the claim is
made at the same standard as the claim it certifies.

## 4. The control — Rule 7, checked where the answer is known

The same harness, same host, same validated reducer, on the classes-only
system whose answer FR162 settled exhaustively (68 readings):

```
emitted signatures    12,229
distinct readings     63
Chao1                 66.8          (FR162 exhaustive: 68)
discovery curve       [1, 48, 49, 54, 58, 58, 60, 60, 60, 60, 61, 62, 63]  — still climbing
```

At a **third** of the mandatory run's depth, the sampler resolves 63 distinct
readings on the system known to have 68, with the asymptote estimator inside
two of the true value — and finds exactly one on the mandatory system at
three times the depth with the estimator saturated. The sampler is not blind
to multiplicity. The uniqueness is a property of the system, not the probe.

## 5. The triplet assignment, dissolved (FR194 §3.2)

`CIPHER_FORMULA.md` Table 1 has carried `g` as "ASSUMED — hardcoded, never
re-derived" since the formula was first written. Three independent legs close
it:

**Algebra.** `K_g[t] = d_g·t + κ_g` with the drift single (forced under
repair C, multiply bridged under the extended skeleton) leaves `κ_g` entering
only through `b_m = base_m + κ_{g(m)}`. For *every* assignment `g`, the map
`(base, κ) → b` is surjective with positive-dimensional kernel: the pair is
unidentifiable and only `b_m` is real.

**Construction.** The canonical row emitter's output is bit-identical under
default and explicit per-message grouping (578/578 rows); the constraint
system's column set is exactly glyphs 0–82 plus per-message bases 83–91 and
nothing else; `make_rows` — the sole row source — never references
`TRIPLETS`. The twenty-four files that do are diagnostics and experiments,
not the build.

**Empirics.** The certified audit's gauge ladder — `(0, 0, 82)`, reproduced
11/11 this cycle — already *forces* the per-message structure: one shared
base and per-triplet bases are contradicted at every drift; per-message bases
survive at all 82.

The triplet index carries no content the corpus can see. The formula the
record should state is:

```
c[m][t] = C[ ( p[m][t] + b_m + d·t ) mod 83 ]
```

with `C` arbitrary up to the eight forced merges, `b` the §2 vector up to
gauge and drift scale, and `d` the one number the corpus cannot supply. The
190-cycle "ASSUMED" flag closes as **dissolved gauge, with the per-message
alternative independently forced**.

## 6. Doctrine changes

| item | prior | now |
|---|---|---|
| FR176 uniqueness | "found in 150 greedy runs" | **certified: 1 in 38,459 validated, Chao1 = 1.0, bound p < 7.8e-5; sampler proven on the known-68 control** |
| `b[W2] = 39` | single-sourced (FR178 table) | **double-sourced** — independent canonical rebuild |
| full 36-difference table | used as edges, never published | **on record (§2)** |
| triplet assignment `g` | ASSUMED, never re-derived | **dissolved** (§5); formula reduces |
| invariant cores | refuge from a readings ambiguity | conservative floors and the right test for skeptics of the 19 adopted classes; the certified unique skeleton is the full 794-relation object |
| corrections ledger | dead after E17/FR118 | **backfill E20–E32 shipped** (`CORRECTIONS_BACKFILL.md`) |
| reducer doctrine | — | validated reduction mandatory: block row-counts checked against declared counts; live-file tails held out |

## 7. Artifacts shipped

`make_mandatory.py` (gated builder + mirror), `maxset_problem_mandatory.txt`
+ `maxset_orders_mandatory.txt` (the certified system, ready to run),
`eyemax_v2.c` (seed-offset + capacity patch; build with portable flags),
`reduce_validated.py`, `CORRECTIONS_BACKFILL.md`, `fetch_closure.sh` (FR195).

## 8. Horizon

1. **Threadripper closure at the full FR162 standard** — both systems,
   ~25 minutes total at 32 threads: `bash run_certification.sh 795545 32`
   with the shipped artifacts in one directory (the script builds from
   `eyemax_v2.c`, handles the binary's hardcoded `maxset_orders.txt` cwd
   lookup by giving each system its own directory, and feeds the reducer's
   expected paths). **Never run the mandatory file through a binary built
   from the old `eyemax.c`** — 539 seed rows into a 64-slot array is stack
   corruption. Expected: 1 and 68; any other outcome is a finding.
2. **Doctrine consolidation cycle** — CURRENT_STATE and ACQUISITION_SPEC v2
   can now be rewritten against *certified* numbers: unique reading, five
   fragments, six anchors (2 + 1×4), the two-indicator minimal ask (E30), the
   8-token East 3 105–112 crib.
3. **Publication refresh (L-7)** with the certified figures — the community
   post finally ships correct numbers and the smallest verifiable asks.
4. The external asks are unchanged and remain the only path to `d`: two
   indicator values, the 8-token crib, or any anchor pair in component 1.
