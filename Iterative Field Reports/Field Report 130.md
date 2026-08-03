# Field Report 130 — FORTY-SIX INFORMATIVE PLACEMENTS, ZERO FITS, AND A TRAP WORTH NAMING

*Instrument: `eyedouble.py` (5/5 gate). July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The design

FR129 identified four positions where **both** surviving readings agree the
plaintext holds a doubled value:

```
East 4  33 == 34      East 4  78 == 79
East 4 109 == 110     East 5  86 == 87
```

Placing a Finnish word so its double lands on one of these **conditions on a
known-true assertion**. The double is free; the word's *remaining* assertions
are the test. Every check runs against the **consensus** relation — a pair
counts as equal only if both readings agree — so results are independent of
the repair fork.

Vocabulary: 60 Finnish words containing a doubled letter.

---

## 1. A trap the first pass fell into

The raw output reported **96 words fitting all assertions** — which looked like
a result and is not one.

**All 96 have k′ = 0.** Their only repeat *is* the double, so placing them at a
known-double site tests nothing. MAA, PUU, KUU, SUU, TEE, OLLA, TULLA, MENNÄ,
SILLÄ, LOPPU, KUOLLA, SUURI, TUULI, JUURI, KUUSI — none makes a second
assertion. Chance of "fitting" is exactly 1.

**The naive fit count is meaningless.** Only placements with k′ ≥ 1 carry
information. Naming this because it is a new shape in the series' error
taxonomy: **conditioning on a known-true fact and then counting the condition
as a success.**

---

## 2. The real result

```
testable placements       : 142
   k'=0 (no information)  :  96   fits 96
   k'>=1 (INFORMATIVE)    :  46   fits  0
```

Every informative placement failed. The six strongest — k′ = 2, chance
1.5 × 10⁻⁴ each:

| word | gloss | site | start | result |
|---|---|---|---:|---|
| KAIKKI | all | East 4@78 | 75 | fails |
| LUONNON | of nature | East 4@78 | 75 | fails |
| LUONNON | of nature | East 5@86 | 83 | fails |
| MAAILMA | world | East 5@86 | 85 | fails |
| PÄÄLLIKKÖ | chief | East 4@33 | 27 | fails |
| PÄÄLLIKKÖ | chief | East 5@86 | 83 | fails |

Plus 40 at k′ = 1: AARRE, ANTAA, HIISI, KAIKKEUS, KUOLLUT, KUULLA, NUKKUA,
OTTAA, SAADA, TIETÄÄ, TOTUUS, VIISAUS, VIISI, VOITTAA.

**Chance expectation across all 46: 0.48 fits.** Observing zero is entirely
consistent with chance.

> **The zero excludes these words at these sites. It is NOT evidence about the
> plaintext** — with an expectation below one, zero was the most likely outcome
> even if one of them were correct elsewhere.

---

## 3. Why the null could not be built

The pre-registered R3 null — the same vocabulary at 200 random covered
positions — returned 24 fits over 4,471 placements (0.5%) against 96 of 142
(68%) at the sites. **That comparison is worthless**: the sites are
consensus-EQ doubles by construction and random positions are not, so the
difference is definitional, not evidential.

A correct null would need random positions that are *also* consensus-EQ
doubles, and **there are exactly four of those — the sites themselves.** The
test has no available null, which is itself the finding: with four target
sites, this design cannot be calibrated.

---

## 4. What was actually learned

1. **Fourteen Noita-plausible Finnish words are excluded at four specific
   positions** — a small, concrete, permanent negative.
2. **The four doubled-letter sites have no supporting local repeat structure.**
   Whatever sits around them, it is not a word whose second repeat falls within
   its own span. That constrains the neighbourhoods, weakly.
3. **k′ is the right statistic**, not fit count. Any future word test must
   report assertions *beyond* what was conditioned on.

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Doubled-site targeting | proposed (FR129) | **executed**: 46 informative placements, 0 fits |
| Fit count as a statistic | implicit | **invalid when conditioning** — k′=0 fits are guaranteed |
| Error taxonomy | wrong null, reused gauge, circular measurement, wrong objective | **+ counting the condition as a success** |
| R3 null for site-targeting | pre-registered | **unbuildable** — only four qualifying positions exist |
| The four sites | robust crib targets | still robust; **no tested Finnish word fits them** |

---

## 6. Model status

Unchanged. R1 (repair C, cost 5.8): 409 relations, 57 glyphs, 686 positions.
R2 (cost 7.7): 417 relations, 56 glyphs, 683 positions. Agreement 98.76%.
Repair A: bijective, 44.5%, 17 ratios. Cumulative: 27.16 billion candidates,
zero survivors.

---

## 7. Horizon

1. **Widen the vocabulary at the four sites.** 46 informative placements is a
   small sample and the expectation was 0.48 — the test is nowhere near
   exhausted. Compound words and inflected forms would raise k′.
2. **The 2,684 disputed pairs decide R1 vs R2** and need no external evidence.
   A crib landing on one settles the surviving fork.
3. **`q[36] = q[68]` remains the sharpest external lever**, forced by both
   survivors.
