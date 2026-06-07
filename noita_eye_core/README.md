# noita_eye_core

A single, tested home for the math shared across the three Noita eye-message
tools (EyeStat, EyeSieve, the workbench), **plus** the depth / crib-drag
keystream-recovery layer recommended in `CONVERGENCE_AND_AUDIT.md` — the natural
convergence point all three tools can feed and consume.

Everything here is validated by `selftest.py` (the math gate). Run it from this
directory:

```bash
cd noita_eye_core
python3 selftest.py        # 62 checks across 8 modules
python3 analyze.py         # depth analysis on the real corpus
```

`numpy` is required.

## Why this exists

The audit found the three tools re-implement the same math (IoC, modular
ciphers, English frequencies, corpus loading) and that none of them runs the
single highest-probability attack: an **N-way depth** attack that exploits the
shared keystream the corpus structure implies. This package fixes both: one
tested implementation of the shared primitives, and the depth layer on top.

## The model (and why the algebra is clean)

The corpus shows **identical ciphertext runs at identical positions** across
messages (e.g. E1/W1/E2 agree on positions 1–24; the universal `66,5` header).
That means the keystream is a function of **absolute position only** and is
**shared by all nine messages** — messages "in depth". Under any linear
combiner (`add`/`sub`/`beaufort`):

```
c_i[t] - c_j[t]  ==  plain_sign * (p_i[t] - p_j[t])   (mod N)
```

so the key cancels: the plaintext **difference** structure is recoverable with
no key at all. Each column then has exactly **one** unknown (its key value),
with up to 9 in-depth samples — i.e. multi-ciphertext Vigenère.

## Modules

| Module | What it provides | Key guarantees (tested) |
|---|---|---|
| `corpus` | single source of truth (`corpus.json`) | byte-identical to the EyeStat data |
| `cipher_ops` | `add`/`sub`/`beaufort` combiners + inverses + key recovery | full `N×N` round-trip KATs; differencing cancels the key |
| `stats` | IoC (alphabet-aware), chi², difference IoC | IoC hand-KATs; difference IoC is key-invariant |
| `lm` | char n-gram Markov model (scorer **and** depth emission/transition) | bigram rows normalise; add-k KAT; words ≫ gibberish |
| `null_model` | empirical null, z-score / p-value, Bonferroni, BH | significance + multiple-testing KATs |
| `prng` | faithful **Noita `NollaPRNG`** port | canonical MINSTD 10000-iterate KAT (1043618065); core == EyeStat Park-Miller V0 |
| `trigram` | base-5 trigram decomposition + per-digit IoC | round-trip for all `0..124`; planted-digit detection |
| `depth` | depth confirmation, crib-drag, Viterbi keystream solver | **synthetic end-to-end recovery**: 92% keystream / 92% symbol; crib-drag exact |

## What is proven vs. what is heuristic (honesty)

* **Exact:** the cipher round-trips, the differencing identity, crib propagation
  (a header guess reveals all nine headers at once), the PRNG core, and the
  trigram decomposition.
* **Provably optimal under its model:** `solve_keystream_viterbi` returns the
  global MAP keystream for a 1st-order Markov model (Viterbi).
* **Demonstrated, with stated limits:** on synthetic in-depth data with a
  language-like (non-uniform) symbol distribution, the solver recovers ~92% of
  the keystream and plaintext. **Caveat:** the *real* corpus has a near-uniform
  unigram (IoC ≈ 0.012), so unsupervised per-column shift recovery is genuinely
  under-determined (a flat unigram gives no per-column signal, and an
  over-deterministic transition model admits spurious "perfect-chain"
  keystreams). In that regime the high-value lever is **crib-drag** plus the
  exact difference structure — not blind Viterbi. The synthetic test makes the
  machinery's correctness explicit; it does not claim the real plaintext.

## How it converges with the existing tools

* `corpus.json` is verified identical to EyeStat's data (`cross_check_eyestat`).
* `prng.NollaPRNG.next_raw()` is verified equal, state-for-state, to EyeStat's
  `ParkMillerV0Rng`.
* `lm.MarkovModel` is both the candidate scorer (replacing brittle substring
  counts) and the depth solver's emission/transition model.
* `null_model` provides the calibrated significance the seed-scan needs before
  any "best score" can be trusted.
