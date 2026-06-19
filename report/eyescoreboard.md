# EyeScoreboard — cipher candidate ranking

*Reproduce: `python3 eyewitness/eyescoreboard.py`. Gate: `python3 noita_eye_core/selftest.py`.*

## Premise check (block-difference / depth model-independent)

- Isomorph abundance (L=12): **51** windows, **z=112.1**
- Keystream scope (body): **PER-TRIPLET keystreams — only within-triplet pairs are in depth (cross z=-0.5, at the uniform baseline); each triplet has its own keystream** (within z=14.6, cross z=-0.5)
- Exploitable 2-deep positions: **136**
- E1/W1 re-sync events: **5**
- Body-proven depth pairs: **2**
- **Premise tenable:** YES

## Candidate ranking (higher score = better fit; not proof of author cipher)

| rank | id | verdict | score | clean | flagged | recovery | refrain L | null p |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | per-msg-progressive | SUPPORTED | 105 | 18 | 44 | 0.86 | 22 | 0.003 |
| 2 | pure-progressive | SUPPORTED | 98 | 18 | 44 | 0.86 | 21 | 0.003 |
| 3 | free-delta | PERMISSIVE | 10 | 18 | 44 | 0.04 | — | — |
| 4 | autokey-1 | PERMISSIVE | 10 | 18 | 44 | 0.04 | — | — |
| 5 | transposition | EXCLUDED | -1000 | — | — | — | — | — |
| 6 | prng-seed | EXCLUDED | -1000 | — | — | — | — | — |
| 7 | otp-unrelated | EXCLUDED | -1000 | — | — | — | — | — |
| 8 | monoalphabetic | EXCLUDED | -1000 | — | — | — | — | — |
| 9 | general-K | EXCLUDED | -1000 | — | — | — | — | — |
| 10 | ct-autokey-global | EXCLUDED | -1000 | — | — | — | — | — |
| 11 | aes-salakieli | EXCLUDED | -1000 | — | — | — | — | — |

## Detail

### 1. `per-msg-progressive` — Per-message progressive + per-triplet K
- **Verdict:** SUPPORTED (score **105**)
- **Family:** `c[m][t]=C[(p+base_m+K_g[t])]`
- **Keyspace:** ~83^6 bases (clustered); searchable=True
- **Plant discrim:** own=True, reject-autokey=True, reject-two-alphabet=True
- **Notes:** clean fraction 29%; pure-progressive nearly as deep

### 2. `pure-progressive` — Pure progressive (no per-message base)
- **Verdict:** SUPPORTED (score **98**)
- **Family:** `c[t]=C[(p+t)] global slide`
- **Keyspace:** header-forced subcase; searchable=False
- **Plant discrim:** own=True, reject-autokey=True, reject-two-alphabet=True
- **Notes:** clean fraction 29%; pure-progressive nearly as deep

### 3. `free-delta` — Free-δ / autokey-1 interrelation
- **Verdict:** PERMISSIVE (score **10**)
- **Family:** `x[D]-x[A]-x[D0]+x[A0]=0 per pair`
- **Keyspace:** per-pair δ absorbs all; searchable=False
- **Plant discrim:** own=True, reject-autokey=False, reject-two-alphabet=False
- **Notes:** permissive on control plants; clean fraction 29%

### 4. `autokey-1` — Ciphertext autokey lag-1 (chaining)
- **Verdict:** PERMISSIVE (score **10**)
- **Family:** `c[t]=p[t]+c[t-1]`
- **Keyspace:** per-pair δ; ≡ free-δ; searchable=False
- **Plant discrim:** own=True, reject-autokey=False, reject-two-alphabet=False
- **Notes:** equivalent to free-δ on plants (chain_models proof); permissive on control plants; clean fraction 29%

### 5. `transposition` — Transposition / periodic block
- **Verdict:** EXCLUDED (score **-1000**)
- **Family:** `permute positions`
- **Keyspace:** —; searchable=False
- **Notes:** repeat_census excluded

### 6. `prng-seed` — PRNG seed × GAK
- **Verdict:** EXCLUDED (score **-1000**)
- **Family:** `small integer seed`
- **Keyspace:** ~3.4e11; searchable=False
- **Notes:** moot: offline author; provenance

### 7. `otp-unrelated` — OTP / unrelated alphabet columns
- **Verdict:** EXCLUDED (score **-1000**)
- **Family:** `independent decks`
- **Keyspace:** 83^L; searchable=False
- **Notes:** isomorphs forbid unrelated alphabets

### 8. `monoalphabetic` — Monoalphabetic substitution
- **Verdict:** EXCLUDED (score **-1000**)
- **Family:** `c=C[p]`
- **Keyspace:** 83!; searchable=False
- **Notes:** flat unigram; classify excluded

### 9. `general-K` — General aperiodic K per triplet
- **Verdict:** EXCLUDED (score **-1000**)
- **Family:** `K_g[t] arbitrary`
- **Keyspace:** 83^300; searchable=False
- **Notes:** fits but not searchable

### 10. `ct-autokey-global` — Global ciphertext-autokey body
- **Verdict:** EXCLUDED (score **-1000**)
- **Family:** `keystream=c[t-1]`
- **Keyspace:** —; searchable=False
- **Notes:** E1/W1 re-sync=5 excludes CT-autokey

### 11. `aes-salakieli` — AES-128-CTR (salakieli)
- **Verdict:** EXCLUDED (score **-1000**)
- **Family:** `N=256 block`
- **Keyspace:** —; searchable=False
- **Notes:** N=83; decrypts to noise

## Read
- **Premise OK** means model-independent structure (isomorphs, triplet depth, re-sync) still supports ciphertext-plaintext *difference* attacks — not that any one cipher formula is confirmed.
- **SUPPORTED / SUGGESTIVE** means the model passes planted controls and beats permissive alternatives — still not unique on the real corpus (see model_audit).
- **PERMISSIVE** models (free-δ, autokey-1) fit even wrong plants — do not use for contamination filtering.
- **EXCLUDED** rows are kept as regression gates; they should never rank above live GF models.
