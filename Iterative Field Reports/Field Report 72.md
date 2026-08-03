# Field Report 72 — THE FIFTH MOTIF: NO PLAINTEXT DELIMITER ABOVE 4%

*Instrument: `eyedelim` (v-channel class-size analysis). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — the method is nearly exhausted, and I missed a motif

FR70 introduced structural priors from the author's *solved* puzzles as a
non-circular source of mechanism hypotheses, and FR71 left "mine the remaining solved
puzzles" as horizon item 2. Surveyed:

- **orb-room quest**: material pouring, not a cipher
- **Crystal Key**: music sequences, not a cipher
- **soundtrack album art**: ciphered text decoding to *"FROM ONE BY THE MEDIATION OF
  ONE"* — but it is another 1:1 rune substitution, structurally identical to the
  already-examined rune alphabet

**The method has largely exhausted its material.** The Cessation Cipher was the only
solved *cryptographic* puzzle of comparable depth, and its motifs were extracted in
FR70.

Except that I extracted four and there were five. The solution path reads:

> *"split this merged section **on square glyphs** into 27 rows"*

**The □ is a delimiter.** One symbol serving as a separator, splitting a stream into
units. I catalogued the pixel-value mapping, the merge along shared sections, the
constant row sums, and the single-element override, and walked past the delimiter.

That is a reading error of the same family as FR69 and FR71: taking a source's
specific statement and carrying away a partial version of it. **Third occurrence in
four cycles**, and the pattern is now consistent enough to name as a standing risk
rather than an incident.

---

## 1. Why the test is not obvious

Under a progressive keystream a plaintext delimiter does **not** appear as a repeated
ciphertext glyph. Every occurrence encrypts differently. Searching the ciphertext for
a delimiter would find nothing whatever the truth.

The v-channel makes it visible: within a (message, component) block, a plaintext
delimiter is a **constant v-value**, so it appears as an unusually large repeat class.
Drift-free and base-free.

---

## 2. Result

```
covered positions   635 in 35 blocks
class-size profile  {1: 462, 2: 76, 3: 7}
largest class       3
classes of size >=4 0
```

Power analysis, simulating a delimiter at frequency *f* over the same block geometry:

| delimiter frequency | mean max class | classes ≥4 |
|---:|---:|---:|
| 0.00 | 3.7 | 0.9 |
| 0.02 | 3.7 | 0.9 |
| **0.05** | **4.3** | **1.8** |
| 0.08 | 5.6 | 4.3 |
| 0.12 | 7.5 | 8.3 |
| 0.20 | 11.1 | 15.7 |
| **corpus** | **3** | **0** |

The corpus sits **below** the no-delimiter baseline. A delimiter at 8% or above would
be plainly visible; at 12% it would produce classes of size 7 or 8.

Corroborated independently by the effective-alphabet bound from FR57 (84.6, CI
[77.3, 93.4]):

| delimiter frequency | implied effective alphabet | |
|---:|---:|---|
| 3% | 80.8 | consistent |
| **5%** | **74.0** | **excluded** |
| 8% | 59.8 | excluded |
| 10% | 50.3 | excluded |

**Two independent channels agree: no plaintext delimiter above roughly 4%.**

---

## 3. What this means for the plaintext

A delimiter at ≤4% means at most one separator per 25 tokens. For comparison, spaces
in English run near 17%, and any punctuation-like separator in a structured record
format would run higher still.

This tightens a picture already visible in FR66. The plaintext has:

- 462 of 545 block-classes occurring exactly once
- effective inventory above ~60
- no contiguous alphabet, no scattered small alphabet
- no first-difference structure above support ~30
- **and now no delimiter above 4%**

**A stream with a large inventory, near-uniform statistics, and no separators is not
a formatted record and not a text.** Every structural hypothesis that would make the
output *parseable* has now been excluded, which is a different and stronger statement
than "not readable as language."

---

## 4. Standing risk, named

Three cycles in four have turned on my carrying away a partial version of an external
statement:

| cycle | the source said | I carried |
|---|---|---|
| FR69 | "83 **consecutive** values from the 125 possible" | "values 0 to 82" |
| FR71 | "provides a 30-bit key" from a **365-day** calendar | "a 30-bit key" |
| FR72 | "split **on square glyphs** into 27 rows" | four motifs, not five |

The corpus work has not shown this failure mode; it is specific to reading
**external prose**. The guard is mechanical rather than attitudinal: when a source
statement enters the ledger, record the **whole sentence**, and check what each clause
would license independently.

---

## 5. Model status — unchanged

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity
clean; exposure 74.1%; 22,550 consistent alphabets; 14.46 bits; alphabet size proven
in [56, 83]; digit analyses offset-robust across 43 offsets.

**Cumulative sweep total: 193.6 million candidates, zero survivors.**

---

## 6. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Plaintext delimiter | never tested | **EXCLUDED above ~4%**, two independent channels |
| Cessation motifs | four extracted (FR70) | **five** — the delimiter was missed |
| Solved-puzzle mining | active method | **largely exhausted**; no further cryptographic puzzles of comparable depth |
| Plaintext character | "not readable as language" | **not parseable either** — no separators, no record structure |
| External-prose reading | incidental errors | **standing risk**, three occurrences in four cycles |

---

## 7. Horizon

1. **The calendar as an anchor source** (FR71). Still needs a candidate mapping; still
   the only live external lead with data attached.
2. **Count the MSB states on the glyph inventory** (FR69). Four confirms the reading;
   five pins the offset to [18, 24].
3. **Decide the success criterion** (FR66). §3 sharpens what is being decided: the
   recoverable object is not merely unreadable, it is unsegmentable. That is a harder
   thing to call a solution, and the decision should be made against that description
   rather than the earlier one.
