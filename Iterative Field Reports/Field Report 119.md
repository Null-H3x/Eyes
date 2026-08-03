# Field Report 119 — THE FIRST DECRYPTION: 461 POSITIONS, 17 CANDIDATES

*Instrument: `eyereveal.py` (5/5 gate). Artifact: `CANDIDATE_READINGS.txt`.*
*July 2026. Cycle: **EYESPIRAL-C**, first application.*

---

## 0. Why the workflow changed

The diagnosis is uncomfortable and exact:

> **118 cycles produced structure, exclusions and tooling. Not one produced an
> actual candidate decryption.**

That is not accident — it is the design. Two lines of EYESPIRAL select for
negatives: **CHALLENGE I** kills items before measurement (ten have now died
there), and **CHALLENGE II** instructs *"pick the one whose failure teaches
most"* — literally optimising for informative failure.

That was correct while the risk was self-deception, and it earned its keep:
FR97's artifact, FR103's over-constrained pool, FR107's reused gauge, FR110's
atlas nesting, FR113's blind-cluster rule, FR118's missing rival. **The engine
works.** But the model is now audited to exhaustion and the risk has shifted
from *believing something false* to *never producing anything*.

**EYESPIRAL-C keeps every gate and inverts the selection:**

| stage | was | becomes |
|---|---|---|
| CHALLENGE I | "is this well-posed?" | **"what artifact does success produce?"** |
| POSTULATE | enumerate approaches | enumerate **constructions** |
| CHALLENGE II | most informative failure | **most usable output** |
| TEST | run the experiment | **BUILD** the artifact |
| PUBLISH | Field Report | **SHIP** something others can use |

**Standing rule: a cycle producing only a finding is a failed cycle.**

---

## 1. What is actually determined, without any anchor

For a determined position,

```
p[t] = A_block + v[t],     v[t] = alpha_g*d1 + beta_g*d2 - d_g*t
```

with `v[t]` known once `(d1, d2)` is chosen, and `A_block = base_component −
b_message`. There are 80 blocks, but **604 alignment cells span two different
blocks and link them.** The linkage leaves:

```
connected block groups : 30
largest group          : 34 blocks, 461 positions  =  44.5% of the corpus
free parameters inside : ONE additive constant
```

> **44.5% of the corpus is relative-decrypted with no external evidence at all.**
> This has been true since FR30 and has only ever been stated as a caveat —
> "conditional on anchors" — never as the result it is.

---

## 2. Seventeen candidates, not 1,394 — and a design flaw the gate caught

Scaling `(d1,d2) → (λd1, λd2)` scales every `v` by `λ`, so

```
p[t] = p[t']  ⟺  v[t] = v[t']  ⟺  λ·v[t] = λ·v[t']
```

The plaintext **equality structure is scale-invariant**. The 82 scales collapse;
only the 17 ratios give distinct readings.

**My first renderer printed raw values and failed its own scale-invariance
gate** — normalised values scale with `λ`, so ratio 8 at scale 1 and scale 2
rendered differently. Corrected: symbols are assigned in **order of first
occurrence**, so the string encodes the equality structure and nothing else.
The gate then passes, and it is the right artifact rather than a prettier
wrong one.

---

## 3. The artifact

`CANDIDATE_READINGS.txt` — 461 positions, 17 candidate readings, each with a
full position index (message / component / offset / ciphertext glyph) so any
character can be traced back to the corpus.

| ratio | distinct plaintext values | equal-pairs |
|---:|---:|---:|
| 1 | 83 | 1368 |
| 8 | 82 | 1378 |
| 9 | 83 | 1412 |
| 15 | 82 | 1431 |
| 22 | 83 | 1391 |
| 28 | 82 | 1368 |
| 35 | 82 | 1317 |
| 40 | 83 | 1407 |
| 48 | 82 | 1356 |
| 51 | 83 | 1362 |
| 53 | 82 | 1398 |
| **55** | 83 | **1467** |
| 74 | 82 | 1405 |
| 76 | 82 | **1292** |
| 77 | 82 | 1353 |
| 78 | 81 | 1426 |
| 82 | 81 | 1377 |

**[R2] all seventeen renderings pairwise distinct.**

---

## 4. An observation logged, NOT claimed

Chance expectation for 461 positions over 83 values is **1,277 equal-pairs**
(sd ≈ 36). Every candidate sits above it, ratio 55 highest at 1,467 (z ≈ +5.3),
ratio 76 lowest at 1,292.

**This is not evidence for ratio 55.** FR115 measured exactly this statistic and
priced it: the elevation is present at *every* candidate including wrong ones —
a property of the skeleton's block geometry, not of any reading — and the
*spread* across candidates is far too small to discriminate (signal/spread 0.42
at inventory 79, against the ≈3 needed). Logged under the FR41/FR42 discipline,
which this series has now applied eight times.

**The distinct-value counts (81–83 of a possible 83) are consistent with the
measured large inventory and discriminate nothing.**

---

## 5. What this is, and what it is not

**It is:** the first materialised output of 119 cycles. 44.5% of the corpus,
relative-decrypted, in a form a human can read and a hypothesis can be tested
against. If the inner layer has recognisable structure — an index sequence, a
coordinate list, a delimited record format — **this is the artifact where it
would show**, and no such artifact existed until now.

**It is not:** a solution, or a claim that any reading is correct. Exactly one
of the seventeen is right *if the model is right*, and FR118 established the
model has a live rival. The free constant means even the correct reading is
displaced by an unknown offset.

---

## 6. Doctrine changes

| item | prior status | status now |
|---|---|---|
| **Workflow** | EYESPIRAL (selects for informative failure) | **EYESPIRAL-C** — selects for usable output; every cycle must ship an artifact |
| 44.5% relative decryption | a caveat ("conditional on anchors") | **a result**, shipped |
| Candidate readings | 1,394 | **17** — scale-invariance collapses the scales |
| Candidate plaintext | never produced | **`CANDIDATE_READINGS.txt`** |
| Equal-pair elevation | — | logged, not claimed; FR115 already priced it powerless |

---

## 7. Model status

Unchanged: 384 relations over 56 glyphs; 74.1% exposure; 17 ratios; conditional
on the progressive form (FR118) and repair A (FR110). Cumulative: 27.16 billion
candidates, zero survivors.

---

## 8. Horizon (constructive)

1. **Extend coverage from 44.5% toward 74.1%.** Twenty-nine block groups remain
   unlinked. Each needs one constant; the alignments that would link them are
   the ones the pool already rejects. Worth checking whether weaker evidence
   (the strict tier, or dot cells) links any group at acceptable risk.
2. **Ship the community package.** `CANDIDATE_READINGS.txt` + `eyecrib.py` +
   `eyemodel.py` + a plain-language guide. The project has a verifier and a
   decryption and has given neither to the people who might recognise
   something.
3. **Render the artifact against inner-layer hypotheses.** With candidates in
   hand, any proposed grammar — index stream, delimited records — can be tested
   directly against seventeen concrete readings instead of argued about.
