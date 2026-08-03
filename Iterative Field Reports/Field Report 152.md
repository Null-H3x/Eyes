# Field Report 152 — THE SKELETON IS NOT UNIQUE: RIVAL MAXIMAL SETS GIVE DIFFERENT ALPHABETS

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The test FR151 called for

FR151 established that "isomorph implies shared passage" is **false** — 23% of
the corpus's 208 strong classes cannot be co-plaintext — and that the model is
therefore *a maximal mutually-consistent set of classes*, not a set of verified
shared passages. The obvious follow-up: **is that maximum unique?**

Built from the 208 classes alone — no pool, no E4/E5 merge, no FR32/33 passage —
greedily adding classes in different orders:

```
set                classes  relations
surprise-ordered       168        496
random 2               199        496
random 5               160        155
random 7               199        496
random 10              199        496
```

**Seven of eleven orders reach 496 relations.** So the maximum is well-defined
and reachable by many routes.

---

## 1. But they are not the same skeleton

Two maximal sets, both determining exactly 496 glyph-pair differences:

```
pairs determined by both : 496
pairs where they DISAGREE: 416
```

**FR30 proved every determined quantity is a fixed multiple of the drift**, so
a disagreement could be a scale difference rather than a real one. Testing the
ratio B/A across all 496 shared pairs:

```
top ratios: (1, 78)  (63, 25)  (zero-mismatch, 15)  (16, 15)  (23, 11)
dominant ratio covers 16% of pairs
```

**Not a scaling.** A drift difference would give one ratio across all 496. The
ratios scatter.

> **The maximal mutually-consistent sets give genuinely different alphabets.
> The skeleton is not unique.**

---

## 2. What this means

The adopted model (794 relations, 61 glyphs) is **one** maximal-consistent
reading among several. Others reach the same relation count and assert
different values for 84% of the pairs they share.

**Choosing among them requires a cost for rejecting a strong isomorph** — and
FR151 established we have no base rate for that, because "isomorph without
shared text" is now known to occur but its frequency is unmeasured.

**FR128's rule bites here.** The surprise-ordered set was preferred because it
takes the strongest classes first. But an alternative rejects only 9 classes
against its 40, and by summed surprise is *cheaper*. Preferring one because it
"determines more" is precisely the error FR128 named — and both determine 496.

---

## 3. Honest restatement of the model's standing

- **794 relations over 61 glyphs** remains internally consistent, drift-stable,
  and passes every consistency check run against it.
- **FR146's 100% mutual prediction against a 2.8% control** remains valid: those
  160 classes genuinely cohere.
- **But coherence is not uniqueness.** Other class sets cohere equally well and
  disagree on most values.
- **The 435-position reading, the 6-anchor programme and the `q[36]=q[68]`
  homophone are all conditional on this class selection**, not just on the
  repair choice.

The project's uncertainty is therefore **larger than any document currently
shipped states.** It is not "17 ratios" or "62 repairs" or "2 serious readings":
it is a choice among maximal-consistent class sets whose size has not been
measured.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Maximal consistent set | assumed unique | **NOT unique** — many reach 496 relations |
| Rival skeletons | none known | **exist**, disagreeing on 416 of 496 shared pairs |
| Disagreement | possibly a drift scaling | **not a scaling** — ratios scatter, dominant covers 16% |
| The adopted model | the reading | **one reading among several** |
| Stated uncertainty | repairs and ratios | **understated** — class selection dominates |

---

## 5. Model status

Content unchanged and still internally sound: 794 relations, 61 glyphs, 8
homophones, 79.1% exposure, 435-position reading, 6 anchors. **Standing
downgraded: one maximal-consistent reading among several, conditional on a class
selection whose alternatives disagree on most values.** Cumulative: 27.16
billion candidates, zero survivors.

---

## 6. Horizon

1. **Measure the size of the maximal-set space.** Eleven greedy orders found
   seven maxima; a systematic count would say whether this is a handful of
   readings or thousands. That number is now the project's headline uncertainty.
2. **An external anchor collapses it.** One known glyph value is consistent with
   only some maximal sets, so acquisition discriminates here exactly as it does
   for repairs — and the discrimination may be much sharper.
3. **Do not rebuild artifacts** until item 1 is measured. Every shipped document
   currently understates the uncertainty.
