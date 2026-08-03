# Field Report 77 — THE ISOMORPH DISCRIMINATOR SURVIVES, AND EXPLAINS THE ODD MESSAGES

*Instrument: `eyeiso` (6/6 selftests, one fundamental error caught before corpus contact). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — the foundational discriminator, never decomposed

Doctrine records long-isomorph abundance as *"the one genuinely non-vacuous
discriminator established so far — ciphertext-value feedback crushes long isomorphs;
the corpus doesn't."* It excludes an entire cipher family and has never been
decomposed.

The worry was specific. **A literal match survives ciphertext feedback perfectly
well**: identical plaintext under an identical key gives identical ciphertext. Only
**non-literal** isomorphs — same repeat pattern, different glyphs — discriminate. And
the corpus contains two near-duplicate pairs (E1/W1 at 44.4%, E4/E5 at 27.2%) that
manufacture long matching windows for free.

If the abundance were literal matches between near-duplicates, the discriminator would
be measuring the corpus's redundancy rather than its cipher.

---

## 1. Gate — a fundamental error caught

The first build counted **3,327 non-literal pairs** on a planted *literal* duplicate.

The cause is structural and would have invalidated everything: with 83 symbols and a
12-window, most windows contain **all distinct glyphs**, giving the trivial pattern
`(0,1,…,11)`. Every such window matches every other. Isomorph counts computed without
excluding them are meaningless.

Corrected to require at least two genuinely repeated positions per window:

```
S2  planted literal duplicate   -> lit 48, non  0
S3  planted relabelled copy     -> lit  0, non 38
S4  random corpus at L=12       -> lit  0, non  0
```

The instrument now separates the two categories cleanly and is silent on noise.

---

## 2. Result — the concern is refuted

| L | literal | non-literal | null (non) | z | near-dup share |
|---:|---:|---:|---:|---:|---:|
| 12 | 2 | 80 | 4.12 | **+17.70** | 18 / 80 (22%) |
| 13 | 4 | 92 | 4.46 | **+22.66** | 21 / 92 (23%) |
| 14 | 3 | 113 | 5.05 | **+27.85** | 25 / 113 (22%) |
| 15 | 3 | 134 | 4.51 | **+34.20** | 28 / 134 (21%) |
| 16 | 3 | 144 | 3.85 | **+38.31** | 30 / 144 (21%) |

**Literal isomorphs are almost nonexistent — two to four at every length.** The
abundance is essentially entirely non-literal, which is exactly the discriminating
kind. And the near-duplicate pairs contribute only **21–23%**, so roughly four fifths
comes from elsewhere.

**The discriminator survives decomposition.** My concern was wrong, and it was worth
testing.

---

## 3. THE REVERSAL — and it resolves FR76

Per-message-pair breakdown of non-literal isomorphs at L=12:

```
West 1 / East 2      28
East 1 / East 2      16
East 1 / West 1      14   <== near-duplicate
East 4 / West 4       5
East 4 / East 5       4   <== near-duplicate
West 4 / East 5       3
```

**The largest contributors are West1/East2 and East1/East2 — not the near-duplicate
pairs.** East 2 is the *odd message* of T1, and FR76 found it **coincidence-silent**
(z = +2.77, +2.67, both below threshold).

FR76 left this as an inference: the odd messages must be attested by the atlas rather
than by coincidence, since class #M places E2 with E1 and W1. **This measures it.**
East 2 is coincidence-poor and isomorph-rich, and the same holds for West 4 in T3.

That is a coherent picture rather than a tension. Aligned coincidence requires shared
plaintext *at the same index*; a non-literal isomorph requires only shared repeat
*structure*, which survives different plaintext and different offsets. **The two
statistics measure different things, and the odd messages are visible to one and
invisible to the other.**

---

## 4. T2 — a fifth independent channel finds nothing

Of the eleven message pairs contributing non-literal isomorphs at L=12, **not one is
a within-T2 pair.** W2/E3, W2/W3 and E3/W3 contribute zero. T2's messages appear only
in cross-triplet pairings (E1/E3, W1/E3, E2/E3, W2/E4, W2/W4), each at 2.

So the channels now agree:

| method | finds within-T2 linkage? |
|---|---|
| FR35 free-w passage scan | no |
| FR74 bridge scan | no |
| FR75 per-triplet coincidence | no (z = +0.07) |
| FR76 grouping re-derivation | no |
| **FR77 non-literal isomorphs** | **no** |

Five independent methods, no positive evidence. Still not a refutation — absence of
shared structure is not proof of separate keys — but the absence is now
comprehensive.

---

## 5. Model status

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity clean;
exposure 74.1%; alphabet 14.46 bits; message bases 19.13 bits; total 33.59 bits;
alphabet size in [56, 83]. **Isomorph discriminator confirmed non-literal and
distributed. Odd messages attested by isomorphs, not coincidence. T2 unattested in
five channels.**

**Cumulative sweep total: 193.6 million candidates, zero survivors.**

---

## 6. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Isomorph abundance | headline figure, undecomposed | **97% non-literal**, near-dup share only 21–23%, z up to +38.3 |
| Literal isomorphs | not distinguished | **2–4 at every length** — negligible |
| Trivial all-distinct windows | not excluded in this instrument | **must be excluded** — they match everything and inflate counts ~40× |
| Odd messages E2, W4 | atlas-attested, mechanism unstated | **isomorph-rich and coincidence-poor**, measured |
| E2's role | odd message of T1 | **largest single source of non-literal isomorphs in the corpus** |
| T2 internal structure | unattested in four channels | **five channels** |

---

## 7. Horizon

1. **Audit the atlas for within-T2 classes** (FR76). Unchanged and now more pointed:
   five channels find nothing, so if the atlas contains within-T2 classes they are the
   sole support and deserve the scrutiny FR50 gave class #2.
2. **Continue the decomposition pattern.** Three cycles running (FR75, FR76, FR77) it
   has produced a finding each time, twice overturning and once confirming. Remaining
   undecomposed figures: the effective-inventory estimate and FR66's deliverable
   artifact, both reported pooled across messages and components.
3. **One crib in West 2** (FR74). Unchanged.
4. **The success criterion** (FR66, FR72, FR73). Unchanged.
