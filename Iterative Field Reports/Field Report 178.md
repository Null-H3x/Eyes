# Field Report 178 — ITEM 1 COMPLETE: 27 FRAGMENTS TO 5, ALL NINE MESSAGES IN ONE

*Artifact: `READING_LINKED.txt`. July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The evidence source the propagation never used

`A_block` propagation has always run on **alignment cells only**. But

```
A_block = base_component - b_message
```

so a **forced base difference** `b[m2] − b[m1]` links every pair of blocks that
share a component across those two messages. That constraint was solved for and
then never used for linking.

Extracting the base differences from the model:

```
forced base differences: 36 of 36 message pairs
```

**Every message pair's base difference is determined.** FR32 recorded seven;
the extended skeleton forces all thirty-six.

---

## 1. A sign error, caught by its own arithmetic

First attempt produced **768 conflicts**. The diagnostic:

```
block pairs testable : 51    agree 4    disagree 47

East 1/East 2 comp 1: forced 77, observed  6      77 + 6  = 83
East 1/West 2 comp 1: forced 39, observed 44      39 + 44 = 83
East 1/East 3 comp 1: forced 52, observed 31      52 + 31 = 83
```

**Every disagreement sums to exactly 83** — `observed = −forced`. A sign
convention error, not an inconsistency, and the four "agreements" were the
`d = 0` cases where the sign does not matter.

Worth recording: the failure diagnosed itself. Had the conflicts been random
the two derivations would genuinely disagree, and that would have been a
serious finding rather than a typo.

---

## 2. The result

```
base-difference edges added : 180
BEFORE : 27 fragments, largest 435, conflicts 0
AFTER  :  5 fragments, largest 491, conflicts 0

fragment sizes: 491, 222, 48, 29, 29
messages in the largest: ALL NINE
```

> **Zero conflicts. Twenty-seven fragments become five, and the largest spans
> all nine messages for the first time in the project's history.**

The two largest now hold **713 of 819** exposed positions. Total shipped:
**819 of 1,036 = 79.1%**, up from 42.0% two cycles ago.

---

## 3. What this does to Goal B

Goal B needs one large object with internally comparable symbols. It now has
one: **491 positions across all nine messages**, plus a 222-position second
fragment.

Before this cycle the reading was 435 positions in one fragment and 384 scattered
across twenty-six others. **The residual freedom is now five constants, not
twenty-seven** — and any single external pin inside a fragment merges it into
whichever fragment the pin's message already touches.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Forced base differences | 7 (FR32) | **36 of 36** — all message pairs |
| Base differences as links | never used | **used**, 180 edges, zero conflicts |
| Fragments | 27 | **5** |
| Largest fragment | 435, 8 messages | **491, ALL NINE MESSAGES** |
| Shipped coverage | 42.0% (FR119–176), 77.9% (FR177) | **79.1%** |
| Free constants | 27 | **5** |

---

## 5. Model status

**One reading, five fragments, 819 positions (79.1%), all nine messages in the
largest.** 794 relations, 61 glyphs, base-5 verified first-hand, stamped header
forced, plaintext inventory 83 uniform. Cumulative: 27.16 billion candidates,
zero survivors.

---

## 6. Item 1's logical conclusion

**All available linking evidence is now in use**: lettered alignment cells and
the full set of forced base differences. The remaining five fragments cannot be
joined internally —

- there is no further class of forced constraint to draw on
- dot cells are rejected (1,110 conflicts, FR177)
- the 22 undetermined glyphs cap exposure at 819 regardless

**Item 1 is closed.** Moving to item 2: Fragment 2's analysis — now a
222-position object rather than the 148 it was when nominated.
