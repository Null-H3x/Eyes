# Field Report 134 — THE WORD-CRIB ROUTE IS CLOSED: 0.32% POWER

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The measurement FR132 called for

FR132 predicted word-crib power against the corrected reading would be "near
zero" and said it should be measured rather than assumed. Measured:

| word | k | span | testable | possible | power |
|---|---:|---:|---:|---:|---:|
| KYSYMYS | 3 | 7 | 5 | 744 | **0.67%** |
| KAIKKI | 3 | 6 | 5 | 751 | 0.67% |
| KALEVALA | 3 | 8 | 4 | 737 | 0.54% |
| MAAILMA | 3 | 7 | 3 | 744 | 0.40% |
| TOSITIETO | 4 | 9 | 1 | 730 | 0.14% |
| VÄINÄMÖINEN | 4 | 11 | **0** | 716 | **0.00%** |
| LEMMINKÄINEN | 5 | 12 | **0** | 709 | **0.00%** |

```
words with any testable placement : 16 of 18
MEAN POWER                        : 0.32%
```

**Progression of the claim:**

```
FR121 (repair A, v-based, claimed) : 6.3%
FR125 (repair C, v-based, claimed) : 9.9%
FR134 (corrected, p-based, REAL)   : 0.32%
```

> **A word that IS in the corpus would be detected with probability 0.32%.**
> Roughly three hundred correct guesses would be needed to expect one
> detection. **The word-crib route is closed**, and closed on measurement.

It is closed for a specific reason worth stating: not because the vocabulary is
wrong, but because the determined region is too small and too fragmented. And
raising it enough would require the coverage that solving the cipher provides —
**the route needs the answer it is meant to find.**

---

## 1. Stale tooling retired

Four instruments consume withdrawn `v`-based readings and would silently test
undetermined positions. All now carry a withdrawal banner:

```
eyehypo.py    -- FR119/FR123 v-based readings
eywordsC.py   -- FR123 v-based repair-C structure
eyedouble.py  -- FR129 v-based consensus sites
eyereveal.py  -- produces the withdrawn CANDIDATE_READINGS.txt
```

`eyeplain.py` (FR132) is the only valid reading instrument.

---

## 2. Where the constructive arc ended up

EYESPIRAL-C was adopted at FR119 because 118 cycles had produced no artifact.
Sixteen cycles later, honestly:

**Produced and standing:**
- `PLAINTEXT_RELATIVE.txt` — 191 positions, `A_block` solved, zero conflicts,
  drift-invariant. **The project's first valid relative decryption.**
- `REPAIR_RANKING.md` — 62 repairs, 32 readings, ranked by evidential cost.
- `eyecrib.py` / `eyemodel.py` — the external verifier.
- `HYPOTHESIS_CATALOG.md`, `eye_corpus_viewer.html`.
- **Repair C** — rank 1 of 62, found by systematic search.
- **Bijectivity ⟺ no T1**, proven by exhaustion.

**Produced and withdrawn:**
- FR119, FR123's readings (built on `v`).
- FR125's coincidence excess (wrong null).
- FR127's "better repair" (wrong objective function).
- FR129's crib targets, FR130's doubled sites (undetermined positions).

**The score is roughly even, and that is the honest summary of the
constructive turn:** it produced real artifacts and an equal number of
retractions, at a much higher rate of both than the sixteen cycles before it.

---

## 3. What the plaintext work established, cumulatively

Six independent lines, no repeat structure anywhere:

| finding | source |
|---|---|
| no language coincidence structure | FR39 |
| local repeat-avoidance was geometry | FR41/42 |
| coincidence elevation at every candidate | FR115 |
| no cross-block short-range excess (correct null) | FR126 |
| nearest within-message repeat at distance 11, all geometric | FR132 |
| 179 discovered cross-message pairs form ONE run — the opening | FR133 |
| **word cribs undetectable at 0.32% power** | **FR134** |

**The plaintext, where this project can see it, is featureless — and the region
where it can be seen is too small to test hypotheses against.**

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Word-crib power | 6.3% / 9.9% (both `v`-based) | **0.32%** |
| Word-crib route | weak but live | **CLOSED on measurement** |
| Stale instruments | runnable | **banner-marked withdrawn** |
| Valid reading instrument | several | **`eyeplain.py` only** |
| Why the route fails | "coverage" | **needs the coverage that solving provides** — circular |

---

## 5. Model status

Unchanged. 409 relations, 57 glyphs under repair C (rank 1 of 62); relative
plaintext 191 positions (18.4%); acquisition 11 anchors or a 15-token crib;
`q[36]=q[68]` forced in every high-coverage repair. Cumulative: 27.16 billion
candidates, zero survivors.

---

## 6. Horizon

1. **Internal constructive work is exhausted.** The reading is built and
   correct; the plaintext has no structure to exploit; hypotheses cannot be
   tested at 0.32% power. Further cycles on this line would re-cover swept
   ground.
2. **Acquisition is untouched by all of it** — it depends on the skeleton, not
   the reading. Eleven anchors or fifteen crib tokens still solve the cipher
   regardless of how unreadable the result proves.
3. **`q[36] = q[68]` remains the single sharpest external test**: forced by
   every high-coverage repair, so one anchor on either glyph adjudicates the
   whole non-bijective family.
