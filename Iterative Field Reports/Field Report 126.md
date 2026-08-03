# Field Report 126 — THE CROSS-BLOCK EXCESS IS WITHDRAWN

*Pre-registered test executed. July 2026. Cycle: EYESPIRAL-C.*

---

## 0. What was pre-registered, and what was wrong with it

FR125 found a cross-block short-range coincidence excess at z = +4.87 that
survived a flat shuffle and a within-block shuffle, and pre-registered a
confirming test: geometry-preserving null, ≥500 draws, one-sided, α = 0.01.

**CHALLENGE I found the pre-registered null was itself wrong.** Under the model

```
p[t] = A_block + d * v[t]        with v[t] KNOWN
```

a block's *interior* is determined, not free. Shuffling within blocks destroys
structure the model asserts is real — the FR42 error one level in.

**The only free quantity is the per-block constant `A_block`.** So the correct
null re-randomises the block constants and leaves every interior untouched:
within-block coincidences are unchanged by construction, cross-block ones are
randomised. That makes the test exactly the right question:

> **Do the model's inferred block constants produce more short-range plaintext
> coincidences than random constants would?**

Also corrected: FR125 counted **word-pattern hits across 112 heterogeneous
words** — a statistic whose value depends on an arbitrary vocabulary. The
direct measure is the cross-block coincidence *count* per distance, needing no
vocabulary.

---

## 1. Result: it does not survive

500 draws, distances 1–8, cross-block pairs only:

| distance | pairs | real | null mean | sd | z |
|---:|---:|---:|---:|---:|---:|
| 1 | 340 | 10 | 4.1 | 2.14 | **+2.73** |
| 2 | 295 | 6 | 3.5 | 1.99 | +1.24 |
| 3 | 310 | 6 | 3.8 | 2.06 | +1.08 |
| 4 | 279 | 2 | 3.4 | 1.76 | −0.80 |
| 5 | 287 | 3 | 3.6 | 1.84 | −0.34 |
| 6 | 304 | 0 | 3.7 | 2.06 | −1.79 |
| 7 | 286 | 1 | 3.3 | 1.76 | −1.32 |
| 8 | 300 | 0 | 3.6 | 1.95 | −1.85 |

```
TOTAL d=1..8 : real 28  null 29.1 ± 5.77  z = -0.19
one-sided empirical p = 292/500 = 0.584
VERDICT at alpha = 0.01 : DOES NOT SURVIVE
```

> **The FR125 excess is WITHDRAWN.** It was an artifact of the word-count
> statistic — 112 overlapping vocabulary patterns of differing span, counted
> as if independent — not a property of the plaintext.

**The model's block constants do no better than random ones at producing
short-range plaintext coincidences.**

---

## 2. A sub-threshold observation, explicitly not claimed

Distance 1 — doubled plaintext values — sits at **10 observed against 4.1
expected, z = +2.73**. Every other distance is at or below chance, and the
total is flat.

**This is not claimed.** With eight distances tested, a +2.7 at one of them is
ordinary; the pre-registration was on the total, and the total failed. Logging
it because the series logs sub-threshold observations rather than discarding
them, and because doubled letters are the one shape a Finnish-language
hypothesis would specifically predict. **Any future test of it must be
pre-registered on distance 1 alone, before looking.**

---

## 3. What this confirms

The plaintext shows **no short-range repeat enrichment** once the geometry is
correctly held fixed. That is now the fourth independent line reaching the same
place:

- FR39 — no natural-language coincidence structure
- FR41/FR42 — apparent local repeat-avoidance was a geometry artifact
- FR115 — coincidence elevation present at every candidate, hence not a reading property
- **FR126 — cross-block coincidences at chance under the correct null**

---

## 4. The methodological pattern, now nine deep

FR39, FR42, FR45, FR48, FR97, FR100, FR107, FR113 and now FR126. Every one has
the same shape: **a statistic that looks significant against a null which holds
the wrong thing fixed.** The remedy has been identical each time — ask what the
null is allowed to vary, and check it is exactly the unknown quantity.

Here the chain ran three deep: flat shuffle (wrong — destroys geometry),
within-block shuffle (wrong — destroys determined interiors), block-constant
randomisation (right — varies only the free parameter). **The first two both
showed the "signal."**

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Cross-block repeat excess | watch-grade, z = +4.87 (FR125) | **WITHDRAWN** — z = −0.19, p = 0.584 |
| FR125's pre-registered null | within-block shuffle | **wrong**; correct null randomises block constants only |
| Word-hit counting as a statistic | used in FR121/FR125 | **unsound for significance** — overlapping patterns are not independent |
| Plaintext short-range structure | open | **none**, fourth independent confirmation |
| Doubled values (d=1) | — | z = +2.73, sub-threshold, **not claimed**; needs its own pre-registration |

---

## 6. Model status

Unchanged. Repair A: 384 relations, 56 glyphs, 17 ratios, 44.5%. Repair C: 409
relations, 57 glyphs, drift forced, 66.2%, one homophone. Both conditional on
the progressive form. Cumulative: 27.16 billion candidates, zero survivors.

---

## 7. Horizon

1. **Do not re-test the excess.** It was pre-registered, executed, and failed.
   Re-running it on a different statistic would be the exact malpractice the
   pre-registration existed to prevent.
2. **Distance-1 doubling is the one live sub-threshold item**, and it is worth
   a cycle only if pre-registered on d = 1 alone, with the block-constant null,
   before any further looking.
3. **Coverage remains the binding constraint on everything constructive.**
   Word-crib power is 9.9%; raising it further needs either another bridge or
   a linking argument for the 29 remaining unlinked groups.
