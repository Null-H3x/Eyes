# Field Report 76 — BODY EVIDENCE SUPPORTS PAIRS, NOT TRIPLETS

*Instrument: `eyegroup` (built on `eyetriplet`). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — rebuild the grouping without assuming it

FR75 showed T2's depth signal is header-only. The natural follow-up is not to patch
T2 but to **discard the grouping entirely and re-derive it** from body evidence, over
all 36 message pairs rather than the 9 within-triplet pairs the premise assumes.

With 36 comparisons, the threshold must come from a max-statistic null rather than a
per-pair one. Measured: max-over-36 null mean 2.62, **95th percentile 4.12**.

---

## 1. Result

```
EDGE THRESHOLD (corrected)  z > 4.12

East 1 / West 1     21    z = +18.42   EDGE
East 4 / East 5     11    z =  +8.94   EDGE
West 4 / East 5      5    z =  +3.61
East 1 / East 2      4    z =  +2.77
West 1 / East 2      4    z =  +2.67
East 2 / East 4      4    z =  +2.44   (cross-triplet)
...
West 2 / West 3      2    z =  +1.08
East 3 / West 3      1    z =  -0.05
West 2 / East 3      0    z =  -0.98
```

**Two edges survive correction, and they are exactly the two near-duplicate pairs.**

Implied grouping: `{East 1, West 1}`, `{East 4, East 5}`, and **five singletons** —
East 2, West 2, East 3, West 3, West 4.

---

## 2. What this does and does not overturn

**It does not refute the triplets**, and the reason is the same one FR75 flagged.
Aligned coincidence measures shared *plaintext*, not shared *keystream*. A message can
sit in perfect depth with two others and carry entirely different text, in which case
this statistic sees nothing. **Low z is not evidence of separate keys.**

**What it does establish** is where the depth grouping's support actually comes from:

> The coincidence evidence supports **pairs**, not triples. Each triplet's
> near-duplicate pair is strongly attested; each triplet's **odd message** is not.

That maps precisely onto the doctrine's own structure — T1 near-dup E1/W1 with odd E2,
T3 near-dup E4/E5 with odd W4 — and shows the odd-message membership was never carried
by this statistic. It must rest on the **isomorph atlas** instead.

For T1 and T3 that is fine and checkable: class #M places E2 alongside E1 and W1
(instances at E1@40, E1@68, W1@40, W1@70, E2@45, E2@80), and class #2 places W4
alongside E4 and E5 (E4@68, W4@71, E5@69). Both odd messages are atlas-attested even
though they are coincidence-silent.

**T2 has neither.** No body coincidence (max +1.08), and — this is the item I cannot
close from here — no within-T2 certified class appears in the record I hold. T2's
appearances are in **cross-triplet bridges**: class #M- (East2@80 × East3@101) and
class #2- (East3@64 × East4@73). And **#M-'s bridge is the instance repair A
discards.**

---

## 3. The specific question this leaves

**Is T2 a keystream group on any evidence at all?**

Three independent methods now find nothing linking its members: FR35's free-w scan,
FR74's bridge scan, FR75/FR76's coincidence. Its forced base difference
(`base[W3] − base[E3] = 54`) was not recovered by FR74 and has no coincidence support
here. And its atlas presence is cross-triplet rather than internal, with one of the two
bridges discarded by repair A.

That is not a refutation — it is an absence of positive evidence across every channel
this project has, which is a different and more actionable thing. **It should be
resolved by auditing the atlas for within-T2 classes**, which requires the atlas spans
I do not hold.

---

## 4. A methodological point worth recording

FR75 and FR76 both turned on the same move: **taking a pooled or assumed structure and
decomposing it.** FR65 verified the depth premise pooled; decomposed, one third of it
vanishes. FR32 established the triplet grouping; re-derived without assuming it, only
the near-duplicate pairs survive.

Neither cycle needed new data. Both needed the existing statistic computed **without
the grouping baked into it.** That is a cheap and repeatable audit pattern, and the
obvious next target is anything else the doctrine reports as a single figure over
structured units.

---

## 5. Model status

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity clean;
exposure 74.1%; alphabet 14.46 bits; message bases 19.13 bits; total 33.59 bits;
alphabet size in [56, 83]. **Depth grouping: pairs {E1,W1} and {E4,E5} attested by
coincidence; odd messages E2 and W4 attested by the atlas; T2 attested by neither.**

**Cumulative sweep total: 193.6 million candidates, zero survivors.**

---

## 6. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Triplet grouping | three triplets, uniformly supported | **pairs attested; odd messages atlas-only; T2 unattested** |
| Coincidence evidence | supports the triplet structure | **supports two pairs**, after correction over 36 comparisons |
| E2, W4 membership | assumed on the same footing as the pairs | **atlas-only** — coincidence-silent but class-attested |
| T2 as a keystream group | [MEASURED] | **no positive evidence in any channel**; not refuted |
| Edge threshold | per-pair | **max-over-36 null, 95th pct = 4.12** |

---

## 7. Horizon

1. **Audit the atlas for within-T2 certified classes.** This is the one question that
   would settle T2, and it needs the class spans. If none exist, T2's grouping rests
   entirely on cross-triplet bridges, one of which repair A discards.
2. **Continue the decomposition pattern** (§4). Any doctrine figure reported as a
   single number over structured units is a candidate.
3. **One crib in West 2** (FR74). Unchanged, still the cheapest external unit, and now
   doubly motivated: W2 is unattested in every channel.
4. **The success criterion** (FR66, FR72, FR73). Unchanged.
