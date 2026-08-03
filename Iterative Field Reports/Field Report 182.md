# Field Report 182 — DELIBERATE FLATNESS: THE OPTIONS, AND THE ONE THAT IS STILL TESTABLE

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The constraint set

FR181 established that whatever produced the flatness must be **substitutional**
(not a rearrangement), must **preserve isomorphs** (deterministic,
structure-preserving), and is **not homophonic** (refuted at 6×10⁻⁵ for two
homophones per letter). A structure-preserving map cannot flatten — so the
source is flat.

The question becomes: **what flat source would an author deliberately choose?**

---

## 1. The permutation hypothesis — the best candidate, and it dies

A permutation is **exactly flat by construction**, requiring no flattening step
at all. And the circumstantial case was strong:

- `corpus.json`'s own metadata carries **`deck_size: 83`**
- **Petri Purho is a stage magician** (confirmed, FR167)
- his public repo carries a **Mnemonica stack** — a memorised deck *order*
- a magician encoding a message would reach for a stack, and a stack is a
  permutation

**It also predicts something.** If the plaintext is a stream of permutations of
83 symbols, then within any 83-position window of one message **no symbol
repeats**.

```
within-message pairs at distance < 83 : 12,344
pairs with the SAME plaintext value   :    137
expected if values were independent   :    150.5
z = -1.10
```

> **137 violations where a permutation stream permits zero — and at exactly the
> rate independent draws predict. REFUTED.**

The magician reading is thematically excellent and empirically wrong. Worth
recording as such: a good prior is not evidence.

---

## 2. The source's profile

```
equal-value pairs WITHIN one message : 157   (expected 164.1)
equal-value pairs ACROSS messages    : 1339  (expected 1302.9)
```

**Repetition is at chance in both directions.** The nine messages repeat *each
other* — that is what the isomorph atlas is — but neither the messages nor the
corpus repeat *internally* beyond chance.

The profile is: **nine near-identical variants of something with no internal
structure.**

---

## 3. What survives, and what each predicts

| hypothesis | status | why |
|---|---|---|
| permutation / deck stream | **REFUTED** | forbids within-83 repeats; 137 observed |
| homophonic expansion | **REFUTED** | isomorphs at 6e-5 (FR181) |
| reading order / cut / shuffle | **IMPOSSIBLE** | frequency is permutation-invariant |
| fractionation / compression | **REFUTED** | both break isomorphs |
| second cipher layer | survives | **predicts nothing** |
| random filler | survives | predicts nothing; contradicted by the effort |
| base-83 digits of a number | survives | needs a candidate number |
| a key / seed stream | survives | predicts nothing |
| **our `q` is wrong** | survives | **the one that is testable** |

Four of the nine are dead. Four of the survivors are unfalsifiable from inside —
consistent with everything, predicting nothing, which is the worst kind of
hypothesis to be left holding.

---

## 4. The answer to the question as posed

**Is the flatness a product of the cipher choice?** No. A Quagmire II with a
progressive key flattens the *ciphertext* — that is what progressive shifting is
for — but it does not flatten the *plaintext*, and it is the plaintext we
measure as flat.

**Is it an additional mathematical function inside the cipher?** Every candidate
of that shape — homophonic expansion, fractionation, compression — is refuted by
the isomorphs. **Any function that flattens also destroys the repeated-passage
structure the corpus visibly has.** Those two properties are in direct tension,
and the corpus has the second.

**Or something else?** Yes, and it is the uncomfortable one: **the flatness may
be ours, not the author's.**

---

## 5. The testable survivor

`p = q[c] − b − d·t`. **If `q` is wrong, `p` is flat regardless of the true
plaintext** — a wrong alphabet scrambles a Zipf source into uniform noise.

So "flat `p`" is evidence for **either** a flat source **or** a contaminated `q`,
and nothing measured so far separates them.

`q`'s support is 794 relations, zero contradictions, and 100% mutual
out-of-sample prediction against a 2.8% control. **That validates that the
accepted alignments cohere — not that they are co-plaintext.** And FR151
established that **23% of strong isomorph classes cannot be co-plaintext at
all**. If any of the accepted 77% are also not co-plaintext, `q` is contaminated,
and a contaminated `q` produces exactly the flatness observed.

---

## 6. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Permutation / deck source | untested, strong prior | **REFUTED** — 137 within-83 repeats |
| Flatness from the cipher choice | open | **no** — progressive shifting flattens ciphertext, not plaintext |
| Flatness from an internal function | open | **no** — every such function destroys isomorphs |
| Flatness from a contaminated `q` | never considered | **live, and the only testable survivor** |
| The mutual-prediction result | validates `q` | **validates coherence, not co-plaintext** |

---

## 7. Horizon

**The next test is whether `q` is contaminated**, and FR151 already supplies the
shape of it: if some accepted classes are not co-plaintext, removing them should
*change the recovered distribution*. A subset of classes whose removal makes `p`
less flat would be direct evidence — and a subset whose removal changes nothing
would close the last testable option.

That is a search over class subsets scored by the distribution of the resulting
`p`. **It is the first fitness function this project has had that does not
require the plaintext to be language** — it asks only whether the recovered
distribution departs from uniform, in any direction.
