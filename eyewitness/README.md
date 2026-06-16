# EyeWitness

**A verifiable structural fingerprint of the Noita eye corpus.**

EyeWitness answers one falsifiable question and signs the answer so anyone can
re-check it:

> Are the 9 messages organised as **pairs + a special E5** (Theory 1), or as
> **triplets** (Theory 2)?

It does **not** try to decrypt anything — that is [EyeCrack](../eyecrack)'s job.
EyeWitness is the low-risk effort: it produces a true, reproducible result
whether or not the puzzle is ever solved, and it emits the contract EyeCrack
consumes.

## Why this is decidable (and not just opinion)

The corpus is already, independently, established to be **in depth** — the 9
messages share a position-indexed keystream (difference-IoC sits ~57 standard
deviations above a shuffle null). Under any linear combiner with a shared key:

```
c_i[t] == c_j[t]   <=>   p_i[t] == p_j[t]   (mod N)
```

So *identical ciphertext spans are identical plaintext spans*, and "which
messages belong together" becomes arithmetic with p-values. The two theories are
just the two ways to factor 9: `8 + 1` (pairs leave E5 over) vs `3 + 3 + 3`
(triplets, no leftover).

## What it computes

1. **Depth premise** — confirms the shared keystream and estimates the depth-only
   collision baseline (the chance two in-depth messages agree with *no* shared
   plaintext).
2. **Model selection over partitions** — each within-group pair is "linked" (one
   Binomial collision rate), each across-group pair "unlinked" (another);
   partitions are ranked by profile log-likelihood with a likelihood-ratio vs a
   no-structure baseline. This adjudicates Theory 1 vs Theory 2 directly.
3. **Data-driven cliques** — thresholds the BH-corrected significant-agreement
   graph and reads off whether maximal cliques are size 2 (pairs) or 3 (triplets)
   with **no theory imposed**.
4. **Robustness** — re-runs after stripping the shared opening, so the verdict
   can't be dismissed as "just shared headers."
5. **Cribs** — the significant identical spans (with run-length p-values) that
   EyeCrack uses to pin the shared keystream.
6. **Power** — the shortest identical run that could even be called significant
   at these message lengths.

## Verdict on the real corpus

```
WINNER : TRIPLETS  -> Theory 2 (triplets)
  TRIPLETS       logL -1053.7   LR-vs-baseline 189.4   (within 20.6% vs across 4.7%)
  PAIRS_PLUS_E5  logL -1129.9   LR-vs-baseline  37.0
  margin: 76.2 logL over pairs; survives stripping the first 40 symbols
data-driven cliques: [E1,W1,E2] and [E4,W4,E5]  (all size 3)
E5 is INSIDE a clique  ->  Theory 1's "E5 is special" is refuted
```

Triplets, not pairs. E5 is not special.

## Usage

```bash
# from this directory (needs numpy; uses ../noita_eye_core for the math)
python3 eyewitness.py                  # print report + write fingerprint.json
python3 eyewitness.py --out fp.json --n-null 2000 --seed 1

# independent re-check — numpy ONLY, no dependency on this stack
python3 verify_fingerprint.py fingerprint.json
```

## The artifact: `fingerprint.json`

A deterministic, signed-by-content (SHA-256) record of everything above,
including the full pair-agreement matrix, the ranked partitions, the cribs, and a
`for_eyecrack` block (`in_depth_set`, `combiner_candidates`) that is EyeCrack's
input contract. `verify_fingerprint.py` re-derives the load-bearing claims —
corpus hash, depth, the maximum-likelihood partition, and that every crib is a
real identical run — from ~150 lines of stdlib + numpy, so the result does not
require trusting the rest of the codebase.

## Math home

All statistics live in [`noita_eye_core/grouping.py`](../noita_eye_core/grouping.py)
and are covered by the package math gate (`python3 noita_eye_core/selftest.py`),
including ground-truth tests on synthetic corpora with a *planted* pair / triplet
grouping. EyeWitness is a thin orchestrator over that tested core.
