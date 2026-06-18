# Maximal-Aligned-Isomorph Extraction — Contamination-Resistant

*Reproduce: `python3 eyewitness/iso_extract.py`. Math gate: `python3 noita_eye_core/selftest.py` (chain_extract 9/9, isomorph 19/19, chain_models 12/12, total 247/247).*

## Why this tool exists

Earlier alphabet-chaining "contradicted" on the real corpus. The cause was not (only) the cipher model — it was **contamination**. `find_isomorphs` matches by *skeleton* (repeated-letter pattern), so it returns partial/misaligned pairs: two windows with the same pattern but **different plaintext** at the singleton positions. Each such pair injects a false alphabet constraint. Strict chaining then contradicts on noise, not on signal.

This tool isolates the genuinely **fully-aligned same-plaintext** isomorphs before any model is judged.

## Mathematical header

Notation: `x[s]` = position of ciphertext symbol `s` in the cipher alphabet `C` (`x = C⁻¹`).

**Per-message-progressive constraint.** Under `c_t = C[(P_t + base_m + t) mod N]` an isomorph pair `(m1,p1)~(m2,p2)` of length `L` forces, for every aligned `i`,
```
x[c_{m2}[p2+i]] − x[c_{m1}[p1+i]] − base_{m2} + base_{m1} ≡ (p2 − p1)  (mod N).
```
A **fully aligned** pair (same plaintext at every `i`) makes these `L` constraints mutually consistent on one global alphabet; a **contaminated** pair makes divergent positions demand different offsets, so once the alphabet is anchored it **contradicts**.

**Free-δ constraint (autokey/clock).** The weakest interrelation: `x[Dᵢ] − x[Aᵢ] = δ` (one unknown constant per pair). Eliminating `δ` by subtracting position 0 gives `x[Dᵢ]−x[Aᵢ]−x[D₀]+x[A₀] ≡ 0`.

**Oracle separation (verified, `selftest`).** Given the *true* alphabet, per-message-progressive separates genuine from contaminated essentially perfectly: on a planted corpus all 1388 genuine pairs reduce to *redundant* and 2683/2684 contaminated pairs reduce to *contradiction*. So the only hard part is bootstrapping a correct alphabet.

**Anchor-then-classify.**
1. **Calibrate** a clean anchor threshold = the highest `min_repeats` at which the shuffle-null isomorph count is ≈ 0.
2. **Robust consensus** from the anchor set: purify-to-fixed-point is initialisation-dependent (a single greedy order can land in a *wrong basin*), so we run several deterministic restarts and keep the alphabet that **explains the most anchor pairs** (the correct alphabet explains far more than any wrong basin).
3. **Classify** the broad isomorph set against the anchored alphabet: clean ⟺ every constraint already implied; contaminated ⟺ any contradiction.
4. **Maximalise** clean windows into maximal aligned runs; recover the alphabet up to rotation.

**Honest recovery measure.** An alphabet is a bijection, so a genuine recovery gives **distinct** positions for distinct symbols (up to one global rotation). Free / under-determined variables collapse onto position 0, so a low `distinct / linked` ratio means the alphabet is only *linked*, **not ordered**.

## Paranoia audit (`chain_extract.selftest`: 9/9; GF primitives in `isomorph.selftest`)

- [PASS] oracle: all genuine pairs are redundant under the true alphabet; <1 % of contaminated survive.
- [PASS] `rows_fn` builds the **same GF** as the validated `per_message_progressive_chain` (single source of truth, no drift).
- [PASS] `GFSystem.classify()` agrees **exactly** with `add()`-on-a-copy (0/1500 mismatches); `snapshot()/restore()` is an exact round-trip.
- [PASS] clean set high-precision vs the **reconstructed true plaintext** (independent ground truth, not a position heuristic) — **min 0.999 across all seeds**.
- [PASS] **held-out generalisation**: an alphabet trained on half the genuine pairs predicts **698/698** unseen genuine pairs as redundant and rejects **0/2259** contaminated — it generalises, it does not memorise.
- [PASS] injective near-full recovery (ratio ≥ 0.95, ≥ 60 symbols) on true-model data **across all seeds**.
- [PASS] parameter-robust (precision 1.000 across N = 83/89/101, varying M/T) and **bit-identical across separate processes**.
- [PASS] GF requires a **prime modulus** (Fermat inverse) — guarded; corpus N = 83 is prime.
- [PASS] **multi-restart consensus escapes the wrong basin** — on the known bad-seed the single greedy order explains 66 pairs (wrong alphabet) while the restart that explains 1040 recovers `C` up to one rotation.
- [PASS] maximalisation does not fabricate misaligned runs (precision ≥ 0.95 vs ground truth).
- [PASS] extraction is deterministic.
- [PASS] **PERMISSIVE (honest limit):** per-message-progressive ALSO recovers a sizable injective alphabet from **autokey** data — so a recovered order is NOT evidence for the model.

Stress test (planted, 66 %-contaminated, 3499 windows / 1388 genuine): recovers the genuine set at **precision ≈ 1.000 (true-plaintext ground truth), recall 1.000** and the full 83-symbol alphabet up to a single rotation.

## Real-corpus result (9 messages, N = 83, L = 13, anchor min_rep = 4)

| model | clean | flagged | linked | distinct | ordered? | maximal runs |
|---|---|---|---|---|---|---|
| per-message-progressive | 18 | 44 | 22 | 19 | no (0.86) | 6 |
| free-δ (autokey/clock) | 18 | 44 | 22 | 1 | no (0.05) | 6 |

**Contamination filtering is model-robust:** both models flag the **identical** 44 of 62 broad isomorphs (Jaccard 1.0) as inconsistent with the clean anchor — so the clean set does not depend on the cipher-model assumption.

**Maximal aligned isomorphs (clean set).** A tight cluster of long aligned runs across messages 1 and 2:

```
m1@38 ~ m1@68  len=15
m1@38 ~ m2@43  len=15
m1@38 ~ m2@78  len=15
m1@68 ~ m2@43  len=15
m1@68 ~ m2@78  len=15
m2@43 ~ m2@78  len=15
```

## Verdict — solid vs not

- **SOLID:** the clean maximal-aligned isomorphs are contamination-filtered (validated precision ≥ 0.95 on planted ground truth). They are the trustworthy anchors / depth pairs for any further attack.
- **SOLID:** contamination filtering is **model-robust** — per-message-progressive and free-δ produce the identical clean/contaminated split.
- **NOT achieved / permissive:** alphabet **ordering** is not pinned and, where an order is produced, it is permissive — the same machinery orders a comparable alphabet from autokey data (validated). So a recovered order is a **candidate to test, not evidence for the model**. Per-message-progressive orders ~19 of 22 linked symbols; free-δ orders almost none.
- **NOT decisive on model:** isomorphs cannot crown per-message-progressive over autokey/clock.

**On a plaintext "find/decrypt" search:** still a step beyond this. Reading out plaintext requires the *full* ordered alphabet plus a mapping anchor (one known symbol→letter). The extractor delivers contamination-filtered anchors and a partial, model-ambiguous linkage — not an order — so a decryption search would currently return nothing meaningful. The next lever is **indirect-symmetry / cross-anchor chaining** plus an external mapping anchor.
