# Field Report 185 — THE ALPHABET IS 78–82, AND THE EIGHT HOMOPHONES ARE DISFAVOURED AT −2.7σ

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The correction that changed the question

FR184 tested the reading's Index of Coincidence against a **fixed** null of
`1/83`. But the alphabet size is not fixed — it is the unknown. **`IC` does not
test "is it structured" against a known `K`. It ESTIMATES `K`.**

`IC` is an unbiased estimator of `Σpᵢ²`; for a uniform source over `K` types
that is `1/K`. So `1/IC` is the **effective alphabet size** (inverse Simpson).

```
observed IC over 491 positions : 0.01244
1/IC                          : 80.4
```

---

## 1. Sweeping the alphabet size

```
   K       1/K  null mean   null sd       z      verdict
  56   0.01786    0.01786   0.00038  -14.24     too flat
  64   0.01562    0.01562   0.00036   -8.94     too flat
  72   0.01389    0.01389   0.00034   -4.28     too flat
  76   0.01316    0.01316   0.00033   -2.21     too flat
  78   0.01282    0.01282   0.00032   -1.17   consistent
  80   0.01250    0.01250   0.00032   -0.20   consistent
  82   0.01220    0.01219   0.00031   +0.77   consistent
```

> **The plaintext alphabet is 78–82. Everything at or below 76 is refuted,
> and 56 — the proven pairwise-distinct floor — is refuted at z = −14.2.**

The long-standing range `[56, 82]` (FR97, FR135, exhaustive over all 3,403
merges) collapses to **[78, 82]** from a completely independent direction: not
the constraint system, but the plaintext's own coincidence rate.

---

## 2. And it contradicts the eight homophones

The standing model carries **eight forced homophones** (FR146), so `C`'s image
is `83 − 8 = 75`. A plaintext drawn from 75 symbols must give `IC ≥ 1/75`.

```
model                            implied K  expected IC       z
8 homophones (FR146 standing)           75      0.01334   -2.73
1 homophone  (repair C)                 82      0.01219   +0.79
0 homophones (C a permutation)          83      0.01206   +1.21
IC point estimate                       80      0.01249   -0.17
```

> **The eight-homophone model requires more coincidence than the plaintext
> shows. A near-permutation `C` fits; a 75-symbol image does not.**

---

## 3. Three independent lines now agree

| line | finding |
|---|---|
| **FR163** | the pipeline manufactures homophones — **23 of 23 false** in synthetic data with an injective alphabet |
| **FR164** | the real corpus forces **8** where an injective control forces **11–53** |
| **FR185** | the plaintext's coincidence rate is **too low** for eight of them to be real, at −2.7σ |

**`C` is closer to a permutation than the model's forced equalities suggest.**
FR164 restored the eight on the grounds that the real corpus sits *below* the
artifact range — that reasoning was sound but incomplete, because it never asked
what the plaintext's own statistics require.

---

## 4. What this does and does not settle

**Does:** the alphabet is 78–82, the eight homophones are disfavoured, and the
`[56, 82]` range that survived every internal test since FR97 is narrowed to a
five-wide window.

**Does not:** identify *which* homophones are spurious, or pin the alphabet
exactly. `1/IC` is the **effective** size — a slightly non-uniform 83-symbol
source and a uniform 80-symbol one are not separated by this statistic.

**Caveat to hold:** this rests on the reading being right. A contaminated `q`
would distort `IC` too — though note the direction: contamination *adds* false
equalities, which would push `IC` **up** and `K` **down**. The observed `K` is
at the **top** of the plausible range, which is the opposite of what
contamination predicts. **That is mild independent evidence that `q` is clean.**

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Alphabet size | [56, 82], no internal narrowing (FR135) | **[78, 82]** from the plaintext's coincidence rate |
| K ≤ 76 | possible | **refuted**, z ≤ −2.2 |
| K = 56 (the proven floor) | the floor | **refuted at −14.2σ** — attainable but not actual |
| The 8 homophones | supported (FR164) | **disfavoured at −2.7σ** |
| `IC` as a statistic | "cannot detect language" (FR175) | **estimates the alphabet size**, which is what it is for here |
| Contaminated `q` | untested residual | **mildly disfavoured** — contamination predicts low K, we observe high |

---

## 6. Model status

794 relations, 61 glyphs, one reading, five fragments, 819 positions (79.1%).
**Alphabet 78–82. Homophone count disputed by the plaintext statistics.**
Cumulative: 27.16 billion candidates, zero survivors.

---

## 7. Horizon

1. **Re-run the homophone question with the IC as an additional constraint.**
   A class selection forcing fewer homophones should now be *preferred*, and
   FR178's five-fragment reading gives more positions to test with.
2. **Fragment 2 (222 positions) as an independent replication** — still the
   cheapest genuine test, and now with a sharper prediction: it should give
   `1/IC` in the high 70s to low 80s if the reading is sound.
3. **The `[78, 82]` window should go into `CURRENT_STATE.md` and
   `INVARIANT_CORE.md`** — it is the first narrowing of the alphabet in eighty
   reports.
