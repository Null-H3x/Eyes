# Field Report 171 — COMMUNITY DOCUMENTS: BASE-7 RESOLVED, FIVE OBSERVATIONS CONFIRMED, AND AN INDEPENDENT WITNESS AGAINST EAST 1

*July 2026. Cycle: EYESPIRAL-C. External source review.*

---

## 0. Base-7 resolved — and both of us were right

From the decompilation guide:

> *The engine performs repeated 64-bit division by 7, finding digits in base 7,
> subtracting 1... base 7 is needed to represent 5 symbols and newlines instead
> of base 6 because it needs a padding symbol (which is 0).*

```
base-7 digit   0 = PADDING (dropped)
               1..5 -> subtract 1 -> 0..4 = the five eye sprites
               6    -> subtract 1 -> 5    = NEWLINE
```

**Base-7 is the storage layer; base-5 trigrams are the glyph layer.** No
conflict, no lossy conversion, and FR101's base-5 finding stands — it was
answering a different question than the engine's arithmetic.

**My worry was unfounded but the check was not wasted**: it exposed that the
modulus 83 is *not* pinned by the constraint analysis at all (every prime 83–149
gives identical results — 55 pivots, 384 relations). It is pinned empirically,
by 1,036 positions using exactly 83 values with none missing.

---

## 1. Five community observations, checked directly

```
1. 'a trigram never follows itself'      : 0 adjacent repeats     CONFIRMED
2. repeat-gap counts (gaps 0..6)         : [0, 5, 9, 26, 11, 12, 12]
   community: gap0=0, gap1=5, gap3=26                             CONFIRMED
3. 'some messages have prime length'     : 103, 137               CONFIRMED
4. pattern a_b_cb_ac in E1/W1/E2         : exactly 6              CONFIRMED
5. pattern ab_c____b_ac in E4/W4/E5      : exactly 3              CONFIRMED
```

**Our corpus reproduces the community's independent observations exactly.** The
transcription chain is verified end-to-end from a second direction.

Also reconciled: the community counts **1,027** symbols to our **1,036**. The
difference is exactly **9** — the per-message indicators, which they exclude and
we include.

---

## 2. The thread worth pulling

Lymm reports the six `a_b_cb_ac` instances, of which **"four can be extended"**
to a longer 18-glyph pattern. My first search found zero — because the
community's letter convention is not first-occurrence (`x` precedes `a`).
Matching on **equality structure** instead:

```
x_____ayb_cb_ac_yx  ->  West 1@34, West 1@64, East 2@39, East 2@74
```

Four hits, exactly as stated. And **which** four is the finding:

```
East 1 @ 40   DOES NOT EXTEND
East 1 @ 68   DOES NOT EXTEND
West 1 @ 40   extends (offset 6)
West 1 @ 70   extends (offset 6)
East 2 @ 45   extends (offset 6)
East 2 @ 80   extends (offset 6)
```

> **The two instances that fail to extend are East 1's — including East 1@68,
> the instance the entire repair fork was built around and which repair C
> discards.**

The community flagged East 1's anomaly from **pattern geometry** in a
public document, independently of FR2's structural anomaly, FR6's four-cycle
contradiction, FR21's injectivity localisation and FR25's minimal cores — all of
which found it from **constraint contradictions**.

That is a **sixth independent line** converging on East 1, and the first from
outside this project.

---

## 3. What it does not do

The long class is already in our 208-class inventory (at L=23, k=5, **surprise
7.25** — far above #M⁻'s 1.70), and adding it changes nothing: **384 relations,
56 glyphs, 0 equalities, unchanged.** It is consistent and fully redundant.

So it is **corroboration, not new information** — which is itself worth having,
since FR146's adoption of 19 non-atlas classes rested on mutual prediction
rather than external agreement.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Base-7 vs base-5 | apparent conflict | **resolved** — storage vs glyph layer, both correct |
| Modulus 83 | assumed established by the model | **not pinned by constraints**; pinned empirically |
| Corpus transcription | validated against journal entries | **also reproduces 5 independent community observations** |
| 1027 vs 1036 | unexplained | **the 9 message indicators** |
| East 1's anomaly | five internal lines | **six** — the sixth external, from pattern geometry |
| Lymm's long pattern | unmatched (wrong convention) | **found**, 4 instances, surprise 7.25, fully redundant |

---

## 5. Model status

Unchanged and better corroborated: 794 relations, 61 glyphs, 79.1% exposure,
435-position reading, 68 maximal readings, two invariant cores, stamped header
forced, plaintext inventory ~83. Cumulative: 27.16 billion candidates, zero
survivors.

---

## 6. Horizon

1. **The `x_____ayb_cb_ac_yx` asymmetry deserves to go back to the community**
   as the cleanest statement of the East 1 problem: it is visible without any
   cipher model at all, from pattern extension alone.
2. **Remaining community material is unread** — `Grand_Glyph_Documentation.md`
   is 2.5 MB and the Emerald Tablet directory is unexamined. Both may contain
   further checks.
3. **Convention-free matching should be standard** when reading external
   pattern claims. My first search returned zero purely from a labelling
   difference, and I nearly recorded a discrepancy that did not exist.
