# Field Report 121 — THE VOCABULARY BATCH: ZERO HITS AT 6% POWER

*Instrument: `eyewords.py` (4/4 gate). July 2026. Cycle: EYESPIRAL-C.*

---

## 0. What was tested

FR120 showed a blind pattern sweep cannot win — any shape strong enough to
discriminate 17 readings is too strong to arise by chance. What can win is a
hypothesis with independent reason to hold at a specific place. This tests a
vocabulary of such hypotheses: **95 candidate words** across Noita nouns,
Finnish cosmology, knowledge/secrecy terms, Kalevala names, Hermetic vocabulary
(Thoth, Tabula, Smaragdina, Secretorum) and English equivalents.

Matching is **exact isomorphism**: same letter → same plaintext value, and
different letters → *different* values.

**15 words carry k ≥ 3 assertions** — the threshold below which nothing can
discriminate 17 readings.

---

## 1. Result: zero hits, and a self-correction on how to read it

```
[R2] interesting hits (k>=3, low false-positive rate) : 0
[R3] shuffled null, k>=3 words                        : 0 over 635 placements
```

**I first reported these as "no power" on the basis of the false-positive
expectation. That was the wrong statistic.** False positives measure how often
a *wrong* word would appear to fit; **power** measures how often a *right* word
would be caught — and they are not the same number.

The correct quantity: a word sitting at a **testable** position is satisfied by
the correct reading with certainty. So

```
POWER = testable placements / possible placements
```

| word | k | span | testable | possible | **POWER** | hits |
|---|---:|---:|---:|---:|---:|---:|
| KALEVALA | 3 | 8 | 83 | 670 | **12.4%** | 0 |
| MAAILMA | 3 | 7 | 80 | 676 | **11.8%** | 0 |
| ESSENCE | 3 | 7 | 78 | 676 | 11.5% | 0 |
| YLHÄÄLLÄ | 4 | 8 | 48 | 670 | 7.2% | 0 |
| TODELLINEN | 3 | 10 | 47 | 658 | 7.1% | 0 |
| SISÄLLÄ | 3 | 7 | 48 | 676 | 7.1% | 0 |
| SALAISUUS | 4 | 9 | 32 | 664 | 4.8% | 0 |
| TOSITIETO | 4 | 9 | 32 | 664 | 4.8% | 0 |
| VÄINÄMÖINEN | 4 | 11 | 31 | 652 | 4.8% | 0 |
| LEMMINKÄINEN | 5 | 12 | 17 | 646 | 2.6% | 0 |
| ENSIMMÄINEN | 5 | 11 | 17 | 652 | 2.6% | 0 |

> **Mean power across the 15 testable words: 6.3%.**
>
> **Zero hits leaves ~94% of the hypothesis space untested.** This batch is
> coverage-limited. It is *not* evidence against the vocabulary.

---

## 2. The structural obstacle, quantified

A word with `k` assertions needs every asserted position covered. Coverage is
461/1036 = 44.5% and **fragmented into 66 runs**, longest 12. So longer and
stronger words — exactly the discriminating ones — are the least testable:

```
k=3, span 7-8   ->  ~12% power
k=4, span 8-9   ->  ~5%  power
k=5, span 11-12 ->  ~2.6% power
```

**The properties that make a word able to discriminate are the same properties
that make it untestable.** That is the mirror of FR120's discrimination gap,
and it is the binding constraint on this entire approach.

---

## 3. One observation, logged not claimed

The 62 words with k < 3 produced **1,050 hits against a chance expectation of
2,411** — a 56% deficit. Consistent with FR115's finding that the plaintext
coincidence rate sits at or below flat, and with FR39's near-uniform inventory.
It cannot be read as a signal: k < 3 words cannot discriminate readings, and
the deficit is aggregated across heterogeneous spans.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Word-crib testing | untried | **built and run**: 95 words, 15 at k≥3 |
| "No power" criterion | false-positive rate | **corrected**: power = testable/possible, an entirely different number |
| Batch verdict | — | **0 hits at 6.3% mean power** — coverage-limited, not evidential |
| Binding constraint | coverage 44.5% | **coverage FRAGMENTATION** — 66 runs, longest 12; strong words cannot fit |
| k<3 hit rate | — | 1,050 vs 2,411 chance; logged, not claimed |

---

## 5. Model status

Unchanged. 384 relations over 56 glyphs; 74.1% exposure; 17 ratios; conditional
on the progressive form (FR118) and repair A (FR110). Cumulative: 27.16 billion
candidates, zero survivors.

---

## 6. Horizon (constructive)

1. **Raising coverage is now the single highest-value action** — and for the
   first time it has a concrete payoff attached. Going from 44.5% to 74.1%
   would take mean word power from 6.3% to roughly 30%, a five-fold
   improvement in the chance any proposed word can be seen at all.
2. **Link a T1 block.** East 1, West 1 and East 2 are entirely dark, and they
   hold the corpus's densest shared-passage region (Lymm's alignments cluster
   at message fronts). Linking one T1 block opens three messages.
3. **Short high-k words remain the best shape**: k≥3 within span ≤8 gives the
   most power per assertion. Finnish doubles (MAA-, -UU-, -KK-) are the natural
   source and the vocabulary should be extended in that direction rather than
   toward longer compounds.
