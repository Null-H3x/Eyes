# Field Report 177 — 77.9% SHIPPED, NOT 42%: THE READING WAS ALWAYS FOUR FRAGMENTS

*Artifact: `READING_FRAGMENTS.txt`. July 2026. Cycle: EYESPIRAL-C.*

---

## 0. What was being thrown away

Every reading artifact since FR119 has shipped **the largest linked group only**
— 435 positions, 42.0%. The other 384 exposed positions were treated as
leftovers.

They are not leftovers. They are **independently-anchored fragments**, each
internally consistent and each with its own additive constant:

```
group sizes: 435, 148, 74, 56, 18, 14, 10, 6, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, ...
```

The second fragment is **148 positions spanning six messages** — East 3, East 4,
East 5, West 2, West 3, West 4. That is a substantial reading in its own right
and it has never been published.

```
FRAGMENT 1  435 positions   8 messages
FRAGMENT 2  148 positions   E3, E4, E5, W2, W3, W4
FRAGMENT 3   74 positions   E1, E2, W1
FRAGMENT 4   56 positions   West 3
```

**Top four cover 713 of 819 exposed positions.** Shipping all fragments of size
≥ 3 gives **807 of 1,036 = 77.9%.**

---

## 1. Why this matters for Goal B

Goal B is: order `C` until the plaintext coheres, then iterate. The binding
input is **how much structure there is to work against**.

```
before : 435 positions, one fragment      42.0%
now    : 807 positions, twenty fragments  77.9%
```

**Nearly double**, at zero evidential risk — no new assumption, no dot cells, no
extra classes. The fragments were always in the solution; the artifact simply
discarded them.

The cost is that symbols are **not comparable across fragments** — each carries
its own constant. But within a fragment they are, and Fragment 2's 148 positions
across six messages is exactly the kind of object a coherence attack needs.

---

## 2. What I checked and rejected

**Dot cells as additional links.** FR138 measured 63% of testable dot cells as
genuinely co-plaintext, and using all 724 available dot-edges would merge 27
fragments into 6 with the largest at 804 positions.

```
groups 27 -> 6, largest 435 -> 804, conflicts 0 -> 1110
```

**1,110 propagation conflicts.** The dot edges are not jointly consistent, so
wholesale use is out. A conflict-free subset could be selected greedily, but
that is precisely FR35's error — *a cell that fails to contradict has not been
shown to belong* — and at a measured 63% hit rate it would corrupt roughly a
third of what it added. **Rejected.**

---

## 3. Doctrine changes

| item | prior status | status now |
|---|---|---|
| The reading | 435 positions, 42.0% | **807 positions, 77.9%**, in 20 fragments |
| Non-largest groups | leftovers | **independently-anchored fragments**, one constant each |
| Fragment 2 | never published | **148 positions across six messages** |
| Dot cells as links | untested for linking | **rejected** — 1,110 conflicts; a greedy subset is FR35's error |
| Coverage ceiling | 819 exposed | 807 of those shipped; the rest are fragments of 1–2 |

---

## 4. Model status

**One reading, twenty fragments, 807 positions (77.9%).** 794 relations, 61
glyphs, base-5 verified first-hand, stamped header forced, plaintext inventory
83 uniform. Freedom: drift (82, scale-invariant) and one constant per fragment.
Cumulative: 27.16 billion candidates, zero survivors.

---

## 5. Highest-value work for Goal B, ranked

1. **Cross-fragment linking is the whole game.** Twenty fragments with
   independent constants is twenty separate puzzles; one link between the two
   largest would create a 583-position object. The only clean route is an
   external pin *inside* a fragment — but note the arithmetic has changed:
   **one anchor now buys a fragment merge, not just a glyph.**
2. **Fragment 2 deserves its own analysis.** It spans six messages including
   West 2 and West 3, the two the project has never been able to read. Nothing
   has ever been run against it.
3. **The 22 undetermined glyphs cap everything at 819.** They are invisible
   internally (FR135), and 229 positions ride on them.
