# Maximal-Aligned-Isomorph Extraction — Contamination-Resistant

*Reproduce: `python3 eyewitness/iso_extract.py`. Math gate: `python3 noita_eye_core/selftest.py` (chain_extract 9/9, total 245/245).*

## Why this tool exists

Earlier alphabet-chaining "contradicted" on the real corpus. The cause was not (only) the cipher model — it was **contamination**. `find_isomorphs` matches by *skeleton* (repeated-letter pattern), so it returns partial/misaligned pairs: two windows with the same pattern but **different plaintext** at the singleton positions. Each such pair injects a false alphabet constraint. Strict chaining then contradicts on noise, not on signal.

This tool isolates the genuinely **fully-aligned same-plaintext** isomorphs before any model is judged.

## Mathematical header

Notation: `x[s]` = position of ciphertext symbol `s` in the cipher alphabet `C` (`x = C⁻¹`).

**Per-message-progressive constraint.** Under `c_t = C[(P_t + base_m + t) mod N]` an isomorph pair `(m1,p1)~(m2,p2)` of length `L` forces, for every aligned `i`,
```
x[c_{m2}[p2+i]] − x[c_{m1}[p1+i]] − base_{m2} + base_{m1} ≡ (p2 − p1)  (mod N).
```
For a **fully aligned** pair (same plaintext at every `i`) these `L` constraints are mutually consistent on one global alphabet; for a **contaminated** pair the divergent positions demand different offsets and the constraints **contradict** once the alphabet is anchored.

**Oracle separation (verified).** Given the *true* alphabet, per-message-progressive separates genuine from contaminated essentially perfectly: on a planted corpus every one of 1388 genuine pairs reduces to *redundant* (already implied) and 2683/2684 contaminated pairs reduce to *contradiction*. So the only hard part is bootstrapping a correct alphabet.

**Anchor-then-classify.**
1. **Calibrate** a clean anchor threshold = the highest `min_repeats` at which the shuffle-null isomorph count is ≈ 0. High-repeat skeletons are specific to genuine repeats, so the anchor set is nearly contamination-free.
2. **Consensus alphabet** from the anchor set by purify-to-fixed-point: solve (dropping contradictions), keep only fully-redundant pairs, re-solve, repeat.
3. **Classify** the broad isomorph set against the anchored alphabet: clean ⟺ every constraint already implied; contaminated ⟺ any contradiction.
4. **Maximalise**: merge clean windows sharing `(m1,m2,p2−p1)` and overlapping into maximal aligned runs; recover the alphabet up to rotation.

**Honest recovery measure.** An alphabet is a bijection, so a genuine recovery gives **distinct** positions for distinct symbols (up to one global rotation). Free / under-determined variables collapse onto position 0, so a low `distinct / linked` ratio means the alphabet is only *linked*, **not ordered**.

## Paranoia audit (`chain_extract.selftest`: 9/9)

- [PASS] oracle: all genuine pairs are redundant under the true alphabet
- [PASS] oracle: <1% of contaminated pairs survive the true alphabet
- [PASS] anchor calibrated to a clean threshold (null ratio < 0.1)
- [PASS] extractor flags the bulk of contamination
- [PASS] recovers a large alphabet up to a SINGLE rotation (planted data)
- [PASS] recovery is INJECTIVE on clean data (distinct positions, ratio ~1)
- [PASS] clean set is high-precision (≥ 0.95) against ground truth
- [PASS] per-msg-prog yields far fewer clean windows on autokey data (discrimination preserved)
- [PASS] autokey alphabet is NOT injectively recovered (low distinct-position ratio)

Stress test (planted, deterministic): from a **66 %-contaminated** isomorph set (3499 windows, 1388 genuine) the extractor recovers the genuine set at **precision 0.996, recall 1.000** and recovers all 83 symbols up to a single rotation.

## Real-corpus result (9 messages, N = 83, L = 13)

| model | clean | flagged | linked | distinct | ordered? | maximal runs |
|---|---|---|---|---|---|---|
| per-message-progressive | 29 | 33 | 40 | 12 | no (0.30) | 11 |
| free-δ (autokey/clock) | 62 | 0 | 62 | 1 | no (0.02) | 18 |

**Maximal aligned isomorphs (per-msg-progressive clean set).** A tight cluster of long, mutually-isomorphic runs around the message bodies:

```
m1@36 ~ m2@41  len=18
m0@36 ~ m0@64  len=16
m1@36 ~ m2@76  len=15
m2@41 ~ m2@76  len=15
m0@36 ~ m2@41  len=14
m0@36 ~ m2@76  len=14
m0@64 ~ m1@36  len=14
m0@64 ~ m2@41  len=14
m0@64 ~ m2@76  len=14
m6@50 ~ m7@52  len=14
m0@36 ~ m1@36  len=13
```

## Verdict — solid vs not

- **SOLID (new):** the clean maximal-aligned isomorphs above are contamination-filtered (validated precision ≥ 0.95 on planted ground truth). They are the trustworthy anchors / depth pairs for any further attack. The corpus contains a *dense* family of long aligned repeats concentrated at positions ~36–78 of messages 0/1/2 — the strongest structural foothold found so far.
- **SELECTIVE, as designed:** per-message-progressive keeps a self-consistent subset and **flags 33/62** isomorphs; free-δ flags none (it is permissive — it fits any isomorph). So the extractor is genuinely discriminating, not curve-fitting.
- **NOT achieved:** the alphabet is **only linked, not ordered**. Under per-message-progressive the 40 linked symbols collapse onto 12 distinct positions (ratio 0.30); under free-δ onto 1. Isomorphs constrain the alphabet but do not pin its order — consistent with the prior finding that **ordering is the open step**.
- **NOT decisive on model:** because free-δ also fits, isomorphs alone cannot crown per-message-progressive as *the* cipher. The 33 flagged isomorphs are either contamination or a genuinely non-positional interrelation.

**On a plaintext "find/decrypt" search:** it is a step beyond this. Reading out plaintext requires the *full* alphabet order plus a mapping anchor (one known symbol→letter). The extractor delivers anchors and a partial linkage, but not an order, so a decryption search would currently return nothing meaningful. The next lever is **indirect-symmetry / cross-anchor chaining** to convert "linked" into "ordered".
