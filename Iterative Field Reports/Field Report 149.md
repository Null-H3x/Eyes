# Field Report 149 — WEST 3 HAS NO STRONG ALIGNMENTS AT ALL, AND NEITHER DOES WEST 2

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. CHALLENGE I retires my own horizon item

FR148 proposed a targeted West 3 search that "can afford a lower bar" than the
corpus-wide `k ≥ 2` enumeration. **That is wrong.**

```
L=14: West 3 windows 111 x other windows 808 = 89,688 pairs
      k=2: expected false positives = 13.02
      k=3: expected false positives =  0.16
```

Pairing one message against eight others still gives ~10⁵ comparisons, so
`k = 2` yields ~13 false positives. **`k ≥ 3` is the correct threshold, which
is what the corpus-wide search already used.** There is no slack to exploit.
Fourteenth item retired on inspection.

The right question is therefore not "search lower" but **"what does West 3 have
at `k ≥ 3`?"** — never asked directly.

---

## 1. The answer is nothing

Direct search, every window pair, lengths 9–30:

```
West 3 alignments with other messages at k>=3 : 0
West 3 INTERNAL repeats at k>=3               : 0
```

**West 3 has no strong isomorph structure of any kind** — not with other
messages, not within itself.

---

## 2. And it is not alone

Counting `k ≥ 3` alignments for every message:

| message | k≥3 alignments | longest |
|---|---:|---:|
| East 1 | 9 | 29 |
| West 1 | 10 | 28 |
| East 2 | 10 | 29 |
| **West 2** | **0** | 0 |
| East 3 | 4 | 28 |
| **West 3** | **0** | 0 |
| East 4 | 4 | 30 |
| West 4 | 5 | 30 |
| East 5 | 4 | 30 |

> **West 2 and West 3 are the only messages with zero strong alignments.** They
> are the two the project has always found hardest: FR35 recorded West 2 as
> "on present evidence uncoupled," and FR148 found West 3's only two alignments
> sit at a single offset.

This is not a glyph-diversity artifact — West 3 runs 0.524 distinct-per-position
against a corpus range of 0.489–0.598, squarely mid-pack. The messages differ in
**shared content**, not in how varied their glyphs are.

---

## 3. What it means

**West 3's 148-position island cannot be joined from internal evidence.** There
is no shared passage to find; the search is now exhaustive at the defensible
threshold rather than merely unsuccessful.

**The seventh-anchor route stands and is now the only route.** One external pin
inside the island folds it into the reading, taking coverage from 435 to ~583
positions (42% → 56%). That is the largest single-anchor yield in the programme
and it is unavoidable rather than optional.

**A structural reading, offered but not claimed:** if T2 = {West 2, East 3,
West 3} and both West messages carry no shared content with anything, T2 may
simply be the triplet whose members say different things. FR32 already found T2
weakly coupled — only East 3 / West 3 has a forced base difference, and West 2
floats free.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Targeted search threshold | "can afford lower" (FR148) | **wrong** — ~10⁵ pairs; `k ≥ 3` required |
| West 3 alignments at k≥3 | unknown | **ZERO**, external and internal |
| West 2 alignments at k≥3 | "uncoupled" (FR35) | **ZERO** — confirmed by direct search |
| Why W2/W3 resist | unexplained | **no shared content**; glyph diversity is mid-pack |
| West 3's island | needs a bridge | **no bridge exists**; anchor-only |

---

## 5. Model status

Extended skeleton unchanged: 794 relations, 61 glyphs, 8 homophones, 79.1%
exposure, 435-position reading across 8 of 9 messages, 0 conflicts.
**Acquisition: 6 anchors for the alphabet, 7 to include West 3's island.**
Cumulative: 27.16 billion candidates, zero survivors.

---

## 6. Horizon

1. **Rebuild the shipped artifacts** on the extended skeleton. Still pending
   across two cycles, and now the only mechanical work outstanding.
2. **The 48 contradictory non-atlas classes** remain unexamined under the
   eight-homophone reading.
3. **Internal structure searching is now exhausted for West 2 and West 3** at
   the only defensible threshold. Do not re-run it lower.
