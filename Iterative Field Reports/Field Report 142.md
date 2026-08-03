# Field Report 142 — THE ISOMORPH-DENSITY GAP IS MOSTLY THE ATLAS BEING A SELECTION

*Instrument: `eyehomo2.py` (4/4 gate). July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The question

FR141 found the corpus carries **~10× more long-isomorph structure** than a
progressive cipher over independent plaintext generates, even with the atlas's
13 classes planted as shared plaintext. Cheapest explanation: FR136 found
**208** distinct classes and the atlas records 13, so planting 13 under-plants
badly.

**Method note.** Planting overlapping spans by assignment lets later classes
overwrite earlier ones and silently destroy the sharing. This uses **union-find
over positions** instead: for every class, instance pair and offset, merge the
two positions, then draw one plaintext value per equivalence class. Every
co-plaintext assertion is planted consistently however the spans overlap.

The binding is visible in the free-value count:

```
planting 13 atlas classes : 766 free plaintext values of 1036
planting all 208 classes  : 495 free plaintext values of 1036
```

---

## 1. Result: most of the gap closes

Positive control at `k = 83` (bijective, no homophones), ratio of simulated to
observed:

| planting | L=12 | L=14 | L=16 |
|---|---:|---:|---:|
| 13 atlas classes | 0.02 | 0.06 | 0.15 |
| **all 208 classes** | **0.30** | **0.55** | **0.77** |

```
                    L=12            L=14            L=16
13 classes   k=83   1.2 +- 2.9      4.5 +- 7.7     13.5 +- 14.9
208 classes  k=83  15.7 +- 23.0    39.8 +- 43.6    71.9 +- 61.5
REAL CORPUS        53              73              93
```

> **Under-planting accounts for most of the density gap.** At L=16 the
> simulation goes from 7× low to 1.3× low. The atlas being a 13-of-208
> selection was the right explanation.

---

## 2. But the control still fails, and the residual is informative

```
[R1] control at k=83, all 208 planted:  L=12 0.30  L=14 0.55  L=16 0.77  -> FAILS
```

L=16 is nearly in range; L=12 is still 3.4× low. **The residual gap is
concentrated at short lengths and shrinks monotonically as length grows.**

That trend points somewhere specific: whatever structure is still missing acts
at **short scales**. Candidates, none tested:

- classes below the `k ≥ 2, ≥2 instances` threshold used to enumerate the 208
- short-range plaintext repetition the 191-position reading cannot see
- something in the encoding at small spans

**No alphabet bound is reported**, per the pre-registration. FR138's
"alphabet ≥ 60" stays withdrawn and the range remains **[56, 82]** with nothing
narrowing it.

---

## 3. What this settles and what it does not

**Settles:** the FR141 anomaly. The corpus is not mysteriously isomorph-rich;
the atlas simply records a small fraction of its shared structure, and a
simulation planting only the atlas under-generates by an order of magnitude.
This also corroborates FR136 from a second direction — the 195 omitted classes
are redundant *for the skeleton* but they are **not** redundant for the corpus's
statistical structure.

**Does not settle:** the alphabet size. The control still fails, so the method
cannot bound `k`, and the simulation's variance is large (15.7 ± 23.0 at L=12)
even where it is closest.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Isomorph-density gap (FR141) | unexplained, ~10× | **mostly under-planting**; 0.15 → 0.77 at L=16 |
| The 195 omitted atlas classes | redundant (FR136) | **redundant for the skeleton, NOT for corpus statistics** |
| Alphabet bound by simulation | withdrawn (FR141) | **still withdrawn** — control fails at L=12 |
| Residual gap | — | **3.4× at L=12, 1.3× at L=16** — concentrated at short scales |
| Planting method | assignment | **union-find over positions** — assignment silently destroys overlapping sharing |

---

## 5. Model status

Unchanged. Repair C: 409 relations, 57 glyphs, 191-position reading, alphabet
[56, 82] unbounded within that range. Cumulative: 27.16 billion candidates,
zero survivors.

---

## 6. Horizon

1. **The short-scale residual is the live thread.** It shrinks monotonically
   with length, which is a shape rather than noise. Lowering the class-enumeration
   threshold below `k ≥ 2` and re-planting is the cheapest next test.
2. **The alphabet is not bounded by this method** and probably will not be —
   the variance at the closest point already exceeds the effect being measured.
3. Acquisition unchanged.
