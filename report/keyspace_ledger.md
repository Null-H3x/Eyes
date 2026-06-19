# Keyspace Ledger — deduced from validated block structure

*Reproduce: `python3 eyewitness/keyspace_ledger.py`*

## Surviving construction

`c[m][t] = C[(p[m][t] + base_m + K_g[t]) mod 83]`

## Live measurements

- Body keystream scope: **PER-TRIPLET keystreams — only within-triplet pairs are in depth (cross z=-0.5, at the uniform baseline); each triplet has its own keystream** (cross z=-0.47, within z=14.65)
- Full-overlap cross z (confounded): 5.09
- Exploitable 2-deep positions: **136**
- E1/W1 re-sync events: **5** (excludes ciphertext-autokey)
- Literal header positions: [1, 2]

## Triplet near-duplicate pairs

| triplet | near-dup | odd | body agree | runs z |
|---|---|---|---|---|
| 1 | East 1/West 1 | East 2 | 44.4% | -7.55 |
| 2 | West 2/West 3 | East 3 | 7.8% | -4.76 |
| 3 | East 4/East 5 | West 4 | 27.2% | -7.89 |

## Body-proven shared keystream pairs

- East 1/West 1: z=20.4, exploitable=54
- East 4/East 5: z=9.4, exploitable=82

## Hypothesis keyspace ledger

| id | hypothesis | keyspace | status | searchable |
|---|---|---|---|---|
| 1 | Progressive + per-msg bases | ~83^6 with pair clustering | FITS | True |
| 2 | General aperiodic K per triplet | 83^300 approx | FITS | False |
| 5 | PRNG seed x GAK | ~3.4e11 | MOOT (offline author) | False |
| 8 | Ciphertext-autokey | — | EXCLUDED | False |
| 9 | Mono/Vigenere/AES/OTP/transposition | — | EXCLUDED | False |

## Search priority

1. Per-triplet progressive + clustered bases
2. Refrain/template plaintext (pins C)
3. Position-0 indicator -> base_m
4. General K_g after #1 fails with calibrated null
