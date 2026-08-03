# Field Report 172 — THE EYES ARE NOT LETTERS, AND THAT EXPLAINS SEVEN YEARS OF NULL RESULTS

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The tension the community documents create

`Grand_Glyph_Documentation.md` catalogues Noita's **other** glyph system, and it
is a plain substitution for **English**:

```
RUBEDO · ETERNAL LIFE · TELEPORT · SEEK THE END · YOUR REWARD
BRING THE TREASURE HERE · KNOWLEDGE THROUGH PAIN · WHAT YOU DESERVE
```

**The author demonstrably encodes English with simple substitutions.** So the
natural expectation is that the eyes do too.

But FR170 measured the eye plaintext at **82 distinct values over 435
positions** — uniform over 83, and flatly inconsistent with a 26-letter
alphabet, which would give ~26.

Three possibilities: the plaintext is not letters; **our reading is wrong**; or
the model is wrong.

---

## 1. The second is testable, and it is an oracle FR36 does not touch

I had dismissed distinct-value counts as scale-invariant. **They are — across
the drift.** `p = d·v − b`, and multiplication by `d` is a bijection, so the
count is identical at every `d`.

**But across READINGS the `v` values themselves differ.** The count is therefore
a genuine discriminator among the 68, and if one reading gave ~26 distinct
values it would be the English one — found without ever solving the drift.

Testing 30 maximal readings:

```
 positions  distinct  expected if uniform   ratio
       435        82                 82.6    0.99

minimum distinct count over 30 readings: 82
```

**Every reading gives exactly 435 positions and 82 distinct values.** No
variation whatsoever.

> **No English-like reading exists. The eye plaintext is not a small alphabet
> under any maximal-consistent reading of this model.**

---

## 2. What that means: the symbols are a larger unit

```
corpus    : 1036 symbols across 9 messages, ~115 per message
inventory : 83, measured and robust across all readings

letters (26-29)   REFUTED -- inventory is 83
syllables         a Finnish syllabary runs 50-200; 83 fits
words             115 words per message is a plausible message
data              no linguistic structure expected
```

**And it explains the seven null results at a stroke.** Every language test run
since FR39 — coincidence structure, repeat avoidance, word cribs, vocabulary
batches — assumed **letter-like statistics**. At the word or syllable level a
1,036-token corpus over an 83-token inventory is far too short for any of them
to have power.

The frequency profile corroborates it exactly: 1,036 tokens over 83 types gives
~12.5 each, and the observed profile is **11, 11, 11, 10, 10, 10, 9, 9, 9…**

**The plaintext was never featureless. We were measuring it at the wrong
granularity.**

---

## 3. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Eye plaintext unit | assumed letters | **NOT letters** — inventory 83 under every reading |
| Distinct-count as an oracle | dismissed as scale-invariant | **discriminates across readings**; tested, no English reading exists |
| The seven null results | "the plaintext is featureless" | **wrong granularity** — letter tests on word/syllable data |
| Noita's other glyphs | context | **English substitution** — the eyes are unique in the game |
| Likely unit | unstated | **syllable or word**; 83 types, ~115 per message |

---

## 4. Model status

Unchanged structurally: 794 relations, 61 glyphs, 79.1% exposure, 435-position
reading, 68 maximal readings, two invariant cores, stamped header forced.
**Plaintext inventory 83, unit is larger than a letter.** Cumulative: 27.16
billion candidates, zero survivors.

---

## 5. Horizon — and this reopens a closed line

1. **Re-run the vocabulary work at word granularity.** FR121/FR125/FR134 tested
   Finnish *spelled in letters* against a token stream. If each token is a word,
   the correct test is entirely different: repeated tokens are repeated *words*,
   and the 41 long-range within-message repeats FR132 dismissed become
   candidate function-word repetitions.
2. **83 word-types is small enough to be a controlled vocabulary** — a list, a
   ritual text, an enumeration. That fits the corpus's structure (9 messages,
   near-duplicates, shared openings) better than prose does.
3. **The Emerald Tablet directory is still unread**, and the Emerald Tablet is
   a canonical alchemical text with exactly this character.
