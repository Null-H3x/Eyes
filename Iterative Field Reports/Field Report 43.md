# Field Report 43 — Two Hypotheses That Cannot Both Be True

**Series note.** Forty-third report of the EYESPIRAL series. FR42 recorded the success
criterion as non-computational and the drift as reachable only by external anchors. This
cycle challenges the second half of that and finds one structure never exploited.
Instrument `eyeind.py`, selftest 7/7 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** Position 0 of each message carries a distinct glyph, and under
the model q[ind_m] = base_m + label_m + K_g[0], so for two messages of one triplet whose
indicators sit in a known component with a forced base difference,
**label_m1 − label_m2 = drift · (Δ₁ − Δ₂ − w)** — a label hypothesis becomes a drift
prediction. Five of the nine indicators are inside the 56-glyph skeleton, but only **one
pair is usable**: East 3 and West 3 share component 1 and have a forced base difference,
giving **label(E3) − label(W3) = −drift**. If the nine labels are nine *consecutive*
values — the natural shape for an ordered message set — every pairwise difference lies in
[−8, +8], so the drift must be one of **sixteen values, a 5.1× narrowing**. FR5's **H1
requires drift 31, which is not among them.** The two hypotheses are therefore
**incompatible: at most one can hold.** Neither is established, and H4's narrowing rests
entirely on the consecutive-label assumption, which is a guess about the author's encoding
rather than a measurement. What is new is that the project's two structural readings now
**constrain each other** — FR34 named a second independent drift prediction as the missing
ingredient for testing the drift internally, and this is one, and it disagrees with the
first.

---

## 1. I1 — the indicator block

| message | triplet | glyph | component | Δ |
|---|---|---|---|---|
| East 1 | T1 | 50 | C1 | 8 |
| West 1 | T1 | 80 | C6 | 28 |
| East 2 | T1 | 36 | — | — |
| West 2 | T2 | 76 | — | — |
| East 3 | T2 | 63 | C1 | 31 |
| West 3 | T2 | 34 | C1 | 61 |
| East 4 | T3 | 27 | C1 | 1 |
| West 4 | T3 | 77 | — | — |
| East 5 | T3 | 33 | — | — |

All nine are distinct. Five sit inside the skeleton — a consequence of FR33's widening,
which recruited glyph 27 among others; before that, fewer were reachable.

## 2. I2 — only one pair is usable

Of the 36 indicator pairs, exactly one satisfies both requirements. The rest fail because
the indicator is outside the skeleton, or the two sit in different components (E1 in C1
against W1 in C6, where an unknown inter-component offset enters), or the pair is
cross-triplet and has no forced base difference.

**East 3 / West 3:** same component, w = 54, giving

> **label(E3) − label(W3) = drift · 82 = −drift**

## 3. I3 — the two hypotheses in contact

| hypothesis | prediction |
|---|---|
| **H1** (FR5, boundary token): q[1] − q[47] = 4 | q[1] − q[47] = 51·drift ⟹ **drift = 31** |
| **H4** (indicator labels consecutive) | drift ∈ {1…8, 75…82} — **16 of 82** |

**31 is not in H4's admissible set.** At most one of the two can hold.

## 4. I4 — what this is and is not worth

**Neither hypothesis is established.** H1 has been unfalsifiable since FR33, because its
coefficient 51 is invertible and therefore *some* drift always satisfies it — consistency
was never evidence. H4's narrowing depends wholly on the labels being consecutive, which
is a hypothesis about how the author encoded an ordered set of messages, not something
measured. If the labels are merely *distinct*, H4 says nothing and the conflict evaporates.

**What is new is the logical structure.** FR34 stated the problem precisely: H1 alone
cannot fail, so the drift becomes testable only when a second independent prediction
arrives. This is that second prediction. It arrives from a completely different part of
the corpus — the indicator block rather than the opening boundary — and it disagrees.

That converts two separately-unfalsifiable guesses into a pair with a joint consequence:
**at least one of the project's two structural readings is wrong.** That is a smaller claim
than resolving either, and it is the first of its kind here.

## 5. Where the model stands

- **384 relations over 56 glyphs**, components 25/11/7/3 plus five pairs, injectivity
  clean, 74.1% exposure.
- **Drift:** still unpinned, but now subject to two mutually inconsistent structural
  hypotheses rather than one unfalsifiable one.
- **Plaintext:** large effective inventory, no structure detected (FR36, FR39, FR40, with
  FR41 withdrawn in FR42).
- **Acquisition** remains the only route to a decisive answer.

## 6. Horizon

(1) **Attack the consecutive-label assumption.** It is the load-bearing premise of H4 and
the cheapest thing to test: if the indicator glyphs were drawn from a structured set, some
independent trace of that should exist — their frequencies, positions in the depth tree,
or relation to the universal header at positions 1–2. (2) **Re-examine H1's provenance.**
It has been carried since FR5 on a crib reading and has never been independently
supported; if H4 is preferred, H1 should be retired rather than left standing. (3) Two
external anchors in component 1 would settle both at once.

## 7. Reproduction

`eyeind.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
7-check gate — the indicator algebra verified on synthetic data with known labels and
drift, the nine indicators confirmed distinct, exactly one usable pair, H1 expressible and
selecting one drift, the consecutive-label narrowing computed, and the incompatibility
asserted, plus the baseline guard. The full run reproduces I1–I4. Failures carry prefix
`XD-MBYG04K-URS3LF`.
