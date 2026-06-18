# Chaining Audit — Autokey vs Per-Message-Progressive

*Generated 2026-06-18 01:06:05 UTC. Reproduce: `python3 eyewitness/chaining_audit.py`. Math gate: `python3 noita_eye_core/selftest.py`.*

## Mathematical header

Notation: `x[s]` = position of ciphertext symbol `s` in the cipher alphabet `C` (i.e. `x = C⁻¹`). An **isomorph** is a pair of ciphertext segments with the same repeated-letter pattern; under interrelated alphabets it arises from the **same plaintext** enciphered with related alphabets.

**Model A — ciphertext-autokey, offset k.** `y_t = x[c_t]`, and `y_t − y_{t−k} = P_t` (plaintext). For an isomorph pair the constraint reduces to `f_i = f_{i−k}` where `f_i = x[c_{m2}[p2+i]] − x[c_{m1}[p1+i]]`. For **k = 1** this is `f_i = f_{i−1}` ⟹ `f_i = const` — **identical to free-δ chaining** (one free constant offset per pair). Hence autokey-1 is PERMISSIVE and cannot discriminate; this report verifies that equivalence empirically.

**Model B — per-message progressive.** `c_t = C[(P_t + base_m + t)]`, so `x[c] = P_t + base_m + t`, giving the per-pair offset `δ = (p2 − p1) + (base_{m2} − base_{m1})` with only `M` (=9) free message bases. This FORCES a positional structure; data not of this form over-determines the 9 bases and contradicts. `base_m` is also the natural home for the position-0 indicator.

**Discrimination principle.** A model is trustworthy only if it is consistent on data of its own form AND contradicts data of other forms. Free-δ / autokey-1 fail this (permissive). Per-message-progressive passes it on clean ground-truth pairs (below).

**Contamination caveat.** `find_isomorphs` matches by skeleton, so it returns some partial/misaligned pairs (same pattern, different plaintext at singleton positions). These inject false constraints that strict models (B) reject and permissive models (A) absorb. We therefore CALIBRATE the real-corpus contradiction rate against the same models run on contaminated plants of known truth.

## Paranoia audit (validated on clean ground-truth pairs)

`chain_models.selftest()`: **12/12 passed**.

- [PASS] GF solve: x1-x0=5, x2-x1=7 -> x2-x0=12
- [PASS] GF solve back-substitution correct
- [PASS] autokey-1 == free-δ (same contradictions)
- [PASS] autokey-1 == free-δ (same redundancy)
- [PASS] per-msg-prog: consistent on its own plant
- [PASS] per-msg-prog: over-determined on its own plant
- [PASS] per-msg-prog: recovers C up to rotation on its own plant
- [PASS] DISCRIM: per-msg-prog CONSISTENT on per-msg-prog plant
- [PASS] DISCRIM: per-msg-prog CONTRADICTS autokey plant
- [PASS] DISCRIM: per-msg-prog CONTRADICTS two-alphabet plant
- [PASS] DISCRIM: autokey-1 permissive (consistent on per-msg-prog plant)
- [PASS] DISCRIM: autokey-1 permissive (consistent on two-alphabet plant)

## Calibration — models on CONTAMINATED plants (known truth)

Each plant is a known cipher with the same plaintext repeated at several positions; we run `find_isomorphs` (NOT clean pairs) to mirror the real-corpus condition. **Key observation:** the per-msg-prog rate is high even on its OWN truth data — `find_isomorphs` partial/misaligned matches dominate and inject false constraints that the strict model rejects. This is the central obstacle (and explains why classical alphabet-chaining 'has not been completely successful').

| plant (truth) | L/mr | pairs | autokey-1 rate | per-msg-prog rate |
|---|---|---|---|---|
| per-msg-prog (truth) | 12/3 | 3759 | 0.000 | 0.910 |
| per-msg-prog (truth) | 14/4 | 637 | 0.000 | 0.775 |
| autokey (truth) | 12/3 | 1047 | 0.000 | 0.768 |
| autokey (truth) | 14/4 | 1047 | 0.000 | 0.852 |
| two-alphabet (truth) | 12/3 | 1979 | 0.000 | 0.077 |
| two-alphabet (truth) | 14/4 | 1266 | 0.000 | 0.090 |

## Real corpus

| L | min_rep | pairs | autokey-1 rate | per-msg-prog rate |
|---|---|---|---|---|
| 10 | 3 | 34 | 0.000 | 0.324 |
| 12 | 3 | 51 | 0.000 | 0.332 |
| 14 | 3 | 74 | 0.000 | 0.225 |
| 14 | 4 | 24 | 0.000 | 0.000 |
| 16 | 4 | 38 | 0.000 | 0.003 |

## Verdict (honest)

1. **Autokey-offset-1 chaining ≡ free-δ chaining** — proven above (identical contradictions/redundancy). It is PERMISSIVE and identifies nothing; autokey-1 rate ≈ 0 everywhere is expected and uninformative.

2. **Per-message-progressive is a validated discriminator on CLEAN ground-truth pairs** (paranoia audit: it recovers C up to rotation on its own plant and CONTRADICTS autokey / two-alphabet). The model and solver are correct.

3. **But it cannot be cleanly applied to the real corpus.** The discriminating isomorphs are the DIFFERENT-position ones, and those are exactly the ones `find_isomorphs` contaminates with partial/misaligned matches — the calibration shows even a true per-msg-prog plant scores ~0.8 contradictions under `find_isomorphs`. So a high real-corpus rate cannot be read as 'refuted', and the low rate at the strictest thresholds (few, cleaner pairs) is SUGGESTIVE but NOT conclusive.

4. **The real bottleneck is clean isomorph extraction** — recovering MAXIMAL, fully-aligned, same-plaintext segments (not mere skeleton matches). That is the prerequisite for any chaining to settle the interrelation/ordering, and it is the genuinely hard open sub-problem.

Net established (this audit): interrelated, non-positional alphabets (from `isomorph`); autokey-1 = free-δ = permissive (proven here); per-msg-progressive = a sound discriminator that the corpus's contaminated isomorphs leave INCONCLUSIVE. Not snake-oil, not a false 'solved'.
