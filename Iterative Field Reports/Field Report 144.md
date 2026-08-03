# Field Report 144 — EAST 3@101 IS NOT THE SOLE T1 BRIDGE, AND FR136'S REDUNDANCY CLAIM IS WRONG

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The crack, tested properly

FR136 tested **12 of 195** non-atlas classes against the skeleton, found all
consistent and fully redundant, and concluded *"a differently chosen atlas gives
the same skeleton."* The other 183 were assumed to follow.

Testing all 195:

```
CONTRADICTORY : 48
REDUNDANT     : 128
ADDS SOMETHING:  19      <- the assumption fails
```

Nineteen classes add relations or glyphs. The largest add **+218 relations and
+2 glyphs.**

> **FR136's conclusion is withdrawn.** The atlas choice does change the
> skeleton. The sampled 12 happened to be redundant; the population is not.

That 48 contradict is itself informative: the atlas selection was **not**
arbitrary. It picked consistent classes. But it also excluded consistent ones
that carry information.

---

## 1. The consequential finding: other T1 bridges exist

FR122 established East 3@101 as the **sole** bridge linking triplet T1, checked
"at atlas, pool, strict-tier and passage level." **Every one of those is the
pool.** The corpus's full class inventory was never checked.

```
classes spanning T1 and another triplet : 16
   in the atlas                         :  1  (#M-, via East 3@101)
   NOT in the atlas                     : 15
```

Deduplicating nested variants, there are **two further distinct bridges**:

| bridge | instances | k | surprise |
|---|---:|---:|---:|
| **West 1@55 x East 3@86** (L=23) | 2 | 3 | **3.14** |
| East 1/West 1/East 2 x East 3@93 (L=16) | 7 | 2 | 1.72 |
| *#M- via East 3@101 (the atlas's, for comparison)* | 7 | 2 | **1.70** |

> **The strongest new bridge is better attested than the one the atlas
> contains.** Surprise 3.14 against #M-'s 1.70, and comparable to #2- (3.45)
> and #M (3.55). It is not the weak tail the community filtered out.

---

## 2. What it buys

Adding `West 1@55 x East 3@86` to **repair A's pool** — which discards East
3@101 entirely:

```
435 relations (+51), 58 glyphs, 2 equalities
largest linked group 692 positions, T1 INCLUDED
```

Compared with the standing options:

| reading | relations | glyphs | eq | linked positions | T1 |
|---|---:|---:|---:|---:|---|
| repair A | 384 | 56 | 0 | 461 | no |
| repair C (adopted) | 409 | 57 | 1 | 686 | yes |
| **repair A + W1xE3 bridge** | **435** | **58** | 2 | **692** | **yes** |

**Better than repair C on relations, glyphs and coverage**, at the cost of one
extra homophone. And it reaches T1 **without keeping East 3@101**, which is the
instance every prior repair was organised around.

---

## 3. What this does NOT establish

**The new bridge is not proven genuine.** Surprise 3.14 means roughly one
chance instance in 1,400 — strong, but the class was excluded by whoever built
the atlas, and the reason is unknown. FR136 showed the selection has no evident
principle; that cuts both ways.

**It does not resolve the repair question.** It adds a fourth option to a space
that already had 62, and its evidential cost has not been priced on the FR128
scale.

**Nothing downstream has been rebuilt on it.** The 191-position reading, the
working assumptions and the acquisition spec all still assume repair C.

---

## 4. Self-correction

Two published claims fall:

1. **FR136: "a differently chosen atlas gives the same skeleton."** Wrong. Based
   on 12 of 195, and 19 of the 195 add relations.
2. **FR122: "East 3@101 is the sole T1 bridge."** True of the pool, **false of
   the corpus.** I verified it at four levels and every one was the same level.

The second is the more instructive error: checking a claim four ways feels
thorough, but all four checks drew on the same source. **Breadth of checking is
not independence of checking.**

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Atlas choice irrelevant to the skeleton | FR136 | **WITHDRAWN** — 19 of 195 non-atlas classes add relations |
| East 3@101 the sole T1 bridge | FR122, verified 4 ways | **false for the corpus** — 16 T1-spanning classes exist, 15 outside the atlas |
| Best T1-linked reading | repair C (409/57/686) | **repair A + W1xE3 (435/58/692)** on the raw figures |
| Non-atlas classes | consistent and redundant | **48 contradict, 128 redundant, 19 informative** |
| Verification breadth | four levels | **all four were the pool**; breadth is not independence |

---

## 6. Model status

Standing model unchanged pending pricing: repair C, 409 relations, 57 glyphs,
191-position reading. **A better-scoring alternative now exists and needs
evidential pricing before adoption.** Cumulative: 27.16 billion candidates,
zero survivors.

---

## 7. Horizon

1. **Price the new bridge on the FR128 cost scale** and re-run the repair
   enumeration with the 19 informative non-atlas classes included. The
   62-repair space was computed from the atlas alone and is now known to be
   incomplete.
2. **The 48 contradictory non-atlas classes deserve a look.** Under a
   non-bijective reading some may be admissible, exactly as FR33's offset-4
   cell was.
3. **Do not rebuild the reading yet.** The repair space needs re-deriving first,
   or the artifact will inherit a choice made from an incomplete inventory.
