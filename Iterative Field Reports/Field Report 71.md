# Field Report 71 — THE CAULDRON CALENDAR SWEPT, AND A LEAD I CLOSED TOO EARLY

*Instrument: `eyecauldron` (10/10 selftests). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. SELF-CORRECTION — FR70 closed this on a misreading

FR70 closed the Cauldron Room lead on the grounds that its "30-bit binary key" was
redundant key material for an already-solved cipher, in a room a developer said
"wasn't finished."

**The 30 bits are an extraction, not the object.** The Void Liquid calendar carries
**365 entries** (366 in leap years), of which the Cessation Cipher consumed only the
**first 30**. That leaves **335 bits unconsumed by any solved puzzle** — the largest
untapped structured data source in the game.

I read "provides a 30-bit key" and stopped, without asking how much data the source
held. That is the same error shape as FR69's *"83 consecutive values"*: substituting
a specific reading for what the source actually said, in both cases from external
text rather than from the corpus. **Second occurrence in two cycles.**

---

## 1. Data acquired and validated

Pulled from `github.com/sdlwdr/cauldron_forecast`, which the wiki lists as the
community reference:

```
regular year : 365 bits    189 air / 176 Void Liquid
leap year    : 366 bits    189 air / 177 Void Liquid  (differs at 28 positions)
first 30 bits: 110011110100111100101001010110
```

**The first 30 bits reproduce the published Cessation key exactly**, which validates
the data source rather than merely my parsing of it. That check is in the gate (S2).

### 1.1 Structure of the bitstring

```
runs test           : observed 172, expected 183.3, z = -1.18   (no periodicity)
run-length profile  : 1:82  2:41  3:24  4:12  5:4  6:4  7:3  8:2
neither count is 83 : 189 / 176 / 177
```

Nothing self-evidently structured. Nothing that names 83.

### 1.2 An arithmetic constraint worth recording

```
bits to index an arbitrary permutation of 83 : log2(83!) = 413.9
bits available                               : 365
shortfall                                    : 49
```

**The calendar cannot directly specify an arbitrary permutation of 83.** If it is
relevant to `C`, it must *seed* a generator rather than *encode* the alphabet. That
is a real structural exclusion, not a heuristic.

The converse is more interesting: this project needs **14.46 bits**. Against 335
unconsumed, the surplus is **23-fold**. If the calendar carries anchors rather than
an alphabet, it is enormously more than sufficient.

---

## 2. The sweep

Seven generator families, every rotation, three sources, both directions, all 6,806
affine pre-compositions:

| generator | construction |
|---|---|
| window k=2,3,4,5 | index *i* keyed by the k-bit window at offset i·k |
| fisher-yates | swap indices drawn from the bitstream |
| mod-rank | index keyed by (position of i-th set bit) mod 83 |
| prefix-sum | index keyed by running bit-sum mod 83 |

| source | rotations | candidates | survivors |
|---|---:|---:|---:|
| regular-365 | 365 | 34,778,660 | **0** |
| leap-366 | 366 | 34,873,944 | **0** |
| unconsumed-335 | 335 | 31,920,140 | **0** |
| **total** | | **101,572,744** | **0** |

73 seconds. Zero false-positive risk at 83⁻³⁷⁸.

---

## 3. SCOPE — what this does and does not establish

**It does not establish that the Cauldron is irrelevant**, and I want that stated
before the number gets quoted as though it did.

A 365-bit string admits an unbounded family of mappings onto an 83-symbol
permutation. I generated seven and swept them exhaustively across rotations. **A hit
would have been decisive; a miss covers only the mappings I thought of.** The savage
filter makes trawling free, but free trawling is not the same as exhaustive coverage,
and the distinction matters more here than in the PRNG sweeps, where the generator
family was fixed by the hypothesis itself.

What the sweep *does* establish: the obvious direct mappings are excluded, and any
surviving relevance requires a **non-obvious bridge** between a daily calendar and a
glyph alphabet.

**The exclusion in §1.2 is stronger than the sweep.** 365 bits cannot encode an
arbitrary permutation of 83. That holds for every mapping, not just mine.

---

## 4. Model status — unchanged

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity
clean; exposure 74.1%; 22,550 consistent alphabets; 14.46 bits; first anchor spent on
gauge; alphabet size proven in [56, 83]; digit analyses offset-robust across 43
offsets.

**Cumulative sweep total: 193.6 million candidates, zero survivors.**

---

## 5. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Cauldron Room | CLOSED (FR70) | **REOPENED** — 335 of 365 bits unconsumed |
| Calendar as direct alphabet source | untested | **EXCLUDED by arithmetic** — 365 bits, 413.9 needed |
| Calendar-derived orderings | untested | **101.5M candidates, zero survivors**, seven generator families |
| Calendar as anchor source | never considered | **live** — 335 bits against 14.46 needed |
| Data provenance | second-hand | **validated** — Cessation key reproduces from the JSON |

---

## 6. Horizon

1. **The calendar as an ANCHOR source, not an alphabet source.** This is the reframe
   §1.2 forces. 365 bits cannot be `C`, but it is 23 times more than the bits this
   project needs. A mapping from *specific days* to (glyph, value) pairs would be
   testable immediately, and three or more such pairs **cross-validate each other**
   at 96% rejection of a corrupted set (FR64), with no language check required.
   **What is missing is a candidate mapping, not a test.**
2. **Mine the remaining solved puzzles for structural priors** (FR70 §3). The
   Cessation Cipher was productive as *method*; the orb-room quest and Crystal Key
   music puzzles are unexamined.
3. **Count the MSB states on the glyph inventory** (FR69). Four confirms the reading;
   five pins the offset to [18, 24]. Still the cheapest external item.
4. **Decide the success criterion** (FR66). Unchanged, still prior to everything.
