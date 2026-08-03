# Field Report 81 — THE CORPUS IS AT 48% OF ITS OWN UNICITY DISTANCE

*Instrument: `eyeunicity` (analytic, built on FR80's inventory estimate). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — I dismissed this analysis, and I was wrong

When surveying novel techniques I listed formal identifiability analysis last, and
wrote that it would *"convert my impression into a theorem — intellectually
satisfying, advances nothing."*

That judgement was wrong, and FR80 is why. The analysis needs a **numerical estimate
of plaintext redundancy**, which the project did not have to sufficient precision
until FR80 tightened the inventory to 82.1 on a 1.9× sample. With that number the
analysis is not decorative; it answers whether the remaining work is possible at all.

---

## 1. The argument

After all depth exploitation, **33.59 bits** of key remain (alphabet 14.46, message
bases 19.13). Every further reduction must come from **plaintext redundancy**, since
FR31, FR34 and FR35 closed the depth routes and FR74 closed the last bridge.

Redundancy is bounded by the measured inventory. An IoC-based inventory `k` implies
Rényi-2 entropy `log₂ k` per symbol, and Shannon entropy is at least Rényi-2, so

```
D  =  log2(83) - H  <=  log2(83) - log2(k)      bits per symbol
```

That is an **upper bound**, which makes any "insufficient" verdict conservative.

---

## 2. Result

| inventory | | D bits/sym | total over 1,036 | vs 33.59 needed |
|---:|---|---:|---:|---|
| 75.9 | CI lower | 0.1290 | 133.7 | sufficient |
| 80.0 | | 0.0531 | 55.0 | sufficient |
| **82.1** | **point estimate** | **0.0157** | **16.3** | **INSUFFICIENT** |
| 83.0 | uniform | 0 | 0 | insufficient |

**The threshold is inventory 81.2.** Above it the corpus contains less exploitable
redundancy than the key has residual entropy.

Restated as unicity distance:

```
at inventory 82.1  ->  unicity distance 2,136 glyphs
corpus length      ->  1,036 glyphs
                        =  48% of what determinacy requires
```

**At the point estimate, the eye messages are information-theoretically
underdetermined.** Not hard. Not unsolved. **Not solvable from the ciphertext alone** —
multiple keys yield plaintexts of indistinguishable likelihood, and no cryptanalysis,
however perfect, can choose between them.

---

## 3. The uncertainty, stated plainly

**The confidence interval straddles the threshold.** At the CI lower bound of 75.9 the
unicity distance is 260 glyphs and the corpus is four times that — comfortably
determinable. The verdict rests on where in [75.9, 89.4] the truth lies, and the
threshold at 81.2 sits inside it.

So this is **not a proof**. It is a point estimate on the "not determinable" side of a
boundary, with real probability mass on the other side. What would settle it is a
tighter inventory estimate, and §7 identifies the route.

Two considerations push the verdict toward "insufficient" rather than away:

- The redundancy figure is an **upper** bound (Rényi-2 ≤ Shannon), so true redundancy
  is at most 16.3 bits at the point estimate, possibly less.
- The residual is computed on my **46-glyph** analysis. The full 56-glyph skeleton has
  nine components rather than four, hence more free base parameters, so the true
  residual is **larger** than 33.59 — widening the gap.

---

## 4. What this settles

**External evidence is not the practical route. It is the only route.** Eighty cycles
of internal work have converged not because the questions ran out but because they hit
an information-theoretic wall. FR31, FR34, FR35, FR74 and FR76 each found a specific
internal channel closed; this says why they all did.

**It puts a floor on acquisition.** At the point estimate, even perfect internal
cryptanalysis leaves **≥ 17 bits** that must come from outside. That is a hard minimum
independent of technique, and it validates the acquisition arithmetic FR54, FR64, FR73
and FR74 built — those were not heuristics, they were the necessary programme.

**It reframes the success criterion.** The question has been *"is the recoverable
object worth having?"* — 462 hapax tokens, no separators, inventory ≥76. The prior
question is now *"is it recoverable?"*, and at the point estimate the answer from the
ciphertext alone is **no**. That is a cleaner decision than the aesthetic one, and it
does not require judging whether a token stream counts as a solution.

**It is consistent with the puzzle being intentional.** A corpus sitting just below
its unicity distance is what you build if you want a puzzle that resists internal
attack but yields to an external key. Offered as an observation, not a finding — but
1,036 glyphs against a 2,136-glyph requirement is a near miss in a suggestive
direction.

---

## 5. Model status

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity clean;
exposure 74.1%; residual key entropy 33.59 bits; plaintext inventory 82.1 CI
[75.9, 89.4]; **exploitable redundancy 16.3 bits; unicity distance 2,136 glyphs
against a corpus of 1,036.**

**Cumulative sweep total: 193.6 million candidates, zero survivors.**

---

## 6. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Identifiability analysis | dismissed as advancing nothing | **decisive**; FR80's estimate made it computable |
| Why internal routes keep closing | five separate empirical closures | **one information-theoretic cause** |
| Corpus vs unicity distance | never computed | **48%** at the point estimate |
| External evidence | the practical route | **the only route**, at the point estimate |
| Minimum external requirement | unquantified | **≥ 17 bits**, independent of technique |
| Success criterion | "is the object worth having?" | **"is it recoverable?"** — prior question, cleaner answer |

---

## 7. Horizon

1. **Tighten the inventory estimate.** It is now the single most consequential number
   in the project, because the threshold at 81.2 sits inside its confidence interval.
   The routes are the full 56-glyph skeleton (needs the five two-glyph components'
   Δ values) and finer passage exclusion. Every other question is downstream of this
   one.
2. **Acquire glyph 76** (FR78) — dual payoff, and now with a floor to measure it
   against: 17 bits needed, this supplies roughly 2.3 plus an alphabet anchor.
3. **The success criterion**, restated per §4. If the corpus is below its unicity
   distance, the decision is not about the value of the output but about whether
   external acquisition is worth pursuing at all.
4. **Audit the atlas for within-T2 classes** (FR76, FR77). Unchanged.
