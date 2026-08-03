# Field Report 136 — THE ATLAS IS A SELECTION, NOT AN INVENTORY — AND THE OMISSIONS ARE REDUNDANT

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The question

The isomorph atlas is inherited from the community and underwrites everything.
It has never been re-derived here. Two questions: **is it correct**, and **is
it complete**?

---

## 1. It is correct

Independent scan of `corpus.json` — all windows, grouped by equality pattern:

**All thirteen atlas classes reproduce exactly, with matching instance counts.**

```
#M-  L= 8 k=2 inst=7    #M   L= 9 k=3 inst=6    #3   L=12 k=3 inst=3
#4   L=14 k=2 inst=3    #3+  L=15 k=3 inst=2    #1   L=18 k=5 inst=4
#F   L=19 k=4 inst=3    #C0  L=24 k=6 inst=2    #2-  L=25 k=3 inst=4
#C1  L=26 k=6 inst=2    #2   L=30 k=5 inst=3    #S   L=31 k=6 inst=2
#2+  L=33 k=6 inst=2
```

Not one discrepancy. **The atlas is not wrong.**

---

## 2. It is not complete, and not the most surprising subset

Deduplicating by instance set (nested variants at different window lengths
collapse):

```
distinct instance sets (k>=2, >=2 instances) : 208
of which in the atlas                        :  13
```

Ranking by **surprise** — `log10(observed instances / chance expectation)`:

```
ATLAS ranks : 1, 7, 8, 10, 16, 17, 19, 67, 76, 78, 92, 145, 179  (of 208)
in top 13   : 4 of 13
in top 20   : 7 of 13
worst       : rank 179 of 208
```

**Classes at ranks 2 and 3 are as surprising as the atlas's best and are
absent from it** — West 1@29 / East 2@34 at L=28 k=7, and its L=27 shift.

> **The atlas is a curated selection, not the significant subset. Six of its
> thirteen members are less surprising than fifty-plus classes it omits.**

---

## 3. SELF-CORRECTION — my first consistency test was wrong

I tested the top non-atlas classes by adding them to the pool with
`exact=True`, which asserts **every** cell as co-plaintext. All six came back
**CONTRADICTORY**, and I nearly reported that the atlas selection is principled
because the omissions contradict.

**That test was invalid.** FR6 established that full-span reading produces
contradictions even for *genuine* classes — it is why the sound-rows doctrine
and dot masking exist. Asserting all cells is the discredited reading.

Redone with the pattern registered so dot cells are masked, as the doctrine
requires:

```
of the top 12 non-atlas classes: 0 contradictory, 12 CONSISTENT
```

**Every one is consistent with the skeleton.** The opposite of what the bad
test said.

---

## 4. The finding: the omissions are redundant, not wrong

Each of the twelve, added to repair A's pool:

```
384 relations (+0), 56 glyphs (+0), 0 equalities   -- all twelve
```

**Not one adds a single relation or reaches a single new glyph.** They are
consistent and completely redundant — every constraint they assert is already
implied by the thirteen.

This is FR38's mutual-predictivity result seen from outside: *what one class
asserts, the others already imply.* It now extends beyond the atlas — **the
atlas's thirteen classes already imply everything the next fifty-plus would
add.**

> **The atlas being a selection does not matter. A differently-chosen atlas
> would give the same skeleton.** The foundation is verified in the way that
> counts: not "these are the right classes" but "the choice of classes does not
> change the answer."

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Atlas correctness | inherited, unverified | **verified** — all 13 reproduce exactly |
| Atlas completeness | assumed | **not complete** — 13 of 208 distinct instance sets |
| Atlas as significant subset | assumed | **false** — 6 of 13 rank below 50+ omitted classes |
| Consequence of incompleteness | unknown | **none** — top 12 omissions add 0 relations, 0 glyphs |
| Full-span consistency testing | used here first | **invalid** (FR6); dot masking is mandatory |
| Skeleton's dependence on atlas choice | assumed load-bearing | **not load-bearing** — redundant classes change nothing |

---

## 6. Model status

Unchanged and now better founded. Repair A: 384 relations, 56 glyphs, 74.1%
exposure. Repair C: 409/57/1, 191-position reading. Cumulative: 27.16 billion
candidates, zero survivors.

---

## 7. Horizon

**Item 1 is closed.** The atlas is correct, incomplete, and its incompleteness
does not matter.

**Item 2 remains:** fit plaintext autokey properly and compare against the
progressive model out-of-sample. That is now the last mathematical question
before educated assumptions.
