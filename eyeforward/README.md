# eyeforward

Five forward-moving modules for the Noita eye-message solve, built on top of
the existing `noita_eye_core` machinery. Every module ships a paranoia
`selftest()` that plants ground truth, attacks it, and asserts recovery — and
that **fails loudly** when the attack is only pretending to work. Where the
mathematics does not support a claim, the audit says so instead of hiding it.

Run everything:

```bash
python3 selftest.py          # all seven audits (~7 min; iso_relax + model_power dominate)
python3 selftest.py --fast   # skip the slow order_anneal read + model_power MC
```

Total audit coverage: **75 checks across 7 modules, all passing.**

---

## The model this targets

Leading hypothesis (per-message-progressive), the same one `noita_eye_core`
converged on:

```
c_m[t] = C[(p_m[t] + base_m + t) mod N]        N = 83 (prime)
```

with `C` an unknown mixed alphabet, `q = C^{-1}` the unknown value→position map,
and `base_m` a per-message offset. `q` is the bottleneck: recover it and the
corpus collapses to a shared monoalphabetic cryptogram.

Everything here is **model-dependent by construction** and the audits prove the
attacks *fail* on autokey/alberti data rather than silently emitting garbage —
so a clean run is evidence for the model, not just for the code.

One caveat `model_power.py` makes precise: the isomorph-based tests confirm the
**linear class** `{pmp, pure, beaufort}`, not `pmp` uniquely — a sign-flipped
Beaufort map is indistinguishable under same-plaintext isomorph constraints. The
read step should try both `+p` and `−p`.

---

## The pipeline

```
iso_relax  ──pins──▶  support_min  ──q──▶  order_anneal  ──▶  plaintext
(anchor graph)      (recover q via        (shared mono-sub
                     support minimisation)  solve, read text)

order_gpu accelerates support_min's objective (CuPy, NumPy fallback)
pyry_gate validates the corpus against the dev conditions + tests for chaining
model_power measures how much the progressive-consistency test actually proves
```

---

## Modules

### `plantlab.py` — shared ground-truth generators (11/11)
Single source of planted corpora so every audit attacks the *same* worlds. Seven
model families (`pmp`, `pure`, `autokey1`, `chain_nz`, `alberti`, plus the
hard-negatives `periodic` and `beaufort`), plaintext coded into `Z_N` by a random
injection, optional shared prefixes, and `groups`/`group_share` for triplet-style
shared openings at real message lengths. KATs verify each generator round-trips
through its own inverse.

### `pyry_gate.py` — dev-conditions oracle + chain battery (13/13)
Encodes the computable **Pyry's Conditions** and checks them on the real corpus:
flat unigram (standardized χ² z-score, not a saturating MC p-value), unbroken
symbol set, header structure, **zero adjacent doubles**, isomorph value-
disjointness, distance-4 excess. Then a **chain battery**: under any
`c[t]=E(p[t])+c[t-1]+αt` the first differences are a monoalphabetic image of the
plaintext, so sweeping α and IoC-scoring against a shuffle null detects fixed-
step chaining.

**Real-corpus result:** all six conditions PASS. C8 zero doubles at z = −3.7 vs
a null expecting ~12; distance-4 excess at 2.24× (matching CodeWarrior0). The
chain battery reports z = 6.3 vs null **but** the winning α is only 2.6σ above
the other α values — so the verdict is honestly *"weak/ambiguous, no single α
dominates"*, not a chain discovery. This is the one place the corpus shows a
faint pulse worth another look; the module refuses to oversell it.

### `support_min.py` — language-free recovery of `q` (11/11) — FLAGSHIP
Under the model, `r_m[t] = (q[c]-t) mod N = (p_m[t]+base_m) mod N`, a per-message
rotation of the plaintext. So the **number of distinct residues per message
equals the plaintext alphabet size** (~20) for the true `q`, and spreads toward
83 for a wrong one. Minimising mean residue support is a **language-free,
ordering-free** objective whose optimum is the true `q`.

Why it dodges the known traps: it is not IoC (a wrong `q` matching IoC still
spreads its residues — audited), it consults no language model (immune to the
Finnish-flavoured-gibberish failure), and it seeds from the contamination-
filtered isomorph chain, not a guessed crib.

**Audited behaviour:** true `q` support z < −15 vs random; recovery scales with
pins — 22 → 82%, 30 → 92%, 40 → 100% (hits true support exactly); autokey data
correctly **fails** to recover (honest negative); rotation-aware scoring;
pin-collision guard.

### `order_anneal.py` — shared monoalphabetic read (6/6)
Once `q` is fixed, reduce to residues, recover **relative bases with no language
model** by differencing the shared openings (Pyry condition #3 solves the
base-alignment subproblem for free), pool all messages into one canonical frame,
and hill-climb the value→char ordering with a character-trigram model across a
language bank (English shipped; Finnish/Karelian pluggable from `eyestat/`).

Fitness is n-gram log-prob (order-sensitive, never IoC); language is an axis of
the search (chosen by score, never assumed). On a planted corpus with the true
`q` it reads the plaintext exactly — *"the work begins before the sun rises and
the work continues after the sun has set the miners walk the long tunnel…"* —
at z ≈ 51 over its own random-O null.

