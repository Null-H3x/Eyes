# Field Report 167 — THE MAGICIAN LEAD: PRIOR CONFIRMED, MECHANISM ABSENT, KEYED ALPHABET REFUTED

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The prior is real

Web search confirms what the Mnemonica association rests on:

> **"Petri is also a stage magician."** *(The Independent Games Wiki)*

Mnemonica is Juan Tamariz's memorised 52-card stack. The association is a
genuine prior about the author, not a guess — which is what FR166 nominated it
for as the last live internal lead.

---

## 1. But the mechanism decides it, and there are only two shapes

The alphabet is 83 symbols; the stack is 52. Something must bridge that.

**(a) Mnemonica as a SEED.** A generator turns the stack into a permutation.
**FR100's doctrine settles this**: a full-range sweep is invariant under any
seeding transform whose image lands in the swept range. The 2³² sweep covers
every seed, so a Mnemonica-derived seed is **already swept** — part of the
27.16 billion candidates that returned zero survivors.

**(b) Mnemonica as a DIRECT CONSTRUCTION.** The stack orders the alphabet by
some extension from 52 to 83. **No evidence names one**, and inventing one to
test would be fitting rather than testing.

---

## 2. What was testable, and it fails

A stage magician building a substitution by hand reaches for a **keyed
alphabet**: write a memorised key, then the remaining symbols in natural order.
Its signature is an **affine segment** — `q[g] = α·g + β` across the ordered
tail.

Testing the invariant core:

```
distinct alpha values over 19 relations : 18
largest subset sharing one alpha        :  2

the largest affine-consistent subset:
   q[22] - q[64] = 0
   q[36] - q[68] = 0
```

The only "shared alpha" is **α = 0**, and it is shared by the two homophones —
which is trivially true of any pair of equal values and carries no ordering
information.

> **No affine segment exists. A keyed alphabet is refuted by the invariant
> core.**

**This test is drift-independent.** `α` scales with `d`, so a shared alpha at
drift 1 is a shared alpha at every drift. FR36 does not apply — unlike the two
assumptions it retired last cycle, this is a genuine constraint on `C`'s
**shape**, and `C` fails it.

---

## 3. Where that leaves the four assumptions

| assumption | status |
|---|---|
| 1. The drift is small | retired FR166 — scale-invariant |
| 2. `C` preserves local order | retired FR166 — reduces to FR53's packing |
| 3. The ±29 base differences | **survives** — an observation, not a test |
| 4. Mnemonica / magician construction | **(a) already swept, (b) no mechanism, keyed alphabet REFUTED** |

**No live internal lead remains.** That is now a measured statement rather than
a tired one: each of the four was tested and each died to a specific, named
result — FR36, FR53, FR100, and the invariant core itself.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Petri as stage magician | project folklore | **confirmed** — a real prior about the author |
| Mnemonica as a seed | un-swept family (FR166) | **swept** — FR100 doctrine covers all seeds |
| Mnemonica as construction | testable lead | **no mechanism**; inventing one would be fitting |
| **Keyed alphabet for `C`** | untested | **REFUTED** — no affine segment in the invariant core |
| `C`'s shape | unconstrained | **not affine, not keyed, not order-preserving in any segment** |

---

## 5. Model status

Unchanged: 794 relations, 61 glyphs, 8 homophones, alphabet [56, 75], 79.1%
exposure, 435-position reading, 6 anchors, 68 maximal readings, 19 invariant
relations, stamped header forced. **Plus: `C` is not a keyed or affine
alphabet.** Cumulative: 27.16 billion candidates, zero survivors.

---

## 6. Horizon

**The invariant core has now done real work twice** — it refuted the keyed
alphabet here, and it is the artifact any external candidate is tested against.
That is what it is for.

Remaining, all external and unchanged:

1. **6 anchors as pairs within one component**, or 7 including West 3's island
2. **15 consecutive plaintext tokens** in any one message
3. **The two invariant homophone tests** — `q[22]=q[64]` and `q[36]=q[68]`

**If a new construction family for `C` is proposed, the 19 invariant relations
test it in seconds.** That is the cheapest contribution anyone outside can make.
