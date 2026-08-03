# Field Report 176 — THE READING IS UNIQUE: THE 68-FOLD AMBIGUITY WAS AN ARTIFACT OF DISCARDING THE ATLAS

*July 2026. Cycle: EYESPIRAL-C. The largest correction in the series.*

---

## 0. Two corrections, and the second is enormous

**FIRST — FR170 overcounted the space by ~500,000×.**

It gave `68 readings × 82 drifts × 83⁴ bases = 2³⁸`, assuming five independent
component bases. **The reading's `A_block` propagation already fixes them
relative to one another**, leaving ONE free constant:

```
free additive constants = number of linked GROUPS = 1 (for the 435-position reading)
space = 68 x 82 x 83 = 462,808  ~ 2^19
```

And the three factors are not equal in kind: the **global constant relabels**
every value, the **drift is scale-invariant** (FR30), and only the **reading**
changes which positions share a symbol.

**SECOND — the 68 readings are not 68.**

```
classes only (eyemax's system)     -> 12 distinct readings in 18 runs
ATLAS POOL mandatory (the model)   ->  1 distinct reading  in 18 runs
```

FR152, FR153 and FR162 built from the **208 classes alone** plus seed rows.
The standing model builds from the **atlas pool plus classes**. Those are
different systems, and I never noticed.

> **With the atlas pool mandatory — which every version of the model has always
> assumed — the reading is UNIQUE. One structure, found in 150 independent
> greedy runs.**

The 68-fold ambiguity exists only if one is willing to **discard
community-certified isomorph classes**, which no version of this model does.

---

## 1. What the space actually is

```
distinct plaintext STRUCTURES : 1
drift                         : 82   (relabels; scale-invariant)
global constant               : 83   (relabels)
```

**There is one plaintext structure.** Everything else is relabeling.

This also explains FR172 cleanly: every sampled reading gave 435 positions and
82 distinct values because **they were all the same reading**.

---

## 2. What this does to the record

| report | claim | status |
|---|---|---|
| FR152 | skeleton not unique, rival maximal sets | **true only for the class-only system** |
| FR153 | ~30 readings, third-order conflict | **class-only system** |
| FR162 | exactly 68 readings, saturated | **class-only system** — a correct count of the wrong object |
| FR170 | remaining space 2³⁸ | **2¹⁹, and structurally just 1 reading** |
| FR154/155/168 | invariant cores across readings | **still valid** — and now a floor rather than the whole story |

**The invariant cores are not weakened.** They were computed over the
class-only system, so they hold across a *larger* ambiguity than the model
actually has. A relation invariant across 68 readings is certainly invariant
across one.

---

## 3. Both of your goals, re-priced

**GOAL A — shrink enough to brute-force.** Achieved, and by more than it
looked. The structural space is **one reading**; the residual `82 × 83` is pure
relabeling.

**GOAL B — order `C` until the plaintext coheres, then iterate.** This is now
the *only* live route, and it is far better posed than it was an hour ago:
there is **one structure** to work against, not sixty-eight. Any symbol
assignment that makes it cohere is the answer, and there is no competing
structure to check first.

The obstacle remains real and unchanged: **the structure's token distribution is
uniform** (FR173, χ² = 93.4 on 81 df), so no assignment produces Zipf-like text.
But that is now a statement about **one** object rather than a hedge across
sixty-eight.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Number of readings | 68, saturated (FR162) | **1**, with the atlas pool mandatory |
| The 68 | the model's ambiguity | **the class-only system's** ambiguity |
| Remaining space | 2³⁸ (FR170) | **2¹⁹**, structurally **1** |
| FR172's "all readings agree" | robustness result | **they were the same reading** |
| Invariant cores | across 68 readings | **valid, and conservative** |

---

## 5. Model status

**One reading.** 794 relations, 61 glyphs, 79.1% exposure, 435-position
plaintext structure, base-5 verified first-hand, stamped header forced,
plaintext inventory 83 with a uniform distribution. Remaining freedom: drift
(82, scale-invariant) and one global constant (83) — **both pure relabeling.**
Cumulative: 27.16 billion candidates, zero survivors.

---

## 6. Horizon

1. **Ship the single structure as the headline artifact.**
   `PLAINTEXT_RELATIVE.txt` already contains it; what changes is that it should
   no longer be hedged as "one of 68".
2. **Goal B is the only route, and it is now well-posed.** One structure, 435
   determined positions, 82 symbols. Either a coherent assignment exists or the
   inner layer is not text — and that is a single question, not sixty-eight.
3. **Re-audit anything else that built on the class-only system.** FR152–FR162
   and FR170 are the known cases; there may be more.
