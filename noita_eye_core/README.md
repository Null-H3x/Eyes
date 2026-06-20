# noita_eye_core

A single, tested home for the math shared across the three Noita eye-message
tools (EyeStat, EyeSieve, the workbench), **plus** the depth / crib-drag
keystream-recovery layer recommended in `CONVERGENCE_AND_AUDIT.md` — the natural
convergence point all three tools can feed and consume.

Everything here is validated by `selftest.py` (the math gate). Run it from this
directory:

```bash
cd noita_eye_core
python3 selftest.py            # aggregate math gate (478 checks; run for current total)
python3 classify.py            # "what TYPE of cipher is this?" on the real corpus
python3 classify.py --selftest # ground-truth checks for the classifier alone
python3 analyze.py             # depth analysis on the real corpus
```

Two front-end efforts build on this core (each with its own README):
[`../eyewitness`](../eyewitness) (the verifiable pairs-vs-triplets fingerprint,
on `grouping`) and [`../eyecrack`](../eyecrack) (depth-fed decryption, on
`oracle`).

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
| `classify` | cipher-**type** discriminator: per-family verdict with null-calibrated significance | ground-truth tested on mono/Vigenère/keystream/uniform/in-depth synthetics |
| `grouping` | message-grouping model selection (pairs vs triplets); EyeWitness core | planted pair/triplet recovery; Bron-Kerbosch clique KATs; agreement tested vs the *depth* baseline (not a shuffle) |
| `oracle` | joint multi-message calibrated verification scorer; EyeCrack core | planted-seed recovery as the unique Bonferroni hit; degenerate-null guard; vectorised-decrypt lock |
| `embedded_key` | intra-triplet "pair + key" test (Model B): is one triplet member the keystream for the other two? | recovers a planted embedded key; refutes the symmetric (global-key) case; does not false-positive on flat plaintext |

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

## Which cipher *type* is it? (`classify`)

Before spending GPU/seed budget you want to know what family of cipher you are
even fighting, and what you can formally rule out. `classify` turns "everyone
assumes polyalphabetic" into falsifiable statements, each with an explicit null
distribution, an effect size, a multiple-testing-corrected p-value, and an honest
power statement (the 3-sigma minimum detectable effect at this length/alphabet).

It runs four discriminating tests and walks a decision tree:

1. **Unigram uniformity** (IoC vs a uniform null). Monoalphabetic substitution
   *and* transposition preserve the language distribution (IoC near language-like);
   polyalphabetic/stream/random flatten it. The result is **banded**: `flat`,
   `residual` (significant but ≪ language-like), or `language_like`.
2. **Periodicity** (per-message Friedman coset-IoC lift + Kasiski). A short
   repeating key (Vigenère) lights up a period; an aperiodic keystream does not.
3. **Depth** (delegated to `depth.confirm_depth`). A shared position-keystream
   makes differencing key-free — and **rules out per-message autokey/running-key**
   (those depend on each message's own plaintext, so they would not cancel across
   messages) and a per-message OTP.
4. **Coordinate / fractionation** (per base-5-digit IoC). Careful: the most
   significant base-5 digit of a value in `0..82` is capped to `0..3`, so it is
   non-uniform *by construction*; the null samples symbols uniformly over the real
   alphabet so that encoding cap is **not** mistaken for cipher structure.

### Verdict on the real corpus (reproduce with `python3 classify.py`)

| Family | Status | Why |
|---|---|---|
| `polyalphabetic_shared_keystream` | **SUPPORTED** | in depth, difference-IoC z ≈ 60 → message-independent position keystream (fixed long key or position PRNG) |
| `monoalphabetic_substitution` / `simple_transposition` | **REFUTED** | unigram only ~9% of the way to language-like — too flat to preserve a language distribution |
| `polyalphabetic_periodic_vigenere` | **REFUTED** | no short period shows a coset-IoC lift |
| `autokey_or_running_key_per_message` | **REFUTED** | incompatible with confirmed cross-message depth |
| `random_or_one_time_pad` | **REFUTED** | column coincidence rules out per-message random keys |
| `fractionation_coordinate` | **UNDETERMINED** | no base-5 digit stands out beyond the encoding cap |

Net: the type is a **polyalphabetic cipher with a message-independent, aperiodic,
position-indexed keystream** — exactly EyeStat's keystream-hunt model plus the
`depth`/crib-drag layer — and the cheap families are formally off the table.

## How it converges with the existing tools

* `corpus.json` is verified identical to EyeStat's data (`cross_check_eyestat`).
* `prng.NollaPRNG.next_raw()` is verified equal, state-for-state, to EyeStat's
  `ParkMillerV0Rng`.
* `lm.MarkovModel` is both the candidate scorer (replacing brittle substring
  counts) and the depth solver's emission/transition model.
* `null_model` provides the calibrated significance the seed-scan needs before
  any "best score" can be trusted.
