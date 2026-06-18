# Maximal-Aligned-Isomorph Extractor — Comprehensive Paranoia Audit

*Reproduce: `python3 eyewitness/iso_extract_audit.py --seeds 8`. Gate: `python3 noita_eye_core/selftest.py`.*

## 1. GF primitives (the engine the whole extractor rests on)

- `classify()` vs `add()`-on-copy mismatches: **0/4000** (OK)
- `snapshot()/restore()` exact round-trip: **True**

## 2. True-model extraction across seeds (precision / recovery)

| seed | clean | precision | recall | linked | distinct | ratio |
|---|---|---|---|---|---|---|
| 0 | 1196 | 0.998 | 0.858 | 79 | 79 | 1.00 |
| 1 | 1198 | 0.997 | 0.856 | 81 | 81 | 1.00 |
| 2 | 1392 | 0.994 | 1.000 | 83 | 82 | 0.99 |
| 3 | 1081 | 0.995 | 0.775 | 75 | 75 | 1.00 |
| 4 | 1215 | 0.998 | 0.873 | 80 | 80 | 1.00 |
| 5 | 1383 | 0.992 | 1.000 | 81 | 81 | 1.00 |
| 6 | 1350 | 0.996 | 0.963 | 80 | 80 | 1.00 |
| 7 | 1169 | 0.992 | 0.841 | 80 | 80 | 1.00 |

- **min precision = 0.992**, min recall = 0.775, min recovery ratio = 0.988, min distinct = 75
- Verdict: contamination filtering is high-precision and recovery is injective on true-model data across all 8 seeds.

## 3. Wrong-basin robustness (why multi-restart consensus matters)

| seed | single-order explained | multi-restart explained | anchor pairs |
|---|---|---|---|
| 0 | 349 | 349 | 351 |
| 1 | 349 | 349 | 349 |
| 2 | 66 | 1040 | 1072 |
| 3 | 348 | 348 | 352 |
| 4 | 347 | 347 | 374 |
| 5 | 1375 | 1375 | 1410 |
| 6 | 349 | 349 | 349 |
| 7 | 345 | 345 | 345 |

- A single greedy order can land in a wrong basin (low explained count); the multi-restart consensus selects the alphabet that explains the most pairs.

## 4. Permissiveness limit — recovery is NOT model identification

| seed | autokey clean | autokey linked | autokey distinct | ratio |
|---|---|---|---|---|
| 0 | 90 | 80 | 80 | 1.00 |
| 1 | 49 | 66 | 32 | 0.48 |
| 2 | 267 | 82 | 1 | 0.01 |
| 3 | 172 | 81 | 1 | 0.01 |
| 4 | 86 | 64 | 21 | 0.33 |
| 5 | 87 | 82 | 1 | 0.01 |
| 6 | 72 | 72 | 72 | 1.00 |
| 7 | 169 | 83 | 1 | 0.01 |

- On **2/8** autokey seeds the per-message-progressive machinery ALSO produced a sizable injective alphabet.
- Verdict: a recovered order is a CANDIDATE to test, **not** evidence for the cipher model. This matches the free-δ permissiveness already documented in FINGERPRINT.md.

## 5. Real corpus

- per-msg-progressive: clean=18 flagged=44 linked=22 distinct=19 ratio=0.86 maximal=6
- free-δ (autokey/clock): clean=18 flagged=44 linked=22 distinct=1 ratio=0.05
- Contamination split model-robust: both flag 44/62 broad isomorphs.

