# EyeCrack

**Decryption attacks on the Noita eye corpus — fed by [EyeWitness](../eyewitness).**

EyeCrack is Effort B: the *bet*. It tries to actually recover plaintext, using
the depth structure EyeWitness confirms. Where EyeWitness produces a true result
no matter what, EyeCrack may never converge — but everything it does routes
through a **calibrated joint oracle** so that a candidate is only ever called a
"hit" if it survives a Bonferroni correction for the entire search. That trust
gate is the piece the community's unconstrained seed scans have lacked.

## The core idea

The 9 messages share one position-indexed keystream (EyeWitness/`depth`). So a
candidate keystream isn't scored against one message — it must make **every
in-depth message decrypt to language-like plaintext simultaneously**. Pooling 9
messages multiplies the signal: the true keystream's z-score grows like
`sqrt(total_symbols)`, while wrong keystreams stay at the noise floor. The oracle
([`noita_eye_core/oracle.py`](../noita_eye_core/oracle.py)) builds an empirical
null from random keystreams and reports a z, an analytic (CLT) p-value, and a
Bonferroni q-value for the number of candidates tried.

## Three prongs (cheap → expensive)

| Prong | Needs LM? | On the real corpus today |
|---|---|---|
| `crib` | no | **exact, works now** |
| `viterbi` | yes (symbol-space) | under-determined on a flat unigram; use with a real LM/mapping |
| `seedscan` | yes | runs; the GPU target |

### `crib` — exact crib-drag (no language model)

A guessed plaintext fragment over a span pins the shared keystream there, and
because the key is shared it reveals that span in **every** message at once. Feed
it the equal-span cribs EyeWitness found (e.g. `E1+W1+E2` share an identical
24-symbol run at positions 1–24):

```bash
python3 eyecrack.py crib --ref "East 1" --start 0 --plain 10,20,30,40,5
python3 eyecrack.py crib --fingerprint ../eyewitness/fingerprint.json  # list cribs
```

### `seedscan` — calibrated PRNG brute force (the GPU target)

```bash
python3 eyecrack.py seedscan --prng nolla --seed-start 0 --count 1000000 --mode add
```

For each seed it generates a keystream (faithful `NollaPRNG` or a generic
stream), decrypts all in-depth messages, scores them, and runs the calibrated
oracle on the top survivors with Bonferroni over the whole window. A null result
is reported as a null result — *"no seed in this window survives correction"* —
which is itself information.

**GPU hand-off (your RTX 5080 / Threadripper).** The per-seed work
— keystream-gen + decrypt + cheap score — is exactly the kernel structure EyeStat
already runs on the GPU; the calibrated survivor test is the CPU stage. This CPU
reference does ~3000 seeds in under a second including null calibration, so the
full 2³² space is a GPU job. Point EyeStat's kernels at `oracle.JointOracle` as
the scoring backend to inherit the trust gate.

### `viterbi` — globally optimal keystream under a 1st-order model

```bash
python3 eyecrack.py viterbi --lm planted --mode add
```

Exact MAP given the model. On the real corpus the unigram is flat, so
unsupervised Viterbi is under-determined (see `noita_eye_core/README`) — trust the
`crib` prong, and use this once a real LM/mapping is supplied.

## Proof it works: `demo`

```bash
python3 eyecrack.py demo
# plants a NollaPRNG seed, scans a window, recovers it uniquely:
#   seed 1234567   z=31.44  q=1.1e-214  trustworthy=True  <== planted
#   recovered the planted seed uniquely: True
```

This is the end-to-end validation that the pipeline (PRNG → keystream → joint
oracle → calibrated verdict) is correct: a planted seed is recovered as the
**unique** Bonferroni-significant hit, and decoys are correctly rejected.

## Honesty

The LM-based prongs are only as good as the supplied language model. In symbol
space a model needs symbol-space training text, which for the real corpus is
unknown without a rune→letter mapping — EyeStat's Hungarian mapping + dictionary
scorer is the production answer there, and `oracle.JointOracle` is scorer-agnostic
so it can wrap that. The `crib` prong needs no LM and is exact today. The math
core (`oracle.py`) is validated by the package gate
(`python3 noita_eye_core/selftest.py`) including an end-to-end planted-seed
recovery; it does **not** claim the real plaintext.

## Input contract

EyeCrack reads `../eyewitness/fingerprint.json` when present:
`for_eyecrack.in_depth_set` (which messages must agree), `combiner_candidates`,
and `cribs`. Without it, EyeCrack derives the in-depth set itself via
`depth.confirm_depth`.
