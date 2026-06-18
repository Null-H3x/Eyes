# Paranoia Audit — `noita_eye_core` + EyeWitness + EyeCrack

**Scope.** A deliberately adversarial review of all math in `noita_eye_core`
(11 modules) and the two front-end efforts built on it — **EyeWitness** (the
verifiable pairs-vs-triplets fingerprint) and **EyeCrack** (depth-fed
decryption). The goal was not to confirm the happy path but to *break* it:
construct inputs designed to trip false positives, degenerate statistics, and
multiple-testing illusions, and fix whatever broke.

**Result.** Two latent bugs found and fixed (both over-claiming hazards), several
assumptions made explicit and guarded with regression tests, and every
foundational KAT re-verified from scratch. Final gate: **99/99** checks across
11 modules.

```
corpus 6 · cipher_ops 6 · stats 9 · lm 6 · null_model 8 · prng 10 ·
trigram 8 · depth 9 · classify 14 · grouping 13 · oracle 10   =  99/99
```

---

## Methodology

Three independent layers, all distribution-free where possible:

1. **Ground truth** — every statistical claim is validated on synthetic data
   whose answer is *known by construction* (planted cipher type, planted
   grouping, planted keystream/seed). A test that can't recover a planted truth
   is not trusted to judge the real corpus.
2. **KATs** — fixed published constants (MINSTD 10000th iterate = `1043618065`),
   hand-computed IoC/add-k values, and known-graph clique enumerations.
3. **Adversarial probes** — inputs engineered to *manufacture* a false positive
   (degenerate nulls, encoding-cap artifacts, depth-vs-grouping confounds,
   majority-link baselines). These are the audit's core and are summarised below.

Everything is seeded and deterministic; determinism was itself checked
(`classify` and `grouping` reproduce bit-for-bit on re-run).

---

## Findings & fixes

### [M] EyeCrack `oracle` — false confidence on a degenerate/under-sampled null

The joint oracle converts a candidate keystream's score to significance via the
z-score, then a Bonferroni-corrected analytic (normal-tail) p-value. **Probe:** a
null with zero spread (sd = 0) and an observation above its mean produces
`z = +inf → p = 0 → q = 0`, i.e. *infinite* confidence from a degenerate null —
exactly the multiple-testing illusion the oracle exists to prevent.

**Fix.** (1) The analytic p is used only when `null_std > 0` and `z` is finite;
otherwise it falls back to the conservative empirical p (floored at
`1/(n_null+1)`), which a large trial budget correctly defeats. (2) Added an
empirical `exceeds_null` gate — a candidate is `trustworthy` only if it *also*
strictly beats every null sample. Regression test added (`degenerate null is not
over-claimed`); it fails on the pre-fix code and passes after. The real-data path
(LM scores always have spread) is unchanged — the planted-seed recovery still
flags the true seed as the unique hit.

### [M] EyeWitness `grouping` — agreement must be tested vs the *depth* baseline

(Found and fixed during development; documented here as the central soundness
point.) The natural null for "do these two messages agree more than chance?" is a
within-message shuffle — but that destroys the **shared-keystream alignment**, so
it tests for *depth* (which every pair already has, z ≈ 57) and flags **all 36
pairs**. The grouping signal lives *above* the depth collision rate.

**Fix.** Agreement is tested against a `Binomial(overlap, q_depth)` null, with
`q_depth` the robust (median) pairwise equal-rate. A within-message shuffle is
*never* used for grouping. The earlier Monte-Carlo p-value floor was also too
coarse to survive BH across 36 pairs, so the per-pair test is the closed-form
normal-tail binomial. Validated on planted pair/triplet/no-structure corpora.

### [A] Assumptions made explicit and guarded

* **`grouping.depth_baseline_rate` median assumption.** The median pairwise rate
  is a *cross-pair* (no-grouping) rate only while linked pairs are a **minority**
  of all `C(n,2)`. Probe confirmed it degrades if a majority of pairs are linked
  (a 7-of-9 group pushes the baseline to a link rate). For the real corpus the
  two theories link 9/36 (triplets) or 4/36 (pairs) — safely a minority — and a
  regression test pins this.
* **`classify` base-5 MSB encoding cap.** The most-significant base-5 digit of a
  value in `0..82` is capped to `0..3` (`82 // 25 = 3`), so its IoC ≈ 0.281 *by
  construction*. The digit null samples over the real alphabet so this cap is not
  mistaken for cipher structure; two regression tests guard it.
* **`classify` unigram banding.** A statistically-significant but near-flat IoC
  (real corpus: ~9 % toward language-like) is banded `residual` and **refutes**
  monoalphabetic/transposition rather than supporting it.
* **`oracle` analytic-p normality.** The pooled per-symbol score is a mean over
  ~1000 symbols, so the CLT justifies the normal-tail p; the `exceeds_null` gate
  is the empirical backstop if the tail is heavier than normal.

### [N] Noted, not changed

* `grouping.compare_partitions` ranks only **named** partitions; all *structured*
  candidates use exactly two parameters (`q_link`, `q_unlink`), so raw
  log-likelihood comparison is fair (no AIC/BIC penalty needed). It is not an
  exhaustive search over all partitions — the unsupervised clique decomposition
  is the cross-check, and on the real corpus it independently recovers the
  consecutive triplets `[E1,W1,E2]` and `[E4,W4,E5]`.
* `oracle` on the *real* corpus needs a symbol-space LM, which is unknown without
  a rune→letter mapping (EyeStat's Hungarian mapping is the production answer;
  the oracle is scorer-agnostic and can wrap it). The exact `crib` prong needs no
  LM and is the trustworthy real-corpus lever today.

---

## Foundational KATs re-verified

| Check | Result |
|---|---|
| MINSTD 10000th iterate (`minstd_iterate` **and** `NollaPRNG.next_raw`) = 1043618065 | PASS |
| `cipher_ops` full `83×83` encrypt/decrypt/recover round-trip (all 3 modes) | PASS |
| `stats` difference-IoC is key-invariant | PASS |
| `null_model` BH monotone + flags the strong hit only | PASS |
| `trigram` base-5 round-trip for all `0..124` | PASS |
| `oracle` vectorised decrypt == `cipher_ops` (all 3 modes) | PASS |
| `grouping` Bron-Kerbosch cliques on known graphs | PASS |

---

## Bottom line

The defaults are mathematically sound. The two fixes both removed *over-claiming*
paths (the more dangerous direction for a puzzle this politically charged): the
tools now under-claim before they over-claim. Every headline — depth (z ≈ 57),
**triplets over pairs** (ΔlogL ≈ 76, E5 not special), the planted-seed recovery —
is reproducible, null-calibrated, and independently re-derivable
(`eyewitness/verify_fingerprint.py`, numpy only).
