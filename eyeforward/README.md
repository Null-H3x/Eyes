# eyeforward

Five forward-moving modules for the Noita eye-message solve, built on top of
the existing `noita_eye_core` machinery. Every module ships a paranoia
`selftest()` that plants ground truth, attacks it, and asserts recovery — and
that **fails loudly** when the attack is only pretending to work. Where the
mathematics does not support a claim, the audit says so instead of hiding it.

Run everything:

```bash
python3 selftest.py          # all nine audits (~11 min; iso_relax + model_power dominate)
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

### `order_anneal.py` — shared monoalphabetic read (7/7)
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

Two additions from the model_power follow-up: `reduce_to_residues` and `solve`
take a **`drift`** kwarg (`+1` pmp default, `−1` reverse, `0` pure) because the
chain test can't pin drift down at real sparsity; and check 6 proves a
**Beaufort plant reads with no code change** (z = 37, 61 word hits) — the sign
flip only relabels canonical residues and the climb learns arbitrary
relabelings. The check exists so a future refactor to a frequency-pinned map
can't silently reintroduce the blind spot.

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

### `ordering_bridge.py` — same-day verdicts for alphabet-ordering hypotheses (15/15)
The bridge between the two workstreams: the anchor graph **links** symbols but
can't **order** them; deck-sweep/primer-cut generates candidate **orderings**
but had no reader. Feed this module any hypothesis — full `q`, full `C`, a
partial ordering prefix, or explicit pins, optionally with claimed letter
assignments — and it returns a scored verdict card.

Because model_power showed the corpus evidence only pins down the linear class
`{pmp, pure, beaufort}`, every read sweeps **drift ∈ {+1, 0, −1}** and
**sign ∈ {+, −}** instead of assuming the pmp defaults. The learned read
(order_anneal's climb) absorbs sign automatically — locked in by
order_anneal's new Beaufort check — so it sweeps drift; the direct read
(claimed letters) sweeps drift × sign × global base offset. On plants the
sweep autonomously picks sign=+ for pmp, sign=− for Beaufort, and drift=−1
for a reverse-drift plant, all reading at z ≈ 51.

Three traps were caught live and are now regression-locked:

- **Shuffle-gap mirage.** A *random* `q` still shows a small positive
  real-vs-shuffled-corpus support gap (corpus-intrinsic compressibility).
  Verdicts use a random-**permutation** null instead: true `q` sits at
  z ≈ −32, a wrong `q` at ≈ −1.5.
- **drift=0 invariance.** At drift 0 the residues are a bare relabeling of
  the ciphertext, and both the support objective and the learned climb are
  relabeling-invariant — every hypothesis scores identically. Completion and
  learned reads refuse drift 0 with an explanation (the real corpus produced
  a z=37.9 "karelian" letter-soup mirage this way); drift-0 models remain
  testable via the direct read.
- **Completed-`q` circularity.** For a partial hypothesis the anneal
  *minimizes* support, so the fitted `q`'s support-z is not evidence (flagged
  `circular` in the card). The verdict-bearing statistic is the completion
  **gap** vs a shuffled control annealed with identical effort: 16 real pins
  give ~+1.6 (below the 5.0 line), 40 true plant pins give +31.6.

A PASS additionally requires **readability** — ≥25% of decoded tokens must be
real words of the winning language — because a climb's z measures "found some
structure," not "text is readable."

---

### `alphabet_sweep.py` — disposition structured alphabet families (16/16)
The devs had to *build* C somehow, and the realistic construction space is
enumerable. EyeStat burned 34+ billion seeds against the PRNG corner; this
module sweeps the **structured** corner, which nobody could afford before the
bridge made a candidate cost microseconds (batch gsupport) and a survivor cost
minutes (readability-gated verdict). Additive constants are absorbed (by
`base_m`, and support is shift-invariant), so the families dedupe **by
construction**: affine is 82 candidates, not 82×83, and pre-shift power maps
with k=1 collapse into affine for every shift.

Families: affine `a·v` (82) · power `a·v^k` (3,198) · pre-shift power
`a·(v+b)^k` (262,236) · base-5 **trigram-digit** maps filtered to closure on
the 83-value glyph set (the complete closed family is only **432**) · deck
deals (160) · keyword columnar transpositions keyed by the en/fi/krl
wordlists (260,376 unique rank tuples). Positive controls: a planted
`q = 17·v` surfaces as a decisive winner (z = −39, third place −1.9) and
end-to-end through the bridge reads at readability 0.94; a reverse-drift
plant surfaces at drift −1; a random-C plant yields zero survivors.

The sweep also exposed the **mirror identity**: `support(q, drift) ≡
support(−q, −drift)` unconditionally (negating q negates residues, a
bijection) — the Beaufort equivalence surfacing again. For negation-closed
families the two drift columns duplicate each other under `a → −a`; for open
families (trigram, deals, keyword) drift −1 is genuine new coverage.

**Real-corpus result: the structured-alphabet corner is EXCLUDED.** All six
families — ~787k constructions, ~1.57M scored (q, drift) hypotheses — produce
**zero survivors** below the −6 line; the deepest observations (−4.78 keyword,
−4.67 prepower) match the expected extremes of that many null draws. Honest
frame caveat: this excludes constructions of q *over the value indices*; a
construction over a different latent glyph labeling would look unstructured in
this frame.

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

- Run through `ordering_bridge` as its first real hypothesis, the 16 pins
  come back **FAIL** — the same negative, now as a one-command reproducible
  verdict: completion gap +1.6 (drift +1) and +1.0 (drift −1) against the 5.0
  line, reads at both drifts refused by the readability gate. This run also
  tested **drift = −1 on the real corpus for the first time** — negative, so
  the reverse-drift blind spot is now closed at current anchor density, the
  same way the Beaufort sign blind spot is closed by sweep.

- `alphabet_sweep` dispositioned the structured-alphabet corner: affine,
  power, pre-shift power, closed trigram-digit, deals, and wordlist-keyed
  columnar constructions (both orientations) are all **excluded** (~1.57M
  scored hypotheses, zero survivors, extremes at chance). Combined with EyeStat's 34B-seed PRNG null,
  the key ordering now retreats into "PRNG under an untested family, a
  structured construction in a different glyph-labeling frame, or a
  non-alphabet source."

This is exactly the open frontier the community names: the alphabet links but
does not order. `support_min` + `order_anneal` are ready to read the moment
`iso_relax` (or a new anchor source) crosses from "linked" to "ordered" — and
`ordering_bridge` turns any candidate ordering from the deck-sweep/primer-cut
side into a same-day PASS / SUPPORT_ONLY / FAIL verdict.

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
