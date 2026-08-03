# Field Report 197 — CERTIFICATION CLOSED: 795,545 ORDERS, ONE OBJECT, AND THE CONTROL SATURATES AT EXACTLY THE KNOWN ANSWER

*July 2026. Cycle: EYESPIRAL-C, closing FR194 priority 1 at the full FR162
standard. Compute: principal's Threadripper, 32 threads, both systems at
795,545 orders. Reduction: `reduce_fast.py`, validated semantics, gated on
known-answer pools before first contact with the campaign data.*

---

## 0. The result

**The atlas-mandatory system has exactly one maximal reading.** At the full
standard the project set for itself in FR162 — 795,545 independent greedy
orders — every single run terminates on the same 794-relation, 61-glyph,
8-equality object, and the same harness at the same depth resolves the
known-68 control system to **exactly 68**, with the estimator saturated at
the observed count on both sides.

```
MANDATORY   runs 795,545   distinct 1    Chao1 1.0    corrupt 0   heldout 0
            curve  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            95% miss bound: p < 3.77e-06 per run
            canonical sha256 7e9ab7231a6eb285...   [PASS vs certified object]

CONTROL     runs 632,883 emitted of 795,545 attempted (79.6% above floor)
            distinct 68   Chao1 68.0   corrupt 0   heldout 0
            curve  [1, 66, 67, 67, 67, 67, 68, 68, 68, 68, 68, 68, 68]
            FR162 exhaustive reference: 68.  FR162's curve: [1, 66, 67, 67, 67, 68, ...]
```

The 68th control reading surfaced between 300k and 350k orders — deep-tail
behavior matching FR162's own discovery profile nearly step for step. The
emission floor replicates for a third time across three environments: 79.1%
(FR161, 2,500 orders), 79.3% (sandbox, 2,000), 79.6% (this run, 795,545).

## 1. The evidence chain for the unique reading

Three independent computational paths, two machines, one object:

| path | scale | signature |
|---|---|---|
| Python mirror (independent implementation, sandbox) | 3 fixed orders | sha `7e9ab723…`, 794 relations |
| C harness, sandbox host | 38,459 random orders | identical, bit-for-bit |
| C harness, Threadripper | **795,545 random orders** | identical, bit-for-bit |

The control's dominant reading also matches across machines (sha
`3930b054…`, sandbox and Threadripper) — the cross-machine identity holds on
the multi-reading system too, not just the unique one.

The standing caveat transfers unchanged from FR162: uniform-shuffle sampling
cannot exclude a reading reachable only on a measure-~0 set of orders. No
sampling method can, and the claim is made at exactly the standard of the
claim it certifies — now with a per-run miss bound of 3.77e-6 at 95%.

## 2. Provenance note: the channel salvage

The raw campaign outputs (~13 GB) exceed the upload channel, which truncated
the first transfer at ~30 MB mid-way through `m_all.txt`'s deflate stream.
The truncated stream itself decompressed to 4.82 GB — **709,046 validated
runs, distinct 1, sha PASS** — closing 89% of the mandatory question before
the full counts arrived by paste. Logged because the recovery method
(streaming a headerless deflate member from a damaged archive) may be needed
again, and because the salvage independently confirmed the paste.

## 3. Doctrine changes

| item | prior | now |
|---|---|---|
| FR176 uniqueness | certified at 38,459 (FR196) | **closed at the full FR162 standard: 795,545/795,545, both systems, two machines, three implementations, Chao1 = observed on both** |
| Rule 7 status for the sampler | contrast + trajectory (FR196 §4) | **exact reproduction of the known answer: 68/68, saturated** |
| the unique reading | — | the canonical object of the record: 794 relations, 61 glyphs, 8 equalities, sha `7e9ab7231a6eb285…` — any candidate alphabet must satisfy it; `eyeverify.py` remains the skeptic's subset test |
| internal programme | "nearly audited shut" (FR194 §7) | **audited shut.** Every FR194 priority-1 through priority-4 item is executed; six internal drift routes closed by test; the reading unique at full standard; the formula minimal |

## 4. What stands, in one place

```
c[m][t] = C[ ( p[m][t] + b_m + d·t ) mod 83 ]

C        arbitrary up to 8 forced merges; unique reading fixes all 794
         determinable relations (sha 7e9ab723…)
b        [0, 0, 77, 39, 52, 23, 53, 24, 53] · d, gauge b[E1]=0  (FR195/196)
d        the one number the corpus cannot supply — six internal routes
         closed by proof (FR30/36/53, FR167/191, FR195)
reading  one; five fragments = five components; 819/1,036 positions (79.1%)
```

## 5. Horizon

1. **Consolidation cycle** — CURRENT_STATE and ACQUISITION_SPEC v2 rewritten
   against certified numbers; the E20–E32 backfill merged into
   CORRECTIONS.md. Nothing in the doctrine layer should quote a superseded
   figure after this.
2. **Publication refresh (L-7)** — the community post with certified figures
   and the smallest verifiable asks: **two indicator values** (E30), the
   **8-token crib at East 3 105–112**, the `q[36]/q[68]` and `q[22]/q[64]`
   pairs, six anchors (2 + 1×4). `eyeverify.py` and both cores attached so
   nothing requires trusting this project's choices.
3. The path from here is external by proof, not by fatigue. When any pin
   arrives, the certified unique reading turns it into plaintext positions
   mechanically — and the §4 residue of FR195 gets its magnitudes explained
   for free.
