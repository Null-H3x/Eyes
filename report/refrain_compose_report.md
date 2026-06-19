# Refrain composer — comprehensive anchored run

*Reproduce: `python3 eyecrack/refrain_compose.py --doubles | --offsets … | --compat … | --anchor …`.
Gate: `python3 noita_eye_core/selftest.py` (`refrain_compose` 23/23). Validation:
`python3 eyecrack/order_solve.py "<crib>"`.*

The 22-glyph refrain (same plaintext at W1@33–54, W1@63–84, E2@38–59, E2@73–94) is
pinned ordering-free to the template:

```
position:  0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21
template:  . . . A B B . . . .  C  .  .  A  .  .  C  .  .  .  .  .
```
A = pos 3 = 13 · B = pos 4 = 5 (the only forced double) · C = pos 10 = 16 · pos 7 free.

## 1. Where doubled letters are allowed (the only sharp slots)

| Adjacent pair | Status |
|---|---|
| (4,5) | **forced double** (the `BB`) |
| (6,7), (7,8) | optional double (involve free slot 7) |
| every other adjacent pair | **forced-different — no double possible** |

A candidate plaintext with a doubled letter at any other adjacency is **dead**.

## 2. Which partial words / fragments narrow — and which don't

- **All-distinct fragments do NOT narrow.** `ing`, `ed`, `er`, `ly`, `tion`, `ment`,
  `un-`, `re-`, `the`, `god` each fit at **16–20 of 20** offsets — they are
  permissive and carry almost no information. (`ing` fits at 18 offsets; it is only
  blocked from covering the (4,5) double because `i,n,g` are distinct.)
- **Doubled-letter fragments are the sharp ones**, fitting at only **2–3** offsets,
  with the double forced onto (4,5)/(6,7)/(7,8):
  - leading double (`ee`,`oo`,`ll`,`ss`,`ff`,`tt`,`eed`,`eep`,`eek`): offsets **[4,6,7]**
  - trailing double (`all`,`ell`,`ess`,`off`,`see`,`too`,`egg`,`add`): offsets **[3,5,6]**
  - mid/end-double suffix (`-ness`,`-less`): offsets **[2,5]**
- **Echo-matching words** (a letter repeating at the template's fixed distances) are
  also sharp: **distance 6 → C(10,16)** (~9,352 dictionary words can place there),
  **distance 10 → A(3,13)** (only **52** words — very rare, very sharp).
- Caveat: ~25,000 dictionary words can place *some* double at (4,5), so the double
  **alone** is not discriminating — expanding the word list widens the space.

## 3. Thematic anchor offsets (expected words)

| word | compatible offsets |
|---|---|
| god | 0,1,2,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19 |
| gods | 0,1,5,6,7,8,9,10,11,12,13,14,15,16,17,18 |
| eye / eyes | **5, 7** (sharp) |
| see / seek | **3, 5, 6** |
| spirit | **5** (unique) |
| clever | **5** (unique) |
| rejoice | **6** (unique) |
| monster | 5,6,7,8,9,11,12,13,14,15 |
| sees | **none** (cannot occur in the refrain) |
| true / know / what / thou / soul / mind | 0,1,5,6,…,18 |

`knowledge`, `impressed`, `congratulations`, `god of gods` — **structurally
excluded** from the refrain (internal repeats land on forced-different pairs).

## 4. Compatible anchor stacks (the real space-collapsing lever)

Largest joint placements found among the expected words:

```
[4] god@0, gods@0, eye@5, see@3   -> godseeye.....s........   ("god see ye / gods eye")
[4] god@0, gods@0, eye@5, what@8  -> godseeyewhat.s..a.....
[3] god@0, gods@0, see@3          -> godsee.......s........
[3] god@1, spirit@5               -> .godsspirit..d..t.....
[3] god@0, clever@5               -> godscclever..s..r.....
[2] god@0, eye@5                  -> god.eeye..............
```

## 5. Composer fills (trigram + dictionary word-coverage)

Top fills per anchor set (wcov over the full English wordlist):

```
god+see   : godseeyouarkistprbmlfn   wcov 95%   ("god see you ar…")
gods+eye  : godseeyeatchismbcfknur   wcov 100%  ("god see ye…")
see+what  : murseewhatchisdoclyknp   wcov 100%  ("…see what…")
see+know  : firseeknowdmusandthycl   wcov 100%  ("…see know…sand…thy")
see+thou  : firseethouandshyalwbcm   wcov 100%  ("…see thou and…")
spirit    : yonesspiritdgewatchbmj   wcov 95%   ("…spirit…watch…")
```

These are template-valid against **all four** ciphertext instances and decompose into
real words — but they are stitched **fragments**, not grammatical sentences (a
character-trigram model cannot enforce syntax).

## 6. Validation against the corpus (`order_solve`) — the decisive gate

Each candidate was fed to `order_solve` (pins the alphabet from the crib under the
default ordering, hill-climbs the residual, scores the whole-corpus decrypt):

| crib | pinned | z | corpus wcov |
|---|---:|---:|---:|
| firseeknowdmusandthycl | 52 | 63.6 | **8%** |
| godseeyeatchismbcfknur | 52 | 64.7 | **3%** |
| murseewhatchisdoclyknp | 52 | 47.9 | **5%** |
| firseethouandshyalwbcm | 52 | 41.6 | **1%** |
| godseeyouarkistprbmlfn | 52 | 60.1 | **3%** |
| yonesspiritdgewatchbmj | 52 | 28.1 | **5%** |

**Read (honest):** the high `z` (28–65) is the **known degenerate signal** — the
residual hill-climb fits *some* trigram structure even on a wrong crib/ordering. The
decisive metric is **corpus word-coverage, which is 1–8% (noise)**. **None of these
candidates validate.** A true (refrain, ordering) pair would light corpus wcov far
higher with consistent real words; these do not.

## 7. Conclusion

- The composer **narrows the refrain candidate space** sharply (double-letter slots,
  sharp anchors, compatible stacks) and produces a ranked, template-valid shortlist.
- It does **not** read the plaintext: every shortlist candidate fails the corpus
  word-coverage gate under the default ordering. **The glyph→character ordering
  remains the wall** (as documented in `FINGERPRINT.md`/`STATE_OF_THE_SOLVE.md`).
- The shortlist and tooling are **ready the instant an ordering anchor arrives** — at
  which point `order_solve` will either light the corpus up or reject each candidate
  decisively.

*Generated from the comprehensive `refrain_compose` + `order_solve` run; all numbers
reproduce from the commands at the top.*
