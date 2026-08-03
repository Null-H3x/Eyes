# Field Report 180 — THE KEYWORD-ALPHABET ATTACK: NEGATIVE IN OUR INDEXING, AND THAT IS THE WHOLE QUESTION

*July 2026. Cycle: EYESPIRAL-C. Opening the cipher-family workflow.*

---

## 0. The attack the placement opens

In **every** Quagmire variant the mixed alphabet is not an arbitrary
permutation. It is **keyword-derived**: write the keyword dropping repeats, then
append the unused letters **in order**. The alphabet is a short scrambled
**head** followed by a long ascending **tail**.

If `C` is keyword-derived, then for consecutive glyph indices in the tail

```
q[g+1] - q[g] = 1   at drift 1,  = d in true units
```

so a **plurality of adjacent-index pairs would share one difference — and that
value would be the drift.**

**FR167 does not cover this.** It refuted `C` being *affine* — monotone with a
constant step across the whole alphabet. A keyword alphabet is monotone with
step 1 only on the tail, jumping over the head letters. Different hypothesis.

---

## 1. The test

```
glyphs determined                        : 61
determined glyph-pair differences        : 794
ADJACENT-INDEX pairs (g, g+1) determined :  18
their difference values : {3:2, 72:1, 27:1, 2:1, 80:1, 19:1, 37:1, 11:1, ...}
most shared difference  : 2 of 18
```

If `C` were keyword-derived with a tail of length `T`, about `18·T/83` of our
eighteen pairs would be tail pairs sharing the drift:

```
tail 40 -> expect  9 of 18        tail 60 -> expect 13 of 18
tail 50 -> expect 11 of 18        tail 80 -> expect 17 of 18
```

**We observe 2, which is the expected maximum from eighteen draws over
eighty-two values by birthday alone.** Generalising to steps 1–8 gives nothing
better.

> **`C` is not keyword-derived in our glyph indexing.**

---

## 2. But the caveat is the entire question

Our glyph index `g ∈ 0..82` comes from the **base-5 trigram reading order**
(FR101). "Adjacent index" means adjacent in *that* order. A keyword alphabet is
monotone in the **engine's** alphabet order, which need not be ours.

**If the two orderings differ by a permutation, the tail pairs scatter and the
signature is destroyed — which is exactly what we observe.**

So the test cannot distinguish *"not keyword-derived"* from *"keyword-derived in
a different order"*, and that distinction is the whole prize: a keyword alphabet
collapses `C` from one of 83! permutations to **a keyword plus an alignment**.

---

## 3. Where the workflow starts

**Step 1 — settle the glyph ordering.** A trigram is three base-5 digits: 6
significance orders × 120 digit-value assignments = **720 natural candidates**.
FR101 reports only 2 of 120 relabelings give an unbroken 0..82, related by a
null relabeling — so the space is nearly forced, but it has never been
enumerated *against this hypothesis*. This needs the trigram-to-value table,
which is not in the local corpus (values arrive pre-converted).

**Step 2 — re-run the tail test under each ordering.** The signature is cheap to
evaluate: count adjacent pairs sharing a difference. 720 orderings × one count
is instant. A hit pins the drift *and* exposes the keyword in one move.

**Step 3 — if a tail appears, read the head.** The head is the keyword's
distinct symbols in order. With 83 symbols and a Finnish or alchemical keyword,
the head is short and the remaining structure is heavily constrained.

**Step 4 — if no ordering produces a tail, the keyword hypothesis is dead** and
with it the last structural shortcut the family offers. What remains is the
literature's own fallback: cribs.

---

## 4. Why this is worth doing before anything else

It is the only route found so far that could **pin the drift from internal
evidence**. FR30, FR36 and FR53 proved every scale-invariant test must fail —
and this one is not scale-invariant, because it asks whether a *specific*
difference value recurs, not whether the structure is distinct.

**Four separate drift-pinning proposals have died to those three results
(FR166, FR167). This is the first that survives them on inspection.**

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Quagmire keyword structure | unrecognised | **the family's defining constraint on `C`** |
| `C` keyword-derived | untested | **negative in our indexing**, 2 of 18 vs 9–17 expected |
| The negative's scope | — | **conditional on glyph ordering**; cannot rule out another order |
| FR167's affine refutation | thought to cover this | **different hypothesis** — affine is constant-step, keyword is tail-monotone |
| Drift-pinning routes | four, all dead | **a fifth that survives FR30/36/53 on inspection** |

---

## 6. Model status

Unchanged: one reading, five fragments, 819 positions (79.1%), 794 relations,
61 glyphs. Cumulative: 27.16 billion candidates, zero survivors.

---

## 7. What I need

**The trigram-to-value table** — which base-5 trigram maps to which of 0..82.
The local corpus stores values already converted, so the ordering is not
recoverable from it. It is in the community transcription
(`noita-eyes.neocities.org`) or derivable from the raw base-5 stream. With it,
step 2 runs in seconds.
