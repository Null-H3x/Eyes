# Field Report 70 — A SOLVED PUZZLE BY THE SAME AUTHOR: DESIGN VOCABULARY AS A PRIOR

*Instrument: `eyesum` (5/5 selftests, one design error caught before corpus contact). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — the lead was weak, but it was pointing at something better

FR68 carried the Cauldron Room's "30-bit binary key" as the only new external lead.
Investigated, it does not survive:

- the key is **the first 30 digits of the Void Liquid Calendar**, and it decrypts the
  **Cessation Cipher, which the community solved without it**
- a developer reportedly stated the Cauldron Room **"wasn't finished"**

So the lead is redundant key material for an already-solved, unrelated cipher, in a
room that may have no intended solution. **Closed.**

But the investigation surfaced something worth more than the key. **The Cessation
Cipher is a solved puzzle by the same author**, and its published solution path is a
worked example of his design vocabulary:

| Cessation motif | eye-corpus analogue |
|---|---|
| six symbols transcribed to **0–5 by pixel value** | five eye orientations → 0–4 |
| **six messages merged along shared sections** | nine messages with certified alignments |
| restructured into **27 rows, each summing to ~30** | rows of ≤39 eyes = **13 trigrams** |
| first glyph of the first row **replaced with a 3** | an explicit single-element override |

Two of these the corpus already exhibits. **The third has never been tested.** That
is the cycle: use a solved puzzle by the same hand as a structural prior, rather than
guessing at mechanisms in the abstract.

---

## 1. Gate — a design error caught before the corpus

The first build planted a constant-sum corpus and measured **raw** dispersion of
block sums. It failed at z = −0.75.

The plant was correct and the statistic was wrong. In a mod-83 system the constraint
is **modular**: block sums land on one residue but differ by multiples of 83, so raw
dispersion is large by construction. Wraparound destroyed the very signal I planted.

Corrected to measure concentration of `block sum mod 83`:

```
S1 planted modular constant-sum : concentration 1.00 vs null 0.05, z = +94.73
S4 wrong block size on the plant: z = -0.71
```

Detector is powerful **and** specific. Had the gate not run, the corpus would have
returned a null for a reason having nothing to do with the corpus.

---

## 2. Result — constant-sum structure is not present

Block sizes 2 through 30, modular concentration and raw dispersion, against a
unigram-preserving within-message null (1,200 draws):

```
B = 13 (one full row, the structurally motivated size) : z = +0.13
best over all sizes: B = 7 at z = +3.75
max-statistic corrected P = 0.0858
```

**Pre-registered threshold was z ≥ +3 AND corrected P < 0.05. It fails.**

Two reasons to hold the line rather than argue for B=7. First, the corrected P is
above the threshold as written. Second, B=7 is **not** the motivated size; it was
selected post hoc from 29 candidates, whereas B=13 — the one the Cessation analogy
predicts — sits at z = +0.13, indistinguishable from nothing.

**Logged watch-grade, not promoted.**

---

## 3. What the exercise buys anyway

**The motif that did not get tested is the interesting one.** In the Cessation
solution, *"the first glyph of the first row is replaced with a 3"* — a deliberate,
documented, single-element exception in an otherwise regular structure.

That is a demonstrated authorial habit, and it bears on **repair A**. The skeleton is
conditional on discarding two isomorph instances (E3@101, E1@68) that would otherwise
force contradictions. That has always been the model's outstanding debt: a hypothesis
that a well-supported instance is spurious.

**A worked example shows this author does insert single-element overrides.** That is
weak evidence, it is not a measurement, and it cannot discriminate *which* instance
to discard. But it moves repair A from "an assumption we had to make" toward "an
assumption consistent with the author's demonstrated style," and the assumption ledger
should record it as such.

**The reusable method.** Structural priors drawn from the author's *solved* puzzles
are non-circular in the way FG-era work required: the Cessation Cipher was solved
without reference to the eyes, so its motifs were not selected to fit them. Of the
handful of external sources this project has, it is the only one that constrains
*mechanism* rather than supplying *values*.

---

## 4. Model status — unchanged

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity
clean; exposure 74.1%; 22,550 consistent alphabets; 14.46 bits; first anchor spent on
gauge; alphabet size proven in [56, 83]; digit analyses offset-robust across all 43
offsets.

---

## 5. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Cauldron Room 30-bit key | new lead (FR68) | **CLOSED** — redundant key for a solved unrelated cipher; room reportedly unfinished |
| Cessation Cipher | unknown to this project | **worked example of the author's design vocabulary**; non-circular structural prior |
| Constant-sum block structure | never tested | **NOT SUPPORTED**; B=13 at z=+0.13, best B=7 corrected P=0.086 |
| Modular vs raw sum statistics | not distinguished | **modular required** in a mod-83 system; raw dispersion cannot see the constraint |
| Repair A | assumption with outstanding debt | unchanged as evidence, but **consistent with a demonstrated authorial habit** of single-element overrides |

---

## 6. Horizon

1. **Count the MSB states on the glyph inventory** (FR69 §3). Four confirms the
   reading; five pins the offset k to [18, 24]. Still the cheapest open item, still
   needs only the glyph set.
2. **Mine the remaining solved puzzles for structural priors.** The Cessation Cipher
   was productive as a *method* even though its one testable motif came back negative.
   The orb-room quest and the Crystal Key music puzzles are the other solved
   author-designed systems, and neither has been examined this way.
3. **Eye-level transcription** — needed for the segmentation and offset tests, and now
   also for the row-structure motifs.
4. **Decide the success criterion** (FR66 §1). Unchanged, and still prior to
   everything else.