### `order_gpu.py` — batched objective, CuPy with NumPy fallback (6/6)
`batch_support(Q, …)` evaluates B candidate permutations at once via one-hot
scatter + per-message reduction; `vectorized_greedy` is a coordinate-descent
polish. **Bit-exact against the pure-Python `support()`** (asserted). No GPU in
the build container, so the CuPy path is SKIP-marked honestly and the NumPy path
is fully exercised; on your RTX 5080 / CUDA 13.2 the `cupy == numpy` assertion
runs for real. This accelerates the objective ~100–1000×, **not** the 83!
combinatorics — its value is affording the extra restarts that close the 22-pin
recovery gap.

### `iso_relax.py` — densify the anchor graph (14/14)
Grows the linked-symbol set past the strict-isomorph ceiling by admitting
shorter, within-message, and one-mismatch isomorphs — each filtered through the
repo's own `consensus_alphabet` (robust multi-restart GF(83)) so coincidental
matches are dropped, not trusted. Exports pins via a **gauge-invariance test**:
solve twice with a reference symbol pinned to two values; a symbol is emitted
only if its position shifts by exactly the gauge delta (free variables fail this
and are never exported).

The audit repeatedly caught false pins from the weaker tiers, which forced the
final architecture: **only strict + within-message-exact pairs determine pins**;
shorter (rep 2) and approximate pairs inform the census only. Every exported pin
is then provably correct up to global rotation on plants.

**Real-corpus result:** 22 symbols strictly linked (19 distinct positions, ratio
0.864 — the known state); **16 gauge-invariant sound pins** exported for
support_min. The approx tier proposed ~147k candidate pairs and consensus
admitted ~1.8k — the rest rejected as coincidental. The full census links all 83
symbols but distinct-position ratio collapses to 0.012: the documented
**"linked but not ordered"** wall, flagged rather than hidden.

### `model_power.py` — what the progressive-consistency test actually proves (14/14)
The leading model leans on one instrument: the progressive chain test comes out
*consistent* on the real corpus. This module measures that instrument's
discrimination power with ground-truth plants and reports four things — three of
which are corrections the paranoia audit forced.

- **Finding 0 — yield is a trap.** It is tempting to argue "autokey/Alberti
  destroy isomorphs, so the observed isomorphs exclude them." That is **wrong**:
  a repeated word's skeleton is a function of its own internal structure
  (partial sums under chaining), invariant to the history offset, so all
  families preserve planted-repeat skeletons at rate ~1.0. Isomorph *yield*
  tells you a repeat existed, not which cipher made it.
- **Finding 1 — the real discriminator is constraint structure.** On clean
  anchors the progressive test rejects the wrong families hard: **periodic
  ~6400, autokey ~7500, Alberti ~7400 contradictions**, while `{pmp, pure,
  beaufort}` sit at **0**. The matching autokey-chain accepts autokey/Alberti
  8/8. So the real corpus's **zero** contradictions genuinely exclude periodic,
  autokey, and Alberti.
- **Finding 2 — it confirms a class, not pmp.** For a same-plaintext isomorph
  pair the plaintext *cancels*, so the test is blind to how plaintext enters.
  A **Beaufort** cipher `c[t]=C[(base_m − p[t] + t)]` (plaintext sign-flipped) is
  **indistinguishable** from pmp — 8/8, 0 contradictions. The confirmed object
  is the linear class `{pmp, pure, beaufort}`. → `order_anneal` should try the
  `−p` (beaufort) map as well as `+p` when reading.
- **Finding 3 — consensus filtering is circular.** `consensus_alphabet` keeps
  only pairs consistent with `per_msg_prog_rows`, so a periodic corpus filtered
  that way then "passes" the progressive test (its ~720 raw contradictions
  collapse to 0). Discrimination must use **raw or clean** pairs, never
  consensus-filtered ones.

**Real-corpus result:** abundant isomorphs (120 pairs at L13/rep2) and
progressive-consistent with **0 contradictions** on raw rep-4 pairs → firmly in
the `{pmp, pure, beaufort}` linear class; autokey/Alberti/periodic excluded.

---

## What the corpus says right now (measured, not claimed)

Running the chain end to end on the real 9 messages:

- 16 sound pins (iso_relax) → support_min anneals to support ≈ 48.3, which is
  z ≈ −11 below its own null band. Real signal that the objective is finding
  structure.
- **But** an overfitting control matters: annealing a per-message-*shuffled*
  copy of the corpus reaches essentially the same floor (gap ≈ +0.5). At this
  message length (~115 glyphs) and alphabet size (83), the support objective
  has enough freedom to compress *any* corpus somewhat, so the current floor is
  **not yet** decisive evidence of the true `q`. The honest reading: the
  machinery is validated on plants and finds *a* structure on the real corpus,
  but more anchors (the iso_relax ordering gap) are needed before the read is
  trustworthy.

This is exactly the open frontier the community names: the alphabet links but
does not order. `support_min` + `order_anneal` are ready to read the moment
`iso_relax` (or a new anchor source) crosses from "linked" to "ordered."

---

## Honest limits (the short version)

- **Model-dependent.** All of this assumes per-message-progressive. The audits
  prove the attacks fail on autokey/alberti, which is the point — a clean real-
  corpus read would *itself* be evidence for the model.
- **Search, not oracle.** `support_min`'s optimum is provably the true `q`, but
  the search is over 83!; it needs a pin floor (~22+) to converge.
- **Ordering is the wall.** `iso_relax` maximises linked symbols and exports
  only provably-determined pins, but full alphabet ordering from isomorphs alone
  remains unsolved — and every module reports which regime (linked vs ordered)
  it is in rather than papering over it.
```
