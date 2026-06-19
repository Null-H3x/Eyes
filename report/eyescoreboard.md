# EyeScoreboard — cipher candidate ranking (methodology-audited)

*Reproduce: `python3 eyewitness/eyescoreboard.py`. Gate: `python3 noita_eye_core/selftest.py`.*

## Premise check (block-difference / depth — model-independent)

- Isomorph abundance (L=12): **51**, z=**112.1**
- Keystream scope (body): **PER-TRIPLET keystreams — only within-triplet pairs are in depth (cross z=-0.5, at the uniform baseline); each triplet has its own keystream**
  (within z=14.6, cross z=-0.5)
- Exploitable depth: **136**; E1/W1 re-sync: **5**
- **Premise tenable:** YES

## Methodology audit (ground-truth challenges)

- chain_models discrimination_audit agrees: **True**
- Real-corpus contradiction rate: per-msg **10.92%**, pure **15.01%**, free-δ **0.00%**
- Extract clean fraction invariant across models: **True**
- Shuffle-null clean fraction: **0.00%** (live **29.03%**)
- Refrain extent gap (per-msg − pure): **1**
- **Audit pass:** YES

**Challenged assumptions (expected on real corpus — not bugs):**
- extract clean/flagged counts are identical across GF models — do not treat clean fraction as a model discriminator
- refrain extent gap per-msg vs pure is only 1 — model not uniquely identified

**Triplet combine probe** (if symbols were meta-trigrams of the triplet set):
- Triplet 1: sum-mod-83 IoC=0.0130 z=0.52 (null 0.0120); digit-sum IoC=0.0100; significant=False
- Triplet 2: sum-mod-83 IoC=0.0164 z=1.99 (null 0.0121); digit-sum IoC=0.0140; significant=False
- Triplet 3: sum-mod-83 IoC=0.0151 z=1.65 (null 0.0122); digit-sum IoC=0.0084; significant=False

## Candidate ranking

| rank | id | verdict | score | real contra | clean | flagged | refrain |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | per-msg-progressive | SUPPORTED | 98 | 10.92% | 18 | 44 | 22 |
| 2 | pure-progressive | SUGGESTIVE | 58 | 15.01% | 18 | 44 | 21 |
| 3 | free-delta | PERMISSIVE | -10 | 0.00% | 18 | 44 | — |
| 4 | autokey-1 | PERMISSIVE | -10 | 0.00% | 18 | 44 | — |
| 5 | transposition | EXCLUDED | -1000 | — | — | — | — |
| 6 | prng-seed | EXCLUDED | -1000 | — | — | — | — |
| 7 | otp-unrelated | EXCLUDED | -1000 | — | — | — | — |
| 8 | monoalphabetic | EXCLUDED | -1000 | — | — | — | — |
| 9 | general-K | EXCLUDED | -1000 | — | — | — | — |
| 10 | ct-autokey-global | EXCLUDED | -1000 | — | — | — | — |
| 11 | aes-salakieli | EXCLUDED | -1000 | — | — | — | — |

## Read
- **SUPPORTED** now requires plant discrimination AND refrain extent strictly beating pure-progressive AND lower real-corpus contradiction rate.
- **SUGGESTIVE** = passes plants but model not uniquely identified on real corpus.
- Block-difference premise is model-independent; triplet **combine** does not produce structured meta-trigrams (sum mod 83 ≈ null).
- Current symbols are base-5 trigrams of individual glyphs (provenance 9/9), not a composite of the three messages in each triplet.
