# Field Report 139 — THE LAST STATISTIC CLOSES; INTERNAL WORK IS COMPLETE

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The overdispersion, chased and closed

FR138 flagged the one unexploited statistic in the corpus: glyph frequency is
**not** uniform.

```
full corpus : chi2 150.4 on 82 df,  z = +5.34,  variance 1.86x multinomial
```

**Hypothesis:** the near-duplicate messages repeat content, so shared positions
are counted twice and inflate the variance. Removing duplicated content
progressively:

| corpus | chi² | n | z |
|---|---:|---:|---:|
| full | 150.4 | 1036 | **+5.34** |
| drop East 1 / West 1 duplicates | 133.5 | 992 | +4.02 |
| drop East 4 / East 5 duplicates | 136.9 | 1005 | +4.29 |
| drop both | 119.6 | 961 | +2.93 |
| **drop all same-triplet duplicates** | **92.9** | 889 | **+0.85** |

> **The overdispersion is entirely the near-duplicate structure.** With
> duplicated content removed the distribution is consistent with uniform
> (z = +0.85). There is no unexploited frequency signal.

That is the expected result under the model — a progressive shift spreads each
plaintext symbol across all 83 glyphs, so glyph frequency should be flat once
the repeated content is counted once. **The corpus behaves as the model
predicts**, which is a small positive rather than merely a null.

---

## 1. Withdrawn artifacts marked

Two invalid artifacts were sitting unmarked in the deliverable package, where
they could be picked up and used:

```
CANDIDATE_READINGS.txt      (FR119)  -- built from v, invalid off-block
PLAINTEXT_STRUCTURE_C.txt   (FR123)  -- same defect
```

Both now carry a withdrawal banner pointing at `PLAINTEXT_RELATIVE.txt`
(FR132), which solves `A_block` along lettered cells only, has zero propagation
conflicts, and covers 191 positions.

---

## 2. Internal work is complete — the closure list

| line | closed by |
|---|---|
| generator sweep — 27.16B candidates, canary-verified | FR99, FR116 |
| enumeration attack — power window complementary to the excluded range | FR115 |
| coordinate-list inner layer | FR100 |
| glyph assets — 5 sprites, 1 informative pixel | FR101 |
| repair fork by internal analysis | FR111 |
| gauge audit — 3 targets, all affected | FR112 |
| alphabet bounds — all 3,403 merges tested | FR135 |
| word-crib route — 0.32% power | FR134 |
| atlas correctness and completeness | FR136 |
| **plaintext autokey — refuted** | **FR137** |
| plaintext structure — 7 independent negatives | FR39…FR134 |
| **frequency overdispersion — explained** | **FR139** |

**No internal question remains open.**

---

## 3. The standing position

**Adopted (FR138):** repair C, one homophone `q[36]=q[68]`, progressive
keystream, dot masking retained, alphabet 60–82.

**Delivers:** 409 relations over 57 glyphs; a 191-position relative-plaintext
reading with one free constant; drift a single parameter; a plaintext that
seven independent lines show to be featureless.

**Costs, stated:** repair C is a 79× bet over the runner-up, not a certainty;
`C` is not a permutation; the dot doctrine is over-conservative by 63% on
testable cells but nothing recoverable is lost.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Frequency overdispersion | unexplained, z = +5.34 | **near-duplicate content**; z = +0.85 after removal |
| Unexploited statistics | one remaining | **none** |
| Withdrawn artifacts | unmarked in the package | **banner-marked** |
| Internal questions | one thread live | **none open** |

---

## 5. Model status

Repair A: 384 relations, 56 glyphs, 74.1% exposure, 17 ratios, bijective.
Repair C (adopted): 409 relations, 57 glyphs, one homophone, single drift,
191-position reading. Alphabet 60–82. Cumulative: 27.16 billion candidates,
zero survivors.

---

## 6. Horizon

**There is no internal horizon left.** Every line is closed, the state is
documented in `CURRENT_STATE.md`, the assumptions in `WORKING_ASSUMPTIONS.md`,
and the acquisition programme in `ACQUISITION_SPEC.md`.

The remaining moves are external and unchanged:

1. **One anchor on glyph 36 or 68** — adjudicates the entire compound position
   at once. Cheapest decisive test in the project.
2. **Three anchors in one component** (C1–C4, non-singular determinant) then one
   per component — 11 total.
3. **Fifteen consecutive plaintext tokens** in any one message.

**Do not reopen a closed line without a genuinely new form of evidence.**
