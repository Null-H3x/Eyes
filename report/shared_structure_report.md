# Model-Independent Shared-Structure Map

*Reproduce: `python3 eyewitness/shared_structure.py`. No cipher-model assumption — only 'same glyph = same glyph' (isomorph skeletons).*

## Opening-extent matrix (isomorph extent from body pos 3)

How many glyphs each message pair shares as the SAME plaintext from the opening (after the (66,5) header).

```
         E1  W1  E2  W2  E3  W3  E4  W4  E5
  E1     0  22  26  10   9  10   7   7   7
  W1    22   0  22  10   9  10   7   7   7
  E2    26  22   0  10   9  10   7   7   7
  W2    10  10  10   0   9  13   7   7   7
  E3     9   9   9   9   0   9   7   7   7
  W3    10  10  10  13   9   0   7   7   7
  E4     7   7   7   7   7   7   0  18  20
  W4     7   7   7   7   7   7  18   0  18
  E5     7   7   7   7   7   7  20  18   0
```

## Triplet shared openings (3-way, null-calibrated)

| triplet | members | shared-opening glyphs | significant? |
|---|---|---|---|
| Triplet 1 | E1/W1/E2 | 22 | YES |
| Triplet 2 | W2/E3/W3 | 9 | no (~null 7.3) |
| Triplet 3 | E4/W4/E5 | 18 | YES |

## Repeated-passage census (maximal, anywhere in the corpus)

| length | count | messages | first occurrences |
|---|---|---|---|
| 20 | 2 | E1 | E1@39, E1@67 |
| 18 | 4 | W1/E2 | W1@39, W1@69, E2@44, E2@79 |
| 15 | 6 | E1/W1/E2 | E1@42, E1@70, W1@42, W1@72, E2@47, E2@82 |
| 15 | 3 | W2/E4/W4 | W2@55, E4@89, W4@92 |
| 15 | 3 | E4/W4/E5 | E4@50, W4@52, E5@51 |
| 14 | 2 | E4/E5 | E4@54, E5@55 |
| 12 | 7 | E1/W1/E2/E3 | E1@36, E1@64, W1@36, W1@66, E2@41, E2@76 |

## Read (what is solid, model-free)
- **Triplet 1 (E1/W1/E2)** shares a long opening (~22 glyphs); **Triplet 3 (E4/W4/E5)** shares ~18. Both far above the null — the messages genuinely come in triplets with shared openings (confirms the original triplet theory, model-free).
- **Triplet 2 (W2/E3/W3)** does NOT share a long opening (~null); W2/W3 share ~13 but E3 is weakly linked to everything — E3 is structurally distinct (and the longest message).
- **No universal opening** beyond the (66,5) header (9-way ~ chance).
- These shared passages are model-free same-plaintext anchors: they constrain the plaintext content directly, and are the highest-value targets for any future ordering/anchor (independent of the cipher model).
